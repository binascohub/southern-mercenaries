"""Colar (Necklace, Paul Wortmann, CC0, opengameart.org/content/necklace): o colar com o pingente e as texturas do pacote (cor, normal e brilho -> rugosidade, 512 px)
num .glb (Necklace.glb), de frente para +Z, 0,3 m de largura, centrado. Serve de ícone do amuleto no inventário (`assets/ui/icons/amulet_D.png` ... `amulet_S.png`,
renderizados por tools/assets/amulet_icons.gd na cor de cada material).
uso: build_necklace.py <pasta necklace_1 extraída> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(src, "obj_export", "necklace_1_001.obj"))
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data
me.transform(obj.matrix_world)
pts = [v.co for v in me.vertices]
dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
print("DIMS", [round(d, 3) for d in dims])
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 0.3 / max(mx.x - mn.x, mx.y - mn.y)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(-(mn + mx) / 2))
mat = bpy.data.materials.new("Necklace")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial"); b = nodes.new("ShaderNodeBsdfPrincipled")
links.new(b.outputs["BSDF"], o_node.inputs["Surface"])
b.inputs["Metallic"].default_value = 0.8
def tex(name, cs="sRGB"):
    t = nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(src, "textures", name)); t.image.scale(512, 512)
    t.image.colorspace_settings.name = cs
    return t
links.new(tex("necklace_1_001_d.png").outputs["Color"], b.inputs["Base Color"])
nm = nodes.new("ShaderNodeNormalMap"); links.new(tex("necklace_1_001_n.png", "Non-Color").outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], b.inputs["Normal"])
b.inputs["Roughness"].default_value = 0.35
me.materials.clear(); me.materials.append(mat)
obj.name = "Necklace"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK necklace", [round(x * k, 3) for x in (mx - mn)])
