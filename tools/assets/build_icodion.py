"""Pedra do Pedregulho (habilidade "boulder" da Terra): "Icodion" (tamminen na Sketchfab, CC BY 4.0; arquivo trazido pelo autor), uma esfera de
estilhaços pontudos. Aqui só fica a malha, centrada e com 1 m de diâmetro, sem a animação de giro (o jogo gira a pedra em game/combat/spell_fx.gd)
e sem material (a cor vem da habilidade); reduzida a ~5 mil triângulos. Vai para assets/models/fx/icodion.glb.
uso: blender -b --python tools/assets/build_icodion.py -- <icodion.glb> <saída.glb>"""
import bpy, sys
import numpy as np
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
obj = next(o for o in bpy.data.objects if o.type == "MESH")
world = obj.matrix_world.copy()
obj.parent = None
obj.data.transform(world)
obj.matrix_world = Matrix.Identity(4)
obj.animation_data_clear()
for o in [o for o in bpy.data.objects if o != obj]:
    bpy.data.objects.remove(o, do_unlink=True)
pts = np.array([v.co[:] for v in obj.data.vertices])
mn, mx = pts.min(axis=0), pts.max(axis=0)
obj.data.transform(Matrix.Translation(-Vector(((mn + mx) / 2).tolist())))
obj.data.transform(Matrix.Scale(1.0 / float((mx - mn).max()), 4))
obj.data.materials.clear()
TARGET = 5000  # projétil: leve para o vídeo integrado (o original tem ~15 mil triângulos)
tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
if tris > TARGET:
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.ratio = TARGET / tris
    bpy.ops.object.modifier_apply(modifier="dec")
obj.name = "icodion"
print("triângulos", sum(len(p.vertices) - 2 for p in obj.data.polygons))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animations=False, export_materials="NONE")
