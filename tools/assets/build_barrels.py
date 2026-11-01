"""Barris (Three Barrels, yd, CC0, opengameart.org/content/three-barrels): Barrel_Oga_1 (com água), Barrel_Oga_2 (vazio) e
Barrel_Oga_Damaged (rachado, com teias), com a textura de cor e a normal embutidas, base em y = 0, 0,95 m de altura, centro na origem.
uso: build_barrels.py <barrelsOGA_1.blend> <pasta de saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
PICK = {"Barrel_Oga_1": ("barrel1", "barrel02D", "barrel"), "Barrel_Oga_2": ("barrel2.003", "barrel02D", "barrel"),
        "Barrel_Oga_Damaged": ("barrel2.011", "barrel02Ddamage.jpg", "barrelDamage")}
HEIGHT = 0.95
for name, (obj_name, color_img, mat_name) in PICK.items():
    bpy.ops.wm.open_mainfile(filepath=src)
    obj = bpy.data.objects[obj_name]
    deps = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    me.transform(obj.matrix_world)
    colour = bpy.data.images[color_img]
    normal = bpy.data.images["barrel02N.jpg"]
    spec_unused = bpy.data.images["barrel02S.jpg"]
    for other in list(bpy.data.objects):
        bpy.data.objects.remove(other, do_unlink=True)
    pts = [v.co for v in me.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    k = HEIGHT / (mx.z - mn.z)
    me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
    c = nodes.new("ShaderNodeTexImage"); c.image = colour
    links.new(c.outputs["Color"], bsdf.inputs["Base Color"])
    n = nodes.new("ShaderNodeTexImage"); n.image = normal; normal.colorspace_settings.name = "Non-Color"
    nm = nodes.new("ShaderNodeNormalMap")
    links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = 0.8
    for img in (colour, normal):
        img.scale(512, 512)
    me.materials.clear()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", export_image_format="JPEG")
    print("OK barrel", name, [round(x * k, 2) for x in (mx - mn)])
