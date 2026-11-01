"""Mago texturizado (Rigged Textured Mage, thecubber, CC BY-SA 3.0, opengameart.org/content/rigged-textured-mage)
como NPC parado, o Macumbeiro de Tortuga: malha na pose do arquivo (braços abertos), pés em y = 0,
1,85 m de altura, textura de cor em 1024 px (JPG) e normal embutida.
uso: build_mage_npc.py <mage_final.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
deps = bpy.context.evaluated_depsgraph_get()
o = bpy.data.objects["mage"]
mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
mesh.transform(o.matrix_world)
pts = [v.co for v in mesh.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
mesh.transform(Matrix.Scale(1.85 / (mx.z - mn.z), 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
for name in ("color.tga", "normal.tga"):
    bpy.data.images[name].scale(1024, 1024)
mat = bpy.data.materials.new("Robe")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
bsdf = nodes["Principled BSDF"]
tex = nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images["color.tga"]
links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
nm = nodes.new("ShaderNodeTexImage"); nm.image = bpy.data.images["normal.tga"]; nm.image.colorspace_settings.name = "Non-Color"
nmap = nodes.new("ShaderNodeNormalMap")
links.new(nm.outputs["Color"], nmap.inputs["Color"]); links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Roughness"].default_value = 0.8
mesh.materials.clear(); mesh.materials.append(mat)
for other in list(bpy.data.objects):
    bpy.data.objects.remove(other, do_unlink=True)
npc = bpy.data.objects.new("Mage", mesh)
bpy.context.scene.collection.objects.link(npc)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK", [round(x * 1.85 / (mx.z - mn.z), 2) for x in (mx - mn)])
