"""Lince da Floresta (assets/models/monsters/lynx.glb): o "lynx-light.glb" do autor (~/Downloads; malha estática de 300 mil vértices, sem esqueleto, autoria e licença a confirmar).
Reduz a malha (~30 mil), monta um esqueleto simples (corpo, cabeça, cauda e quatro pernas, pesos por região) e cria as animações:
  idle (respira, mexe a cabeça e a cauda), walk (passo em diagonal), run (galope: pernas largas, coluna que ondula) e attack (o bote: corpo se ergue, patas dianteiras à frente).
O Lince olha para -Y no Blender (+Z no glTF). uso: blender -b -P tools/assets/build_lynx.py -- <lynx-light.glb> <saida.glb>"""
import bpy, sys, math
from math import radians

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
body = [o for o in bpy.data.objects if o.type == "MESH"][0]
for o in list(bpy.data.objects):
    if o is not body:
        bpy.data.objects.remove(o, do_unlink=True)
body.parent = None
bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
dec = body.modifiers.new("dec", "DECIMATE")
dec.ratio = min(1.0, 14000.0 / len(body.data.vertices))
bpy.ops.object.modifier_apply(modifier="dec")
print("VERTS", len(body.data.vertices))

Z_HIP, X_LEG = 0.46, 0.14
Y_FRONT, Y_HIND = -0.30, 0.28
arm_data = bpy.data.armatures.new("LynxArmature")
arm = bpy.data.objects.new("LynxArmature", arm_data)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
root = arm_data.edit_bones.new("Body")
root.head, root.tail = (0, -0.1, Z_HIP), (0, 0.2, Z_HIP)
head = arm_data.edit_bones.new("Head")
head.head, head.tail = (0, -0.3, 0.6), (0, -0.45, 0.72)
head.parent = root
tail = arm_data.edit_bones.new("Tail")
tail.head, tail.tail = (0, 0.4, 0.5), (0, 0.5, 0.35)
tail.parent = root
for fh, ly in (("F", Y_FRONT), ("H", Y_HIND)):
    for side, sx in (("L", 1), ("R", -1)):
        b = arm_data.edit_bones.new(fh + side)
        b.head, b.tail = (sx * X_LEG, ly, Z_HIP), (sx * X_LEG, ly, 0.0)
        b.parent = root
bpy.ops.object.mode_set(mode="OBJECT")

for n in ("Body", "Head", "Tail", "FL", "FR", "HL", "HR"):
    body.vertex_groups.new(name=n)
ymid = (Y_FRONT + Y_HIND) / 2
for v in body.data.vertices:
    c = v.co
    leg = max(0.0, min(1.0, (0.44 - c.z) / 0.14)) if c.z < 0.44 else 0.0
    hd = max(0.0, min(1.0, (-0.3 - c.y) / 0.1)) if (c.y < -0.3 and c.z > 0.5) else 0.0
    tl = max(0.0, min(1.0, (c.y - 0.36) / 0.1)) if (c.y > 0.36 and c.z > 0.25) else 0.0
    if leg > 0.0:
        body.vertex_groups[("F" if c.y < ymid else "H") + ("L" if c.x > 0 else "R")].add([v.index], leg, "REPLACE")
    if hd > 0.0:
        body.vertex_groups["Head"].add([v.index], hd, "REPLACE")
    if tl > 0.0:
        body.vertex_groups["Tail"].add([v.index], tl, "REPLACE")
    rest = 1.0 - max(leg, hd, tl)
    if rest > 0.0:
        body.vertex_groups["Body"].add([v.index], rest, "REPLACE")
mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm
body.parent = arm

bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
arm.animation_data_create()
pb = arm.pose.bones
for b in pb:
    b.rotation_mode = "XYZ"
LEGS = ("FL", "FR", "HL", "HR")


def key(frame, **rot):
    for n, e in rot.items():
        pb[n].rotation_euler = e
        pb[n].keyframe_insert("rotation_euler", frame=frame)


def reset(frame):
    for n in pb.keys():
        pb[n].rotation_euler = (0, 0, 0)
        pb[n].keyframe_insert("rotation_euler", frame=frame)
        pb[n].location = (0, 0, 0)
        pb[n].keyframe_insert("location", frame=frame)


def cycle(name, frames, swing, bob, pitch, phases, tail_sway, head_nod):
    act = bpy.data.actions.new(name)
    arm.animation_data.action = act
    for f in range(0, frames + 1, 2):
        t = f / frames
        for n, ph in phases.items():
            pb[n].rotation_euler = (swing * math.sin(2 * math.pi * (t + ph)), 0, 0)
            pb[n].keyframe_insert("rotation_euler", frame=f + 1)
        pb["Body"].location = (0, 0, bob * abs(math.sin(2 * math.pi * t * 2)))
        pb["Body"].keyframe_insert("location", frame=f + 1)
        pb["Body"].rotation_euler = (pitch * math.sin(2 * math.pi * t * 2 + 0.8), 0, radians(2.5) * math.sin(2 * math.pi * t))
        pb["Body"].keyframe_insert("rotation_euler", frame=f + 1)
        pb["Head"].rotation_euler = (head_nod * math.sin(2 * math.pi * t * 2 + 1.6), 0, 0)
        pb["Head"].keyframe_insert("rotation_euler", frame=f + 1)
        pb["Tail"].rotation_euler = (radians(8) * math.sin(2 * math.pi * t * 2), tail_sway * math.sin(2 * math.pi * t), 0)
        pb["Tail"].keyframe_insert("rotation_euler", frame=f + 1)


cycle("walk", 28, radians(24), 0.012, radians(1.5), {"FL": 0.0, "HR": 0.0, "FR": 0.5, "HL": 0.5}, radians(14), radians(3))
cycle("run", 14, radians(52), 0.045, radians(7), {"FL": 0.0, "FR": 0.08, "HL": 0.5, "HR": 0.58}, radians(18), radians(5))
idle = bpy.data.actions.new("idle")
arm.animation_data.action = idle
for f, k in ((1, 0.0), (31, 1.0), (61, 0.0)):
    for n in LEGS:
        key(f, **{n: (0, 0, 0)})
    pb["Body"].location = (0, 0, 0.007 * k)
    pb["Body"].keyframe_insert("location", frame=f)
    key(f, Body=(0, 0, 0), Head=(radians(4) * k - radians(2), radians(14) * (k - 0.5), 0), Tail=(0, radians(22) * (k - 0.5), 0))
attack = bpy.data.actions.new("attack")
arm.animation_data.action = attack
for f, up, reach in ((1, 0.0, 0.0), (6, -0.28, -0.5), (12, 0.12, 0.9), (20, 0.0, 0.0)):
    pb["Body"].location = (0, 0.1 * -reach * (1 if f == 12 else 0), 0.12 * (1 if f == 12 else 0))
    pb["Body"].keyframe_insert("location", frame=f)
    key(f, Body=(up, 0, 0), Head=(-up * 0.8, 0, 0), Tail=(radians(15), 0, 0),
        FL=(-reach * 1.0, 0, 0), FR=(-reach * 1.0, 0, 0), HL=(reach * 0.7, 0, 0), HR=(reach * 0.7, 0, 0))
arm.animation_data.action = None
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_apply=True, export_animation_mode="ACTIONS", export_yup=True, use_selection=False, export_image_format="WEBP")
print("OK", out, [a.name for a in bpy.data.actions])
