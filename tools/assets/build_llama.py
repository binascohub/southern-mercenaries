"""Lhama da Fazenda com pernas que se mexem (assets/models/characters/llama_walk.glb): parte da malha estática llama_farm.glb (modelo do autor, reduzido
por reduce_scan_model.py), monta um esqueleto simples (corpo, cabeça e quatro pernas, pesos por região) e cria as animações "walk" (passo em diagonal, 1,1 s;
a cabeça balança) e "idle" (respiração e cabeça mexendo). A cabeça fica virada para +Z (o glTF converte -Y do Blender em +Z). O llama_farm.glb original fica como estava.
uso: blender -b -P tools/assets/build_llama.py -- <llama_farm.glb> <saida.glb>"""
import bpy, sys, math
from math import radians

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
body = [o for o in bpy.data.objects if o.type == "MESH"][0]
body.parent = None
bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
vs = [v.co for v in body.data.vertices]
y_front, y_hind, x_leg, z_hip = -0.30, 0.52, 0.14, 0.76  # juntas (medidas na malha: cabeça em -Y, corpo de y = -0.67 a 0.76, pernas até z ~ 0.5)
y_mid = (y_front + y_hind) / 2

arm_data = bpy.data.armatures.new("LlamaArmature")
arm = bpy.data.objects.new("LlamaArmature", arm_data)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
root = arm_data.edit_bones.new("Body")
root.head, root.tail = (0, 0.0, z_hip), (0, 0.3, z_hip)
head_bone = arm_data.edit_bones.new("Head")
head_bone.head, head_bone.tail = (0, -0.5, 1.15), (0, -0.55, 1.7)
head_bone.parent = root
for fh, ly in (("F", y_front), ("H", y_hind)):
    for side, sx in (("L", 1), ("R", -1)):
        b = arm_data.edit_bones.new(fh + side)
        b.head, b.tail = (sx * x_leg, ly, z_hip), (sx * x_leg, ly, 0.0)
        b.parent = root
bpy.ops.object.mode_set(mode="OBJECT")

for n in ("Body", "Head", "FL", "FR", "HL", "HR"):
    body.vertex_groups.new(name=n)
for v in body.data.vertices:
    c = v.co
    leg = max(0.0, min(1.0, (0.64 - c.z) / 0.2)) if c.z < 0.64 else 0.0       # só do alto da perna para baixo
    head = max(0.0, min(1.0, (c.z - 1.12) / 0.15)) if (c.z > 1.12 and c.y < -0.3) else 0.0  # pescoço e cabeça
    if leg > 0.0:
        name = ("F" if c.y < y_mid else "H") + ("L" if c.x > 0 else "R")
        body.vertex_groups[name].add([v.index], leg, "REPLACE")
    if head > 0.0:
        body.vertex_groups["Head"].add([v.index], head, "REPLACE")
    rest = 1.0 - max(leg, head)
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
SWING = radians(26)
walk = bpy.data.actions.new("walk")
arm.animation_data.action = walk
phase = {"FL": 0.0, "HR": 0.0, "FR": 0.5, "HL": 0.5}
FRAMES = 27
for f in range(0, FRAMES + 1, 3):
    t = f / FRAMES
    for n, ph in phase.items():
        pb[n].rotation_euler = (SWING * math.sin(2 * math.pi * (t + ph)), 0, 0)
        pb[n].keyframe_insert("rotation_euler", frame=f + 1)
    pb["Body"].location = (0, 0, 0.02 * abs(math.sin(2 * math.pi * t * 2)))
    pb["Body"].rotation_euler = (0, radians(2.5) * math.sin(2 * math.pi * t), 0)
    pb["Head"].rotation_euler = (radians(5) * math.sin(2 * math.pi * t * 2 + 1.0), 0, 0)
    for n in ("Body", "Head"):
        pb[n].keyframe_insert("location" if n == "Body" else "rotation_euler", frame=f + 1)
    pb["Body"].keyframe_insert("rotation_euler", frame=f + 1)
idle = bpy.data.actions.new("idle")
arm.animation_data.action = idle
for f, k in ((1, 0.0), (25, 1.0), (49, 0.0)):
    for n in ("FL", "FR", "HL", "HR"):
        pb[n].rotation_euler = (0, 0, 0)
        pb[n].keyframe_insert("rotation_euler", frame=f)
    pb["Body"].location = (0, 0, 0.008 * k)
    pb["Body"].rotation_euler = (0, 0, 0)
    pb["Body"].keyframe_insert("location", frame=f)
    pb["Body"].keyframe_insert("rotation_euler", frame=f)
    pb["Head"].rotation_euler = (radians(6) * k - radians(3), radians(8) * (k - 0.5), 0)
    pb["Head"].keyframe_insert("rotation_euler", frame=f)
arm.animation_data.action = None
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_apply=True, export_animation_mode="ACTIONS", export_yup=True, use_selection=False, export_image_format="AUTO")
print("OK", out, [a.name for a in bpy.data.actions])
