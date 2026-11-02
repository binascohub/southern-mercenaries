"""Rei Golem de Pedra (stone-golem.glb, malha estática de ~400 mil polígonos, sem esqueleto nem animação) para o chefe da Toca dos Répteis:
reduz a malha (~12 mil polígonos), põe os pés em y = 0, centra em x/z, 1 m de altura (o tamanho vem dos dados do monstro), frente em +Z,
texturas em JPEG de 1024 px. O jogo o move por código em MonsterModel (modo "static").
uso: blender -b -P tools/assets/build_stone_golem_king.py -- <stone-golem.glb> <saída.glb> [giro em graus em volta da vertical]"""
import bpy, sys, math
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
turn = float(args[2]) if len(args) > 2 else 0.0
TARGET = 12000
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
objs = [o for o in bpy.data.objects if o.type == "MESH"]
for o in objs:
    o.parent = None
    o.matrix_world = o.matrix_world  # mantém a pose
bpy.ops.object.select_all(action="DESELECT")
for o in objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
if len(objs) > 1:
    bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
mod = obj.modifiers.new("d", "DECIMATE")
mod.ratio = min(1.0, TARGET / max(1, len(obj.data.polygons)))
bpy.ops.object.modifier_apply(modifier="d")
mesh = obj.data
mesh.transform(Matrix.Rotation(math.radians(turn), 4, "Z"))  # Z é a vertical no Blender; o exportador troca por Y
pts = [v.co for v in mesh.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
height = mx.z - mn.z
mesh.transform(Matrix.Scale(1.0 / height, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
    img.file_format = "JPEG"
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="JPEG", export_jpeg_quality=85)
print("OK", out, "polígonos:", len(mesh.polygons), "x,y,z (m, 1 = altura):", [round((mx - mn)[i] / height, 2) for i in range(3)])
