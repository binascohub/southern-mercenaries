"""Demônio da Noite (Night Demon, nubux / morgan strauss, CC BY 3.0, opengameart.org/content/night-demon):
o pacote só traz a malha em T-pose (o rig Rigify não vem com animações), então os braços são baixados aqui
girando os vértices em torno do ombro, ponderados pelos grupos de vértices de ombro/braço/mão/dedos; no jogo o
corpo todo balança, avança e cai por código (`static` em MonsterModel). Pés em y = 0, 1 m de altura (o tamanho vem dos
dados do monstro), frente em +Z; cor, normal e brilho (specular -> rugosidade) em 1024 px.
uso: blender -b -P tools/assets/build_night_demon.py -- <pasta do pacote extraído> <saída.glb> [render.png]"""
import bpy, sys, os, math
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
preview = args[2] if len(args) > 2 else None
ARM_DOWN = math.radians(68)   # quanto o braço desce a partir do T
bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "demon-RIG.blend"))
o = bpy.data.objects["Low Poly"]
metarig = bpy.data.objects["Armature.001"]
mesh = o.data
groups = {g.index: g.name for g in o.vertex_groups}
ARM_KEYS = ("shoulder", "upper_arm", "forearm", "hand", "palm", "finger", "thumb")
for side, sign in (("L", None), ("R", None)):
    pivot = o.matrix_world.inverted() @ (metarig.matrix_world @ metarig.data.bones["upper_arm." + side].head_local)
    # o braço aponta para o lado do ombro: gira em torno de Y (frente/trás) para descer
    direction = 1 if pivot.x > 0 else -1
    rot = Matrix.Rotation(direction * ARM_DOWN, 4, "Y")
    for v in mesh.vertices:
        w = sum(g.weight for g in v.groups
                if groups[g.group].endswith("." + side) or ("." + side + ".") in groups[g.group]
                if any(k in groups[g.group] for k in ARM_KEYS))
        w = min(w, 1.0)
        if w > 0:
            v.co = pivot + (rot @ (v.co - pivot)) * w + (v.co - pivot) * (1 - w)
# malha final (sem modificadores), em metros reais -> 1 m de altura, pés em 0, centro em x/y
deps = bpy.context.evaluated_depsgraph_get()
body = bpy.data.meshes.new_from_object(o, preserve_all_data_layers=True, depsgraph=deps)  # pose já está nos vértices
for m in list(body.vertices):
    pass
body.transform(o.matrix_world)
pts = [v.co for v in body.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
body.transform(Matrix.Scale(1.0 / (mx.z - mn.z), 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = bpy.data.materials.new("NightDemon")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
bsdf = nodes["Principled BSDF"]
def tex(name, colorspace="sRGB"):
    img = bpy.data.images.load(os.path.join(src, name))
    img.scale(1024, 1024)
    img.colorspace_settings.name = colorspace
    node = nodes.new("ShaderNodeTexImage")
    node.image = img
    return node
links.new(tex("colorMap.png").outputs["Color"], bsdf.inputs["Base Color"])
nmap = nodes.new("ShaderNodeNormalMap")
links.new(tex("normalMap.png", "Non-Color").outputs["Color"], nmap.inputs["Color"])
links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Roughness"].default_value = 0.75
body.materials.clear(); body.materials.append(mat)
for other in list(bpy.data.objects):
    bpy.data.objects.remove(other, do_unlink=True)
demon = bpy.data.objects.new("NightDemon", body)
bpy.context.scene.collection.objects.link(demon)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK", [round(x / (mx.z - mn.z), 2) for x in (mx - mn)])
if preview:
    sc = bpy.context.scene
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam)
    cam.location = (0.0, -2.6, 0.55); cam.rotation_euler = (math.radians(90), 0, 0); sc.camera = cam
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sun.rotation_euler = (math.radians(50), 0, math.radians(20))
    sc.collection.objects.link(sun)
    sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"
    sc.render.resolution_x = sc.render.resolution_y = 600; sc.render.filepath = preview
    bpy.ops.render.render(write_still=True)
