"""Demônio do mini-chefe do Esgoto (a malha demon-twelve.glb do autor + as texturas PBR de demon_tex.rar, também do autor; autor/licença a confirmar): a malha (28 mil vértices,
sem esqueleto nem animação, 2,2 m, `static` em MonsterModel) recebe aqui o material de verdade em vez da textura única do arquivo: cor, rugosidade, metal e normal (OpenGL) a 1024 px.
A pasta do pacote tem Demon_default_tex (Demon1_*, pele cinza de pedra) e Demon_damaged_tex (Demon2_*, o mesmo desenho, ferido e sujo de sangue); o terceiro argumento escolhe: default | damaged.
O mapa UV é o mesmo da malha (conferido). Gera assets/models/monsters/demon_boss.glb.
uso: blender -b -P tools/assets/build_demon_boss.py -- <demon-twelve.glb> <pasta Demon_tex extraída> <saida.glb> [default|damaged]"""
import bpy, sys, os
a = sys.argv[sys.argv.index("--") + 1:]
src, pack, out = a[:3]
variant = a[3] if len(a) > 3 else "damaged"
folder, prefix = ("Demon_default_tex", "Demon1") if variant == "default" else ("Demon_damaged_tex", "Demon2")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
obj = next(o for o in bpy.data.objects if o.type == 'MESH')


def load(name, color=True):
    img = bpy.data.images.load(os.path.join(pack, folder, "%s_%s.png" % (prefix, name)))
    img.scale(1024, 1024)
    img.colorspace_settings.name = "sRGB" if color else "Non-Color"
    img.pack()
    return img


mat = bpy.data.materials.new("DemonBoss")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
o_node = nt.nodes.new("ShaderNodeOutputMaterial")
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
nt.links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
for slot, name, color in (("Base Color", "BaseColor", True), ("Roughness", "Roughness", False), ("Metallic", "Metallic", False)):
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = load(name, color)
    nt.links.new(t.outputs["Color"], bsdf.inputs[slot])
tn = nt.nodes.new("ShaderNodeTexImage")
tn.image = load("Normal_OpenGL", False)
nmap = nt.nodes.new("ShaderNodeNormalMap")
nt.links.new(tn.outputs["Color"], nmap.inputs["Color"])
nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
obj.data.materials.clear()
obj.data.materials.append(mat)
for p in obj.data.polygons:
    p.material_index = 0
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85)
print("OK", out, variant)
