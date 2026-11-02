"""Bolsa de moedas quebrável (Bag of Coins / purse01, yd, CC0, opengameart.org/content/bag-of-coins): a malha simples
com a textura de cor e a normal embutidas, em pé, base em y = 0, 0,45 m de altura.
uso: build_coin_bag.py <purse01.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
for o in list(bpy.data.objects):
    if o.name != "pursesimple":
        bpy.data.objects.remove(o, do_unlink=True)
obj = bpy.data.objects["pursesimple"]
me = obj.data
me.transform(obj.matrix_world)
obj.matrix_world = Matrix.Identity(4)
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
me.transform(Matrix.Scale(0.45 / (mx.z - mn.z), 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = me.materials[0]
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
c = nodes.new("ShaderNodeTexImage"); c.image = bpy.data.images["purse01D.png"]
links.new(c.outputs["Color"], bsdf.inputs["Base Color"])
n = nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images["purse01N.png"]; n.image.colorspace_settings.name = "Non-Color"
nm = nodes.new("ShaderNodeNormalMap")
links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Roughness"].default_value = 0.7
for img in (c.image, n.image):
    img.scale(512, 512)
obj.name = "Coin_Bag"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK coin bag")
