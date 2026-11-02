"""Garrafa de Almas Condenadas (souls_bottle.glb enviado pelo autor do projeto; modelo do Sketchfab, autoria/licença a confirmar): relíquia da missão do Azazel (Esgoto), que o Gator Velho
solta ao morrer. Os 10 pedaços (vidro, rolha, anel, almas dentro) viram uma malha só (~60 mil polígonos, sem redução), as texturas vão a 1024 px, a base fica em y = 0, centrada em x/z,
com SIZE metros de altura (as relíquias do jogo têm de 0,35 a 0,5 m). Gera assets/models/props/Souls_Bottle.glb (valioso "souls_bottle" em data/valuables.json).
uso: blender -b -P tools/assets/build_souls_bottle.py -- <souls_bottle.glb> <saida.glb> [altura_m=0.4]"""
import bpy, sys
import numpy as np
from mathutils import Matrix

args = sys.argv[sys.argv.index("--") + 1:]
src, dst = args[:2]
SIZE = float(args[2]) if len(args) > 2 else 0.4
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
dg = bpy.context.evaluated_depsgraph_get()
parts = []
for o in [o for o in bpy.data.objects if o.type == 'MESH']:
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    mesh.transform(o.matrix_world)
    mats = list(o.data.materials)
    mesh.materials.clear()
    for m in mats:
        mesh.materials.append(m)
    ob = bpy.data.objects.new("P_" + o.name, mesh)
    bpy.context.scene.collection.objects.link(ob)
    parts.append(ob)
for o in list(bpy.data.objects):
    if o not in parts:
        bpy.data.objects.remove(o, do_unlink=True)
for o in bpy.data.objects:
    o.select_set(o in parts)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "Souls_Bottle"
for im in bpy.data.images:
    if im.size[0] > 1024 or im.size[1] > 1024:
        im.scale(1024, 1024)
v = np.array([tuple(p.co) for p in body.data.vertices])
k = SIZE / (v[:, 2].max() - v[:, 2].min())
body.data.transform(Matrix.Scale(k, 4) @ Matrix.Translation((-(v[:, 0].min() + v[:, 0].max()) / 2, -(v[:, 1].min() + v[:, 1].max()) / 2, -v[:, 2].min())))
print("POLÍGONOS", len(body.data.polygons), "escala", round(k, 3))
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', use_selection=True, export_animations=False)
print("OK", dst)
