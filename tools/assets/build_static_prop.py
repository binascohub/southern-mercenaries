"""Decorações estáticas dos modelos do autor (~/Downloads/pixellabs-*.glb; autoria e licença a confirmar): aplica as transformações, reduz a malha (~10 mil vértices) e exporta
com as texturas em WEBP. Usadas: Banner_Dragon (pixellabs-banner-3761.glb, estandarte na entrada do Cemitério) e Skull_Throne (pixellabs-skull-throne-3562.glb, sala do chefe do Cemitério).
uso: blender -b -P tools/assets/build_static_prop.py -- <entrada.glb> <saida.glb> [vertices]"""
import bpy, sys
args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[:2]
target = float(args[2]) if len(args) > 2 else 10000.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
o = [x for x in bpy.data.objects if x.type == "MESH"][0]
bpy.context.view_layer.objects.active = o
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
d = o.modifiers.new("dec", "DECIMATE")
d.ratio = min(1.0, target / len(o.data.vertices))
bpy.ops.object.modifier_apply(modifier="dec")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_image_format="WEBP")
print("OK", out, len(o.data.vertices))
