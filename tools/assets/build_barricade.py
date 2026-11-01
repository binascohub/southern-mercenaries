"""Barricada de toras com pontas (Barricade, Sullivan, CC-BY 3.0): assets/models/maps/Pr_Barricade.glb.
Junta as toras numa malha só (aplicando as transformações), refaz o material com a cor e o relevo embutidos no .blend,
deixa em pé (base em y = 0), centrada em x/z e na escala do jogo (~1,9 m de largura).
uso: blender -b -P tools/assets/build_barricade.py -- <barricade.blend> <saida.glb> [escala]"""
import bpy, sys
from mathutils import Vector, Matrix
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from farm_palette import unify_wood

args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
scale = float(args[2]) if len(args) > 2 else 0.28
bpy.ops.wm.open_mainfile(filepath=src)
logs = [o for o in bpy.data.objects if o.type == "MESH"]
for o in list(bpy.data.objects):
    if o not in logs:
        bpy.data.objects.remove(o, do_unlink=True)
for o in logs:
    o.data.transform(o.matrix_world)
    o.matrix_world = Matrix.Identity(4)
mat = bpy.data.materials["Material.001"]
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
out_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Roughness"].default_value = 0.9
links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
color = nodes.new("ShaderNodeTexImage")
color.image = bpy.data.images["col.001"]
unify_wood(color.image)  # tom único de madeira da Fazenda (farm_palette.py)
links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
normal_tex = nodes.new("ShaderNodeTexImage")
normal_tex.image = bpy.data.images["normals"]
normal_tex.image.colorspace_settings.name = "Non-Color"
normal_map = nodes.new("ShaderNodeNormalMap")
links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])
for o in logs:
    o.data.materials.clear()
    o.data.materials.append(mat)
bpy.ops.object.select_all(action="DESELECT")
for o in logs:
    o.select_set(True)
bpy.context.view_layer.objects.active = logs[0]
bpy.ops.object.join()
whole = bpy.context.view_layer.objects.active
whole.name = whole.data.name = "Pr_Barricade"
pts = [v.co for v in whole.data.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
whole.data.transform(Matrix.Scale(scale, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
bpy.ops.object.select_all(action="DESELECT")
whole.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=85)
print("OK", out, "caixa %.1f x %.1f x %.1f m" % tuple((mx[i] - mn[i]) * scale for i in range(3)))
