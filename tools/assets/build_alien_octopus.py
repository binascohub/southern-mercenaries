"""Polvo Abissal das Docas, no lugar do Espantalho Afogado ("Alien Octopus", agasherev, Sketchfab, CC BY 4.0; arquivo trazido pelo autor).
O arquivo: bípede de ~2,27 m com cabeça de polvo e armadura, esqueleto de 208 ossos, 32 mil triângulos, 17 texturas de 1024 px e uma animação
(Take 001, ~4 s: anda curvado esticando os braços).
Aqui: a esfera de desenhar ossos sai, as malhas são reduzidas (DECIMATE) a ~0,4, as texturas a 512 px (WEBP), a animação vira "idle" (o jogo a usa
para parar, andar e atacar; sem morte: chave no objeto do esqueleto, como no pirata, estraga a exportação deste arquivo, e o corpo só afunda). O modelo
olha para -X no Blender: é virado (só no vazio do topo) para -Y = +Z no glTF, a frente no jogo; pés em y = 0. O jogo usa a escala 1/2,27.
A animação do arquivo vira "walk" (o jogo a usa para andar e correr). Com o hero_male.glb (Universal Animation Library), os movimentos dos heróis passam
para o tronco, os braços e a cabeça dele quadro a quadro, como no Esqueleto Pirata (tools/assets/build_skeleton_pirate.py): idle (Zombie_Idle_Loop),
attack (Zombie_Scratch), hit (Hit_Chest) e die (Death01). As pernas (de joelho invertido, não servem as dos heróis), os tentáculos, a armadura e os dedos
ficam na pose do primeiro quadro do arquivo; o quadril recebe o giro do quadril do herói e, só na morte, também o deslocamento (o corpo todo tomba).
uso: blender -b -P tools/assets/build_alien_octopus.py -- <alien_octopus.glb> <saída: assets/models/monsters/alien_octopus.glb> [hero_male.glb]"""
import bpy, sys, math
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[:2]
hero_path = args[2] if len(args) > 2 else "assets/models/characters/hero_male.glb"
CLIPS = {"idle": "Zombie_Idle_Loop", "attack": "Zombie_Scratch", "hit": "Hit_Chest", "die": "Death01"}
MAP = {"pelvis": "Pelvis_02", "spine_01": "spine_03", "spine_03": "spine1_04", "neck_01": "neck_05", "Head": "head_06",
       "clavicle_r": "clavicle_R_042", "upperarm_r": "uper_arm_R_048", "lowerarm_r": "forearm_R_050",
       "clavicle_l": "clavicle_L_082", "upperarm_l": "uper_arm_L_0106", "lowerarm_l": "forearm_L_0108"}
RATIO = 0.4
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in [o for o in bpy.data.objects if o.type == "MESH" and o.parent is None]:
    bpy.data.objects.remove(o, do_unlink=True)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
top = arm
while top.parent:
    top = top.parent
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
for o in meshes:
    bpy.context.view_layer.objects.active = o
    if o.data.shape_keys:
        o.shape_key_clear()
    mod = o.modifiers.new("dec", "DECIMATE")
    mod.ratio = RATIO
    while o.modifiers.find("dec") > 0:
        bpy.ops.object.modifier_move_up(modifier="dec")
    bpy.ops.object.modifier_apply(modifier="dec")
for img in bpy.data.images:
    if img.size[0] > 512:
        img.scale(512, 512)
walk = bpy.data.actions[0]
walk.name = "walk"
walk.use_fake_user = True

# de frente para -Y (era -X): giro de +90 graus em volta de Z, e pés no chão
bpy.context.scene.frame_set(0)
top.matrix_world = Matrix.Rotation(math.pi / 2, 4, "Z") @ top.matrix_world
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
pts = [o.matrix_world @ v.co for o in meshes for v in o.evaluated_get(deps).to_mesh().vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
top.matrix_world = Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))) @ top.matrix_world
bpy.context.view_layer.update()
height = mx.z - mn.z

# --- movimentos dos heróis (como em build_skeleton_pirate.py): cada osso do par copia a orientação no mundo do osso do herói, depois de alinhar as
# direções de repouso; o quadril copia a posição, na proporção das pernas. Os outros ossos ficam na pose do quadro 0 do arquivo.
scene = bpy.context.scene
scene.frame_set(0)
base_pose = {p.name: p.matrix_basis.copy() for p in arm.pose.bones}
# A caminhada do arquivo só tem chaves em parte dos ossos: os outros pegariam a pose que sobrasse das outras ações. Ganha chave em todos, quadro a quadro.
for p in arm.pose.bones:
    p.rotation_mode = "QUATERNION"
w0, w1 = int(walk.frame_range[0]), int(walk.frame_range[1])
walk_frames = []
for f in range(w0, w1 + 1):
    scene.frame_set(f)
    walk_frames.append({p.name: p.matrix_basis.copy() for p in arm.pose.bones})
for f, pose in zip(range(w0, w1 + 1), walk_frames):
    for p in arm.pose.bones:
        p.matrix_basis = pose[p.name]
        for path in ("location", "rotation_quaternion", "scale"):
            p.keyframe_insert(path, frame=f)
arm.animation_data.action = None
bpy.ops.import_scene.gltf(filepath=hero_path)
hero = next(o for o in bpy.data.objects if o.type == "ARMATURE" and o is not arm)
for o in list(bpy.data.objects):
    if o.type == "MESH" and o not in meshes:
        bpy.data.objects.remove(o, do_unlink=True)
hero.animation_data_create()
for p in arm.pose.bones:
    p.rotation_mode = "QUATERNION"
    p.matrix_basis = base_pose[p.name]
scene.frame_set(0)
bpy.context.view_layer.update()


def rot_world(obj, m4):
    return (obj.matrix_world @ m4).to_3x3().normalized()


def dir_world(obj, bone):
    return (obj.matrix_world.to_3x3() @ (bone.tail_local - bone.head_local)).normalized()


def length(obj, names):
    return sum((obj.matrix_world.to_3x3() @ (obj.data.bones[n].tail_local - obj.data.bones[n].head_local)).length for n in names)


# O repouso deste esqueleto não bate com a malha (as pernas ficam 6 m abaixo do corpo) e os ossos têm escala na pose: a referência dele é a pose do
# quadro 0 do arquivo, de pé, e a escala de cada osso fica. Nos membros, a direção vai de uma junta à seguinte (a ponta dos ossos do arquivo não segue
# o membro); quadril, tronco, clavículas e cabeça só recebem o giro do herói a partir do repouso dele.
LIMBS = {"uper_arm_R_048": ("forearm_R_050", "lowerarm_r"), "forearm_R_050": ("forearm_twist_01_R_052", "hand_r"),
         "uper_arm_L_0106": ("forearm_L_0108", "lowerarm_l"), "forearm_L_0108": ("forearm_twist_01_L_0110", "hand_l")}


def pos_arm(name):
    return arm.matrix_world @ arm.pose.bones[name].head


def pos_hero(name):
    return hero.matrix_world @ hero.data.bones[name].head_local


CORR = {}
for h, t in MAP.items():
    hb, pb = hero.data.bones[h], arm.pose.bones[t]
    q = Matrix.Identity(3)
    if t in LIMBS:
        nxt, hero_nxt = LIMBS[t]
        q = (pos_arm(nxt) - pos_arm(t)).normalized().rotation_difference((pos_hero(hero_nxt) - pos_hero(h)).normalized()).to_matrix()
    CORR[t] = rot_world(hero, hb.matrix_local).inverted() @ q @ rot_world(arm, pb.matrix)
SCALE = {t: arm.pose.bones[t].matrix.to_scale() for t in MAP.values()}
ORDER = [b.name for b in arm.data.bones if b.name in CORR]
K = pos_arm("Pelvis_02").z / pos_hero("pelvis").z  # altura do quadril dele por metro do herói
PELVIS_BASE, PELVIS_HERO = pos_arm("Pelvis_02"), pos_hero("pelvis")
arm_inv = arm.matrix_world.inverted()
arm_rot_inv = arm.matrix_world.to_3x3().normalized().inverted()
print("K", round(K, 2))


def retarget(move_pelvis):
    for p in arm.pose.bones:
        p.matrix_basis = base_pose[p.name]
    bpy.context.view_layer.update()
    for t in ORDER:
        h = next(k for k, v in MAP.items() if v == t)
        target = rot_world(hero, hero.pose.bones[h].matrix) @ CORR[t]
        pb = arm.pose.bones[t]
        head = pb.matrix.to_translation()
        if t == "Pelvis_02" and move_pelvis:  # só na morte o quadril sai do lugar (as pernas paradas não acompanham agachar)
            hp = hero.matrix_world @ hero.pose.bones["pelvis"].head
            head = arm_inv @ (PELVIS_BASE + (hp - PELVIS_HERO) * K)
        pb.matrix = Matrix.Translation(head) @ (arm_rot_inv @ target).to_4x4() @ Matrix.Diagonal(SCALE[t].to_4d())
        bpy.context.view_layer.update()


for out_name, src_name in CLIPS.items():
    new = bpy.data.actions.new(out_name)
    new.use_fake_user = True
    action_src = next(a for a in bpy.data.actions if a.name.split("|")[-1] == src_name)
    hero.animation_data.action = action_src
    if action_src.slots:
        hero.animation_data.action_slot = action_src.slots[0]
    arm.animation_data.action = new
    f0, f1 = int(action_src.frame_range[0]), int(action_src.frame_range[1])
    for i, f in enumerate(range(f0, f1 + 1)):
        scene.frame_set(f)
        retarget(out_name == "die")
        for p in arm.pose.bones:
            p.keyframe_insert("rotation_quaternion", frame=i)
            p.keyframe_insert("location", frame=i)
            p.keyframe_insert("scale", frame=i)  # a escala da pose (o glTF volta a 1 o canal sem chave)
    print("clipe", out_name, "<-", src_name, f1 - f0 + 1, "quadros")
hero.animation_data.action = None
for a in list(bpy.data.actions):
    if a.name not in CLIPS and a is not walk:
        bpy.data.actions.remove(a)
bpy.data.objects.remove(hero, do_unlink=True)
arm.animation_data.action = bpy.data.actions["idle"]

bpy.context.scene.frame_set(0)
print("OK alien octopus: altura %.2f m, %d triângulos, ações %s" % (height, sum(len(o.data.polygons) for o in meshes), sorted(a.name for a in bpy.data.actions)))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85,
                          export_animation_mode="ACTIONS", export_force_sampling=True)  # sem amostrar, as peças saem soltas e enormes
