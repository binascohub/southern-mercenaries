"""Moça dançando no quarto do rei (Capital, sala king_bedroom): "Bouncy Beach babe walking in bikini (animated)", Jungle Jim na Sketchfab, CC BY 4.0
(arquivo trazido pelo autor do projeto). Personagem do Character Creator (esqueleto CC_Base de ~100 ossos), de biquíni, que no arquivo só caminha.
Aqui ela é limpa e reduzida como as que andam (tools/assets/build_walking_npc.py: ~40 mil triângulos, texturas de 512 px) e ganha a dança da heroína
(Dance_Loop de hero_female.glb, Universal Animation Library), passada para o esqueleto dela quadro a quadro: cada osso copia a orientação no mundo do osso
da heroína (nos braços, depois de alinhar as direções de repouso); o quadril copia a posição, na proporção das pernas. A caminhada do arquivo fica como "walk";
a dança é "dance" e a primeira pose dela é "idle". Fica com ~1,7 m, de pé no chão, olhando para -Y (+Z no glTF).
Vai para assets/models/characters/<nome>.glb (game/actors/npc_model.gd).
uso: blender -b --python tools/assets/build_dancing_npc.py -- <arquivo.glb> <hero_female.glb> <saída.glb>"""
import bpy, re, sys
import numpy as np
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index("--") + 1:]
src, hero_path, out = args[:3]
drop = []
TARGET_TRIS = 40000
MAX_TEX = 512
HEIGHT = 1.7
DANCE = "Dance_Loop"
# herói -> osso do Character Creator (sem o número do fim, que muda de arquivo para arquivo)
MAP = {"pelvis": "Hip", "spine_01": "Waist", "spine_02": "Spine01", "spine_03": "Spine02", "neck_01": "NeckTwist01", "Head": "Head",
       "clavicle_l": "L_Clavicle", "upperarm_l": "L_Upperarm", "lowerarm_l": "L_Forearm", "hand_l": "L_Hand",
       "clavicle_r": "R_Clavicle", "upperarm_r": "R_Upperarm", "lowerarm_r": "R_Forearm", "hand_r": "R_Hand",
       "thigh_l": "L_Thigh", "calf_l": "L_Calf", "foot_l": "L_Foot", "ball_l": "L_ToeBase",
       "thigh_r": "R_Thigh", "calf_r": "R_Calf", "foot_r": "R_Foot", "ball_r": "R_ToeBase"}

bpy.ops.wm.read_factory_settings(use_empty=True)
# O repouso vem das matrizes de "bind" do arquivo: com o palpite do importador, os ossos do Character Creator ficam desmontados (quadril e canela no mesmo ponto).
bpy.ops.import_scene.gltf(filepath=src, guess_original_bind_pose=False, bone_heuristic="TEMPERANCE")
rig = max((o for o in bpy.data.objects if o.type == "ARMATURE"), key=lambda o: len(o.data.bones))
doomed = set()
for o in bpy.data.objects:
    skinned_to = next((m.object for m in o.modifiers if m.type == "ARMATURE" and m.object), None) if o.type == "MESH" else None
    if skinned_to is not None and skinned_to is not rig:
        doomed.add(o.name)  # a placa do "shadow catcher" (o esqueleto pequeno fica: às vezes é o pai de tudo)
    elif o.name.startswith("Icosphere") or o.name in drop:
        doomed.add(o.name)
for name in doomed:
    bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
bodies = [o for o in bpy.data.objects if o.type == "MESH"]
total = sum(len(o.data.polygons) for o in bodies)
ratio = min(1.0, TARGET_TRIS / total)
for o in bodies:
    if len(o.data.polygons) < 600:
        continue  # olhos, lágrimas, língua: pequenos demais para reduzir
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    o.shape_key_clear()  # expressões do rosto: não são usadas, e o Decimate não aceita malha com shape keys
    mod = o.modifiers.new("dec", "DECIMATE")
    mod.ratio = ratio
    bpy.ops.object.modifier_move_to_index(modifier="dec", index=0)
    bpy.ops.object.modifier_apply(modifier="dec")
for image in bpy.data.images:
    w, h = image.size
    if max(w, h) > MAX_TEX:
        image.scale(max(1, w * MAX_TEX // max(w, h)), max(1, h * MAX_TEX // max(w, h)))
print("triângulos", total, "->", sum(len(o.data.polygons) for o in bodies))


walk = max(bpy.data.actions, key=lambda a: a.frame_range[1] - a.frame_range[0])
for a in list(bpy.data.actions):
    if a is not walk:
        bpy.data.actions.remove(a)
walk.name = "walk"
walk.use_fake_user = True
rig.animation_data_create()
rig.animation_data.action = None
names = {}
for b in rig.data.bones:
    m = re.match(r"CC_Base_(.+)_\d+$", b.name)
    if m:
        names.setdefault(m.group(1), b.name)
MAP = {h: names[c] for h, c in MAP.items() if c in names}
print("ossos ligados", len(MAP))
for o in bodies:
    for m in o.modifiers:
        m.show_viewport = False

bpy.ops.import_scene.gltf(filepath=hero_path)
hero = next(o for o in bpy.data.objects if o.type == "ARMATURE" and o is not rig)
for o in list(bpy.data.objects):
    if o.type == "MESH" and o not in bodies:
        bpy.data.objects.remove(o, do_unlink=True)
hero.animation_data_create()
scene = bpy.context.scene
scene.frame_set(0)
bpy.context.view_layer.update()


def rot_world(obj, m4):
    return (obj.matrix_world @ m4).to_3x3().normalized()


def dir_world(obj, bone):
    return (obj.matrix_world.to_3x3() @ (bone.tail_local - bone.head_local)).normalized()


def length(obj, bones):
    return sum((obj.matrix_world.to_3x3() @ (obj.data.bones[n].tail_local - obj.data.bones[n].head_local)).length for n in bones)


# P = R_herói_pose · R_herói_repouso⁻¹ · Q · R_moça_repouso (nos braços, Q leva a direção de repouso do osso dela à do osso da heroína).
CORR = {}
for h, t in MAP.items():
    hb, tb = hero.data.bones[h], rig.data.bones[t]
    # Só os braços alinham o repouso (A-pose x T-pose); tronco, cabeça e pernas já estão de pé nos dois (e a ponta do osso da cabeça às vezes vai
    # para um brinco, o que viraria a cabeça).
    arm = h.startswith(("clavicle", "upperarm", "lowerarm", "hand"))
    q = dir_world(rig, tb).rotation_difference(dir_world(hero, hb)).to_matrix() if arm else Matrix.Identity(3)
    CORR[t] = rot_world(hero, hb.matrix_local).inverted() @ q @ rot_world(rig, tb.matrix_local)
BACK = {t: h for h, t in MAP.items()}
ORDER = [b.name for b in rig.data.bones if b.name in CORR]
K = length(rig, [MAP["thigh_l"], MAP["calf_l"]]) / length(hero, ["thigh_l", "calf_l"])
hip = MAP["pelvis"]
hip_rest = rig.matrix_world @ rig.data.bones[hip].head_local
hero_rest = hero.matrix_world @ hero.data.bones["pelvis"].head_local
rig_inv = rig.matrix_world.inverted()
rig_rot_inv = rig.matrix_world.to_3x3().normalized().inverted()
for p in rig.pose.bones:
    p.rotation_mode = "QUATERNION"
dance_src = next(a for a in bpy.data.actions if a.name.split("|")[-1] in (DANCE, DANCE.replace("_Loop", "")))
hero.animation_data.action = dance_src
if dance_src.slots:
    hero.animation_data.action_slot = dance_src.slots[0]
dance = bpy.data.actions.new("dance")
dance.use_fake_user = True
rig.animation_data.action = dance
f0, f1 = int(dance_src.frame_range[0]), int(dance_src.frame_range[1])
for f in range(f0, f1 + 1):
    scene.frame_set(f)
    for p in rig.pose.bones:
        p.rotation_quaternion = (1, 0, 0, 0)
        p.location = (0, 0, 0)
    bpy.context.view_layer.update()
    for t in ORDER:
        target = rot_world(hero, hero.pose.bones[BACK[t]].matrix) @ CORR[t]
        pb = rig.pose.bones[t]
        head = pb.matrix.to_translation()
        if t == hip:
            disp = (hero.matrix_world @ hero.pose.bones["pelvis"].head) - hero_rest
            head = rig_inv @ (hip_rest + disp * K)
        pb.matrix = Matrix.Translation(head) @ (rig_rot_inv @ target).to_4x4()
        bpy.context.view_layer.update()
    for t in ORDER:
        rig.pose.bones[t].keyframe_insert("rotation_quaternion", frame=f - f0)
    rig.pose.bones[hip].keyframe_insert("location", frame=f - f0)
print("dança", f1 - f0 + 1, "quadros, K", round(K, 3))
scene.frame_set(f0)
idle = bpy.data.actions.new("idle")
idle.use_fake_user = True
pose = {p.name: (p.location.copy(), p.rotation_quaternion.copy()) for p in rig.pose.bones}
rig.animation_data.action = idle
for p in rig.pose.bones:
    p.location, p.rotation_quaternion = pose[p.name]
    p.keyframe_insert("location", frame=0)
    p.keyframe_insert("rotation_quaternion", frame=0)
hero.animation_data.action = None
for a in list(bpy.data.actions):
    if a.name not in ("walk", "dance", "idle"):
        bpy.data.actions.remove(a)
bpy.data.objects.remove(hero, do_unlink=True)
for o in bodies:
    for m in o.modifiers:
        m.show_viewport = True

rig.animation_data.action = idle
scene.frame_set(0)
dg = bpy.context.evaluated_depsgraph_get()
pts = np.concatenate([np.array([o.matrix_world @ v.co for v in o.evaluated_get(dg).to_mesh().vertices]) for o in bodies])
mn, mx = pts.min(0), pts.max(0)
k = HEIGHT / (mx[2] - mn[2])
top = rig
while top.parent:
    top = top.parent
top.matrix_world = Matrix.Translation(Vector((-(mn[0] + mx[0]) / 2 * k, -(mn[1] + mx[1]) / 2 * k, -mn[2] * k))) @ Matrix.Scale(k, 4) @ top.matrix_world
print("escala", round(k, 4))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_animations=True, export_animation_mode="ACTIONS",
                          export_image_format="AUTO", export_image_quality=82)
