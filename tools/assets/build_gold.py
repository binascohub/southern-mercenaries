"""Pilhas de barras de ouro (Free Low Poly Gold, Nobiax, CC0) em .glb: Gold_Pile_1..5, em pé (base em y = 0),
na escala 2,2 (a mesma dos caixotes do Yughues), textura g_diffuse reduzida a WebP.
uso: blender -b -P build_gold.py -- <pasta do pacote extraído> <saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
dl, out = sys.argv[sys.argv.index("--") + 1:]
PILES = {"Gold_Pile_1": "Gold-01", "Gold_Pile_2": "Gold-05", "Gold_Pile_3": "Gold-10", "Gold_Pile_4": "Gold-15",
         "Gold_Pile_5": "Gold-20"}
SCALE = 2.2
for name, src in PILES.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=os.path.join(dl, src + ".obj"))
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and len(o.data.polygons) > 0]
    pts = []
    for o in meshes:
        o.data.transform(o.matrix_world)
        o.parent = None
        o.matrix_world = Matrix.Identity(4)
        pts += [v.co.copy() for v in o.data.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    fix = Matrix.Scale(SCALE, 4) @ Matrix.Translation(-Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z)))
    image = bpy.data.images.load(os.path.join(dl, "g_diffuse.tga"))
    for o in meshes:
        o.data.transform(fix)
        o.data.materials.clear()
        mat = bpy.data.materials.new(name + "_Mat")
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        nodes.clear()
        out_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
        bsdf.inputs["Roughness"].default_value = 0.35
        bsdf.inputs["Metallic"].default_value = 0.6
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = image
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        o.data.materials.append(mat)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB",
        export_image_format="WEBP", export_image_quality=88)
    print("OK", name, [round(v * SCALE, 2) for v in (mx - mn)])
