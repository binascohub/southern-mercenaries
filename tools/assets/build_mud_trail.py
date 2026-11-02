"""Mancha de barro da trilha da Floresta (assets/models/maps/Trail_Mud.glb): o quadrado de 2,8 m com a textura de lama rachada do projeto
(Ground_FarmMud, da biblioteca de texturas assets/textures/maps; Lattice, CC0), com a borda irregular e transparente (como Trail_Dirt e Trail_Moss, de
tools/assets/build_mossy_trail.py), que se sobrepõe às vizinhas para formar o leito da trilha. A base fica em y = 0, centrada em x/z.
uso: blender -b -P tools/assets/build_mud_trail.py -- <Ground_FarmMud_Ground_FarmMud.jpg> <saída.glb>"""
import bpy, sys
import numpy as np
src_path, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
src = bpy.data.images.load(src_path)
w, h = src.size
px = np.array(src.pixels[:], dtype=np.float32).reshape(h, w, 4)
yy, xx = np.mgrid[0:h, 0:w]
r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2))
rng = np.random.default_rng(11)
coarse = rng.random((9, 9)).astype(np.float32)
big = np.kron(coarse, np.ones((h // 8 + 1, w // 8 + 1), dtype=np.float32))[:h, :w]
edge = 0.78 + 0.22 * big
px[:, :, 3] = np.clip((edge - r) / 0.22, 0.0, 1.0)
img = bpy.data.images.new("Trail_Mud_rgba", w, h, alpha=True)
img.pixels = px.ravel().tolist()
img.pack()
mat = bpy.data.materials.new("Trail_Mud")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.55   # lama úmida: um pouco de brilho
t = nodes.new("ShaderNodeTexImage"); t.image = img
links.new(t.outputs["Color"], bsdf.inputs["Base Color"]); links.new(t.outputs["Alpha"], bsdf.inputs["Alpha"])
if hasattr(mat, "surface_render_method"):
    mat.surface_render_method = "BLENDED"
elif hasattr(mat, "blend_method"):
    mat.blend_method = "BLEND"
mat.use_backface_culling = False
mesh = bpy.data.meshes.new("Trail_Mud")
s = 1.4
mesh.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
uv = mesh.uv_layers.new(name="UV")
for loop, co in zip(mesh.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
    uv.data[loop.index].uv = co
mesh.materials.append(mat)
obj = bpy.data.objects.new("Trail_Mud", mesh)
bpy.context.scene.collection.objects.link(obj)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_image_format="WEBP", export_image_quality=82)
print("OK patch Trail_Mud", out)
