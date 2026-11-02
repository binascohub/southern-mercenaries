"""Carvalho velho (Old oak tree, Julius Krischan Makowka, GPL 2.0 / GPL 3.0 / CC BY-SA 3.0, opengameart.org/content/old-oak-tree):
árvore da Floresta, assets/models/maps/Oak_Tree.glb. Do pacote vem o oak.obj (555 triângulos, tronco + copa de folhas em cartões) e as
texturas do tronco (oakbark.jpg) e da folha (oakleaf_light.tga, com alfa: vira recorte). Em pé, base em y = 0, centrada em x/z, 7 m de altura
(o jogo escala cada uma ao espalhar).
uso: blender -b -P tools/assets/build_oak.py -- <pasta models do zip> <saída.glb> [render.png]"""
import bpy, sys, os, math
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
preview = args[2] if len(args) > 2 else None
HEIGHT = 7.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(src, "oak.obj"))
tree = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]


def material(name, image, leaf):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(src, image))
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.95
    if leaf:
        links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
        mat.blend_method = "CLIP" if hasattr(mat, "blend_method") else None
        mat.use_backface_culling = False
    return mat


names = [s.material.name if s.material else "" for s in tree.material_slots]
print("materiais:", names)
for slot in tree.material_slots:
    leaf = "blaetter" in slot.material.name or "leaf" in slot.material.name
    slot.material = material("OakLeaf" if leaf else "OakBark", "oakleaf_light.tga" if leaf else "oakbark.jpg", leaf)
bpy.context.view_layer.update()
pts = [tree.matrix_world @ Vector(c) for c in tree.bound_box]
mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
print("caixa original", mn, mx)
# o obj do Quake tem o tronco no eixo Z (depois da importação padrão do Blender): se for mais largo que alto, deita-se de volta
tree.data.transform(tree.matrix_world); tree.matrix_world = Matrix.Identity(4)
s = HEIGHT / (mx.z - mn.z)
tree.data.transform(Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
bpy.ops.object.select_all(action="DESELECT"); tree.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="AUTO", export_apply=False)
print("OK escala %.3f largura %.2f x %.2f m" % (s, (mx.x - mn.x) * s, (mx.y - mn.y) * s))
if preview:
    sc = bpy.context.scene
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam)
    cam.location = (0, -16, 3.5); cam.rotation_euler = (math.radians(90), 0, 0); sc.camera = cam
    sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"
    sc.render.resolution_x = sc.render.resolution_y = 600; sc.render.filepath = preview
    bpy.ops.render.render(write_still=True)
