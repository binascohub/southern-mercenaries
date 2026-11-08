"""Pedra de energia na entrada do Bordel de Tortuga ("tiny_planet_friends_3d-energy-3212", zh123; arquivo trazido pelo autor do projeto): cristal roxo-estrelado de
duas pirâmides, malha parada de 500 mil triângulos, 1,2 m de altura, três texturas de 2048 px. Aqui ela é reduzida (~TARGET_TRIS triângulos; a forma é de faces
planas, não perde nada), as texturas vão a 512 px, fica com HEIGHT m, centrada e apoiada no chão. Vira uma peça do kit (assets/models/props/Brothel_Stone.glb),
a saída "brothel_door" da rua de Tortuga (tools/assets/build_brothel.py), sem portal nem marca no minimapa.
uso: blender -b --python tools/assets/build_brothel_stone.py -- <arquivo.glb> <saída.glb>"""
import bpy, sys
import numpy as np
from mathutils import Matrix, Vector

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
TARGET_TRIS = 20000
MAX_TEX = 512
HEIGHT = 1.4
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
total = sum(len(o.data.polygons) for o in meshes)
for o in meshes:
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    mod = o.modifiers.new("dec", "DECIMATE")
    mod.ratio = min(1.0, TARGET_TRIS / total)
    bpy.ops.object.modifier_apply(modifier="dec")
for image in bpy.data.images:
    w, h = image.size
    if max(w, h) > MAX_TEX:
        image.scale(max(1, w * MAX_TEX // max(w, h)), max(1, h * MAX_TEX // max(w, h)))
pts = np.concatenate([np.array([o.matrix_world @ v.co for v in o.data.vertices]) for o in meshes])
mn, mx = pts.min(0), pts.max(0)
k = HEIGHT / (mx[2] - mn[2])
for o in [o for o in bpy.data.objects if o.parent is None]:
    o.matrix_world = Matrix.Translation(Vector((-(mn[0] + mx[0]) / 2 * k, -(mn[1] + mx[1]) / 2 * k, -mn[2] * k))) @ Matrix.Scale(k, 4) @ o.matrix_world
print("triângulos", total, "->", sum(len(o.data.polygons) for o in meshes), "escala", round(k, 3))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_image_format="WEBP", export_image_quality=85)
