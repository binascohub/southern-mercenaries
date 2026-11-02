"""Fantasma feliz (Hapy ghoust, pracalic / GiggaWatt, CC0, opengameart.org/content/hapy-ghoust): o espírito com a animação de parado
("idle", em laço) e a textura do pacote (512 px), 0,5 m de altura, base em y = 0 (flutua um pouco acima). Item de missão do Padre
da Capital: a Alma do Rei (Quest_Ghost.glb), com o ícone de inventário `assets/ui/icons/royal_soul.png`.
uso: build_ghost.py <pasta com duch.blend e teksturaDuchaD4.png> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "duch.blend"))
for o in list(bpy.data.objects):
    if o.type in ("CAMERA", "LIGHT"):
        bpy.data.objects.remove(o, do_unlink=True)
arm = bpy.data.objects["Armature"]
mesh = bpy.data.objects["Sphere"]
act = bpy.data.actions["ArmatureAction"]
act.name = "idle"
ad = arm.animation_data_create()
ad.action = None
track = ad.nla_tracks.new()
track.name = "idle"
track.strips.new("idle", int(act.frame_range[0]), act)
tex = bpy.data.images.load(os.path.join(src, "teksturaDuchaD4.png"))
tex.scale(512, 512)
mat = bpy.data.materials.new("Ghost")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
bsdf.inputs["Roughness"].default_value = 0.5
bsdf.inputs["Emission Strength"].default_value = 0.4
t = nodes.new("ShaderNodeTexImage"); t.image = tex
links.new(t.outputs["Color"], bsdf.inputs["Base Color"]); links.new(t.outputs["Color"], bsdf.inputs["Emission Color"])
mesh.data.materials.clear()
mesh.data.materials.append(mat)
bpy.context.view_layer.update()
pts = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 0.5 / (mx.z - mn.z)
arm.scale = arm.scale * k
arm.location = Vector((arm.location.x - (mn.x + mx.x) / 2 * k, arm.location.y - (mn.y + mx.y) / 2 * k, arm.location.z - mn.z * k))
bpy.context.view_layer.update()
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG", export_animations=True, export_animation_mode="NLA_TRACKS")
print("OK ghost", [round(x * k, 2) for x in (mx - mn)])
