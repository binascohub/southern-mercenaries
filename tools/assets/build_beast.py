"""Besta Quitinosa (Beast 02, Atmostatic, CC BY 3.0 / CC BY-SA 3.0 / GPL, opengameart.org/content/beast-02) para a Floresta:
malha única sem esqueleto nem animação (o jogo a move por código em MonsterModel, modo "static"). Pés em y = 0, centrada em x/z,
frente em +Z, 1 m de comprimento (o tamanho vem dos dados do monstro); cor e normal em 1024 px.
uso: build_beast.py <pasta beast02 extraída> <saída.glb> [giro em graus em volta da vertical]"""
import bpy, sys, os, math
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
turn = float(args[2]) if len(args) > 2 else 0.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(src, "chitinous_beast.obj"))
obj = next(o for o in bpy.data.objects if o.type == "MESH")
mesh = obj.data
mesh.transform(Matrix.Rotation(math.radians(turn), 4, "Z"))
pts = [v.co for v in mesh.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
length = max(mx.x - mn.x, mx.y - mn.y)
mesh.transform(Matrix.Scale(1.0 / length, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = bpy.data.materials.new("Beast")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.7


def tex(name, colorspace="sRGB"):
    img = bpy.data.images.load(os.path.join(src, name))
    img.scale(1024, 1024)
    img.colorspace_settings.name = colorspace
    node = nodes.new("ShaderNodeTexImage")
    node.image = img
    return node


color = tex("chiting_beast_diffuse copy.png")
links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
normal = tex("chiting_beast_diffuse_NRM.png", "Non-Color")
nmap = nodes.new("ShaderNodeNormalMap")
links.new(normal.outputs["Color"], nmap.inputs["Color"])
links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
mesh.materials.clear()
mesh.materials.append(mat)
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="JPEG")
size = [round((mx - mn)[i] / length, 2) for i in range(3)]
print("OK", out, "x,y,z (m, 1 = comprimento):", size)
