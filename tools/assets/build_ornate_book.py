"""Grimório das Brasas (ornate_book.glb enviado pelo autor do projeto; modelo do Sketchfab, autoria/licença a confirmar): o livro que o Azazel entrega ao abrir a missão do Gator Velho (Esgoto)
e que, lido no altar do Gator no centro do mapa, o invoca. Os 5 pedaços (capa, lombada, páginas, fechos) viram uma malha só (~20 mil polígonos, sem redução), as texturas de 8192 px vão a
1024 px, o livro fica em pé (capa para +Z), com a base em y = 0, centrado em x/z, e SIZE metros de altura (relíquia de missão, como a Garrafa de Almas).
Gera assets/models/props/Ornate_Book.glb (valioso "gator_book" em data/valuables.json).
uso: blender -b -P tools/assets/build_ornate_book.py -- <ornate_book.glb> <saida.glb> [altura_m=0.4]"""
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
body.name = "Ornate_Book"
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
