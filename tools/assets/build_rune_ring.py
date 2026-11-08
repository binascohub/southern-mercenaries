"""Anel Rúnico do golpe "rune_ring" (o Selo Rúnico do Senhor da Cripta): "Dark Magician Ring (Yugioh)" (Anthony Yanez na Sketchfab, CC BY 4.0;
arquivo trazido pelo autor), um anel de runas douradas que brilham. Aqui as duas malhas (a faixa e as runas) ficam deitadas no chão (plano XZ do jogo),
centradas e com 1 m de diâmetro, sem a animação de giro (o jogo gira e desce o anel em game/levels/hazards.gd). Vai para assets/models/fx/rune_ring.glb.
uso: blender -b --python tools/assets/build_rune_ring.py -- <anel.glb> <saída.glb>"""
import bpy, sys
import numpy as np
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
for obj in meshes:
    world = obj.matrix_world.copy()
    obj.parent = None
    obj.data.transform(world)
    obj.matrix_world = Matrix.Identity(4)
for o in [o for o in bpy.data.objects if o not in meshes]:
    bpy.data.objects.remove(o, do_unlink=True)
pts = np.concatenate([np.array([v.co[:] for v in o.data.vertices]) for o in meshes])
mn, mx = pts.min(axis=0), pts.max(axis=0)
size = mx - mn
thin = int(np.argmin(size))  # o eixo fino é a normal do anel: ela vai para cima (z no Blender = y no jogo)
turn = {0: Matrix.Rotation(np.pi / 2, 4, "Y"), 1: Matrix.Rotation(np.pi / 2, 4, "X"), 2: Matrix.Identity(4)}[thin]
center = Matrix.Translation(-Vector(((mn + mx) / 2).tolist()))
scale = Matrix.Scale(1.0 / float(size.max()), 4)
for obj in meshes:
    obj.data.transform(scale @ turn @ center)
    obj.animation_data_clear()
print("malhas", len(meshes), "eixo fino", thin, "tamanho", size.round(1))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animations=False, export_image_format="WEBP", export_image_quality=85)
