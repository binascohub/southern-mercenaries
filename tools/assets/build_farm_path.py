"""Remendos de terra de borda irregular e macia para os caminhos da Fazenda (assets/models/maps/Ground_FarmPath{A,B,C}.glb,
Ground_FarmMudPatch.glb): em vez de ladrilhos quadrados, manchas redondas de 2 x 2 m cujo canal alfa é um círculo
deformado por ruído, com a borda desfeita em terra solta; sobrepostas, formam um caminho sinuoso. A textura é a terra batida
(dirt_1, CC0, Lattice) com sulcos e pedrinhas leves.
uso: blender -b -P tools/assets/build_farm_path.py -- <pasta assets/textures/maps> <pasta de saída>"""
import bpy, sys, os
import numpy as np

tex_dir, out = sys.argv[sys.argv.index("--") + 1:][:2]
N = 256


def load(name):
    img = bpy.data.images.load(os.path.join(tex_dir, name + ".webp"))
    img.scale(N, N)
    return np.array(img.pixels[:], dtype=np.float32).reshape(N, N, 4)[:, :, :3]


def smooth(t, lo, hi):
    t = np.clip((t - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def blob_alpha(seed):
    r = np.random.RandomState(seed)
    y, x = np.mgrid[0:N, 0:N].astype(np.float32)
    x, y = (x / (N - 1)) * 2 - 1, (y / (N - 1)) * 2 - 1
    ang = np.arctan2(y, x)
    rad = np.hypot(x, y)
    wob = np.zeros_like(rad)
    for k in range(2, 7):
        wob += r.uniform(0.02, 0.07) / (k * 0.5) * np.sin(k * ang + r.uniform(0, 6.28))
    edge = 0.72 + wob
    grain = r.rand(N // 8, N // 8).astype(np.float32)
    grain = np.kron(grain, np.ones((8, 8), dtype=np.float32))
    a = 1.0 - smooth(rad, edge - 0.28, edge)
    a = np.clip(a * (0.9 + 0.2 * grain) - 0.12 * smooth(grain, 0.7, 1.0) * (1 - smooth(rad, 0, edge - 0.3)) * 0, 0, 1)
    return a


dirt = load("dirt_1")
KINDS = {
    "Ground_FarmPathA": (np.array([1.18, 0.97, 0.74]), 5),
    "Ground_FarmPathB": (np.array([1.12, 0.93, 0.72]), 17),
    "Ground_FarmPathC": (np.array([1.22, 1.0, 0.78]), 29),
    "Ground_FarmMudPatch": (np.array([0.72, 0.6, 0.46]), 41),
}
for name, (tint, seed) in KINDS.items():
    shift = np.roll(dirt, seed * 7, axis=(0, 1))
    rgb = np.clip(shift * tint, 0, 1)
    a = blob_alpha(seed)
    rgb = rgb * (0.78 + 0.22 * smooth(a, 0.0, 0.6))[:, :, None]  # borda mais escura e úmida
    bpy.ops.wm.read_factory_settings(use_empty=True)
    img = bpy.data.images.new(name, N, N, alpha=True)
    px = np.ones((N, N, 4), dtype=np.float32)
    px[:, :, :3] = rgb
    px[:, :, 3] = a
    img.pixels = px.ravel().tolist()
    img.alpha_mode = "STRAIGHT"
    img.pack()
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [], [(0, 1, 2, 3)])
    uv = mesh.uv_layers.new(name="UV")
    for loop, co in zip(mesh.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[loop.index].uv = co
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = "BLEND"
    nt = mat.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    bsdf = nt.nodes["Principled BSDF"]
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 1.0
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", export_image_format="AUTO")
    print("OK", name)
