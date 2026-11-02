"""Altar de invocação dos mini-chefes (altar.glb do autor): o arquivo traz o altar de jogo (SM_Altar_01, 14 mil vértices, 5 materiais PBR de 4K, com o livro,
as raízes e as folhas) e uma escultura de 1 milhão de vértices ao lado ("altar"), que não vai para o jogo. Aqui fica só o altar de jogo e as 20 texturas de
4096 px descem para 1024 (WebP no .glb). ~2,7 x 2,6 m de base e 1,24 m de altura, base em z = 0 e centro na origem.
uso: blender -b -P tools/assets/build_altar.py -- <altar.glb> <saida.glb>"""
import bpy, sys
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in list(bpy.data.objects):
    if o.name != "SM_Altar_01":
        bpy.data.objects.remove(o, do_unlink=True)
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85)
print("OK", out)
