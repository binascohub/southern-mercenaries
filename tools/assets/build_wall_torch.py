"""Tocha de parede (Wall mounted torch, scribe, CC BY 3.0): assets/models/props/Wall_Torch.glb. Malha única (107 faces) com a textura
pdtexture.jpg e o mapa alfa do pacote. A placa fica no plano x/y = 0 (a parede) e a tocha sai para +Z (a frente do glTF); o
modelo já vem a 1,3 m do chão (a base) e tem ~0,9 m de altura, para ser posto direto contra a face da parede.
uso: blender -b <Wall mounted torch.blend> -P tools/assets/build_wall_torch.py -- assets/models/props/Wall_Torch.glb"""
import bpy, sys
from mathutils import Vector, Matrix
out = sys.argv[sys.argv.index("--") + 1]
HEIGHT, LIFT = 0.9, 1.3
o = bpy.data.objects["torch"]
mat = o.data.materials[0]
nodes, links = mat.node_tree.nodes, mat.node_tree.links
for n in [n for n in nodes if n.type == "BSDF_DIFFUSE" or (n.type == "OUTPUT_MATERIAL" and n.name != "Material Output")]:
    nodes.remove(n)  # o material antigo traz uma saída extra com um Diffuse, que o exportador pegava no lugar do Principled
nodes["Material Output"].target = "ALL"
bsdf = nodes["Principled BSDF"]
color = nodes.new("ShaderNodeTexImage"); color.image = bpy.data.images["pdtexture.jpg"]
links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
alpha = nodes.new("ShaderNodeTexImage"); alpha.image = bpy.data.images["alpha map4.png"]; alpha.image.colorspace_settings.name = "Non-Color"
links.new(alpha.outputs["Color"], bsdf.inputs["Alpha"])
bsdf.inputs["Roughness"].default_value = 0.85
bsdf.inputs["Emission Color"].default_value = (1.0, 0.55, 0.2, 1)
bsdf.inputs["Emission Strength"].default_value = 0.0
mat.blend_method = "CLIP" if hasattr(mat, "blend_method") else None
mat.use_backface_culling = False
pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
s = HEIGHT / (mx.z - mn.z)
# Blender: parede em y = 0, tocha para -y, altura em z  ->  glTF: parede em z = 0, tocha para +z, altura em y.
fix = Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -mx.y, -mn.z + LIFT / s)))
o.data.transform(fix @ o.matrix_world)
o.matrix_world = Matrix.Identity(4)
bpy.ops.object.select_all(action="DESELECT")
o.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=85)
print("OK", out)
