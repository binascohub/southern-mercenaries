"""Rocha musgosa (Mossy Rock, hooded_kian, CC0, opengameart.org/content/mossy-rock): a rocha de fotogrametria (5,5 mil triângulos, sem fundo) com a cor e a normal
(2048 -> 512 px, JPG) num .glb (Rock_Mossy.glb), 3 m de largura, base em y = 0, centrada. Para a Floresta e o Cemitério (tools/assets/add_mossy_rocks.py).
uso: build_mossy_rock.py <rock.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
o = bpy.data.objects["Rock"]
deps = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
me.transform(o.matrix_world)
color, normal = bpy.data.images["Rock_Color"], bpy.data.images["Rock_Normal"]
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 3.0 / (mx.x - mn.x)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z - 0.05))))  # afunda 5 cm no chão (a rocha não tem fundo)
mat = bpy.data.materials.new("MossyRock")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial"); b = nodes.new("ShaderNodeBsdfPrincipled")
links.new(b.outputs["BSDF"], o_node.inputs["Surface"]); b.inputs["Roughness"].default_value = 0.9
c = nodes.new("ShaderNodeTexImage"); c.image = color; c.image.scale(512, 512)
links.new(c.outputs["Color"], b.inputs["Base Color"])
n = nodes.new("ShaderNodeTexImage"); n.image = normal; n.image.scale(512, 512); n.image.colorspace_settings.name = "Non-Color"
nm = nodes.new("ShaderNodeNormalMap")
links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], b.inputs["Normal"])
me.materials.clear(); me.materials.append(mat)
for poly in me.polygons:
    poly.use_smooth = True
ob = bpy.data.objects.new("Rock_Mossy", me)
bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK rock", [round(x * k, 2) for x in (mx - mn)])
