"""Demônio Doze (demon-twelve.glb do autor; autor/licença a confirmar): malha única de 28 mil vértices sem esqueleto nem animação (`static` em MonsterModel:
balança, avança e cai por código), ~1,2 x 2,2 m, pés em y = 0. Aqui só a textura de 2048 px (PNG de 4,7 MB) desce para 1024 (WebP no .glb).
uso: blender -b -P tools/assets/build_demon_twelve.py -- <demon-twelve.glb> <saida.glb>"""
import bpy, sys
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85)
print("OK", out)
