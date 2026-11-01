"""Escudo redondo viking/eslavo (Shield, Mev Lyshkin, CC-BY 3.0, opengameart.org/content/shield-1): a malha "Sphere" (o
escudo inteiro; a "Sphere.001" é uma cópia inclinada) com a textura de madeira embutida, de pé, a frente (o umbigo de
ferro) para +Z, centro na origem, 0,7 m de diâmetro. Para pendurar nas paredes da Capital.
uso: build_viking_shield.py <tarcza.blend> <saída.glb>"""
import bpy, sys, math
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
obj = bpy.data.objects["Sphere"]
deps = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(obj.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
me.transform(obj.matrix_world)
tex = bpy.data.images["untitled.jpg"]
for other in list(bpy.data.objects):
    bpy.data.objects.remove(other, do_unlink=True)
me.transform(Matrix.Rotation(math.radians(90), 4, "X"))  # a frente (+Z do arquivo) vira -Y do Blender = +Z no glTF
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
me.transform(Matrix.Scale(0.7 / max(mx.x - mn.x, mx.z - mn.z), 4) @ Matrix.Translation(-(mn + mx) / 2))
mat = bpy.data.materials.new("Shield")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
t = nodes.new("ShaderNodeTexImage"); t.image = tex
links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.8
tex.scale(512, 512)
me.materials.clear()
me.materials.append(mat)
ob = bpy.data.objects.new("Shield_Viking", me)
bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK shield", [round(x, 2) for x in (mx - mn)])
