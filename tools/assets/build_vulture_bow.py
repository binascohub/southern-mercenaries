"""Arco abutre (Vulture Bow, Mophs / genderfreak, CC-BY 4.0, opengameart.org/content/vulture-bow): o arco do Arqueiro como peça 3D
(Bow_Vulture.glb: de pé, 1,2 m de altura, textura de cor em 512 px) para os ícones do inventário (`assets/ui/icons/bow_D.png` ... `bow_S.png`,
renderizados por tools/assets/bow_icons.gd na cor de cada material).
uso: build_vulture_bow.py <pasta Vulture_Bow> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(src, "Vulture_Bow.obj"))
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data
me.transform(obj.matrix_world)
obj.matrix_world = Matrix.Identity(4)
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
dims = [mx[i] - mn[i] for i in range(3)]
tall = max(range(3), key=lambda i: dims[i])  # o maior eixo é a altura do arco
if tall == 1:
    me.transform(Matrix.Rotation(1.5707963, 4, "X"))
elif tall == 0:
    me.transform(Matrix.Rotation(1.5707963, 4, "Y"))
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 1.2 / (mx.z - mn.z)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = bpy.data.materials.new("VultureBow")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
bsdf.inputs["Roughness"].default_value = 0.6
t = nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(src, "diffuse.png"))
t.image.scale(512, 512)
links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
me.materials.clear()
me.materials.append(mat)
obj.name = "Bow_Vulture"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK bow", [round(x * k, 2) for x in (mx - mn)], "eixo alto", tall)
