"""Monge (Monk, CDmir, CC0, opengameart.org/content/monk) como NPC parado de animação "idle": o Padre da Capital.
Liga as texturas de cor e normal aos materiais, escala para 1,8 m de altura (pés em y = 0) e guarda só a animação
"idle" (Idle.000).
uso: build_monk.py <MONK_1.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
for o in list(bpy.data.objects):
    if o.type == "LIGHT":
        bpy.data.objects.remove(o, do_unlink=True)
arm = bpy.data.objects["Armature"]
for act in list(bpy.data.actions):
    if act.name != "Idle.000":
        bpy.data.actions.remove(act)
act = bpy.data.actions["Idle.000"]
act.name = "idle"
arm.animation_data_create().action = act
TEX = {"Monk-Body": ("monk-tuc-body", "monk-tuc-body-norm512.png"),
       "Monk-Head": ("monk-tuc-head", "monk-tuc-head-norm512.png"),
       "Hair": ("hair-skin.png", None)}
for name, (color, normal) in TEX.items():
    mat = bpy.data.materials[name]
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
    c = nodes.new("ShaderNodeTexImage"); c.image = bpy.data.images[color]
    links.new(c.outputs["Color"], bsdf.inputs["Base Color"])
    if normal:
        n = nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images[normal]; n.image.colorspace_settings.name = "Non-Color"
        nm = nodes.new("ShaderNodeNormalMap")
        links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = 0.85
    bsdf.inputs["Specular IOR Level"].default_value = 0.1
# Altura e base: bounding box das malhas no mundo.
bpy.context.view_layer.update()
pts = []
for o in bpy.data.objects:
    if o.type == "MESH":
        pts += [o.matrix_world @ v.co for v in o.data.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 1.8 / (mx.z - mn.z)
arm.scale = arm.scale * k
arm.location = Vector((arm.location.x - (mn.x + mx.x) / 2 * k, arm.location.y - (mn.y + mx.y) / 2 * k, arm.location.z - mn.z * k))
bpy.context.view_layer.update()
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG", export_animations=True,
                          export_animation_mode="ACTIONS", export_force_sampling=True)
print("OK monk", [round(x * k, 2) for x in (mx - mn)])
