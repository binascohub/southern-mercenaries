"""Conversor de Collada (.dae, estilo OpenCOLLADA do 3ds Max, como o "3D Fantasy Ruins Pack") para .glb, feito porque o
Blender 5 e o Godot 4.7 não leem esses arquivos. Lê as geometrias, os UVs, os nós (translate / rotate / scale / matrix, em
árvore) e as texturas difusas dos materiais; descarta o nó "Collision" (malha de colisão do Torque). A peça sai em pé, com a
base em y = 0 e o centro em x/z, no tamanho pedido (altura, largura máxima ou escala), e as texturas reduzidas a 512 px.
uso: blender -b -P dae_to_glb.py -- <arquivo.dae> <saida.glb> <h=altura_m | w=largura_m | s=escala> [nome_do_nó_a_ignorar,...]
(as imagens ficam na mesma pasta do .dae, com o nome do arquivo que o .dae cita)"""
import bpy, sys, os, math
import xml.etree.ElementTree as ET
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index("--") + 1:]
dae_path, out_path, size_spec = args[0], args[1], args[2]
skip_nodes = set(args[3].split(",")) if len(args) > 3 else set()
skip_nodes.add("Collision")
folder = os.path.dirname(dae_path)
root = ET.parse(dae_path).getroot()
NS = {"c": root.tag.split("}")[0].strip("{")}


def q(path):
    return path.replace("/", "/c:").join(["c:", ""]) if False else "/".join("c:" + p for p in path.split("/"))


def find_all(el, path):
    return el.findall(".//" + "/".join("c:" + p for p in path.split("/")), NS)


def floats(text):
    return [float(v) for v in text.split()]


unit = root.find("c:asset/c:unit", NS)
unit_scale = float(unit.get("meter", "1")) if unit is not None else 1.0

# --- Imagens e materiais -------------------------------------------------------------------------------
image_file = {}
for img in find_all(root, "library_images/image"):
    image_file[img.get("id")] = os.path.basename(img.find("c:init_from", NS).text.strip().replace("\\", "/"))
effect_image = {}
for eff in find_all(root, "library_effects/effect"):
    surfaces = {}
    for p in eff.findall(".//c:newparam", NS):
        s = p.find("c:surface/c:init_from", NS)
        smp = p.find("c:sampler2D/c:source", NS)
        if s is not None:
            surfaces[p.get("sid")] = s.text.strip()
        if smp is not None:
            surfaces[p.get("sid")] = ("sampler", smp.text.strip())
    tex = eff.find(".//c:diffuse/c:texture", NS)
    if tex is not None:
        ref = surfaces.get(tex.get("texture"))
        if isinstance(ref, tuple):
            ref = surfaces.get(ref[1])
        effect_image[eff.get("id")] = image_file.get(ref)
material_effect = {}
for m in find_all(root, "library_materials/material"):
    material_effect[m.get("id")] = m.find("c:instance_effect", NS).get("url").lstrip("#")

bpy.ops.wm.read_factory_settings(use_empty=True)
bl_materials = {}


def material_for(material_id):
    """Material do Blender com a textura difusa (reduzida a 512 px); None se o material não tem imagem."""
    if material_id in bl_materials:
        return bl_materials[material_id]
    name = effect_image.get(material_effect.get(material_id, ""))
    mat = None
    if name and os.path.exists(os.path.join(folder, name)):
        mat = bpy.data.materials.new(os.path.splitext(name)[0])
        mat.use_nodes = True
        node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        img = bpy.data.images.load(os.path.join(folder, name), check_existing=True)
        if img.size[0] > 512:
            img.scale(512, max(1, int(img.size[1] * 512 / img.size[0])))
        node.image = img
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        mat.node_tree.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
        if name.lower().endswith(".png"):
            mat.node_tree.links.new(node.outputs["Alpha"], bsdf.inputs["Alpha"])
            mat.blend_method = "BLEND" if hasattr(mat, "blend_method") else None
        bsdf.inputs["Roughness"].default_value = 0.9
        mat.use_backface_culling = False
    bl_materials[material_id] = mat
    return mat


# --- Geometrias ---------------------------------------------------------------------------------------
geometries = {}
for g in find_all(root, "library_geometries/geometry"):
    mesh_el = g.find("c:mesh", NS)
    sources = {s.get("id"): floats(s.find("c:float_array", NS).text) for s in mesh_el.findall("c:source", NS)}
    strides = {s.get("id"): int(s.find("c:technique_common/c:accessor", NS).get("stride")) for s in mesh_el.findall("c:source", NS)}
    vertices = {v.get("id"): v.find("c:input[@semantic='POSITION']", NS).get("source").lstrip("#") for v in mesh_el.findall("c:vertices", NS)}
    prims = []
    for t in mesh_el.findall("c:triangles", NS) + mesh_el.findall("c:polylist", NS):
        inputs = [(i.get("semantic"), int(i.get("offset")), i.get("source").lstrip("#"), int(i.get("set", "0"))) for i in t.findall("c:input", NS)]
        stride = max(o for _, o, _, _ in inputs) + 1
        p = [int(v) for v in t.find("c:p", NS).text.split()]
        if t.tag.endswith("polylist"):
            counts = [int(v) for v in t.find("c:vcount", NS).text.split()]
        else:
            counts = [3] * int(t.get("count"))
        prims.append((t.get("material"), inputs, stride, p, counts))
    geometries[g.get("id")] = (sources, strides, vertices, prims)


def build_mesh(geom_id, bind):
    sources, strides, vertices, prims = geometries[geom_id]
    verts, faces, face_uv, face_mat = {}, [], [], []
    pos_source = None
    slots, slot_of = [], {}
    for symbol, inputs, stride, p, counts in prims:
        mat_id = bind.get(symbol)
        if mat_id not in slot_of:
            slot_of[mat_id] = len(slots)
            slots.append(mat_id)
        vtx = [i for i in inputs if i[0] == "VERTEX"][0]
        pos_source = vertices[vtx[2]]
        uvs = sorted([i for i in inputs if i[0] == "TEXCOORD"], key=lambda i: i[3])
        pos_stride = strides[pos_source]
        cursor = 0
        for n in counts:
            corner = []
            for k in range(n):
                row = p[(cursor + k) * stride:(cursor + k + 1) * stride]
                corner.append((row[vtx[1]], row[uvs[-1 if len(uvs) > 1 else 0][1]] if uvs else 0))
            cursor += n
            faces.append([c[0] for c in corner])
            face_uv.append([c[1] for c in corner])
            face_mat.append(slot_of[mat_id])
    pos = sources[pos_source]
    ps = strides[pos_source]
    n_verts = max(max(f) for f in faces) + 1
    coords = [Vector(pos[i * ps:i * ps + 3]) for i in range(n_verts)]
    mesh = bpy.data.meshes.new(geom_id)
    mesh.from_pydata(coords, [], faces)
    uv_src = None
    for symbol, inputs, stride, p, counts in prims:
        for i in inputs:
            if i[0] == "TEXCOORD":
                uv_src = (i[2], i[3])
    if uv_src:
        uv_sorted = sorted({i for sym, ins, st, pp, cc in prims for i in ins if i[0] == "TEXCOORD"}, key=lambda i: i[3])
        chosen = uv_sorted[-1] if len(uv_sorted) > 1 else uv_sorted[0]
        us = sources[chosen[2]]
        ust = strides[chosen[2]]
        layer = mesh.uv_layers.new(name="UVMap")
        li = 0
        for fuv in face_uv:
            for ui in fuv:
                layer.data[li].uv = (us[ui * ust], us[ui * ust + 1])
                li += 1
    for poly, mi in zip(mesh.polygons, face_mat):
        poly.material_index = mi
        poly.use_smooth = True
    for mat_id in slots:
        mesh.materials.append(material_for(mat_id))
    return mesh, slots


# --- Cena: nós em árvore -----------------------------------------------------------------------------------
def node_matrix(node):
    m = Matrix.Identity(4)
    for child in node:
        tag = child.tag.split("}")[1]
        if tag == "matrix":
            v = floats(child.text)
            m = m @ Matrix([v[0:4], v[4:8], v[8:12], v[12:16]])
        elif tag == "translate":
            m = m @ Matrix.Translation(Vector(floats(child.text)))
        elif tag == "rotate":
            x, y, z, a = floats(child.text)
            if abs(a) > 1e-9:
                m = m @ Matrix.Rotation(math.radians(a), 4, Vector((x, y, z)))
        elif tag == "scale":
            sx, sy, sz = floats(child.text)
            m = m @ Matrix.Diagonal((sx, sy, sz, 1.0))
    return m


objects = []


def walk(node, parent_matrix):
    name = node.get("name", "")
    if name in skip_nodes or name.lower().startswith(("col", "geom-col", "collision")):
        return
    m = parent_matrix @ node_matrix(node)
    for inst in node.findall("c:instance_geometry", NS):
        gid = inst.get("url").lstrip("#")
        bind = {im.get("symbol"): im.get("target").lstrip("#") for im in inst.findall(".//c:instance_material", NS)}
        mesh, slots = build_mesh(gid, bind)
        obj = bpy.data.objects.new(name or gid, mesh)
        obj.matrix_world = Matrix.Identity(4)
        mesh.transform(m)
        bpy.context.scene.collection.objects.link(obj)
        objects.append(obj)
    for child in node.findall("c:node", NS):
        walk(child, m)


scene = find_all(root, "library_visual_scenes/visual_scene")[0]
for top in scene.findall("c:node", NS):
    walk(top, Matrix.Scale(unit_scale, 4))
objects = [o for o in objects if o.data.materials and any(o.data.materials)]
assert objects, "nenhuma malha com textura"


def _box(o):
    vs = [v.co for v in o.data.vertices]
    return tuple(round(min(v[i] for v in vs) / 0.3) for i in range(3)) + tuple(round(max(v[i] for v in vs) / 0.3) for i in range(3))


# Peças com vários níveis de detalhe (LOD) vêm com as malhas uma sobre a outra: fica a de mais vértices de cada caixa.
best = {}
for o in objects:
    key = _box(o)
    if key not in best or len(o.data.vertices) > len(best[key].data.vertices):
        best[key] = o
objects = [o for o in objects if o in best.values()]

# --- Normaliza e exporta -----------------------------------------------------------------------------------
pts = [v.co for o in objects for v in o.data.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
kind, value = size_spec[0], float(size_spec[2:])
scale = value / (hi.z - lo.z) if kind == "h" else value / max(hi.x - lo.x, hi.y - lo.y) if kind == "w" else value
shift = Matrix.Scale(scale, 4) @ Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)))
for o in objects:
    o.data.transform(shift)
bpy.ops.object.select_all(action="DESELECT")
for o in objects:
    o.select_set(True)
bpy.context.view_layer.objects.active = objects[0]
bpy.ops.export_scene.gltf(filepath=out_path, export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=82)
# Colisão: caixas dos pedaços altos (colunas, muros), achadas pelos vértices entre 1,2 e 3,5 m agrupados em células de 0,5 m
# (no tamanho final; x/z do jogo). Gravadas em RUIN_PARTS_DIR/<peça>.json se a variável existir.
parts_dir = os.environ.get("RUIN_PARTS_DIR")
if parts_dir:
    import json
    cell = 0.5
    cells = {}
    for o in objects:
        for v in o.data.vertices:
            if 1.2 <= v.co.z <= 3.5:
                cells.setdefault((int(math.floor(v.co.x / cell)), int(math.floor(-v.co.y / cell))), []).append(v.co)
    seen, boxes = set(), []
    for start in cells:
        if start in seen:
            continue
        stack, comp = [start], []
        seen.add(start)
        while stack:
            cx, cz = stack.pop()
            comp.append((cx, cz))
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    nb = (cx + dx, cz + dz)
                    if nb in cells and nb not in seen:
                        seen.add(nb)
                        stack.append(nb)
        xs = [v.x for c in comp for v in cells[c]]
        zs = [-v.y for c in comp for v in cells[c]]
        boxes.append({"center": [round((min(xs) + max(xs)) / 2, 2), round((min(zs) + max(zs)) / 2, 2)],
                      "size": [round(max(xs) - min(xs), 2), round(max(zs) - min(zs), 2)], "verts": sum(len(cells[c]) for c in comp)})
    os.makedirs(parts_dir, exist_ok=True)
    json.dump(boxes, open(os.path.join(parts_dir, os.path.splitext(os.path.basename(out_path))[0] + ".json"), "w"), indent=1)
print("OK", os.path.basename(out_path), "%.2f x %.2f x %.2f m" % ((hi.x - lo.x) * scale, (hi.y - lo.y) * scale, (hi.z - lo.z) * scale),
      "%d vértices" % sum(len(o.data.vertices) for o in objects), [m.name for m in bl_materials.values() if m])
