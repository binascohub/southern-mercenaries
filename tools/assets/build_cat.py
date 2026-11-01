"""Gato (Simple Cat, drummyfish, CC0): modelo de poucos polígonos com uma caminhada feita de
duas formas de malha (shape keys, ação "KeyAction"). Troca a textura pela `cat_free.png` (a que o
autor fez do zero, para a licença ficar sem dúvida), tira câmera e luzes e exporta o corpo com
a caminhada nomeada "walk".
uso: blender -b cat_2-80.blend --python build_cat.py -- <cat_free.png> <saida.glb>"""
import bpy, sys

texture, out = sys.argv[sys.argv.index("--") + 1:][:2]

# O arquivo traz dois gatos: o "Cube" parado (sem a caminhada) e o "Cube.001" com as formas de malha.
# Fica só o animado.
for o in list(bpy.data.objects):
    if o.type in ("CAMERA", "LIGHT") or o.name == "Cube":
        bpy.data.objects.remove(o, do_unlink=True)

image = bpy.data.images.load(texture)
image.pack()
for mat in bpy.data.materials:
    if not mat.node_tree:
        continue
    for node in mat.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            node.image = image
    for node in mat.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            node.inputs["Roughness"].default_value = 0.95
            if "Specular IOR Level" in node.inputs:
                node.inputs["Specular IOR Level"].default_value = 0.0

for action in bpy.data.actions:
    if action.name == "KeyAction":
        action.name = "walk"

bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animations=True,
                          export_morph=True, export_apply=False, export_yup=True,
                          export_animation_mode="ACTIONS")
print("gato exportado:", out)
