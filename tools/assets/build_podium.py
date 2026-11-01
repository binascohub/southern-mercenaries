"""Altar/púlpito (Podium, Dm3d / Skorpio, CC-BY-SA 3.0, opengameart.org/content/podium): o púlpito de madeira com a textura de cor
(podiumCv2.jpg, 512 px), em pé, base em y = 0, centrado na planta, 1,3 m de altura, frente para +Z. É o altar da igreja da Capital.
uso: build_podium.py <pasta do pacote descompactado> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(src, "Podium.obj"))
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data
me.transform(obj.matrix_world)
obj.matrix_world = Matrix.Identity(4)
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 1.3 / (mx.z - mn.z)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = bpy.data.materials.new("Podium")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
bsdf.inputs["Roughness"].default_value = 0.75
t = nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(src, "podiumCv2.jpg"))
t.image.scale(512, 512)
links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
me.materials.clear()
me.materials.append(mat)
obj.name = "Podium"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK podium", [round(x * k, 2) for x in (mx - mn)])
