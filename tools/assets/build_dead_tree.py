"""Árvore morta (Dead Tree, piacenti, CC BY 3.0, opengameart.org/content/dead-tree-0): decoração da Floresta,
assets/models/maps/Dead_Tree.glb. O .blend traz a árvore de 15 mil triângulos e uma de ~450 (Group1.001) com
textura de cor e normal em 1024 px; fica a de 450. Em pé, base em y = 0, centrada em x/z, 4,5 m de altura (o jogo
escala cada uma ao espalhar).
uso: blender -b -P tools/assets/build_dead_tree.py -- <tree game_2.blend> <saída.glb> [render.png]"""
import bpy, sys, os, math
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
preview = args[2] if len(args) > 2 else None
HEIGHT = 4.5
bpy.ops.wm.open_mainfile(filepath=src)
tree = bpy.data.objects["Group1.001"]
color, normal = bpy.data.images["low diff"], bpy.data.images["low normal"]
mat = bpy.data.materials.new("DeadTree")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
bsdf = nodes["Principled BSDF"]
c = nodes.new("ShaderNodeTexImage"); c.image = color
n = nodes.new("ShaderNodeTexImage"); n.image = normal; normal.colorspace_settings.name = "Non-Color"
nm = nodes.new("ShaderNodeNormalMap")
links.new(c.outputs["Color"], bsdf.inputs["Base Color"])
links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Roughness"].default_value = 0.95
for o in list(bpy.data.objects):
    if o is not tree:
        bpy.data.objects.remove(o, do_unlink=True)
for mod in list(tree.modifiers):
    tree.modifiers.remove(mod)
tree.data.materials.clear(); tree.data.materials.append(mat)
world = tree.matrix_basis.copy()   # o objeto vem girado 90° em X (tronco = eixo Y local) e fora da cena, onde matrix_world não é atualizada
pts = [world @ Vector(cc) for cc in tree.bound_box]
mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
s = HEIGHT / (mx.z - mn.z)
tree.parent = None
if tree.name not in bpy.context.scene.collection.objects:
    bpy.context.scene.collection.objects.link(tree)   # no .blend ela fica numa coleção fora da cena
tree.data.transform(world); tree.matrix_world = Matrix.Identity(4)
tree.data.transform(Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
bpy.ops.object.select_all(action="DESELECT"); tree.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="JPEG", export_apply=False)
print("OK escala %.3f largura %.2f x %.2f m" % (s, (mx.x - mn.x) * s, (mx.y - mn.y) * s))
if preview:
    sc = bpy.context.scene
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam)
    cam.location = (0, -11, 2.3); cam.rotation_euler = (math.radians(90), 0, 0); sc.camera = cam
    sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"
    sc.render.resolution_x = sc.render.resolution_y = 600; sc.render.filepath = preview
    bpy.ops.render.render(write_still=True)
