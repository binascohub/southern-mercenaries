"""Móveis medievais (medieval_furniture.glb enviado pelo autor do projeto: uma cena de 286 malhas (83 mil polígonos, 86 MB com as texturas) com cadeiras, mesas, estante, tambor, caixa, garrafas, pratos,
livros e armas, num grupo "group1" de escala 0,0008 em que 1 m real vale ~0,087 no arquivo; autor/licença a confirmar). Aqui saem só os móveis, cada um como uma peça (as malhas do grupo viram uma só,
com os materiais e as texturas dele, a 1024 px), na escala real (x 11,5), centrada em x/z e com a base em y = 0:
Furn_Chair_1, Furn_Chair_2, Furn_Chair_3, Furn_BigTable, Furn_SmallTable, Furn_Table, Furn_Shelf, Furn_Box e Furn_Drum.
Gera assets/models/props/Furn_*.glb.
uso: blender -b -P tools/assets/build_medieval_furniture.py -- <medieval_furniture.glb> <pasta de saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix

src, outdir = sys.argv[sys.argv.index("--") + 1:][:2]
FACTOR = 11.5
GROUPS = {"chair1": "Furn_Chair_1", "chair2": "Furn_Chair_2", "chair3": "Furn_Chair_3", "big_table1": "Furn_BigTable", "small_table1": "Furn_SmallTable",
          "table_01": "Furn_Table", "shell1": "Furn_Shelf", "box": "Furn_Box", "drum1": "Furn_Drum"}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for im in bpy.data.images:
    if im.size[0] > 1024 or im.size[1] > 1024:
        im.scale(1024, 1024)
dg = bpy.context.evaluated_depsgraph_get()


def meshes_under(o):
    out = []
    for c in o.children:
        if c.type == 'MESH':
            out.append(c)
        out += meshes_under(c)
    return out


group1 = bpy.data.objects["group1"]
built = {}
for gname, out_name in GROUPS.items():
    root = next(c for c in group1.children if c.name == gname)
    parts = meshes_under(root) + ([root] if root.type == 'MESH' else [])
    new_objs = []
    for o in parts:
        mesh = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        mesh.transform(o.matrix_world)
        mats = [m for m in o.data.materials]
        idx = [p.material_index for p in mesh.polygons]
        mesh.materials.clear()
        for m in mats:
            mesh.materials.append(m)
        for p, i in zip(mesh.polygons, idx):
            p.material_index = i
        ob = bpy.data.objects.new("P_" + o.name, mesh)
        bpy.context.scene.collection.objects.link(ob)
        new_objs.append(ob)
    built[out_name] = new_objs
# nada do cenário original além das cópias
for o in list(bpy.data.objects):
    if not o.name.startswith("P_"):
        bpy.data.objects.remove(o, do_unlink=True)
for out_name, objs in built.items():
    objs = [o for o in objs if o.name in bpy.data.objects]
    for o in bpy.data.objects:
        o.select_set(o in objs)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    v = [Vector(p.co) for p in ob.data.vertices]
    cx = (min(p.x for p in v) + max(p.x for p in v)) / 2
    cy = (min(p.y for p in v) + max(p.y for p in v)) / 2
    ob.data.transform(Matrix.Scale(FACTOR, 4) @ Matrix.Translation((-cx, -cy, -min(p.z for p in v))))
    ob.name = out_name
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    dst = os.path.join(outdir, out_name + ".glb")
    bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', use_selection=True, export_animations=False)
    print("OK", out_name, len(ob.data.polygons), [round(x, 2) for x in ob.dimensions])
    bpy.data.objects.remove(ob, do_unlink=True)
