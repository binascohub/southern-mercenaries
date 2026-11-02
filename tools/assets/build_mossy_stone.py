"""Pedra musgosa (Mossy Stone Rock, mastahcez, CC0, opengameart.org/content/mossy-stone-rock): a pedra de 152 triângulos, com o albedo e a normal
(1024 -> 512 px, JPG) num .glb (Rock_MossyStone.glb), 1 m de largura, base em y = 0, centrada. Para o círculo de pedras da fogueira do acampamento
da Floresta (tools/assets/add_forest_campfire.py).
uso: blender -b -P tools/assets/build_mossy_stone.py -- <stone.OBJ> <stone_albedo.png> <stone_normal.png> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
obj_path, albedo, normal, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=obj_path)
o = next(x for x in bpy.data.objects if x.type == "MESH")
me = o.data
me.transform(o.matrix_world)
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 1.0 / max(mx.x - mn.x, mx.y - mn.y)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z - 0.03))))  # afunda 3 cm no chão
mat = bpy.data.materials.new("MossyStone")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial"); b = nodes.new("ShaderNodeBsdfPrincipled")
links.new(b.outputs["BSDF"], o_node.inputs["Surface"]); b.inputs["Roughness"].default_value = 0.85
c = nodes.new("ShaderNodeTexImage"); c.image = bpy.data.images.load(albedo); c.image.scale(512, 512)
links.new(c.outputs["Color"], b.inputs["Base Color"])
n = nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(normal); n.image.scale(512, 512); n.image.colorspace_settings.name = "Non-Color"
nm = nodes.new("ShaderNodeNormalMap")
links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], b.inputs["Normal"])
me.materials.clear(); me.materials.append(mat)
for poly in me.polygons:
    poly.use_smooth = True
ob = bpy.data.objects.new("Rock_MossyStone", me)
bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK stone", [round(x * k, 2) for x in (mx - mn)], "triângulos:", len(me.polygons))
