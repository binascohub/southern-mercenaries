"""Deita o leito de ouro (assets/models/props/Gold_Bed.glb, de build_gold_bed.py): o arquivo saiu em pé (5,6 m de altura, 0,76 m de espessura) e
aparecia como uma placa de ouro vertical no Esgoto e na Mina. Gira a malha para a face de moedas ficar para cima (base em y = 0, centrada).
Idempotente: só gira se o modelo estiver mais alto que largo.
uso: blender -b -P tools/assets/fix_gold_bed.py -- assets/models/props/Gold_Bed.glb"""
import bpy, sys, math
from mathutils import Vector, Matrix

path = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=path)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]


def box():
    pts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


mn, mx = box()
if mx.z - mn.z > max(mx.x - mn.x, mx.y - mn.y):
    for o in meshes:  # a face de moedas olhava para -Y do Blender (+Z no glTF): vai para cima
        o.data.transform(o.matrix_world)
        o.matrix_world = Matrix.Identity(4)
        o.data.transform(Matrix.Rotation(-math.pi / 2, 4, "X"))
    mn, mx = box()
    for o in meshes:
        o.data.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    mn, mx = box()
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_image_format="AUTO")
    print("OK gold bed deitado: %.2f x %.2f x %.2f" % tuple(mx - mn))
else:
    print("OK gold bed já deitado")
