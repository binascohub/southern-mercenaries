"""Moeda do ouro no chão (Old coin, yd / Gtoknu, CC0, opengameart.org/content/old-coin): a malha coin01 com a textura de
cor (1024x512) e a normal embutidas, deitada (face para cima), base em y = 0, 0,36 m de diâmetro.
uso: build_coin.py <coin03.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
obj = bpy.data.objects["coin01"]
deps = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(obj.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
me.transform(obj.matrix_world)
colour, normal = bpy.data.images["coin01_2.png"], bpy.data.images["coin01N.jpg"]
for other in list(bpy.data.objects):
    bpy.data.objects.remove(other, do_unlink=True)
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
me.transform(Matrix.Scale(0.36 / max(mx.x - mn.x, mx.y - mn.y), 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = bpy.data.materials.new("Coin")
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
bsdf.inputs["Metallic"].default_value = 0.6
bsdf.inputs["Roughness"].default_value = 0.45
for img in (colour, normal):
    img.scale(512, 256)
me.materials.clear()
me.materials.append(mat)
ob = bpy.data.objects.new("Coin_Gold", me)
bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK coin", [round(x, 3) for x in (mx - mn)])
