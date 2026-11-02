"""Falcão (falcon.glb enviado pelo autor do projeto, malha de 37 mil vértices em pose de planeio com 2,5 m de envergadura, esqueleto de 2 ossos e nenhuma animação,
autor/licença a confirmar), companheiro de Ar do Invocador. Aqui ele ganha um esqueleto próprio (corpo, e duas asas com ombro e ponta) com pesos por distância
ao eixo do corpo e duas animações: "Fly_Loop" (bater de asas) e "Attack" (mergulho com batidas rápidas). A malha é girada para olhar para +Z (o glTF o traz olhando para -X),
centrada e com as garras em y = 0.
Gera assets/models/props/Falcon.glb.
uso: blender -b -P tools/assets/build_falcon_companion.py -- <falcon.glb> <saida.glb>"""
import bpy, sys, math
import numpy as np
from mathutils import Vector, Euler

src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
bird = max((o for o in bpy.data.objects if o.type == 'MESH'), key=lambda o: len(o.data.vertices))  # o importador cria também uma esfera de osso (Icosphere)
bpy.context.view_layer.update()
world = bird.matrix_world.copy()
for o in list(bpy.data.objects):
    if o is not bird:
        bpy.data.objects.remove(o, do_unlink=True)
bird.parent = None
bird.modifiers.clear()
bird.vertex_groups.clear()
bird.data.transform(world)
bird.matrix_world = world.__class__.Identity(4)
# gira para a cabeça ficar para -Y do Blender (= +Z do glTF): o glTF a traz para -X
bird.data.transform(bpy.data.objects.new("t", None).matrix_world.__class__.Rotation(math.radians(90), 4, "Z"))
v = np.array([tuple(x.co) for x in bird.data.vertices])
v[:, 0] -= (v[:, 0].min() + v[:, 0].max()) / 2
v[:, 1] -= (v[:, 1].min() + v[:, 1].max()) / 2
v[:, 2] -= v[:, 2].min()
for i, vert in enumerate(bird.data.vertices):
    vert.co = Vector(v[i])
half = float(max(abs(v[:, 0].min()), v[:, 0].max()))
zc = float((v[:, 2].min() + v[:, 2].max()) / 2)
print("SPAN", half * 2, "Y", v[:, 1].min(), v[:, 1].max(), "Z", v[:, 2].min(), v[:, 2].max())

# esqueleto: corpo e, de cada lado, ombro (0-45% da asa) e ponta
arm_data = bpy.data.armatures.new("Armature")
arm = bpy.data.objects.new("Armature", arm_data)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones
body = eb.new("Body"); body.head = (0, 0, zc); body.tail = (0, 0, zc + 0.3)
defs = {}
for side, sx in (("L", 1), ("R", -1)):
    w1 = eb.new("Wing1_" + side); w1.head = (sx * 0.08, 0, zc); w1.tail = (sx * half * 0.45, 0, zc); w1.parent = body
    w2 = eb.new("Wing2_" + side); w2.head = w1.tail; w2.tail = (sx * half, 0, zc); w2.parent = w1
    w2.use_connect = True
bpy.ops.object.mode_set(mode='OBJECT')

# pesos pela distância ao eixo do corpo (|x|): corpo no meio, ombro e ponta com transição suave
def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)
t = np.abs(v[:, 0])
w_out = smooth(0.5 * half, 0.85 * half, t)
w_in = smooth(0.08 * half, 0.3 * half, t) - w_out
w_body = 1 - smooth(0.08 * half, 0.3 * half, t)
side_l = v[:, 0] >= 0
weights = {"Body": w_body}
for side, mask in (("L", side_l), ("R", ~side_l)):
    weights["Wing1_" + side] = np.where(mask, w_in, 0)
    weights["Wing2_" + side] = np.where(mask, w_out, 0)
for name, w in weights.items():
    vg = bird.vertex_groups.new(name=name)
    for i in np.nonzero(w > 0.001)[0]:
        vg.add([int(i)], float(w[i]), 'REPLACE')
bird.parent = arm
md = bird.modifiers.new("Armature", 'ARMATURE'); md.object = arm
bird.name = "Falcon_Body"

# eixo e sinal de cada osso: mede qual rotação sobe a ponta (asas) ou o bico (corpo) em z
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones
for p in pb:
    p.rotation_mode = 'XYZ'


def probe(bone_name, point):
    best = (0, 0, 0.0)
    for axis in range(3):
        for p in pb:
            p.rotation_euler = Euler((0, 0, 0))
        pb[bone_name].rotation_euler[axis] = 0.3
        bpy.context.view_layer.update()
        m = pb[bone_name].matrix @ pb[bone_name].bone.matrix_local.inverted()
        dz = (m @ Vector(point)).z - point[2]
        if abs(dz) > abs(best[2]):
            best = (axis, 1 if dz > 0 else -1, dz)
    for p in pb:
        p.rotation_euler = Euler((0, 0, 0))
    bpy.context.view_layer.update()
    return best


axes = {}
for side, sx in (("L", 1), ("R", -1)):
    axes["Wing1_" + side] = probe("Wing1_" + side, (sx * half * 0.45, 0, zc))
    axes["Wing2_" + side] = probe("Wing2_" + side, (sx * half, 0, zc))
axes["Body"] = probe("Body", (0, -0.4, zc))  # o bico: positivo = bico sobe
print("AXES", axes)

FPS = 30
bpy.context.scene.render.fps = FPS


def key(bone, frame, angle):
    axis, sign, _ = axes[bone]
    pb[bone].rotation_euler[axis] = sign * angle
    pb[bone].keyframe_insert("rotation_euler", index=axis, frame=frame)


def make_action(name, frames, fn):
    action = bpy.data.actions.new(name)
    arm.animation_data_create()
    arm.animation_data.action = action
    for p in pb:
        p.rotation_euler = Euler((0, 0, 0))
    for f in range(frames + 1):
        fn(f, f / frames)
    action.use_fake_user = True
    arm.animation_data.action = None
    return action


A1, A2 = 0.38, 0.6


def fly(f, u):
    ph = 2 * math.pi * u
    for side in ("L", "R"):
        key("Wing1_" + side, f + 1, A1 * math.sin(ph))
        key("Wing2_" + side, f + 1, A2 * math.sin(ph - 0.9))
    key("Body", f + 1, 0.06 * math.sin(ph - 1.4))


def attack(f, u):
    ph = 4 * math.pi * u
    dip = math.sin(math.pi * u)
    for side in ("L", "R"):
        key("Wing1_" + side, f + 1, A1 * 1.3 * math.sin(ph) - 0.2 * dip)
        key("Wing2_" + side, f + 1, A2 * 1.3 * math.sin(ph - 0.9) - 0.4 * dip)
    key("Body", f + 1, -0.55 * dip)  # bico para baixo no mergulho


make_action("Fly_Loop", 30, fly)
make_action("Attack", 24, attack)
bpy.ops.object.mode_set(mode='OBJECT')
for p in pb:
    p.rotation_euler = Euler((0, 0, 0))
bpy.ops.object.select_all(action='DESELECT')
for o in (bird, arm):
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
                          export_animation_mode='ACTIONS', export_skins=True, use_selection=False, export_force_sampling=True)
print("OBJS", [(o.name, o.type, o.visible_get(), o.hide_viewport) for o in bpy.context.scene.objects], "POLYS", len(bird.data.polygons))
print("OK", dst)
