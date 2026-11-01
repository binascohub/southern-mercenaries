"""Canecas brancas do "Free Mug Pack 1" (rubberduck, OpenGameArt, CC0): o jarro alto creme (mug_1) e a garrafa de mármore
branco (mug_3), em assets/models/props/ como Mug_Jar e Mug_Bottle, cada uma com os cacos (Mug_Jar_Shards, Mug_Bottle_Shards:
a malha partida em até 8 pedaços por quadrante e altura, cada um com a origem no próprio centro, para voarem ao quebrar,
como os potes do Esgoto). A caneca de cobre (mug_2) não foi usada. Mesma escala nas duas (jarro com 0,95 m), base em y = 0.
uso: blender -b mugs-1.blend --python tools/assets/build_mugs.py -- <saída: assets/models/props>
(as texturas mug1.png e mug3.png ficam ao lado do .blend)"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix

out = sys.argv[sys.argv.index("--") + 1]
SRC = os.path.dirname(bpy.data.filepath)
PIECES = {"mug_1": ("Mug_Jar", "mug1.png"), "mug_3": ("Mug_Bottle", "mug3.png")}
JAR_HEIGHT = 0.95
for o in list(bpy.data.objects):
    if o.name not in PIECES:
        bpy.data.objects.remove(o, do_unlink=True)
jar = bpy.data.objects["mug_1"]
scale = JAR_HEIGHT / jar.dimensions.z


def material(name, tex):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    node = nodes.new("ShaderNodeTexImage")
    node.image = bpy.data.images.load(os.path.join(SRC, tex), check_existing=True)
    links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.55
    mat.use_backface_culling = False       # os cacos são folhas finas: aparecem dos dois lados
    return mat


def export(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True,
                              export_image_format="WEBP", export_image_quality=85)


for src_name, (piece, tex) in PIECES.items():
    src = bpy.data.objects[src_name]
    mat = material(piece, tex)
    # Cópia da malha com o objeto aplicado: base em z = 0, centro em x/y.
    mesh = src.data.copy()
    mesh.transform(src.matrix_world)
    pts = [v.co for v in mesh.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    mesh.transform(Matrix.Scale(scale, 4) @ Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))))
    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.materials.clear()
    mesh.materials.append(mat)
    whole = bpy.data.objects.new(piece, mesh)
    bpy.context.scene.collection.objects.link(whole)
    export([whole], os.path.join(out, piece + ".glb"))

    # Cacos: quadrante (em volta do eixo) x metade de cima/de baixo.
    height = (hi.z - lo.z) * scale
    chunks = {}
    for poly in mesh.polygons:
        c = poly.center
        key = (int(((math.atan2(c.y, c.x) + math.pi) / (math.tau)) * 4) % 4, 0 if c.z < height / 2 else 1)
        chunks.setdefault(key, []).append(poly.index)
    shards = []
    for key, faces in sorted(chunks.items()):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()
        keep = set(faces)
        drop = [f for f in bm.faces if f.index not in keep]
        bmesh.ops.delete(bm, geom=drop, context="FACES")
        loose = [v for v in bm.verts if not v.link_faces]
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
        center = sum((v.co for v in bm.verts), Vector()) / max(len(bm.verts), 1)
        bmesh.ops.translate(bm, vec=-center, verts=bm.verts)
        piece_mesh = bpy.data.meshes.new("%s_Shard_%d_%d" % (piece, *key))
        bm.to_mesh(piece_mesh)
        bm.free()
        piece_mesh.materials.append(mat)
        shard = bpy.data.objects.new("Shard_%d_%d" % key, piece_mesh)
        shard.location = center
        bpy.context.scene.collection.objects.link(shard)
        shards.append(shard)
    export(shards, os.path.join(out, piece + "_Shards.glb"))
    print("OK", piece, "%.2f x %.2f x %.2f m" % ((hi.x - lo.x) * scale, (hi.y - lo.y) * scale, height), len(shards), "cacos")
