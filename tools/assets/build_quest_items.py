"""Adaga (foice) de osso de dinossauro, o item de missão da Exploradora da Floresta: bone-sickle.zip do autor (4 peças com texturas de 2048 px; autoria e licença a confirmar) vira UMA malha
de 0,7 m, centrada, com as texturas a 1024 px (assets/models/props/Bone_Sickle.glb). A Chave de Espadas que ela dá em troca já existe (Key_Spades.glb, Card Suits Keys, CC-BY 4.0).
uso: blender -b -P tools/assets/build_quest_items.py -- <bone_sickle.glb> <pasta de saída (assets/models/props)>"""
import bpy, sys, os
from mathutils import Vector

sickle_glb, out_dir = sys.argv[sys.argv.index("--") + 1:][:2]


def fit(obj, length, up_axis="y"):
    """Centra a malha e a reduz para que a maior dimensão tenha `length` m."""
    pts = [v.co for v in obj.data.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    k = length / max(hi - lo)
    c = (lo + hi) / 2
    for v in obj.data.vertices:
        v.co = (v.co - c) * k


def join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = name
    return o


def export(path):
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_image_format="WEBP", export_image_quality=85, export_animations=False)


# --- Foice de osso
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sickle_glb)
parts = []
deps = bpy.context.evaluated_depsgraph_get()
for o in [o for o in bpy.data.objects if o.type == "MESH" and len(o.data.vertices) > 20]:
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    mesh.transform(o.matrix_world)
    new = bpy.data.objects.new(o.name, mesh)
    bpy.context.scene.collection.objects.link(new)
    parts.append(new)
for o in list(bpy.data.objects):
    if o not in parts:
        bpy.data.objects.remove(o, do_unlink=True)
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
    if img.size[0] > 0:
        img.pack()
sickle = join(parts, "Bone_Sickle")
fit(sickle, 0.7)
for v in sickle.data.vertices:  # em pé no jogo (a maior dimensão do arquivo é Y do Blender; o glTF a leva para Z): gira 90 graus em X para ficar vertical
    v.co = Vector((v.co.x, -v.co.z, v.co.y))
export(os.path.join(out_dir, "Bone_Sickle.glb"))
print("OK Bone_Sickle", [round(v, 2) for v in sickle.dimensions])

