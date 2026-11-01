"""Carroças de madeira (Carts, cemkalyoncu, CC-BY 3.0): assets/models/maps/Pr_CartSmall.glb e Pr_CartLarge.glb.
O .blend traz duas carroças (cada uma com o seu esqueleto, que só gira as rodas): aqui cada uma vira uma malha só,
na pose do primeiro quadro, com materiais refeitos (a textura de madeira embutida nos "uv", cor lisa nos outros),
com as rodas no chão (base em y = 0), centrada em x/z.
uso: blender -b -P tools/assets/build_carts.py -- <cart_0.blend> <pasta de saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from farm_palette import unify_wood

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
NAMES = {"Armature": "Pr_CartSmall", "Armature.001": "Pr_CartLarge"}
bpy.ops.wm.open_mainfile(filepath=src)
bpy.context.scene.frame_set(1)
deps = bpy.context.evaluated_depsgraph_get()
wood = bpy.data.images["wood tex2.png"]
wood = unify_wood(wood, sat_limit=1.01)  # tom único de madeira da Fazenda (farm_palette.py)
for mat in bpy.data.materials:
    color = tuple(mat.diffuse_color)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.9
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    if mat.name.lower().endswith("uv"):
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = wood
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        if "wood" in mat.name.lower():  # madeira lisa: o tom da cerca, com o claro/escuro da cor original
            from farm_palette import WOOD
            lum = 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]
            k = min(max(lum / 0.3, 0.55), 1.3)
            color = (WOOD[0] * k, WOOD[1] * k, WOOD[2] * k, 1.0)
        bsdf.inputs["Base Color"].default_value = color
made = []
for arm_name, name in NAMES.items():
    parts = []
    for o in bpy.data.objects:
        if o.type == "MESH" and o.parent and o.parent.name == arm_name:
            mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
            mesh.transform(o.matrix_world)
            obj = bpy.data.objects.new("p_" + o.name, mesh)
            bpy.context.scene.collection.objects.link(obj)
            parts.append(obj)
    bpy.ops.object.select_all(action="DESELECT")
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    whole = bpy.context.view_layer.objects.active
    whole.name = whole.data.name = name
    pts = [v.co for v in whole.data.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    whole.data.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    made.append(whole)
    print("PART", name, "caixa %.2f x %.2f x %.2f m" % tuple(mx[i] - mn[i] for i in range(3)))
for o in [o for o in bpy.data.objects if o not in made]:
    bpy.data.objects.remove(o, do_unlink=True)
for whole in made:
    for other in bpy.context.scene.objects:
        other.select_set(other == whole)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, whole.name + ".glb"), export_format="GLB", use_selection=True,
                              export_image_format="WEBP", export_image_quality=85)
    print("OK", whole.name)
