"""Espírito Sombrio (shadow-spirit.glb do autor; autor/licença a confirmar): malha única de 6,6 mil vértices sem esqueleto nem animação (`static` em MonsterModel: flutua,
balança, avança e cai por código), ~0,96 x 2,5 m, pés em y = 0. Aqui só a textura de 2048 px (PNG de 4,4 MB) desce para 1024 (WebP no .glb).
uso: blender -b -P tools/assets/build_shadow_spirit.py -- <shadow-spirit.glb> <saida.glb>"""
import bpy, sys
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85)
print("OK", out)
