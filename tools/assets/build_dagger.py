"""Adaga do Ninja (Simple 3D Dagger, danilomattos, CC0): de pé (ponta para +Z no
Blender = +Y no Godot), 0,55 m, centrada; textura 512 px.
uso: build_dagger.py <dagger.blend> <textura> <saida.glb>"""
import bpy, sys, math
from mathutils import Vector, Matrix
src, tex, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
o = bpy.data.objects["dagger"]
deps = bpy.context.evaluated_depsgraph_get()
mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
mesh.transform(o.matrix_world)
pts = [v.co for v in mesh.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
# Ponta: o lado do eixo X mais fino (a lâmina) fica para cima.
mid = (lo + hi) / 2
mesh.transform(Matrix.Translation(-mid))
left = [v.co for v in mesh.vertices if v.co.x < 0]; right = [v.co for v in mesh.vertices if v.co.x > 0]
spread = lambda P: max(p.z for p in P) - min(p.z for p in P)
angle = math.radians(90) if spread(right) < spread(left) else math.radians(-90)
mesh.transform(Matrix.Rotation(angle, 4, "Y"))
mesh.transform(Matrix.Rotation(math.pi, 4, "X"))  # lâmina para cima
mesh.transform(Matrix.Scale(0.55 / (hi.x - lo.x), 4))
img = bpy.data.images.load(tex); img.scale(512, 512)
mat = bpy.data.materials.new("Dagger"); mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
bsdf = nodes.get("Principled BSDF")
t = nodes.new("ShaderNodeTexImage"); t.image = img
links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Metallic"].default_value = 0.6; bsdf.inputs["Roughness"].default_value = 0.35
mesh.materials.clear(); mesh.materials.append(mat)
for x in list(bpy.data.objects): bpy.data.objects.remove(x, do_unlink=True)
new = bpy.data.objects.new("Dagger", mesh); bpy.context.scene.collection.objects.link(new)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=88)
print("OK", out)
