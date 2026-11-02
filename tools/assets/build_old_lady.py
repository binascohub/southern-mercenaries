"""Velha (Old Lady, cdmir, CC0): modelo rigado do Blender com as texturas
embutidas (pele com oclusão, relevo e especular) mas o material sem ligação.
Refaz o material (cor + relevo), tira câmera, luzes e as formas de controle do
esqueleto e exporta o corpo, o cabelo e o esqueleto num .glb. Só tem a animação
de sentada (2051 quadros): fica o começo dela ("sit"), e a pose de repouso é ela
de pé com as mãos na cintura. Altura ~135 unidades.
uso: blender -b oldlady.blend --python build_old_lady.py -- <saida.glb> [quadros]"""
import bpy, sys

args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
frames = int(args[1]) if len(args) > 1 else 240

keep = {"Armature", "OldLady", "Hair"}
for o in list(bpy.data.objects):
    if o.name not in keep:
        bpy.data.objects.remove(o, do_unlink=True)

mat = bpy.data.materials.new("OldLady")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Roughness"].default_value = 0.85
out_node = nodes.new("ShaderNodeOutputMaterial")
links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
color = nodes.new("ShaderNodeTexImage")
color.image = bpy.data.images["oldlady-skin+AO.png"]
links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
normal = nodes.new("ShaderNodeTexImage")
normal.image = bpy.data.images["oldlady-norm.png"]
normal.image.colorspace_settings.name = "Non-Color"
normal_map = nodes.new("ShaderNodeNormalMap")
links.new(normal.outputs["Color"], normal_map.inputs["Color"])
links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])
for name in ("OldLady", "Hair"):
    data = bpy.data.objects[name].data
    data.materials.clear()
    data.materials.append(mat)

for action in list(bpy.data.actions):
    if action.name == "Sitting":
        action.name = "sit"
        action.use_fake_user = True
    else:
        bpy.data.actions.remove(action)
armature = bpy.data.objects["Armature"]
armature.animation_data_create()
armature.animation_data.action = bpy.data.actions["sit"]
scene = bpy.context.scene
scene.frame_start, scene.frame_end = 0, frames

bpy.context.view_layer.objects.active = armature
for o in bpy.data.objects:
    o.select_set(o.name in keep)
bpy.ops.export_scene.gltf(
    filepath=out, export_format="GLB", use_selection=True,
    export_animations=True, export_animation_mode="ACTIONS", export_force_sampling=True,
    export_frame_range=True, export_image_format="WEBP", export_apply=False, export_yup=True,
)
print("velha exportada:", out)
