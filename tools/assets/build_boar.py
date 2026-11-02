"""Javali (Boar, Teh_Bucket / Saltflower, CC0, opengameart.org/content/boar): o javali rigado com a textura (1024 -> 512 px) e as animações do arquivo (walk, attack e a
pose parada "default", renomeada "idle") num .glb (Boar.glb), 1,1 m de comprimento, pés em y = 0, cabeça para +Z. É o javali do Invocador (companheiro de Terra).
uso: build_boar.py <boar.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
for o in list(bpy.data.objects):
    if o.type in ("CAMERA", "LIGHT"):
        bpy.data.objects.remove(o, do_unlink=True)
arm = bpy.data.objects["boar_armature"]
mesh = bpy.data.objects["boar_mesh.000"]
bpy.data.actions["default"].name = "idle"
ad = arm.animation_data_create()
ad.action = None
for name in ("idle", "walk", "attack"):
    act = bpy.data.actions[name]
    track = ad.nla_tracks.new()
    track.name = name
    track.strips.new(name, int(act.frame_range[0]), act)
# O arquivo guarda só metade do corpo (modificador Mirror, que o exportador não aplica em malha com esqueleto): aplica aqui, antes do resto da pilha.
bpy.context.view_layer.objects.active = mesh
mesh.select_set(True)
for mod in [m for m in mesh.modifiers if m.type == "MIRROR"]:
    bpy.ops.object.modifier_apply(modifier=mod.name)
img = bpy.data.images["boar"]
img.scale(512, 512)
mat = mesh.data.materials[0]
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial"); b = nodes.new("ShaderNodeBsdfPrincipled")
links.new(b.outputs["BSDF"], o_node.inputs["Surface"]); b.inputs["Roughness"].default_value = 0.85
t = nodes.new("ShaderNodeTexImage"); t.image = img
links.new(t.outputs["Color"], b.inputs["Base Color"])
bpy.context.view_layer.update()
pts = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 1.1 / (mx.y - mn.y)
arm.scale = arm.scale * k
arm.location = Vector((arm.location.x - (mn.x + mx.x) / 2 * k, arm.location.y - (mn.y + mx.y) / 2 * k, arm.location.z - mn.z * k))
bpy.context.view_layer.update()
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG", export_animations=True, export_animation_mode="NLA_TRACKS")
print("OK boar", [round(x * k, 2) for x in (mx - mn)])
