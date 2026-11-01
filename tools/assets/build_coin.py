"""Moeda pirata (3d Pirate Coin, Acasas, CC-BY 3.0, opengameart.org/content/3d-pirate-coin): a malha do OBJ com a cor
pintada à mão e a normal embutidas, deitada (face para cima), base em y = 0, 0,36 m de diâmetro.
uso: build_coin.py <pasta com Obj/ e Textures/> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(src, "Obj", "Pirate Coin.obj"))
objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
if len(objs) > 1:
    bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active
me = obj.data
me.transform(obj.matrix_world)
obj.matrix_world = Matrix.Identity(4)
pts = [v.co.copy() for v in me.vertices]
size = Vector([max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)])
thin = min(range(3), key=lambda i: size[i])  # o eixo fino da moeda vira o vertical (Z do Blender)
if thin == 0:
    me.transform(Matrix.Rotation(1.5707963, 4, "Y"))
elif thin == 1:
    me.transform(Matrix.Rotation(1.5707963, 4, "X"))
pts = [v.co.copy() for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
diameter = max(mx.x - mn.x, mx.y - mn.y)
me.transform(Matrix.Scale(0.36 / diameter, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = bpy.data.materials.new("Coin")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
c = nodes.new("ShaderNodeTexImage")
c.image = bpy.data.images.load(os.path.join(src, "Textures", "Pirate Coin_default_color.png"))
links.new(c.outputs["Color"], bsdf.inputs["Base Color"])
n = nodes.new("ShaderNodeTexImage")
n.image = bpy.data.images.load(os.path.join(src, "Textures", "Pirate Coin_normals-.png"))
n.image.colorspace_settings.name = "Non-Color"
nm = nodes.new("ShaderNodeNormalMap")
links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Metallic"].default_value = 0.6
bsdf.inputs["Roughness"].default_value = 0.45
for img in (c.image, n.image):
    img.scale(512, 512)
me.materials.clear()
me.materials.append(mat)
obj.name = "Coin_Gold"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK coin", [round(x, 3) for x in size], "thin axis", thin)
