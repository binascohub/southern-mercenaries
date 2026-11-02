"""Coelho (Rabbit, Snabisch, CC0): modelo rigado e animado do Blender 2.76, com
as texturas embutidas mas os materiais sem ligação (o formato antigo não vira
nós). Refaz os materiais (pele + relevo no corpo; pelos com transparência),
tira câmera, luzes e o plano, e exporta o corpo, os pelos e o esqueleto num .glb
só com as animações usadas no jogo, com os nomes: jump (pulo), run (corrida),
idle (em guarda, repete) e sit (sentado).
uso: blender -b rabbit.blend --python build_rabbit.py -- <saida.glb>"""
import bpy, sys

out = sys.argv[sys.argv.index("--") + 1]

for o in list(bpy.data.objects):
    if o.type in ("CAMERA", "LIGHT") or o.name == "Plane":
        bpy.data.objects.remove(o, do_unlink=True)


def textured(material_name, image_name, normal_name=None, alpha=False):
    mat = bpy.data.materials.new(material_name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.95
    out_node = nodes.new("ShaderNodeOutputMaterial")
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images[image_name]
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if alpha:
        links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
        mat.blend_method = "BLEND"
    if normal_name:
        normal_tex = nodes.new("ShaderNodeTexImage")
        normal_tex.image = bpy.data.images[normal_name]
        normal_tex.image.colorspace_settings.name = "Non-Color"
        normal_map = nodes.new("ShaderNodeNormalMap")
        links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
        links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


body = bpy.data.objects["Rabbit"]
fur = bpy.data.objects["Fur"]
body.data.materials.clear()
body.data.materials.append(textured("Rabbit", "rabbot-skinn", "rabbit-NORM"))
fur.data.materials.clear()
fur.data.materials.append(textured("Fur", "Fur-skin", None, alpha=True))

# Só as animações do jogo, com nomes curtos.
keep = {"Jump": "jump", "Running": "run", "Guarding": "idle", "Sitting.001": "sit"}
for action in list(bpy.data.actions):
    if action.name in keep:
        action.name = keep[action.name]
        action.use_fake_user = True
    else:
        bpy.data.actions.remove(action)

armature = bpy.data.objects["Armature"]
if armature.animation_data is None:
    armature.animation_data_create()
armature.animation_data.action = bpy.data.actions["idle"]

bpy.ops.object.select_all(action="DESELECT")
for o in (armature, body, fur):
    o.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=out, export_format="GLB", use_selection=True,
    export_animations=True, export_animation_mode="ACTIONS", export_force_sampling=True,
    export_image_format="WEBP", export_apply=False, export_yup=True,
)
print("coelho exportado:", out)
