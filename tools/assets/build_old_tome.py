"""Livro antigo (Old Tome 2, bobjh / Varkalandar, CC-BY 4.0, opengameart.org/content/old-tome-2): o tomo de alquimia com a textura de cor
e a normal do pacote (512 px), deitado, base em y = 0, 0,3 m de largura (Book_Tome.glb). Serve de ícone do livro do Invocador no inventário
(`assets/ui/icons/book_D.png` ... `book_S.png`, renderizados por tools/assets/book_icons.gd na cor de cada material).
As imagens do livro vêm da Wikimedia Commons (CC-BY 4.0 / CC0 / domínio público; ver SOURCES.txt do pacote).
uso: build_old_tome.py <pasta old_book2 extraída> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "old_book2.blend"))
obj = bpy.data.objects["old_book2"]
deps = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(obj.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
me.transform(obj.matrix_world)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 0.3 / (mx.x - mn.x)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = bpy.data.materials.new("OldTome")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
bsdf.inputs["Roughness"].default_value = 0.75
c = nodes.new("ShaderNodeTexImage"); c.image = bpy.data.images.load(os.path.join(src, "olc_book2.png")); c.image.scale(512, 512)
links.new(c.outputs["Color"], bsdf.inputs["Base Color"])
n = nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(os.path.join(src, "olc_book2Normal.png")); n.image.scale(512, 512)
n.image.colorspace_settings.name = "Non-Color"
nm = nodes.new("ShaderNodeNormalMap")
links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
me.materials.clear()
me.materials.append(mat)
ob = bpy.data.objects.new("Book_Tome", me)
bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK tome", [round(x * k, 2) for x in (mx - mn)])
