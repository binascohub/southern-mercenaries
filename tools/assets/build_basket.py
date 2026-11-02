"""Cesto de vime com alça (Willow Basket with Handle, ulf, CC-BY-SA 3.0): assets/models/props/Pr_Basket.glb.
Pega só o cesto novo ("clean"; o "old" é a versão escura), refaz o material com a cor e o relevo do pacote, em pé
(base em y = 0), centrado em x/z, 1,2x o tamanho do arquivo (~0,67 m de altura).
uso: blender -b -P tools/assets/build_basket.py -- <willow_basket_handle.blend> <saida.glb> [escala]"""
import bpy, sys
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
scale = float(args[2]) if len(args) > 2 else 1.2
bpy.ops.wm.open_mainfile(filepath=src)
basket = bpy.data.objects["willow_basket_handle_clean"]
for o in list(bpy.data.objects):
    if o != basket:
        bpy.data.objects.remove(o, do_unlink=True)
mat = bpy.data.materials["willow_basket_handle"]
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
out_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Roughness"].default_value = 0.9
links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
color = nodes.new("ShaderNodeTexImage")
color.image = bpy.data.images["willow_basket_dif"]
color.image.scale(1024, 1024) if color.image.size[0] > 1024 else None
links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
normal_tex = nodes.new("ShaderNodeTexImage")
normal_tex.image = bpy.data.images["willow_basket_handle_nor"]
normal_tex.image.colorspace_settings.name = "Non-Color"
normal_tex.image.scale(1024, 1024) if normal_tex.image.size[0] > 1024 else None
normal_map = nodes.new("ShaderNodeNormalMap")
links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])
basket.data.materials.clear()
basket.data.materials.append(mat)
basket.data.transform(basket.matrix_world)
basket.matrix_world = Matrix.Identity(4)
pts = [v.co for v in basket.data.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
basket.data.transform(Matrix.Scale(scale, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
basket.name = basket.data.name = "Pr_Basket"
bpy.ops.object.select_all(action="DESELECT")
basket.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=85)
print("OK", out, "caixa %.2f x %.2f x %.2f m" % tuple((mx[i] - mn[i]) * scale for i in range(3)))
