"""Feiticeiro-aranha (Wizard, piacenti, CC BY-SA 3.0, opengameart.org/content/wizard-3), o chefe do Esgoto:
malha única sem esqueleto nem animação (o jogo o move por código em MonsterModel). Pés em y = 0, 1 m de altura (o tamanho vem dos dados do monstro),
frente em +Z; cor, normal e emissão (o olho e as runas) em 1024 px.
uso: build_demon.py <wizard2.blend> <pasta com as texturas> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, texdir, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
deps = bpy.context.evaluated_depsgraph_get()
o = bpy.data.objects["wizard"]
mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
mesh.transform(o.matrix_world)
pts = [v.co for v in mesh.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
mesh.transform(Matrix.Scale(1.0 / (mx.z - mn.z), 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = bpy.data.materials["wizard"]
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
out_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
def tex(name, size, colorspace="sRGB"):
    img = bpy.data.images.load(os.path.join(texdir, name))
    img.scale(size, size)
    img.colorspace_settings.name = colorspace
    node = nodes.new("ShaderNodeTexImage")
    node.image = img
    return node
color = tex("texture_low.png", 1024)
links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
normal = tex("normal_low.png", 1024, "Non-Color")
nmap = nodes.new("ShaderNodeNormalMap")
links.new(normal.outputs["Color"], nmap.inputs["Color"]); links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
emit = tex("emition.png", 1024)
links.new(emit.outputs["Color"], bsdf.inputs["Emission Color"])
bsdf.inputs["Emission Strength"].default_value = 1.5
bsdf.inputs["Roughness"].default_value = 0.8
mesh.materials.clear(); mesh.materials.append(mat)
for other in list(bpy.data.objects):
    bpy.data.objects.remove(other, do_unlink=True)
demon = bpy.data.objects.new("Demon", mesh)
bpy.context.scene.collection.objects.link(demon)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK", [round(x / (mx.z - mn.z), 2) for x in (mx - mn)])
