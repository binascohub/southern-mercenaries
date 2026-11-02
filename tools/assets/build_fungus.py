"""Tio Fungo (Uncle Fungus, piacenti, CC BY-SA 3.0, opengameart.org/content/uncle-fungus): a versão "low" (2728 triângulos) do arquivo,
sem esqueleto nem animação (o jogo o move por código em MonsterModel, família "static"). Pés em y = 0, 1 m de altura (o tamanho vem dos
dados), frente em +Z; cor e normal em 1024 px (as imagens estão embutidas no .blend).
uso: blender -b "fungus game.blend" --python build_fungus.py -- <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
out = sys.argv[sys.argv.index("--") + 1]
deps = bpy.context.evaluated_depsgraph_get()
o = bpy.data.objects["low fungus"]
mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
mesh.transform(o.matrix_world)
pts = [v.co for v in mesh.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
h = mx.z - mn.z
mesh.transform(Matrix.Scale(1.0 / h, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = bpy.data.materials.new("fungus")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
out_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
def tex(name, colorspace="sRGB"):
    img = bpy.data.images[name]
    img.scale(1024, 1024)
    img.colorspace_settings.name = colorspace
    node = nodes.new("ShaderNodeTexImage")
    node.image = img
    return node
color = tex("low text.png")
links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
normal = tex("low normal.png", "Non-Color")
nmap = nodes.new("ShaderNodeNormalMap")
links.new(normal.outputs["Color"], nmap.inputs["Color"]); links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Roughness"].default_value = 0.8
mesh.materials.clear(); mesh.materials.append(mat)
for other in list(bpy.data.objects):
    bpy.data.objects.remove(other, do_unlink=True)
bpy.context.scene.collection.objects.link(bpy.data.objects.new("Fungus", mesh))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP")
print("OK", [round(x / h, 2) for x in (mx - mn)])
