"""Leito de ouro do dragão (GoldPile / Dragon's Bed, Dm3d, CC-BY-SA 3.0, opengameart.org/content/goldpile): a pilha de moedas
com gemas, que fica no tesouro do mapa do chefe final. A cor e o canal alfa (DragonsBedAlpha.jpg) viram uma textura RGBA
de 1024 px; a malha sai deitada, base em y = 0, centrada, com 5 m de largura.
uso: build_gold_bed.py <pasta do pacote extraído> <saída.glb>"""
import bpy, sys, os
import numpy as np
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(src, "Onecompletemesh.obj"))
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data
me.transform(obj.matrix_world)
obj.matrix_world = Matrix.Identity(4)
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
me.transform(Matrix.Scale(5.0 / max(mx.x - mn.x, mx.y - mn.y), 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
colour = bpy.data.images.load(os.path.join(src, "DragonsBed.jpg"))
alpha = bpy.data.images.load(os.path.join(src, "DragonsBedAlpha.jpg"))
for img in (colour, alpha):
    img.scale(1024, 1024)
c = np.array(colour.pixels[:], dtype=np.float32).reshape(-1, 4)
a = np.array(alpha.pixels[:], dtype=np.float32).reshape(-1, 4)
c[:, 3] = (a[:, 0] > 0.5).astype(np.float32)
rgba = bpy.data.images.new("DragonsBedRGBA", 1024, 1024, alpha=True)
rgba.pixels[:] = c.reshape(-1)
rgba.pack()
mat = bpy.data.materials.new("GoldBed")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
t = nodes.new("ShaderNodeTexImage"); t.image = rgba
links.new(t.outputs["Color"], bsdf.inputs["Base Color"]); links.new(t.outputs["Alpha"], bsdf.inputs["Alpha"])
bsdf.inputs["Metallic"].default_value = 0.5
bsdf.inputs["Roughness"].default_value = 0.4
mat.blend_method = "CLIP" if hasattr(mat, "blend_method") else None
me.materials.clear()
me.materials.append(mat)
obj.name = "Gold_Bed"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP")
print("OK gold bed", [round(x, 2) for x in (mx - mn)])
