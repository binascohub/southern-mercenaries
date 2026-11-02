"""Troll da Floresta (troll.glb do autor: troll de ombros floridos e saia de cascas, malha parada de 400 mil triângulos): reduzido a ~45 mil triângulos
(Decimate), de pé em y = 0 e com 2,3 m, mantendo as texturas (WebP). Vai para assets/models/monsters/forest_troll.glb.
uso: blender -b --python build_forest_troll.py -- <troll.glb> <saída.glb>"""
import bpy, sys
import numpy as np
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
HEIGHT = 2.3
TARGET = 45000
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
obj = next(o for o in bpy.data.objects if o.type == "MESH")
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
mod = obj.modifiers.new("dec", "DECIMATE")
mod.ratio = TARGET / len(obj.data.polygons)
bpy.ops.object.modifier_apply(modifier="dec")
obj.matrix_world = obj.matrix_world  # a malha vem com a transformação do arquivo
obj.data.transform(obj.matrix_world)
obj.matrix_world = Matrix.Identity(4)
pts = np.array([v.co[:] for v in obj.data.vertices])
mn, mx = pts.min(axis=0), pts.max(axis=0)
obj.data.transform(Matrix.Translation(-Vector(((mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]))))
obj.data.transform(Matrix.Scale(HEIGHT / (mx[2] - mn[2]), 4))
for poly in obj.data.polygons:
    poly.use_smooth = True
obj.name = "forest_troll"
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=80)
print("OK troll", len(obj.data.polygons), "polys")
