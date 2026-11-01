"""Espreitador (Stalker 3D, GuieA_7, CC BY-SA 4.0, opengameart.org/content/stalker-3d): olho gigante com asas, malha única
na pose de repouso (o jogo a move por código em MonsterModel, família "static"). Maior dimensão de 1 m, centrado em x/z,
base em y = 0, olhando para +Z; textura em 1024 px.
uso: blender -b <stalker.blend> --python build_stalker.py -- <saída.glb> [rotação em graus em torno do eixo vertical]"""
import bpy, sys, math
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
turn = float(args[1]) if len(args) > 1 else 0.0
deps = bpy.context.evaluated_depsgraph_get()
o = bpy.data.objects["stalker"]
mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
mesh.transform(o.matrix_world)
mesh.transform(Matrix.Rotation(math.radians(turn), 4, "Z"))
pts = [v.co for v in mesh.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
big = max(mx - mn)
mesh.transform(Matrix.Scale(1.0 / big, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
for other in list(bpy.data.objects):
    bpy.data.objects.remove(other, do_unlink=True)
obj = bpy.data.objects.new("Stalker", mesh)
bpy.context.scene.collection.objects.link(obj)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP")
print("OK", [round(x / big, 2) for x in (mx - mn)])
