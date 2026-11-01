"""Conjunto de sofás (Sofa-group 5, sandsound / Duion2, CC-BY-SA 3.0, opengameart.org/content/sofa-group-5): três sofás, mesa
de centro e tapete numa peça só (Sofa_Group.glb) para a sala do rei da Capital. Os sofás levam a textura do arquivo
(cor + normal); a mesa e o tapete usavam texturas que não vêm no pacote e ficam em cor lisa (madeira escura e vermelho).
Base em y = 0, centro da planta na origem, 4,2 m de largura.
uso: build_sofa_group.py <pasta com sofa_group_5.blend e as texturas> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "sofa_group_5.blend"))
deps = bpy.context.evaluated_depsgraph_get()
parts = {}
for name in ("Cube", "Cube.001", "Cube.002"):
    o = bpy.data.objects[name]
    me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    me.transform(o.matrix_world)
    parts[name] = me
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
pts = [v.co for me in parts.values() for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 4.2 / (mx.x - mn.x)
fix = Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))


def material(name, colour=None, tex=None, normal=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = 0.8
    if tex:
        t = nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(src, tex))
        links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = colour
    if normal:
        n = nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(os.path.join(src, normal)); n.image.colorspace_settings.name = "Non-Color"
        nm = nodes.new("ShaderNodeNormalMap")
        links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


mats = {"Cube": material("Sofa", tex="sofa_group_5.png", normal="sofa_5_skin_n.png"),
        "Cube.001": material("Table", colour=(0.07, 0.035, 0.02, 1.0)),
        "Cube.002": material("Carpet", colour=(0.3, 0.03, 0.05, 1.0))}
for name, me in parts.items():
    me.transform(fix)
    me.materials.clear()
    me.materials.append(mats[name])
    ob = bpy.data.objects.new("Sofa_" + name.replace(".", "_"), me)
    bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK sofa group", [round(x * k, 2) for x in (mx - mn)])
