"""Ferramentas de fazenda (Retextured Gnarly Tools, Mev Lyshkin, CC-BY 3.0): o narzedzia.blend traz todas as
ferramentas numa malha só; aqui cada peça solta vira um .glb (de pé, cabeça para +Y, origem no meio do comprimento,
tamanho do jogo; mesma convenção das armas, build_weapons.py), com a textura do autor refeita no material.
uso: blender -b -P build_farm_tools.py -- <narzedzia.blend> <pasta de saída>"""
import bpy, bmesh, sys, os
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
# (x mínimo da peça no arquivo -> nome, comprimento em metros)
PARTS = {-0.69: ("Tool_Shovel", 1.35), 1.25: ("Tool_Pitchfork", 1.5), 2.98: ("Tool_Hoe", 1.4),
         4.54: ("Tool_Scythe", 1.7), -4.44: ("Tool_Sickle", 0.5)}
bpy.ops.wm.open_mainfile(filepath=src)
shovel = bpy.data.objects["Shovel"]
image = bpy.data.images["narzedzia.jpg"]
bm = bmesh.new()
bm.from_mesh(shovel.data)
uv = bm.loops.layers.uv.active
seen, islands = set(), []
for v in bm.verts:
    if v.index in seen:
        continue
    stack, comp = [v], []
    seen.add(v.index)
    while stack:
        a = stack.pop()
        comp.append(a)
        for e in a.link_edges:
            b = e.other_vert(a)
            if b.index not in seen:
                seen.add(b.index)
                stack.append(b)
    islands.append(comp)
made = []
for comp in islands:
    key = round(min(v.co.x for v in comp), 2)
    match = [k for k in PARTS if abs(k - key) < 0.004]
    if not match:
        continue
    name, length = PARTS[match[0]]
    idx = {v.index for v in comp}
    part = bm.copy()
    for v in [v for v in part.verts if v.index not in idx]:
        part.verts.remove(v)
    mesh = bpy.data.meshes.new(name)
    part.to_mesh(mesh)
    part.free()
    pts = [v.co.copy() for v in mesh.vertices]
    # Cabo ao longo de Y (o arquivo deita as ferramentas assim); a cabeça é a ponta mais larga em X.
    ys = [p.y for p in pts]
    mid = (min(ys) + max(ys)) / 2
    top = [abs(p.x) for p in pts if p.y > mid]
    low = [abs(p.x) for p in pts if p.y <= mid]
    wide_top = (max(top) if top else 0) >= (max(low) if low else 0)
    # Ferramentas com cabeça mais larga em x (pá, forcado, enxada, foice) ficam com a cabeça para cima.
    cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
    cz = (min(p.z for p in pts) + max(p.z for p in pts)) / 2
    flip = Matrix.Rotation(3.14159265, 4, "X") if not wide_top else Matrix.Identity(4)
    # Blender Y -> Z (para cima no glTF vira +Y): gira -90° em torno de X depois de centralizar.
    mesh.transform(Matrix.Translation((-cx, -mid, -cz)))
    mesh.transform(flip)
    mesh.transform(Matrix.Rotation(1.5707963, 4, "X"))
    size_y = max(p.z for p in [v.co for v in mesh.vertices]) - min(v.co.z for v in mesh.vertices)
    mesh.transform(Matrix.Scale(length / size_y, 4))
    mat = bpy.data.materials.new("Tools")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.85
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    made.append(obj)
    print("PART", name, length, "cabeça invertida" if not wide_top else "")

# Cada ferramenta numa .glb própria (só o objeto selecionado vai no arquivo).
for obj in made:
    for o in bpy.context.scene.objects:
        o.select_set(o == obj)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, obj.name + ".glb"), export_format="GLB", use_selection=True,
        export_image_format="WEBP", export_image_quality=85)
    print("OK", obj.name)
