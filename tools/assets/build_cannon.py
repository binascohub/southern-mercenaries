"""Canhão de navio (Ship Cannon, jameswhite, CC0): assets/models/props/Ship_Cannon.glb. Malha única com a textura de 256x128;
fica com as rodas em y = 0, centrado em x/z, 1,5 m de comprimento, boca para +Z.
uso: blender -b <pasta do pacote>/Mesh/cannon_mesh.blend -P tools/assets/build_cannon.py -- <pasta do pacote>/Texture/cannon_diffuse.png assets/models/props/Ship_Cannon.glb"""
import bpy, sys
from mathutils import Vector, Matrix
tex, out = sys.argv[sys.argv.index("--") + 1:]
o = bpy.data.objects["cannon_body"]
mat = o.data.materials[0]
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
out_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
img = nodes.new("ShaderNodeTexImage")
img.image = bpy.data.images.load(tex, check_existing=False)
links.new(img.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.7
pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
s = 1.5 / (mx.y - mn.y)
o.data.transform(Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))) @ o.matrix_world)
o.matrix_world = Matrix.Identity(4)
bpy.ops.object.select_all(action="DESELECT")
o.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=90)
print("OK", out)
