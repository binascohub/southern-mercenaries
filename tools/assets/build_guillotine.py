"""Guilhotina (Guillotine, RayB2, CC0, opengameart.org/content/guillotine-0): o cadafalso de madeira com a lâmina e a textura do pacote (512 px)
num .glb (Guillotine.glb), 3 m de altura, base em y = 0, centrado na planta. Cenário da praça da Capital.
uso: build_guillotine.py <guillotine.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
o = bpy.data.objects["guillotine.001"]
deps = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
me.transform(o.matrix_world)
tex = next(i for i in bpy.data.images if i.packed_file)
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 3.0 / (mx.z - mn.z)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = bpy.data.materials.new("Guillotine")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial"); b = nodes.new("ShaderNodeBsdfPrincipled")
links.new(b.outputs["BSDF"], o_node.inputs["Surface"]); b.inputs["Roughness"].default_value = 0.75
t = nodes.new("ShaderNodeTexImage"); t.image = tex
links.new(t.outputs["Color"], b.inputs["Base Color"])
me.materials.clear(); me.materials.append(mat)
ob = bpy.data.objects.new("Guillotine", me)
bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK guillotine", [round(x * k, 2) for x in (mx - mn)])
