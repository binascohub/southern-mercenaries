"""Pisos de 2 x 2 m dos mapas ao ar livre (assets/models/maps/Ground_*.glb): quadrado com textura de ruído
sem emenda, gerada aqui (grama, terra batida, terra acinzentada do cemitério). Roda com o Python do Blender:
blender -b -P tools/assets/build_ground.py -- <saída> [piso ...]
(sem nomes, gera todos; com nomes, só esses, ex.: Ground_Grave)"""
import bpy, sys, os, random, math
_args = sys.argv[sys.argv.index("--") + 1:]
out = _args[0]
ONLY = _args[1:]
SIZE = 256
KINDS = {"Ground_Grass": ((0.16, 0.3, 0.1), (0.07, 0.14, 0.05), 11), "Ground_Dirt": ((0.36, 0.28, 0.18), (0.18, 0.13, 0.08), 23),
         "Ground_Grave": ((0.18, 0.165, 0.15), (0.075, 0.07, 0.065), 37)}


def noise_grid(seed, cell):
    r = random.Random(seed)
    n = SIZE // cell
    g = [[r.random() for _ in range(n)] for _ in range(n)]

    def sample(x, y):
        fx, fy = x / cell, y / cell
        x0, y0 = int(fx) % n, int(fy) % n
        x1, y1 = (x0 + 1) % n, (y0 + 1) % n
        tx, ty = fx - int(fx), fy - int(fy)
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        return (g[y0][x0] * (1 - tx) + g[y0][x1] * tx) * (1 - ty) + (g[y1][x0] * (1 - tx) + g[y1][x1] * tx) * ty
    return sample


for name, (light, dark, seed) in KINDS.items():
    if ONLY and name not in ONLY:
        continue
    big, mid, fine = noise_grid(seed, 64), noise_grid(seed + 1, 16), noise_grid(seed + 2, 4)
    img = bpy.data.images.new(name, SIZE, SIZE)
    px = []
    for y in range(SIZE):
        for x in range(SIZE):
            t = 0.5 * big(x, y) + 0.3 * mid(x, y) + 0.2 * fine(x, y)
            px += [light[i] * t * 1.6 + dark[i] * (1 - t) * 0.9 for i in range(3)] + [1.0]
    img.pixels = px
    img.filepath_raw = os.path.join(out, name + "_tex.png")
    img.file_format = "PNG"
    img.save()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [], [(0, 1, 2, 3)])
    uv = mesh.uv_layers.new(name="UV")
    for loop, co in zip(mesh.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[loop.index].uv = co
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(out, name + "_tex.png"))
    mat.node_tree.links.new(tex.outputs["Color"], mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", export_image_format="JPEG")
    os.remove(os.path.join(out, name + "_tex.png"))
    print("OK", name)
