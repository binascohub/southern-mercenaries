"""Peças da trilha do Cemitério a partir do "Mossy Rock Environment Pack" (rubberduck, OpenGameArt, CC0), em assets/models/maps/:
- Mossy_Slab_1..5: as cinco pedras (mossy_rock_01..05, malha LOD 1) achatadas a no máximo ~16 cm, para virarem lajes da trilha;
- Mossy_Formation_1..4: as quatro formações rochosas (LOD 1), para as margens da trilha;
- Trail_Dirt e Trail_Moss: manchas quadradas de 2,8 m com a textura de solo mossy_03 (terra seca com pedrinhas) e mossy_06
  (chão musgoso), com a borda irregular e transparente, que se sobrepõem para formar o leito da trilha.
Texturas reduzidas a 512 px (cor e normal) em WebP. A base de cada peça fica em y = 0, centrada em x/z.
uso: blender -b <pasta>/mossy_rock_env_pack.blend --python build_mossy_trail.py -- <pasta com mossy_03 e mossy_06> <saída: assets/models/maps>"""
import bpy, sys, os, math
import numpy as np
from mathutils import Vector, Matrix

tex_dir, out = sys.argv[sys.argv.index("--") + 1:][:2]
rock_dir = os.path.dirname(bpy.data.filepath)
MAX_SLAB = 0.16


def load(path, size=512):
    img = bpy.data.images.load(path, check_existing=True)
    if img.size[0] > size:
        img.scale(size, max(1, int(img.size[1] * size / img.size[0])))
    return img


def pbr(name, color_path, normal_path=None, alpha_image=None, roughness=0.9):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = roughness
    color = nodes.new("ShaderNodeTexImage")
    color.image = alpha_image if alpha_image else load(color_path)
    links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
    if alpha_image:
        links.new(color.outputs["Alpha"], bsdf.inputs["Alpha"])
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = "BLENDED"
        elif hasattr(mat, "blend_method"):
            mat.blend_method = "BLEND"
    if normal_path:
        norm = nodes.new("ShaderNodeTexImage")
        norm.image = load(normal_path)
        norm.image.colorspace_settings.name = "Non-Color"
        nmap = nodes.new("ShaderNodeNormalMap")
        links.new(norm.outputs["Color"], nmap.inputs["Color"])
        links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    mat.use_backface_culling = False
    return mat


def export(obj, name):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", use_selection=True,
                              export_image_format="WEBP", export_image_quality=82)


def rock_piece(src_name, name, flatten):
    src = bpy.data.objects[src_name + "_LOD_1"]
    mesh = src.data.copy()
    mesh.transform(src.matrix_world)
    pts = [v.co for v in mesh.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    # Em pé com a base em z = 0 e o centro em x/y; as lajes ficam achatadas.
    zscale = min(1.0, MAX_SLAB / (hi.z - lo.z)) if flatten else 1.0
    mesh.transform(Matrix.Diagonal((1, 1, zscale, 1)) @ Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))))
    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.materials.clear()
    mesh.materials.append(pbr(name, os.path.join(rock_dir, src_name + ".png"), os.path.join(rock_dir, src_name + "_norm.png")))
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    export(obj, name)
    return (hi.x - lo.x, hi.y - lo.y, (hi.z - lo.z) * zscale)


for i in range(1, 6):
    print("OK slab", i, tuple(round(v, 2) for v in rock_piece("mossy_rock_0%d" % i, "Mossy_Slab_%d" % i, True)))
for i in range(1, 5):
    print("OK formation", i, tuple(round(v, 2) for v in rock_piece("mossy_rock_formation_0%d" % i, "Mossy_Formation_%d" % i, False)))


# Manchas de solo: o quadrado da textura com um recorte irregular e suave (alfa) nas bordas.
def soil_patch(name, tex_file, seed):
    src = load(os.path.join(tex_dir, tex_file), 512)
    w, h = src.size
    px = np.array(src.pixels[:], dtype=np.float32).reshape(h, w, 4)
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2))
    rng = np.random.default_rng(seed)
    coarse = rng.random((9, 9)).astype(np.float32)
    big = np.kron(coarse, np.ones((h // 8 + 1, w // 8 + 1), dtype=np.float32))[:h, :w]
    edge = 0.78 + 0.22 * big                       # raio do recorte varia ao redor
    px[:, :, 3] = np.clip((edge - r) / 0.22, 0.0, 1.0)
    img = bpy.data.images.new(name + "_rgba", w, h, alpha=True)
    img.pixels = px.ravel().tolist()
    img.pack()
    mat = pbr(name, "", alpha_image=img, roughness=1.0)
    mesh = bpy.data.meshes.new(name)
    s = 1.4
    mesh.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    uv = mesh.uv_layers.new(name="UV")
    for loop, co in zip(mesh.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[loop.index].uv = co
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    export(obj, name)
    print("OK patch", name)


soil_patch("Trail_Dirt", "mossy_03.png", 3)
soil_patch("Trail_Moss", "mossy_06.jpg", 6)
