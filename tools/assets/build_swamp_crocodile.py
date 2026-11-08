"""Crocodilo do Pântano ("Jungle Water Crocodile", vanshtandon321 na Sketchfab, CC BY 4.0; arquivo trazido pelo autor do projeto): crocodilo com esqueleto
Biped do 3ds Max (30 ossos: coluna, pescoço, cabeça, mandíbula "Bone01", quatro patas e quatro gomos de cauda), textura de 512 px e só a animação "swim".
Aqui ele fica com 2,4 m de comprimento, de barriga no chão (z = 0), centrado, olhando para -Y (+Z no glTF, a frente dos monstros no jogo), e ganha as
animações que faltam, feitas girando os ossos no espaço do mundo (os eixos dos ossos do Biped são tortos):
  swim (o original: o corpo ondula, as patas recolhidas) -> andar e correr;
  idle (respira, a cauda balança devagar, a cabeça mexe um pouco);
  attack (o bote: ergue a cabeça e abre a boca, avança e fecha com força, volta);
  hit (a cabeça e o corpo recuam e voltam);
  die (vira de barriga para cima, a cauda cai, e fica).
Vai para assets/models/monsters/swamp_crocodile.glb (game/actors/monster_model.gd, família "swamp_crocodile").
uso: blender -b --python tools/assets/build_swamp_crocodile.py -- <jungle_water_crocodile.glb> <saída.glb>"""
import bpy, sys, math
import numpy as np
from mathutils import Matrix, Vector, Quaternion

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
LENGTH = 2.4
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in list(bpy.data.objects):
    if o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
body = next(o for o in bpy.data.objects if o.type == "MESH")
top = next(o for o in bpy.data.objects if o.parent is None)
scene = bpy.context.scene
scene.render.fps = 24

# Tamanho e lugar: a raiz da cena ganha a escala e o deslocamento (o esqueleto e a malha seguem juntos).
scene.frame_set(0)
pts = np.array([body.matrix_world @ v.co for v in body.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh().vertices])
mn, mx = pts.min(0), pts.max(0)
k = LENGTH / (mx[1] - mn[1])
# Meia volta: com a malha deformada pelo esqueleto (como o Godot a mostra), o focinho fica em +Y.
top.matrix_world = Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation(Vector((-(mn[0] + mx[0]) / 2 * k, -(mn[1] + mx[1]) / 2 * k, -mn[2] * k))) @ Matrix.Scale(k, 4) @ top.matrix_world
bpy.context.view_layer.update()
pts = np.array([body.matrix_world @ v.co for v in body.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh().vertices])
print("tamanho", (pts.max(0) - pts.min(0)).round(2), "chão", round(float(pts.min(0)[2]), 3))

swim = bpy.data.actions[0]
swim.name = "swim"
swim.use_fake_user = True
arm.animation_data_create()
for p in arm.pose.bones:
    p.rotation_mode = "QUATERNION"
NAMES = {"pelvis": "Bip01_Pelvis_00", "spine": "Bip01_Spine_01", "spine1": "Bip01_Spine1_010", "spine2": "Bip01_Spine2_011",
         "neck": "Bip01_Neck_012", "head": "Bip01_Head_013", "jaw": "Bone01_014",
         "tail": "Bip01_Tail_024", "tail1": "Bip01_Tail1_026", "tail2": "Bip01_Tail2_027", "tail3": "Bip01_Tail3_028"}
ARM_ROT = arm.matrix_world.to_3x3().normalized()
LATERAL, UP, FORWARD = Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, -1, 0))


def rest_pose():
    for p in arm.pose.bones:
        p.rotation_quaternion = (1, 0, 0, 0)
        p.location = (0, 0, 0)
    bpy.context.view_layer.update()


def turn(key, axis, degrees, pivot=None):
    """Gira o osso (e tudo o que vem depois dele) em volta de um eixo do mundo, pela cabeça do osso (ou por `pivot`, um ponto do mundo)."""
    pb = arm.pose.bones[NAMES[key]]
    a = (ARM_ROT.inverted() @ axis).normalized()
    head = pb.matrix.to_translation() if pivot is None else arm.matrix_world.inverted() @ pivot
    pb.matrix = Matrix.Translation(head) @ Quaternion(a, math.radians(degrees)).to_matrix().to_4x4() @ Matrix.Translation(-head) @ pb.matrix
    bpy.context.view_layer.update()


def shift(key, world_offset):
    pb = arm.pose.bones[NAMES[key]]
    m = pb.matrix.copy()
    m.translation = m.translation + ARM_ROT.inverted() @ (world_offset / arm.matrix_world.to_scale()[0])
    pb.matrix = m
    bpy.context.view_layer.update()


def make(name, frames, pose_at, loop):
    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    arm.animation_data.action = action
    for f in range(frames + 1):
        rest_pose()
        pose_at(f / frames)
        for p in arm.pose.bones:
            p.keyframe_insert("rotation_quaternion", frame=f)
            p.keyframe_insert("location", frame=f)
    print("ação", name, frames + 1, "quadros", "(loop)" if loop else "")
    return action


def bump(t, start, peak, end):
    """0 -> 1 -> 0 entre start, peak e end (suave)."""
    if t <= start or t >= end:
        return 0.0
    x = (t - start) / (peak - start) if t < peak else 1.0 - (t - peak) / (end - peak)
    return 0.5 - 0.5 * math.cos(math.pi * x)


TAIL = ("tail", "tail1", "tail2", "tail3")


def idle(t):
    w = math.sin(t * 2 * math.pi)
    turn("spine1", UP, 1.5 * w)
    for i, key in enumerate(TAIL):
        turn(key, UP, 6.0 * math.sin(t * 2 * math.pi - i * 0.8))
    turn("neck", UP, -3.0 * w)
    turn("head", LATERAL, -2.0 * (0.5 + 0.5 * math.sin(t * 4 * math.pi)))


def attack(t):
    rise = bump(t, 0.0, 0.35, 0.75)
    snap = bump(t, 0.3, 0.5, 0.9)
    shift("pelvis", FORWARD * 0.35 * snap)
    turn("spine2", LATERAL, -6.0 * rise)
    turn("neck", LATERAL, -14.0 * rise)
    turn("head", LATERAL, -8.0 * rise)
    turn("jaw", LATERAL, 32.0 * bump(t, 0.05, 0.38, 0.5))
    for i, key in enumerate(TAIL):
        turn(key, UP, 10.0 * snap * (1 if i % 2 == 0 else -1))


def hit(t):
    h = bump(t, 0.0, 0.25, 1.0)
    shift("pelvis", FORWARD * -0.12 * h)
    turn("neck", LATERAL, -10.0 * h)
    turn("neck", UP, 12.0 * h)
    turn("tail1", UP, -10.0 * h)


def die(t):
    roll = bump(min(t, 0.6), 0.0, 0.6, 2.0) if t < 0.6 else 1.0
    turn("pelvis", FORWARD, 175.0 * roll, BELLY)
    shift("pelvis", UP * 0.12 * bump(t, 0.0, 0.3, 0.6))
    turn("neck", LATERAL, 10.0 * roll)
    turn("jaw", LATERAL, 18.0 * roll)
    for key in TAIL:
        turn(key, UP, 6.0 * roll)


# Eixo do corpo (meia altura, na linha do quadril): o crocodilo vira em volta dele ao morrer.
BELLY = arm.matrix_world @ arm.pose.bones[NAMES["pelvis"]].head
BELLY = Vector((0.0, BELLY.y, float(pts.max(0)[2]) / 2))
make("idle", 48, idle, True)
make("attack", 22, attack, False)
make("hit", 10, hit, False)
make("die", 30, die, False)
arm.animation_data.action = swim
if swim.slots:
    arm.animation_data.action_slot = swim.slots[0]
rest_pose()
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_animations=True, export_animation_mode="ACTIONS",
                          export_image_format="WEBP", export_image_quality=85)
