"""Sapo (Frog Guy, opengameart.org/content/frog-guy, CC0): malha única de pé, sem animação (o jogo a move por código
em MonsterModel, família "static"). Pose de repouso do esqueleto aplicada; pés em y = 0, 1 m de altura (o tamanho vem dos dados),
frente em +Z, textura da foto do sapo em 1024 px.
uso: blender -b <frog.blend> --python build_frog.py -- <frog.png> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
texture, out = sys.argv[sys.argv.index("--") + 1:]
deps = bpy.context.evaluated_depsgraph_get()
o = bpy.data.objects["frog"]
mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
mesh.transform(o.matrix_world)
pts = [v.co for v in mesh.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
h = mx.z - mn.z
mesh.transform(Matrix.Scale(1.0 / h, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
# a frente do Blender é -Y; o glTF (+Z) pede a rotação de 180° em torno de Z antes da conversão de eixos
mesh.transform(Matrix.Rotation(3.14159265, 4, "Z"))
mat = bpy.data.materials.new("frog")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
out_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
img = bpy.data.images.load(texture)
img.scale(1024, 1024)
tex = nodes.new("ShaderNodeTexImage")
tex.image = img
links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.6
mesh.materials.clear(); mesh.materials.append(mat)
for other in list(bpy.data.objects):
    bpy.data.objects.remove(other, do_unlink=True)
frog = bpy.data.objects.new("Frog", mesh)
bpy.context.scene.collection.objects.link(frog)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP")
print("OK", [round(x / h, 2) for x in (mx - mn)])
