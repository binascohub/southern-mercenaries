"""Ossos e crânios do "3D Dungeon Debris - Skull and Bones" (Paul Wortmann, OpenGameArt, CC0), em assets/models/maps/ como
Dungeon_*: dois crânios, osso solto, ossos cruzados com crânio, pilha de crânios, seis pilhas de ossos e as peças de esqueleto
(braço, perna, coluna, caixa torácica, pélvis). Os OBJ vêm sem .mtl: os do pacote 1 (crânios e ossos) usam a textura skull_1_001
e os do pacote 2 (peças e pilhas), bone_1_001, ambas com normal, reduzidas a 512 px. As peças deitam no chão (base em y = 0,
centradas em x/z) e saem em escala 0,5 da original (crânio com ~0,4 m), para a câmera de cima ler bem.
uso: blender -b -P tools/assets/build_bone_debris.py -- <pasta dungeon_debris_-_skull_and_bones_2 extraída> <saída: assets/models/maps>"""
import bpy, sys, os
from mathutils import Vector, Matrix

base, out = sys.argv[sys.argv.index("--") + 1:][:2]
SCALE = 0.5
SKULL_TEX = ("textures_1/skull_1_001_d.png", "textures_1/skull_1_001_n.png")
BONE_TEX = ("textures_2/bone_1_001_d.png", "textures_2/bone_1_001_n.png")
# (arquivo OBJ, nome da peça, textura)
PIECES = [
    ("export_obj_1/skull_1_001.obj", "Dungeon_Skull_1", SKULL_TEX),
    ("export_obj_1/skull_1_002.obj", "Dungeon_Skull_2", SKULL_TEX),
    ("export_obj_1/bones_1_001.obj", "Dungeon_CrossBones", SKULL_TEX),
    ("export_obj_1/bones_1_002.obj", "Dungeon_BonePile_1", SKULL_TEX),
    ("export_obj_1/bones_1_003.obj", "Dungeon_SkullPile", SKULL_TEX),
    ("export_obj_1/bones_1_004.obj", "Dungeon_Bone", SKULL_TEX),
    ("export_obj_2/arm_2_001.obj", "Dungeon_Arm", BONE_TEX),
    ("export_obj_2/leg_2_001.obj", "Dungeon_Leg", BONE_TEX),
    ("export_obj_2/spine_2_001.obj", "Dungeon_Spine", BONE_TEX),
    ("export_obj_2/ribcage_2_001.obj", "Dungeon_Ribcage", BONE_TEX),
    ("export_obj_2/pelvis_2_001.obj", "Dungeon_Pelvis", BONE_TEX),
    ("export_obj_2/bone_pile_2_001.obj", "Dungeon_BonePile_2", BONE_TEX),
    ("export_obj_2/bone_pile_2_002.obj", "Dungeon_BonePile_3", BONE_TEX),
    ("export_obj_2/bone_pile_2_003.obj", "Dungeon_BonePile_4", BONE_TEX),
    ("export_obj_2/bone_pile_2_004.obj", "Dungeon_BonePile_5", BONE_TEX),
    ("export_obj_2/bone_pile_2_005.obj", "Dungeon_BonePile_6", BONE_TEX),
]

for obj_file, name, (color_path, normal_path) in PIECES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=os.path.join(base, obj_file))
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    mesh = obj.data
    mesh.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    pts = [v.co for v in mesh.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    mesh.transform(Matrix.Scale(SCALE, 4) @ Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))))
    # Um material só, com a textura do conjunto.
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.75
    color = nodes.new("ShaderNodeTexImage")
    color.image = bpy.data.images.load(os.path.join(base, color_path))
    color.image.scale(512, 512)
    links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
    norm = nodes.new("ShaderNodeTexImage")
    norm.image = bpy.data.images.load(os.path.join(base, normal_path))
    norm.image.colorspace_settings.name = "Non-Color"
    norm.image.scale(512, 512)
    nmap = nodes.new("ShaderNodeNormalMap")
    links.new(norm.outputs["Color"], nmap.inputs["Color"])
    links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    mat.use_backface_culling = False
    mesh.materials.clear()
    mesh.materials.append(mat)
    for p in mesh.polygons:
        p.material_index = 0
        p.use_smooth = True
    obj.name = name
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", use_selection=True,
                              export_image_format="WEBP", export_image_quality=82)
    print("OK", name, "%.2f x %.2f x %.2f m" % ((hi.x - lo.x) * SCALE, (hi.y - lo.y) * SCALE, (hi.z - lo.z) * SCALE), len(mesh.polygons), "faces")
