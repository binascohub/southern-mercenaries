"""Ponte de tábuas da Fazenda: assets/models/maps/Pr_Bridge.glb, feita para o jogo (sem pacote externo).
5 m ao longo de X (a travessia), 2 m de largura em Z, tábuas atravessadas com vão entre elas, três postes por lado e
dois corrimãos; a textura é a da cerca de madeira do kit (T_WoodTrim_BaseColor), para ficar no mesmo tom de madeira do mapa.
uso: blender -b -P tools/assets/build_bridge.py -- <T_WoodTrim_BaseColor.webp> <saida.glb>"""
import bpy, sys

tex_path, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
LENGTH, WIDTH = 5.0, 2.0
boxes = []


def box(cx, cy, cz, sx, sy, sz):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, cz))
    o = bpy.context.view_layer.objects.active
    o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    boxes.append(o)


# Blender: x = travessia, y = largura, z = altura (no jogo: z vira -y, y vira z)
n = 20
step = LENGTH / n
for i in range(n):  # tábuas do convés (topo em z = 0,25; descem 0,1 abaixo)
    box(-LENGTH / 2 + step * (i + 0.5), 0, 0.2, step - 0.03, WIDTH, 0.1)
for sy in (-1, 1):
    for px in (-LENGTH / 2 + 0.1, 0.0, LENGTH / 2 - 0.1):
        box(px, sy * (WIDTH / 2 - 0.08), 0.65, 0.14, 0.14, 0.9)  # postes
    box(0, sy * (WIDTH / 2 - 0.08), 1.0, LENGTH, 0.08, 0.1)    # corrimão de cima
    box(0, sy * (WIDTH / 2 - 0.08), 0.62, LENGTH, 0.06, 0.08)  # corrimão do meio
for sx in (-1, 1):  # vigas por baixo, de ponta a ponta
    pass
box(0, -WIDTH / 2 + 0.25, 0.08, LENGTH + 0.2, 0.22, 0.16)
box(0, WIDTH / 2 - 0.25, 0.08, LENGTH + 0.2, 0.22, 0.16)
bpy.ops.object.select_all(action="DESELECT")
for o in boxes:
    o.select_set(True)
bpy.context.view_layer.objects.active = boxes[0]
bpy.ops.object.join()
bridge = bpy.context.view_layer.objects.active
bridge.name = bridge.data.name = "Pr_Bridge"
mat = bpy.data.materials.new("BridgeWood")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.9
tex = nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(tex_path)
links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bridge.data.materials.append(mat)
bpy.ops.object.select_all(action="DESELECT")
bridge.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=85)
print("OK", out)
