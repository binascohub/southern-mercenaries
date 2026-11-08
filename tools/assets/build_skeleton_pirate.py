"""Esqueleto Pirata das Docas ("Skeleton Pirate \\"The Captin\\"", FireGoat na Sketchfab, CC BY 4.0; arquivo trazido pelo autor do projeto): esqueleto de pirata
de chapéu, casaca, sabre na mão direita e perna de pau, 60 mil triângulos, esqueleto próprio de 72 ossos (em centímetros, ~24 m de altura no arquivo),
6 texturas e só a animação de correr ("RunningAtPlayerAnimation"; a pose de repouso já é meio agachada).
Aqui:
 - a malha é reduzida (~24 mil triângulos) e as texturas vão a 1024 px;
 - os movimentos dos heróis (Universal Animation Library, hero_male.glb) passam para o esqueleto dele quadro a quadro: idle (Sword_Idle, de sabre em
   guarda), walk (Walk_Loop), run (Jog_Fwd_Loop), attack (Sword_Regular_A e a volta à guarda; o Sword_Attack é um golpe com salto), hit (Hit_Chest) e die (Death01). Cada osso copia a orientação no
   mundo do osso do herói depois de alinhar as direções de repouso (os dois repousos são diferentes); o quadril copia a posição, na proporção das pernas;
   a corrida também é a dos heróis (Jog_Fwd_Loop): a do arquivo sai deitada depois de exportada;
 - o conjunto fica na escala de ~1,9 m, de pé no chão, olhando para -Y (+Z no glTF, a frente dos monstros no jogo).
Vai para assets/models/monsters/skeleton_pirate.glb (game/actors/monster_model.gd, família "skeleton_pirate").
uso: blender -b --python tools/assets/build_skeleton_pirate.py -- <skeleton_pirate__the_captin.glb> <hero_male.glb> <saída.glb>"""
import bpy, sys
from mathutils import Matrix, Vector

src, hero_path, out = sys.argv[sys.argv.index("--") + 1:][:3]
TARGET_TRIS = 24000
MAX_TEX = 1024
CLIPS = {"idle": "Sword_Idle", "walk": "Walk_Loop", "run": "Jog_Fwd_Loop", "attack": ["Sword_Regular_A", "Sword_Regular_A_Rec"], "hit": "Hit_Chest", "die": "Death01"}
MAP = {"pelvis": "Pelvis_02", "spine_01": "Spine3_03", "spine_02": "Spine2_04", "spine_03": "Spine1_05", "neck_01": "neck_06", "Head": "Headbase_07",
       "clavicle_r": "R_collar_013", "upperarm_r": "R_shoulder_014", "lowerarm_r": "R_forarm_015", "hand_r": "HandleBone_019",
       "clavicle_l": "L_Collar_031", "upperarm_l": "L_shoulder_032", "lowerarm_l": "L_forarm_033",
       "thigh_l": "L_leg_050", "calf_l": "L_knee_051", "foot_l": "L_foot_052", "thigh_r": "R_leg_053", "calf_r": "R_Knee_054", "foot_r": "R_foot_055"}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in list(bpy.data.objects):
    if o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)
rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
bodies = [o for o in bpy.data.objects if o.type == "MESH"]
for a in list(bpy.data.actions):  # a corrida do arquivo sai deitada no glTF exportado (gira o osso raiz): fica a dos heróis
    bpy.data.actions.remove(a)
rig.animation_data_create()
rig.animation_data.action = None

# Malha mais leve (o modificador de esqueleto continua depois do Decimate).
total = sum(len(o.data.polygons) for o in bodies)
for o in bodies:
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    mod = o.modifiers.new("dec", "DECIMATE")
    mod.ratio = min(1.0, TARGET_TRIS / total)
    bpy.ops.object.modifier_move_to_index(modifier="dec", index=0)
    bpy.ops.object.modifier_apply(modifier="dec")
for image in bpy.data.images:
    w, h = image.size
    if max(w, h) > MAX_TEX:
        image.scale(max(1, w * MAX_TEX // max(w, h)), max(1, h * MAX_TEX // max(w, h)))
for o in bodies:
    for m in o.modifiers:
        m.show_viewport = False  # mais rápido durante o retarget

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


def length(obj, names):
    return sum((obj.matrix_world.to_3x3() @ (obj.data.bones[n].tail_local - obj.data.bones[n].head_local)).length for n in names)


# Correção fixa por osso: P = R_herói_pose · R_herói_repouso⁻¹ · Q · R_pirata_repouso (Q leva a direção de repouso do pirata à do herói:
# com o herói em repouso, o osso do pirata aponta para onde aponta o do herói).
CORR = {}
for h, t in MAP.items():
    hb, tb = hero.data.bones[h], rig.data.bones[t]
    q = dir_world(rig, tb).rotation_difference(dir_world(hero, hb)).to_matrix()
    CORR[t] = rot_world(hero, hb.matrix_local).inverted() @ q @ rot_world(rig, tb.matrix_local)
ORDER = [b.name for b in rig.data.bones if b.name in CORR]
K = length(rig, ["L_leg_050", "L_knee_051"]) / length(hero, ["thigh_l", "calf_l"])  # unidades do pirata por metro do herói
rig_root = rig.matrix_world @ rig.data.bones["Root_01"].head_local
rig_inv = rig.matrix_world.inverted()
rig_rot_inv = rig.matrix_world.to_3x3().normalized().inverted()
print("K", round(K, 1))
for p in rig.pose.bones:
    p.rotation_mode = "QUATERNION"


def retarget():
    for p in rig.pose.bones:
        p.rotation_quaternion = (1, 0, 0, 0)
        p.location = (0, 0, 0)
    bpy.context.view_layer.update()
    for t in ORDER:
        h = next(k for k, v in MAP.items() if v == t)
        target = rot_world(hero, hero.pose.bones[h].matrix) @ CORR[t]
        pb = rig.pose.bones[t]
        head = pb.matrix.to_translation()
        if t == "Pelvis_02":
            hp = hero.matrix_world @ hero.pose.bones["pelvis"].head
            world = Vector((rig_root.x + hp.x * K, rig_root.y + hp.y * K, hp.z * K))
            head = rig_inv @ world
        pb.matrix = Matrix.Translation(head) @ (rig_rot_inv @ target).to_4x4()
        bpy.context.view_layer.update()


for out_name, src_names in CLIPS.items():
    new = bpy.data.actions.new(out_name)
    new.use_fake_user = True
    out_frame = 0
    for src_name in ([src_names] if isinstance(src_names, str) else src_names):  # uma lista vira um clipe só, em sequência
        action_src = next(a for a in bpy.data.actions if a.name.split("|")[-1] == src_name)
        hero.animation_data.action = action_src
        if action_src.slots:
            hero.animation_data.action_slot = action_src.slots[0]
        rig.animation_data.action = new
        f0, f1 = int(action_src.frame_range[0]), int(action_src.frame_range[1])
        for f in range(f0, f1 + 1):
            scene.frame_set(f)
            retarget()
            for t in ORDER:
                rig.pose.bones[t].keyframe_insert("rotation_quaternion", frame=out_frame)
            rig.pose.bones["Pelvis_02"].keyframe_insert("location", frame=out_frame)
            out_frame += 1
    print("clipe", out_name, "<-", src_names, out_frame, "quadros")

hero.animation_data.action = None
for a in list(bpy.data.actions):
    if a.name not in CLIPS:
        bpy.data.actions.remove(a)
bpy.data.objects.remove(hero, do_unlink=True)
for o in bodies:
    for m in o.modifiers:
        m.show_viewport = True
for p in rig.pose.bones:
    p.rotation_quaternion = (1, 0, 0, 0)
    p.location = (0, 0, 0)
rig.animation_data.action = bpy.data.actions["idle"]
# Escala: as pernas do pirata viram as do herói (K unidades = 1 m) e o conjunto vai ao chão, centrado.
top = rig
while top.parent:
    top = top.parent
top.matrix_world = Matrix.Scale(1.0 / K, 4) @ top.matrix_world
bpy.context.view_layer.update()
top.matrix_world = Matrix.Translation(Vector((-rig_root.x / K, -rig_root.y / K, 0.0))) @ top.matrix_world
print("tris", sum(len(o.data.polygons) for o in bodies), "ações", [a.name for a in bpy.data.actions])
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_animations=True, export_animation_mode="ACTIONS",
                          export_image_format="WEBP", export_image_quality=85)
