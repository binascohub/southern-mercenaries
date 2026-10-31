"""Potes quebráveis do Esgoto (Stylized Vases And Pots, FabinhoSC, CC0): o pote
inteiro e os cacos dele (cada caco com a origem no próprio centro, para voarem
ao quebrar), na mesma escala e com a base em y = 0. Texturas 128 px, WebP.
uso: build_pots.py <pasta do pacote> <saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
base, out = sys.argv[sys.argv.index("--") + 1:]
SCALE = 0.7
POTS = [
    ("Pot_Large", "Variation01/StylizedPot01(Large).fbx", "Broken /Variation01/StylizedPot01(Parts)(Large).fbx", "01"),
    ("Pot_Small", "Variation02/StylizedPot02(Variation02)(Small).fbx", "Broken /Variation02/StylizedPot02(Parts)(Variation02)(Small).fbx", "02"),
    ("Vase_Big", "Variation02/StylizedVase03(Variation02)(Big).fbx", "Broken /Variation02/StylizedVase03(Parts)(Variation02)(Big).fbx", "02"),
]

def load(path, tex):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(base, "Models/FBX", path))
    image = bpy.data.images.load(os.path.join(base, "Textures/TextureVaseAndPots%s.png" % tex))
    for mat in bpy.data.materials:
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        nodes.clear()
        out_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = 0.75
        node = nodes.new("ShaderNodeTexImage")
        node.image = image
        node.interpolation = "Closest"
        links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    for o in list(bpy.data.objects):
        if o.type != "MESH":
            bpy.data.objects.remove(o, do_unlink=True)
    # Transformações aplicadas nos vértices (sem pais, sem escala no objeto).
    for o in meshes:
        world = o.matrix_world.copy()
        o.parent = None
        o.data.transform(world)
        o.matrix_world = Matrix.Identity(4)
    return meshes

def bottom_center(meshes):
    pts = [v.co for o in meshes for v in o.data.vertices]
    return Vector(((min(p.x for p in pts) + max(p.x for p in pts)) / 2, (min(p.y for p in pts) + max(p.y for p in pts)) / 2, min(p.z for p in pts)))

def export(path):
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_image_format="WEBP", export_image_quality=90)

for name, whole, broken, tex in POTS:
    meshes = load(whole, tex)
    center = bottom_center(meshes)
    fix = Matrix.Scale(SCALE, 4) @ Matrix.Translation(-center)
    for o in meshes:
        o.data.transform(fix)
        o.name = name
    export(os.path.join(out, name + ".glb"))
    meshes = load(broken, tex)
    for i, o in enumerate(meshes):
        o.data.transform(fix)
        pts = [v.co for v in o.data.vertices]
        mid = sum(pts, Vector()) / len(pts)
        o.data.transform(Matrix.Translation(-mid))
        o.location = mid
        o.name = "Shard_%02d" % i
    export(os.path.join(out, name + "_Shards.glb"))
    print("OK", name, len(meshes), "cacos")
