"""Borboleta animada (Butterfly (animated), Čestmír Dammer / cdmir, CC0, opengameart.org/content/butterfly-animated; textura derivada de fotos de Rick Hoppmann):
124 polígonos, rig de 25 ossos e as animações Flying (batida de asas, 10 quadros) e Sitting1/2, num .glb (Butterfly_Anim.glb), 0,4 m de envergadura, pousada em y = 0.
A peça toca a primeira animação (Flying) em laço no cenário (game/levels/prototype_arena.gd). Para a Floresta (tools/assets/add_forest_butterflies.py).
uso: blender -b --disable-autoexec <butterfly.blend> -P tools/assets/build_butterfly_anim.py -- <saída.glb>"""
import bpy, sys
from mathutils import Vector
out = sys.argv[sys.argv.index("--") + 1]
for ob in list(bpy.data.objects):
    if ob.type in ("LIGHT", "CAMERA"):
        bpy.data.objects.remove(ob, do_unlink=True)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
mesh = next(o for o in bpy.data.objects if o.type == "MESH")
for img in bpy.data.images:
    if img.name != "butterfly-skin" and img.users == 0:
        bpy.data.images.remove(img)
span = max(mesh.dimensions.x, mesh.dimensions.y)
k = 0.4 / span
arm.scale = arm.scale * k
# O material do arquivo usa a textura no formato antigo: refaz com a imagem do corpo e das asas (transparência nas bordas das asas).
skin = bpy.data.images["butterfly-skin"]
mat = bpy.data.materials["Butterfly"]
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial"); b = nodes.new("ShaderNodeBsdfPrincipled")
links.new(b.outputs["BSDF"], o_node.inputs["Surface"]); b.inputs["Roughness"].default_value = 0.8
t = nodes.new("ShaderNodeTexImage"); t.image = skin
links.new(t.outputs["Color"], b.inputs["Base Color"]); links.new(t.outputs["Alpha"], b.inputs["Alpha"])
mat.use_backface_culling = False
if hasattr(mat, "blend_method"):
    mat.blend_method = "CLIP"
if arm.animation_data is None:
    arm.animation_data_create()
arm.animation_data.action = bpy.data.actions["Flying"]
kwargs = dict(filepath=out, export_format="GLB", export_image_format="AUTO", export_animations=True)
try:
    bpy.ops.export_scene.gltf(export_animation_mode="ACTIONS", **kwargs)   # todas as ações viram animações do .glb
except TypeError:
    for act in bpy.data.actions:
        tr = arm.animation_data.nla_tracks.new(); tr.name = act.name
        tr.strips.new(act.name, int(act.frame_range[0]), act)
    bpy.ops.export_scene.gltf(export_nla_strips=True, **kwargs)
print("OK butterfly", out, [a.name for a in bpy.data.actions])
