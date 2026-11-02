"""Poções (pot.rar enviado pelo autor do projeto: vzor.blend com 4 frascos de poção "small health potion" de 0,45 m (azul, verde, roxo e vermelho, 94 a 118 polígonos cada) numa cena de
vitrine, mais textures.rar com as texturas JPG de 1024 px; autor/licença a confirmar). Aqui cada frasco vira um modelo com a textura a 512 px (WebP), em pé, centrado em x/z e com a base em
y = 0, e as variações de cor que o jogo precisa saem de uma rotação de matiz da textura: Potion_Red (vida), Potion_Blue (recurso), Potion_Aqua (elemental de Água), Potion_Orange (Fogo),
Potion_Yellow (Ar), Potion_Green (Terra) e Potion_Purple (sobra do pacote).
Gera assets/models/props/Potion_*.glb.
uso: blender -b -P tools/assets/build_potions.py -- <vzor.blend> <pasta com textures/> <pasta de saída>"""
import bpy, sys, os, math
import numpy as np
from mathutils import Vector, Matrix

blend, texroot, outdir = sys.argv[sys.argv.index("--") + 1:][:3]
# frasco do .blend -> textura base
SOURCE = {"small health poti": None, "small health poti.001": "1467", "small health poti.003": "1469", "small health poti.004": "1466"}
# modelo -> (frasco, textura, rotação de matiz em graus)
OUT = {"Potion_Red": ("small health poti", "1465", 0), "Potion_Blue": ("small health poti.004", "1466", 0), "Potion_Green": ("small health poti.001", "1467", 0),
       "Potion_Purple": ("small health poti.003", "1469", 0), "Potion_Aqua": ("small health poti.004", "1466", -35), "Potion_Orange": ("small health poti", "1465", 28),
       "Potion_Yellow": ("small health poti.001", "1467", -65)}


def hue_rotate(px, degrees):
    """Gira o matiz (rotação no plano de crominância do YIQ)."""
    if degrees == 0:
        return px
    a = math.radians(degrees)
    c, s = math.cos(a), math.sin(a)
    rgb = px[:, :3]
    y = rgb @ np.array([0.299, 0.587, 0.114])
    i = rgb @ np.array([0.596, -0.274, -0.322])
    q = rgb @ np.array([0.211, -0.523, 0.312])
    i2, q2 = i * c - q * s, i * s + q * c
    out = np.stack([y + 0.956 * i2 + 0.621 * q2, y - 0.272 * i2 - 0.647 * q2, y - 1.106 * i2 + 1.703 * q2], axis=1)
    px = px.copy()
    px[:, :3] = np.clip(out, 0, 1)
    return px


for name, (src_name, tex, shift) in OUT.items():
    bpy.ops.wm.open_mainfile(filepath=blend)
    keep = bpy.data.objects[src_name]
    for o in list(bpy.data.objects):
        if o is not keep:
            bpy.data.objects.remove(o, do_unlink=True)
    keep.parent = None
    keep.data.transform(keep.matrix_world)
    keep.matrix_world = Matrix.Identity(4)
    v = np.array([tuple(p.co) for p in keep.data.vertices])
    cx = (v[:, 0].min() + v[:, 0].max()) / 2
    cy = (v[:, 1].min() + v[:, 1].max()) / 2
    keep.data.transform(Matrix.Translation((-cx, -cy, -v[:, 2].min())))
    # material novo: só a textura (já girada), sem os nós do arquivo
    img = bpy.data.images.load(os.path.join(texroot, "textures", tex + ".jpg"))
    img.scale(512, 512)
    n = 512 * 512
    px = np.array(img.pixels[:]).reshape(n, 4)
    px = hue_rotate(px, shift)
    out_img = bpy.data.images.new(name + "_tex", 512, 512)
    out_img.pixels[:] = px.ravel().tolist()
    out_img.pack()
    mat = bpy.data.materials.new("m_" + name.lower())
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.35
    t = mat.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = out_img
    mat.node_tree.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    keep.data.materials.clear()
    keep.data.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT')
    keep.select_set(True)
    bpy.context.view_layer.objects.active = keep
    dst = os.path.join(outdir, name + ".glb")
    bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', use_selection=True, export_animations=False)
    print("OK", dst, [round(x, 2) for x in keep.dimensions])
