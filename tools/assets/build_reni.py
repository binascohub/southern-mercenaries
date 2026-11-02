"""Reni (reni.rar do autor: "Lal Suite Wali Women", Mixamo Fuse 1.3.0; autoria e licença a confirmar): mulher de malha única em T-pose
(10 mil vértices, cinco materiais com difusa e normal: corpo, top, calça, sapatos e cabelo). Aqui o OBJ é importado, os materiais refeitos
(difusa + normal, 1024 px no máximo) e a malha salva com o nome "Reni"; depois tools/assets/rig_to_ual.py prende a malha ao esqueleto dos heróis (1,7 m)
e ela ganha as animações deles:
  blender -b -P tools/assets/build_reni.py -- "<pasta>/Lal Suite Wali Women.obj" <saida.blend>
  blender -b -P tools/assets/rig_to_ual.py -- assets/models/characters/hero_female.glb <saida.blend> Reni assets/models/characters/reni.glb 1.7"""
import bpy, sys, os

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
folder = os.path.dirname(src)
prefix = os.path.splitext(os.path.basename(src))[0] + "_"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=src)
body = [o for o in bpy.data.objects if o.type == "MESH"][0]
body.name = "Reni"


def load(name, colorspace):
    path = os.path.join(folder, prefix + name + ".png")
    if not os.path.exists(path):
        return None
    img = bpy.data.images.load(path)
    if img.size[0] > 1024:
        img.scale(1024, 1024)
    img.colorspace_settings.name = colorspace
    img.pack()
    return img


for mat in body.data.materials:
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    o_node = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.7
    bsdf.inputs["Specular IOR Level"].default_value = 0.2
    nt.links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
    diffuse = load(mat.name + "_diffuse", "sRGB")
    if diffuse:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = diffuse
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    normal = load(mat.name + "_normal", "Non-Color")
    if normal:
        ntex = nt.nodes.new("ShaderNodeTexImage")
        ntex.image = normal
        nmap = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(ntex.outputs["Color"], nmap.inputs["Color"])
        nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
bpy.ops.wm.save_as_mainfile(filepath=out)
print("OK", out, [round(v, 2) for v in body.dimensions], len(body.data.vertices), [m.name for m in body.data.materials])
