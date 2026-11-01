"""Anglerman (Angler Man 3D, piacenti sobre arte de 5hiroi, CC BY 3.0, opengameart.org/content/angler-man-3d): malha única (sem a
animação, que o arquivo não tem), em pé, pés em y = 0, 1 m de altura, frente em +Z; cor, normal e brilho dos olhos em 1024 px.
uso: build_angler.py <angler game.blend> <pasta das texturas> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, texdir, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
o = bpy.data.objects["angler final"]
for m in o.modifiers:
    if m.type == "DISPLACE":
        m.show_viewport = False  # o relevo vem do normal map; o deslocamento de 4096 px pesaria
    if m.type == "SUBSURF":
        m.levels = 1
deps = bpy.context.evaluated_depsgraph_get()
mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), depsgraph=deps)
mesh.transform(o.matrix_world)
pts = [v.co for v in mesh.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
mesh.transform(Matrix.Scale(1.0 / (mx.z - mn.z), 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = bpy.data.materials.new("Angler")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
bsdf = nodes["Principled BSDF"]
def tex(name, cs="sRGB"):
    n = nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(os.path.join(texdir, name)); n.image.colorspace_settings.name = cs; n.image.scale(1024, 1024)
    return n
c = tex("texture final.png"); links.new(c.outputs["Color"], bsdf.inputs["Base Color"])
n = tex("normal final.png", "Non-Color"); nm = nodes.new("ShaderNodeNormalMap")
links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Roughness"].default_value = 0.6
mesh.materials.clear(); mesh.materials.append(mat)
for other in list(bpy.data.objects):
    bpy.data.objects.remove(other, do_unlink=True)
ob = bpy.data.objects.new("Angler", mesh)
bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK", len(mesh.polygons), [round(x / (mx.z - mn.z), 2) for x in (mx - mn)])
