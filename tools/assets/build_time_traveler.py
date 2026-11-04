"""Viajante do Tempo (assets/models/characters/time_traveler.glb): o "alien grey" com esqueleto do autor (~/Downloads/alien-grey-rigged.glb, autoria e licença a confirmar).
O arquivo tem 167 mil vértices e só as animações walk e run; aqui a malha é reduzida a ~16 mil (Decimate antes do Armature), a esfera solta é removida e se cria um "idle"
(respiração na coluna e a cabeça balançando de leve). Exporta com as texturas em WEBP.
uso: blender -b -P tools/assets/build_time_traveler.py -- <alien-grey-rigged.glb> <saida.glb>"""
import bpy, sys, math
from math import radians

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in list(bpy.data.objects):
    if o.type == "MESH" and o.name != "char1":
        bpy.data.objects.remove(o, do_unlink=True)
body = bpy.data.objects["char1"]
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
bpy.context.view_layer.objects.active = body
dec = body.modifiers.new("dec", "DECIMATE")
dec.ratio = min(1.0, 16000.0 / len(body.data.vertices))
while body.modifiers[0].name != "dec":
    bpy.ops.object.modifier_move_up(modifier="dec")
bpy.ops.object.modifier_apply(modifier="dec")
print("VERTS", len(body.data.vertices))
names = [b.name for b in arm.data.bones]
print("BONES", names)
# --- idle
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
arm.animation_data_create()
pb = arm.pose.bones
for b in pb:
    b.rotation_mode = "XYZ"
idle = bpy.data.actions.new("idle")
arm.animation_data.action = idle
spine = next((n for n in ("Spine01", "Spine02", "Spine") if n in pb), None)
head = next((n for n in names if "head" in n.lower()), None)
for f, k in ((1, 0.0), (31, 1.0), (61, 0.0)):
    if spine:
        pb[spine].rotation_euler = (radians(2.0) * k, 0, 0)
        pb[spine].keyframe_insert("rotation_euler", frame=f)
    if head:
        pb[head].rotation_euler = (radians(3) * (k - 0.5), radians(9) * (k - 0.5), 0)
        pb[head].keyframe_insert("rotation_euler", frame=f)
arm.animation_data.action = None
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_apply=False, export_animation_mode="ACTIONS", export_yup=True, use_selection=False, export_image_format="WEBP")
print("OK", out, [a.name for a in bpy.data.actions])
