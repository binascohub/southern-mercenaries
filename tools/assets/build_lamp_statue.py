"""Estátua do poste de luz: assets/models/maps/Statue_Lamp.glb ("Statue holding lightpost", Colorado Stark, OpenGameArt, CC0):
um homem de pedra segurando um poste com lampião, 6294 triângulos. A malha vem em OBJ com texturas TGA de 2048 px (cor,
normal e emissiva da lâmpada); aqui as texturas caem para 1024 px (WebP), a lâmpada fica acesa (emissão), e a peça sai em pé,
com os pés na origem (x/z), base em y = 0 e 3,4 m de altura.
uso: blender -b -P tools/assets/build_lamp_statue.py -- <pasta Statue do pacote extraído> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
HEIGHT = 3.4
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(src, "Statue_With_Lamp_LP.obj"))   # o OBJ tem o Y para cima (padrão)
obj = [o for o in bpy.data.objects if o.type == "MESH"][0]
mesh = obj.data


def tex(name, noncolor=False):
    img = bpy.data.images.load(os.path.join(src, name))
    img.scale(1024, 1024)
    if noncolor:
        img.colorspace_settings.name = "Non-Color"
    return img


mat = bpy.data.materials.new("Statue_Lamp")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.85
color = nodes.new("ShaderNodeTexImage")
color.image = tex("Statue_dDo03_d.tga")
links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
norm = nodes.new("ShaderNodeTexImage")
norm.image = tex("Statue_dDo03_n.tga", True)
nmap = nodes.new("ShaderNodeNormalMap")
links.new(norm.outputs["Color"], nmap.inputs["Color"])
links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
emit = nodes.new("ShaderNodeTexImage")
emit.image = tex("Emissive_Map.tga")
links.new(emit.outputs["Color"], bsdf.inputs["Emission Color"])
bsdf.inputs["Emission Strength"].default_value = 3.0
mat.use_backface_culling = False
mesh.materials.clear()
mesh.materials.append(mat)
for poly in mesh.polygons:
    poly.use_smooth = True

mesh.transform(obj.matrix_world)
obj.matrix_world = Matrix.Identity(4)
pts = [v.co for v in mesh.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
feet = [p for p in pts if p.z < lo.z + (hi.z - lo.z) * 0.04]           # a base: o centro dos pés é a origem
fx = sum(p.x for p in feet) / len(feet)
fy = sum(p.y for p in feet) / len(feet)
s = HEIGHT / (hi.z - lo.z)
mesh.transform(Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-fx, -fy, -lo.z))))
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=85)
print("OK", os.path.basename(out), "%.2f x %.2f x %.2f m" % ((hi.x - lo.x) * s, (hi.y - lo.y) * s, (hi.z - lo.z) * s))
