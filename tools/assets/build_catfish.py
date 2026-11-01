"""Bagre (3d low poly catfish, gfroad / Snabisch, CC0, opengameart.org/content/3d-low-poly-catfish): o modelo de 284 polígonos (o pacote traz as
animações de nadar e pular só em .max, que o Blender não abre; no jogo o peixe nada por código), com a textura de cor (512 px), deitado,
0,6 m de comprimento, centrado, base em y = 0, cabeça para +Z. Peixes do riacho da Fazenda e do mar das Docas.
uso: build_catfish.py <pasta com catfishRawModel.obj e catfish.png> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(src, "catfishRawModel.obj"))
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data
me.transform(obj.matrix_world)
obj.matrix_world = Matrix.Identity(4)
pts = [v.co for v in me.vertices]
dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
long_axis = max(range(3), key=lambda i: dims[i])
print("DIMS", [round(d, 2) for d in dims], "eixo longo", long_axis)
# o comprimento do peixe vira o eixo Y do Blender (-Y do Blender = +Z do glTF = a cabeça, se a cabeça estiver no lado -Y)
if long_axis == 0:
    me.transform(Matrix.Rotation(1.5707963, 4, "Z"))
elif long_axis == 2:
    me.transform(Matrix.Rotation(1.5707963, 4, "X"))
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 0.6 / (mx.y - mn.y)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = bpy.data.materials.new("Catfish")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
bsdf.inputs["Roughness"].default_value = 0.4
t = nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(src, "catfish.png")); t.image.scale(512, 512)
links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
me.materials.clear()
me.materials.append(mat)
obj.name = "Fish_Catfish"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK catfish", [round(x * k, 2) for x in (mx - mn)])
