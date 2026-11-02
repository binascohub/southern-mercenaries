"""Kit do Bunker (3D Dungeon Modular Wall Set 2, Paul Wortmann, CC0): assets/models/maps/Bk_*.glb, uma peça por OBJ.
Módulo de 2 m (comprimento da parede ao longo de Z, espessura de 0,5 em X, 3 m de altura); todas usam a mesma textura
(dungeon_wall_2_001_d.png, sem o relevo _n.png). Origem no centro da peça em planta, chão em y = 0.
uso: blender -b -P tools/assets/build_bunker_kit.py -- <pasta Dungeon_002 extraída> <pasta de saída>"""
import bpy, sys, os

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
NAMES = {"wall_1td_001": "Bk_Wall", "wall_1td_002": "Bk_WallThick", "wall_1ts_001": "Bk_WallA", "wall_1tl_001": "Bk_WallB",
         "wall_1ta_001": "Bk_Lintel", "wall_1tp_001": "Bk_Pillar", "wall_1tc_001": "Bk_Corner", "wall_1te_001": "Bk_End",
         "wall_1tt_001": "Bk_T", "wall_1tx_001": "Bk_X", "wall_2tds_001": "Bk_StairsDown", "wall_2tus_001": "Bk_StairsUp",
         "wall_3td_001": "Bk_Wall3"}
for stem, name in NAMES.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=os.path.join(src, "dungeon_002_%s.obj" % stem), forward_axis="NEGATIVE_Z", up_axis="Y")
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    piece = bpy.context.view_layer.objects.active
    piece.name = piece.data.name = name
    mat = bpy.data.materials.new("Bunker")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.9
    color = nodes.new("ShaderNodeTexImage")
    color.image = bpy.data.images.load(os.path.join(src, "dungeon_wall_2_001_d.png"))
    color.image.scale(1024, 1024)  # atlas de 2048 com 4 quadrantes (tijolo, musgo, pedra, sangue): 1024 basta e pesa 1/4
    links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
    piece.data.materials.clear()
    piece.data.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    piece.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", use_selection=True,
                              export_image_format="WEBP", export_image_quality=85)
    print("OK", name)

# Bk_Rock: bloco de rocha de uma célula (2 x 1,2 x 2 m, baixo para não esconder o herói) para tapar o que fica fora das paredes, com o quadrante de pedra escura
# do atlas (canto inferior esquerdo) nas seis faces.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
rock = bpy.context.view_layer.objects.active
rock.name = rock.data.name = "Bk_Rock"
rock.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 1.0)))
rock.scale = (1.0, 1.0, 0.6)
bpy.ops.object.transform_apply(scale=True)
rock.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 0)))
for loop in rock.data.uv_layers.active.data:
    loop.uv = (loop.uv[0] * 0.5, loop.uv[1] * 0.5)
mat = bpy.data.materials.new("Bunker")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.95
tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(os.path.join(src, "dungeon_wall_2_001_d.png"))
tex.image.scale(1024, 1024)
mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
rock.data.materials.append(mat)
bpy.ops.object.select_all(action="DESELECT")
rock.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Bk_Rock.glb"), export_format="GLB", use_selection=True,
                          export_image_format="WEBP", export_image_quality=85)
print("OK Bk_Rock")
