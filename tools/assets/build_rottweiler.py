"""Benny, o Rottweiler (Benny, the Rottweiler, umask007 / Acorn, CC-BY-SA 3.0, opengameart.org/content/benny-the-rottweiler): o cão rigado com a textura do
pacote (benny3.png, 512 px) e as animações do arquivo (idle, run, attack, attack2, flinch, die; "walk" é a corrida também, para o companheiro) num .glb
(Rottweiler.glb), 0,9 m de comprimento, pés em y = 0. É a companheira de Fogo do Invocador (no lugar da raposa).
uso: build_rottweiler.py <pasta com benny.blend e benny3.png> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "benny.blend"))
for o in list(bpy.data.objects):
    if o.type in ("CAMERA", "LIGHT"):
        bpy.data.objects.remove(o, do_unlink=True)
arm = bpy.data.objects["dogArmature"]
mesh = bpy.data.objects["Cube"]
ad = arm.animation_data_create()
ad.action = None
for track_name, action in (("idle", "idle"), ("walk", "run"), ("run", "run"), ("attack", "attack"), ("attack2", "attack2"), ("flinch", "flinch"), ("die", "die")):
    act = bpy.data.actions[action]
    track = ad.nla_tracks.new()
    track.name = track_name
    track.strips.new(track_name, int(act.frame_range[0]), act)
tex = bpy.data.images.load(os.path.join(src, "benny3.png"))
tex.scale(512, 512)
for mat in mesh.data.materials:
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial")
    b = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(b.outputs["BSDF"], o_node.inputs["Surface"])
    b.inputs["Roughness"].default_value = 0.8
    t = nodes.new("ShaderNodeTexImage")
    t.image = tex
    links.new(t.outputs["Color"], b.inputs["Base Color"])
# O cão vem deitado ao longo de X: gira o esqueleto para a cabeça (focinho) ficar para +Z do glTF (-Y do Blender).
import math
snout = [i for i, m in enumerate(mesh.data.materials) if m.name == "schnauze"]
bpy.context.view_layer.update()
sv = [mesh.matrix_world @ mesh.data.vertices[v].co for p in mesh.data.polygons if p.material_index in snout for v in p.vertices]
allv = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
center_x = (max(v.x for v in allv) + min(v.x for v in allv)) / 2
head_sign = 1.0 if (sum(v.x for v in sv) / max(len(sv), 1)) > center_x else -1.0
arm.rotation_euler.z += -head_sign * math.pi / 2
print("FOCINHO em", "+X" if head_sign > 0 else "-X")
bpy.context.view_layer.update()
pts = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
long_axis = max(range(3), key=lambda i: mx[i] - mn[i])
print("DIMS", [round(x, 2) for x in (mx - mn)], "eixo longo", long_axis)
k = 0.9 / (mx[long_axis] - mn[long_axis])
arm.scale = arm.scale * k
arm.location = Vector((arm.location.x - (mn.x + mx.x) / 2 * k, arm.location.y - (mn.y + mx.y) / 2 * k, arm.location.z - mn.z * k))
bpy.context.view_layer.update()
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG", export_animations=True, export_animation_mode="NLA_TRACKS")
print("OK rottweiler", [round(x * k, 2) for x in (mx - mn)])
