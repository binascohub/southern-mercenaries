"""Exporta peças escolhidas de um pacote da Quaternius (CC0) como .gltf separados
numa pasta do jogo; as texturas (atlas compartilhados) ficam uma vez só, em 1024 px.
uso: export_kit.py <pasta_gltf_do_pacote> <pasta_destino> <Peca1,Peca2,...>"""
import bpy, sys, os
args = sys.argv[sys.argv.index("--") + 1:]
src, dst, names = args[0], args[1], args[2].split(",")
os.makedirs(dst, exist_ok=True)
for n in names:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(src, n + ".gltf"))
    for img in bpy.data.images:
        if img.size[0] > 1024:
            img.scale(1024, 1024)
    bpy.ops.export_scene.gltf(filepath=os.path.join(dst, n + ".gltf"), export_format="GLTF_SEPARATE",
        export_texture_dir="", export_image_format="WEBP", export_image_quality=85, export_animations=False)
    print("OK", n)
