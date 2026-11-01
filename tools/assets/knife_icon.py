"""Ícone de inventário da adaga rank D do Ninja (128 px) a partir do Iron Knife (Clint Bellanger, CC0,
opengameart.org/content/iron-knife), com a textura do pacote. uso: knife_icon.py <iron_knife.blend> <pasta de texturas> <saída.png>"""
import bpy, sys, math
from mathutils import Vector
src, texdir, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
keep = bpy.data.objects["IronKnife"]
for o in list(bpy.data.objects):
    if o != keep:
        bpy.data.objects.remove(o, do_unlink=True)
mat = keep.data.materials[0]
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
t = nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(texdir + "/iron_knife_diffuse.png")
links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.45
bsdf.inputs["Metallic"].default_value = 0.4
from mathutils import Matrix
me = keep.data
me.transform(keep.matrix_world)
keep.matrix_world = Matrix.Identity(4)
pts = [v.co for v in me.vertices]
ext = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
axis = ext.index(max(ext))
# Eixo do comprimento para +Z (na vista de frente, para cima) e inclina 45° (ponta para cima e à direita).
me.transform({0: Matrix(((0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 0, 1))), 1: Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1))), 2: Matrix.Identity(4)}[axis])
keep.rotation_euler = (0, math.radians(45), 0)
bpy.context.view_layer.update()
wp = [keep.matrix_world @ v.co for v in keep.data.vertices]
mid = Vector([(max(p[i] for p in wp) + min(p[i] for p in wp)) / 2 for i in range(3)])
size = max(max(p[i] for p in wp) - min(p[i] for p in wp) for i in (0, 2))
sc = bpy.context.scene
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.type = "ORTHO"; cam.data.ortho_scale = size * 1.1
cam.location = (mid.x, mid.y - 20, mid.z); cam.rotation_euler = (math.pi / 2, 0, 0); sc.camera = cam
for ang, e in ((50, 3.5), (-30, 1.2)):
    l = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); l.data.energy = e
    l.rotation_euler = (math.radians(ang), math.radians(-15), math.radians(30)); sc.collection.objects.link(l)
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.5, 0.5, 0.52, 1); sc.world = w
sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = 128
sc.render.image_settings.color_mode = "RGBA"; sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("OK knife icon")
