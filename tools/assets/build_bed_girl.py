"""Moça sentada na cama do quarto do rei (SEXYY.glb de girl2.zip, enviado pelo autor do projeto, gerado por IA/Tripo: uma mulher adulta sentada, apoiada num braço, de camisola e meias, em
1 malha de ~1,9 milhão de polígonos e 3 texturas de 2048 px; sem esqueleto nem animação; autor/licença a confirmar). Aqui a malha tem as emendas soldadas e é reduzida a ~40 mil polígonos
(Decimate), as texturas vão a 1024 px, a frente (+Z no glTF) fica como está, o modelo é centrado em x/z e a parte mais baixa (o colchão) fica em y = 0, e ele é ampliado por SCALE
(o arquivo é pequeno: 0,67 m sentada; a 1,7 ela fica com ~1,1 m de altura, 1,5 m de largura e 1,2 m de fundo). Gera assets/models/props/Girl_Bed.glb, que o decor da Capital (data/arenas.json) usa como peça "Girl_Bed".
uso: blender -b -P tools/assets/build_bed_girl.py -- <SEXYY.glb> <saida.glb> [escala=1.7] [polígonos=40000]"""
import bpy, sys, bmesh
import numpy as np
from mathutils import Matrix

args = sys.argv[sys.argv.index("--") + 1:]
src, dst = args[:2]
SCALE = float(args[2]) if len(args) > 2 else 1.7
TARGET = int(args[3]) if len(args) > 3 else 40000
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
if len(parts) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "Girl_Bed"
print("POLÍGONOS antes", len(body.data.polygons))
bm = bmesh.new()
bm.from_mesh(body.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00005)
bm.to_mesh(body.data)
bm.free()
mod = body.modifiers.new("d", 'DECIMATE')
mod.ratio = min(1.0, TARGET / max(1, len(body.data.polygons)))
mod.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier="d")
print("POLÍGONOS depois", len(body.data.polygons))
for im in bpy.data.images:
    if im.size[0] > 1024 or im.size[1] > 1024:
        im.scale(1024, 1024)
v = np.array([tuple(p.co) for p in body.data.vertices])
cx = (v[:, 0].min() + v[:, 0].max()) / 2
cy = (v[:, 1].min() + v[:, 1].max()) / 2
body.data.transform(Matrix.Scale(SCALE, 4) @ Matrix.Translation((-cx, -cy, -v[:, 2].min())))
print("TAMANHO", [round(x, 2) for x in body.dimensions])
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', use_selection=True, export_animations=False)
print("OK", dst)
