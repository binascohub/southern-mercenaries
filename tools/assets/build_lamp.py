"""Lampião de parede (Lamp, Mev Lyshkin, CC-BY 3.0): assets/models/maps/Pr_WallLamp.glb.
O .blend traz uma malha só, sem textura (suporte de ferro com volutas e a lanterna pendurada). Aqui: a lanterna (faces
abaixo de z = -0,4) vira vidro emissivo quente e o resto, ferro escuro; a placa que vai na parede fica em z = 0 (o braço
sai para +Z do jogo) e o topo da peça em y = 0 (o lampião pende; pendure-a a ~2,3 m com "y"). Escala 0,11 (~0,5 m de altura, braço de ~0,85 m).
uso: blender -b -P tools/assets/build_lamp.py -- <lampa.blend> <saida.glb> [escala]"""
import bpy, sys, math
from mathutils import Matrix

args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
scale = float(args[2]) if len(args) > 2 else 0.11
bpy.ops.wm.open_mainfile(filepath=src)
lamp = bpy.data.objects["Cube"]
for o in list(bpy.data.objects):
    if o != lamp:
        bpy.data.objects.remove(o, do_unlink=True)
mesh = lamp.data
mesh.transform(lamp.matrix_world)
lamp.matrix_world = Matrix.Identity(4)
pts = [v.co for v in mesh.vertices]
max_x = max(p.x for p in pts)
max_z = max(p.z for p in pts)
mesh.transform(Matrix.Translation((-max_x, 0, -max_z)))
mesh.transform(Matrix.Scale(scale, 4))
mesh.transform(Matrix.Rotation(math.radians(90), 4, "Z"))  # o braço (que ia para -x) passa a sair para -y do Blender = +Z do jogo
mesh.materials.clear()
iron = bpy.data.materials.new("LampIron")
iron.use_nodes = True
iron.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.09, 0.08, 1)
iron.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.6
iron.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.55
glass = bpy.data.materials.new("LampGlass")
glass.use_nodes = True
b = glass.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (1.0, 0.7, 0.3, 1)
b.inputs["Emission Color"].default_value = (1.0, 0.6, 0.2, 1)
b.inputs["Emission Strength"].default_value = 3.0
mesh.materials.append(iron)
mesh.materials.append(glass)
cut = (-0.4 - max_z) * scale  # z original -0,4: logo abaixo da cúpula da lanterna
for poly in mesh.polygons:
    zc = sum(mesh.vertices[i].co.z for i in poly.vertices) / len(poly.vertices)
    poly.material_index = 1 if zc < cut else 0
lamp.name = mesh.name = "Pr_WallLamp"
bpy.ops.object.select_all(action="DESELECT")
lamp.select_set(True)
bpy.context.view_layer.objects.active = lamp
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True)
ys = [v.co.y for v in mesh.vertices]
zs = [v.co.z for v in mesh.vertices]
xs = [v.co.x for v in mesh.vertices]
print("OK", out, "x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" % (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
