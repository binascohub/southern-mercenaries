"""Joias de ouro para a decoração das salas dos chefes: "gold assets" (Pranav 3d na Sketchfab, CC BY 4.0; arquivo trazido pelo autor).
O original é um mostruário de ~20 joias lado a lado (1,76 milhão de polígonos, 59 MB). Aqui as partes viram grupos (caixas que se tocam),
e PICKS escolhe oito pelo centro no arquivo; cada uma é juntada numa malha, reduzida a no máximo MAX_TRIS triângulos, deitada no chão
(z = 0, centrada) com `size` metros no lado maior. Saem como peças do Kit em assets/models/maps/: Gold_<nome>.glb.
uso: blender -b --python tools/assets/build_gold_treasure.py -- <gold_assets.glb> <pasta de saída>"""
import bpy, sys, os, collections
from mathutils import Vector, Matrix
src, out_dir = sys.argv[sys.argv.index("--") + 1:][:2]
MAX_TRIS = 4000
GAP = 1.0                                   # unidades do arquivo: partes mais próximas que isso são da mesma joia
PICKS = {                                   # nome: (centro x, centro y no arquivo, lado maior em metros)
    "Necklace": (30.6, -52.5, 1.2),         # colar de placas
    "Bangle": (125.7, -1.6, 0.7),          # bracelete com pedras roxas
    "Brooch": (228.4, -58.4, 0.45),         # broche sextavado
    "Band": (283.7, -57.7, 0.65),            # tiara de filigrana
    "Plate": (433.0, -62.1, 0.65),           # placa quadrada lavrada
    "Orb": (168.2, -70.3, 0.4),             # esfera
    "Medallion": (0.0, 0.0, 0.4),           # medalhão redondo
    "Ring": (153.6, -32.1, 0.5),            # aro liso
}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
# Materiais: o original é metal puro (metallic 1), que no renderizador do jogo (sem reflexo do céu) sai preto. O ouro fica mais claro, meio
# metálico e com um brilho leve próprio; as pedras ficam com a cor delas, sem metal e brilhando um pouco.
for mat in bpy.data.materials:
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if mat.node_tree else None
    if bsdf is None or bsdf.inputs["Base Color"].is_linked:
        continue
    r, g, b, _a = bsdf.inputs["Base Color"].default_value
    gold = r > g > b and b < 0.15
    color = (0.85, 0.55, 0.12, 1.0) if gold else (r, g, b, 1.0)
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = 0.5 if gold else 0.0
    bsdf.inputs["Roughness"].default_value = 0.35 if gold else 0.2
    bsdf.inputs["Emission Color"].default_value = color
    bsdf.inputs["Emission Strength"].default_value = 0.08 if gold else 0.3
root = next(o for o in bpy.data.objects if o.name.startswith("GLTF_SceneRootNode"))
parts = []
for o in [o for o in bpy.data.objects if o.parent == root]:
    meshes = [c for c in [o] + list(o.children_recursive) if c.type == "MESH"]
    if meshes:
        pts = [c.matrix_world @ Vector(v) for c in meshes for v in c.bound_box]
        parts.append((meshes, Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])))
group = list(range(len(parts)))


def find(i: int) -> int:
    while group[i] != i:
        group[i] = group[group[i]]
        i = group[i]
    return i


for i in range(len(parts)):
    for j in range(i + 1, len(parts)):
        a, b = parts[i], parts[j]
        if all(a[1][k] - GAP <= b[2][k] and b[1][k] - GAP <= a[2][k] for k in range(3)):
            group[find(i)] = find(j)
clusters = collections.defaultdict(list)
for i in range(len(parts)):
    clusters[find(i)].append(i)


def center(ids: list) -> Vector:
    mn = Vector([min(parts[i][1][k] for i in ids) for k in range(3)])
    mx = Vector([max(parts[i][2][k] for i in ids) for k in range(3)])
    return (mn + mx) / 2


for name, (cx, cy, size) in PICKS.items():
    ids = min(clusters.values(), key=lambda ids: (center(ids).x - cx) ** 2 + (center(ids).y - cy) ** 2)
    pieces = []
    for i in ids:
        for src_obj in parts[i][0]:
            mesh = src_obj.data.copy()
            mesh.transform(src_obj.matrix_world)
            obj = bpy.data.objects.new("Gold_" + name, mesh)
            bpy.context.scene.collection.objects.link(obj)
            pieces.append(obj)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in pieces:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = pieces[0]
    if len(pieces) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    if tris > MAX_TRIS:
        mod = obj.modifiers.new("dec", "DECIMATE")
        mod.ratio = MAX_TRIS / tris
        bpy.ops.object.modifier_apply(modifier="dec")
    vs = [v.co for v in obj.data.vertices]
    mn = Vector([min(v[i] for v in vs) for i in range(3)])
    mx = Vector([max(v[i] for v in vs) for i in range(3)])
    k = size / max(mx.x - mn.x, mx.y - mn.y)
    obj.data.transform(Matrix.Scale(k, 4) @ Matrix.Translation(-Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))))
    obj.name = "Gold_" + name
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    print("peça", obj.name, sum(len(p.vertices) - 2 for p in obj.data.polygons), "tri", [round((mx - mn)[i] * k, 2) for i in range(3)], "m")
    bpy.ops.export_scene.gltf(filepath=os.path.join(out_dir, "Gold_%s.glb" % name), export_format="GLB", use_selection=True,
                              export_image_format="WEBP", export_image_quality=80)
