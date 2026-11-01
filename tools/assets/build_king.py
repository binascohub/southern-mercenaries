"""Rei da sala do trono da Capital: converte ~/Downloads/king.glb (modelo estático de 432 mil vértices, autor/licença a confirmar)
em assets/models/props/King.glb (decimado, textura 2048 JPEG), em pé, com os pés no chão e de frente para +Z.
uso: blender -b -P tools/assets/build_king.py -- <king.glb> <saida.glb>"""
import bpy, sys
src, dst = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
o = [x for x in bpy.data.objects if x.type == 'MESH'][0]
bpy.context.view_layer.objects.active = o
m = o.modifiers.new("d", 'DECIMATE'); m.ratio = 40000 / max(1, len(o.data.polygons)); bpy.ops.object.modifier_apply(modifier="d")
for img in bpy.data.images:
    if img.size[0] > 2048:
        img.scale(2048, 2048)
    img.file_format = 'JPEG'
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='JPEG', export_jpeg_quality=85)
print("OK", len(o.data.polygons))
