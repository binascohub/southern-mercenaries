"""Objetos de cenário do OpenGameArt (todos CC0) em .glb: barril de cerveja com
torneira (eugeneloza), caneco de madeira (rehcub), baú do tesouro (mastahcez),
chave (codeinfernogames) e caixotes de madeira (Yughues). Malhas juntas com as transformações aplicadas, base em
y = 0, altura padronizada; texturas reduzidas (WebP) ou cores lisas quando o
arquivo original não traz a imagem.
uso: build_props.py <pasta dl> <saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
dl, out = sys.argv[sys.argv.index("--") + 1:]
PROPS = [
    # nome, arquivo, altura (m), textura, {material: cor} quando não há textura
    # (o barril vem junto com um banquinho: fica só o grupo de peças do barril)
    ("Beer_Barrel", "beer/DwarfBeerBarrel.blend", 1.05, "beer/DwarfBeerBarrel_texture4.png", {}, [], True),
    ("Mug_Wood", "mug/woodmug_0.blend", 0.16, "", {"Material.001": (0.42, 0.26, 0.13, 1), "Material.002": (0.45, 0.45, 0.48, 1)}, ["Mug Detail"], False),
    ("Treasure_Chest", "chest/treasure_chest.obj", 0.85, "chest/Treasurechest_DIFF.png", {}, [], False),
    # Caixotes de madeira (Yughues, CC0): todos na mesma escala (x2,2).
    ("Crate_Open", "crates/Crate-01.obj", 0.40, "crates/diffuse.tga", {}, [], False),
    ("Crate_Small", "crates/Crate-02.obj", 0.37, "crates/diffuse.tga", {}, [], False),
    ("Crate_Long", "crates/Crate-03.obj", 0.53, "crates/diffuse.tga", {}, [], False),
    ("Crate_Big", "crates/Crate-04.obj", 1.17, "crates/diffuse.tga", {}, [], False),
    ("Bucket_Crate", "crates/Crate-05.obj", 0.44, "crates/diffuse.tga", {}, [], False),
    # Poço coberto (iconoclast, CC0): textura embutida no .blend ("@").
    ("Well_Covered", "well/well.coveredopen.blend", 2.3, "well/well_color.png", {}, [], False),
    # Cogumelos (Clint Bellanger, CC BY 3.0) para o Esgoto: os vermelhos e os pálidos.
    ("Mushroom_Cluster", "mush/shrooms.blend", 0.6, "mush/shroom_color.png", {}, ["Shroom%d" % i for i in range(1, 10)], False),
    ("Mushroom_Tall", "mush/shrooms.blend", 0.65, "mush/shroom_color2.png", {}, ["Shroom4", "Shroom5", "Shroom6"], False),
    ("Mushroom_Flat", "mush/shrooms.blend", 0.15, "mush/shroom_color.png", {}, ["Shroom7", "Shroom8", "Shroom9"], False),
    # Arqueria (yd, CC0): arco longo do Arqueiro, aljava com flechas e alvo.
    ("Bow_Long", "archery/archerySetOGA.blend", 1.3, "@bow01D", {}, ["bow"], False),
    ("Quiver", "archery/archerySetOGA.blend", 0.9, "@bow01D", {}, ["quiver"] + ["Circle.%03d" % i for i in (4, 5, 6, 7, 8, 9, 10, 11, 12, 14)], False),
    ("Archery_Target", "archery/archerySetOGA.blend", 1.0, "@aim", {}, ["aim"], False),
    # Medieval Props 2 (Daniel74, CC0): torre de vigia, banco, banquinho, carroça, carrinho de mão.
    ("Watch_Tower", "mprops/Props2.blend", 4.0, "mprops/wood floor 2.png", {}, ["WoodenTower"], False),
    ("Bench_Wood", "mprops/Props2.blend", 1.0, "mprops/Wood.jpg", {}, ["Bench"], False),
    ("Stool_Wood", "mprops/Props2.blend", 0.45, "mprops/Wood.jpg", {}, ["Stool"], False),
    ("Cart_Wood", "mprops/Props2.blend", 1.0, "mprops/wood floor 2.png", {}, ["Wagon"], False),
    ("Wheelbarrow", "mprops/Props2.blend", 0.45, "mprops/wood floor 2.png", {}, ["WheelBarrow"], False),
    # Barricada de estacas (sullivan, CC BY 3.0).
    ("Barricade_Stakes", "barricade/barricade.blend", 1.5, "barricade/barricade_color.png", {}, [], False),
    ("Key_Gold", "key/key.blend", 0.32, "", {"Material": (0.95, 0.75, 0.25, 1), "Key_Gold_Mat": (0.95, 0.75, 0.25, 1)}, [], False),
]

def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    full = os.path.join(dl, path)
    if path.endswith(".blend"):
        with bpy.data.libraries.load(full) as (src, dst):
            dst.objects = src.objects
            dst.images = src.images  # texturas embutidas que os materiais antigos não citam
        for o in dst.objects:
            if o is not None and o.type == "MESH":
                bpy.context.scene.collection.objects.link(o)
    else:
        bpy.ops.wm.obj_import(filepath=full)
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and len(o.data.polygons) > 0]

def biggest_cluster(o):
    """Só as partes soltas que caem na caixa da maior (o barril, sem o banquinho)."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.verts.ensure_lookup_table()
    seen, parts = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, part = [v], []
        seen.add(v.index)
        while stack:
            cur = stack.pop()
            part.append(cur)
            for e in cur.link_edges:
                other = e.other_vert(cur)
                if other.index not in seen:
                    seen.add(other.index)
                    stack.append(other)
        parts.append(part)
    big = max(parts, key=len)
    lo = Vector([min(v.co[i] for v in big) for i in range(3)])
    hi = Vector([max(v.co[i] for v in big) for i in range(3)])
    pad = (hi - lo) * 0.15
    gone = []
    for part in parts:
        c = sum((v.co for v in part), Vector()) / len(part)
        if not all(lo[i] - pad[i] <= c[i] <= hi[i] + pad[i] for i in range(3)):
            gone += part
    bmesh.ops.delete(bm, geom=gone, context="VERTS")
    bm.to_mesh(o.data)
    bm.free()

for name, path, height, tex, colors, keep, cluster in PROPS:
    meshes = load(path)
    for o in meshes:  # o primeiro mapa UV é o das texturas
        if o.data.uv_layers:
            o.data.uv_layers[0].active = True
            o.data.uv_layers[0].active_render = True
    if keep:
        meshes = [o for o in meshes if o.name in keep]
    # Malha avaliada (modificadores aplicados: array, curva, subdivisão…).
    deps = bpy.context.evaluated_depsgraph_get()
    for o in meshes:
        mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
        mesh.transform(o.matrix_world)
        o.modifiers.clear()
        o.data = mesh
        o.parent = None
        o.matrix_world = Matrix.Identity(4)
        if not o.material_slots or all(sl.material is None for sl in o.material_slots):
            o.data.materials.clear()
            o.data.materials.append(bpy.data.materials.new(name + "_Mat"))
    if cluster:
        for o in meshes:
            biggest_cluster(o)
    pts = [v.co for o in meshes for v in o.data.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    scale = height / (mx.z - mn.z)
    fix = Matrix.Scale(scale, 4) @ Matrix.Translation(-Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z)))
    if tex.startswith("@"):
        image = bpy.data.images.get(tex[1:])
    else:
        image = bpy.data.images.load(os.path.join(dl, tex)) if tex else None
    if image and image.size[0] > 512:
        image.scale(512, 512)
    for o in meshes:
        o.data.transform(fix)
        for slot in o.material_slots:
            mat = slot.material
            if mat is None:
                continue
            mat.use_nodes = True
            nodes, links = mat.node_tree.nodes, mat.node_tree.links
            nodes.clear()
            out_node = nodes.new("ShaderNodeOutputMaterial")
            bsdf = nodes.new("ShaderNodeBsdfPrincipled")
            links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
            bsdf.inputs["Roughness"].default_value = 0.7
            if image:
                node = nodes.new("ShaderNodeTexImage")
                node.image = image
                links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
            else:
                bsdf.inputs["Base Color"].default_value = colors.get(mat.name, (0.5, 0.5, 0.5, 1))
                if name == "Key_Gold":
                    bsdf.inputs["Metallic"].default_value = 0.9
                    bsdf.inputs["Roughness"].default_value = 0.3
    for o in list(bpy.context.scene.objects):
        if o not in meshes:
            bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB",
        export_image_format="WEBP", export_image_quality=88)
    print("OK", name, [round(v * scale, 2) for v in (mx - mn)], len(meshes))
