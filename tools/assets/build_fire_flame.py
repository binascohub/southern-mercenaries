"""Chama da fogueira (Fire, janexx, CC BY-SA 3.0, opengameart.org/content/fire): a imagem de preview da chama (200 x 200, com transparência) em três planos
cruzados (0,9 x 1,1 m, base em y = 0), com transparência e brilho próprio (não recebe sombra), num .glb (Fire_Flame.glb). A oscilação da chama é feita por código
(decor "flicker" em game/levels/prototype_arena.gd). Para a fogueira do acampamento da Floresta (tools/assets/add_forest_campfire.py).
uso: blender -b -P tools/assets/build_fire_flame.py -- <fire_prev.png> <saída.glb>"""
import bpy, sys, math
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
img = bpy.data.images.load(src)
mat = bpy.data.materials.new("Flame")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial"); b = nodes.new("ShaderNodeBsdfPrincipled")
links.new(b.outputs["BSDF"], o_node.inputs["Surface"])
t = nodes.new("ShaderNodeTexImage"); t.image = img
links.new(t.outputs["Color"], b.inputs["Base Color"]); links.new(t.outputs["Color"], b.inputs["Emission Color"])
links.new(t.outputs["Alpha"], b.inputs["Alpha"])
b.inputs["Emission Strength"].default_value = 2.5
b.inputs["Roughness"].default_value = 1.0
mat.use_backface_culling = False
if hasattr(mat, "blend_method"):
    mat.blend_method = "BLEND"
W, H = 0.9, 1.1
verts, faces = [], []
for k in range(3):
    a = math.radians(60 * k)
    dx, dy = math.cos(a) * W / 2, math.sin(a) * W / 2
    i = len(verts)
    verts += [(-dx, -dy, 0), (dx, dy, 0), (dx, dy, H), (-dx, -dy, H)]
    faces.append((i, i + 1, i + 2, i + 3))
me = bpy.data.meshes.new("Fire_Flame")
me.from_pydata(verts, [], faces)
uv = me.uv_layers.new(name="UVMap")
for poly in me.polygons:
    for j, li in enumerate(poly.loop_indices):
        uv.data[li].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][j]
me.materials.append(mat)
ob = bpy.data.objects.new("Fire_Flame", me)
bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="AUTO")
print("OK flame", out)
