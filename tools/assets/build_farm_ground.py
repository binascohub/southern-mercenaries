"""Pisos da Fazenda (assets/models/maps/Ground_FarmGrass.glb, Ground_FarmDirt.glb, Ground_FarmMud.glb), quadrados de 2 x 2 m
feitos com a biblioteca de texturas contínuas (assets/textures/maps, Lattice, CC0):
 - FarmGrass: mistura de grass1, grass2 e clover_1 por máscaras periódicas (continua sem emenda) com manchas claras e escuras;
 - FarmDirt: dirt_1 esquentada para terra batida (caminhos, pátios, horta);
 - FarmMud: a mesma terra, mais escura e úmida (curral dos porcos).
uso: blender -b -P tools/assets/build_farm_ground.py -- <pasta assets/textures/maps> <pasta de saída>"""
import bpy, sys, os
import numpy as np

tex_dir, out = sys.argv[sys.argv.index("--") + 1:][:2]
N = 512


def load(name):
    img = bpy.data.images.load(os.path.join(tex_dir, name + ".webp"))
    img.scale(N, N)
    return np.array(img.pixels[:], dtype=np.float32).reshape(N, N, 4)[:, :, :3]


def periodic_noise(seed, octaves=4):
    """Ruído suave que repete a cada tile (somas de senos de frequência inteira): 0..1."""
    r = np.random.RandomState(seed)
    y, x = np.mgrid[0:N, 0:N].astype(np.float32) / N
    total = np.zeros((N, N), dtype=np.float32)
    amp = 1.0
    for o in range(octaves):
        for _ in range(3):
            fx, fy = r.randint(1, 3 + 2 * o), r.randint(1, 3 + 2 * o)
            total += amp * np.sin(2 * np.pi * (fx * x + fy * y) + r.uniform(0, 6.28))
        amp *= 0.55
    total = (total - total.min()) / (total.max() - total.min())
    return total


def smooth(t, lo, hi):
    t = np.clip((t - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


g1, g2, cl, dirt = load("grass1"), load("grass2"), load("clover_1"), load("dirt_1")
m1, m2, tone = periodic_noise(3), periodic_noise(8), periodic_noise(21, 3)
grass = g2 * (1 - smooth(m1, 0.4, 0.62))[:, :, None] + g1 * smooth(m1, 0.4, 0.62)[:, :, None]
grass = grass * (1 - 0.65 * smooth(m2, 0.55, 0.75))[:, :, None] + cl * (0.65 * smooth(m2, 0.55, 0.75))[:, :, None]
grass = grass * (0.82 + 0.3 * tone)[:, :, None]
grass = np.clip(grass * np.array([0.95, 1.05, 0.9]), 0, 1)
warm = np.clip(dirt * np.array([1.18, 0.97, 0.74]), 0, 1)
mud = np.clip(dirt * np.array([0.72, 0.6, 0.46]), 0, 1)
KINDS = {"Ground_FarmGrass": grass, "Ground_FarmDirt": warm, "Ground_FarmMud": mud}
for name, rgb in KINDS.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    img = bpy.data.images.new(name, N, N)
    px = np.ones((N, N, 4), dtype=np.float32)
    px[:, :, :3] = rgb
    img.pixels = px.ravel().tolist()
    img.pack()
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [], [(0, 1, 2, 3)])
    uv = mesh.uv_layers.new(name="UV")
    for loop, co in zip(mesh.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[loop.index].uv = co
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = img
    mat.node_tree.links.new(tex.outputs["Color"], mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", export_image_format="JPEG", export_image_quality=88)
    print("OK", name)
