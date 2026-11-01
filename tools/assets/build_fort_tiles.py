"""Peças do Forte (3D Dungeon Tileset, Skorpio, CC BY-SA 3.0, opendungeons): as 94 pedras "Claimed_<máscara>"
(a máscara diz quais dos 8 vizinhos N,NE,E,SE,S,SW,W,NW também são pedra) e o piso Claimed0, como .gltf
em assets/models/maps/fort/ (Fort_<máscara>, Fort_Floor). As texturas (parede e piso, cor e normal) ficam
uma vez só na pasta. Células de 2,5 m; o piso sai com 2 m (o lado do piso do kit).
uso: build_fort_tiles.py <pasta obj_export> <pasta textures> <saída>"""
import bpy, sys, os, glob
src, texdir, out = sys.argv[sys.argv.index("--") + 1:]
TEX = {"Claimed": ("ClaimedE.png", "Claimed_nor2.png"), "Claimedwall": ("Claimedwall2C.png", "Claimedwall2_nor3.png")}
files = sorted(glob.glob(os.path.join(src, "Claimed_*.obj"))) + [os.path.join(src, "Claimed0.obj")]


def material(name):
    color, normal = TEX[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    c = nodes.new("ShaderNodeTexImage"); c.image = bpy.data.images.load(os.path.join(texdir, color))
    links.new(c.outputs["Color"], bsdf.inputs["Base Color"])
    n = nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(os.path.join(texdir, normal)); n.image.colorspace_settings.name = "Non-Color"
    nm = nodes.new("ShaderNodeNormalMap")
    links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = 0.9
    mat.use_backface_culling = False  # topo e piso do pacote olham para dentro: a câmera do jogo vê por cima
    return mat


for path in files:
    stem = os.path.splitext(os.path.basename(path))[0]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=path)
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    for o in objs:
        names = [m.name for m in o.data.materials]
        o.data.materials.clear()
        for name in names:
            key = "Claimedwall" if "wall" in name.lower() else "Claimed"
            o.data.materials.append(material(key))
        # O piso sai com 2 m (o lado do piso do kit); as pedras ficam com metade da altura (1,4 m): a câmera olha do sul
        # e uma parede de 2,8 m na frente esconderia o herói.
        o.scale = (0.8, 0.8, 1.0) if stem == "Claimed0" else (1.0, 1.0, 0.5)
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.transform_apply(scale=True)
    name = "Fort_Floor" if stem == "Claimed0" else "Fort_" + stem.split("_")[1]
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".gltf"), export_format="GLTF_SEPARATE", export_image_format="JPEG")
print("OK", len(files))
