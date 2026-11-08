"""Gaivota de decoração das Docas: "Ring-Billed Gull" (osuecampus na Sketchfab, CC BY 4.0; arquivo trazido pelo autor), com esqueleto e a
animação "Head Turn" (o jogo toca a primeira animação da peça em laço: ela vira a cabeça). Aqui o modelo fica de pé em y = 0, centrado, com
HEIGHT de altura (um pouco maior que a real, para aparecer na câmera de cima). Vai para assets/models/maps/docks/Seagull.glb (peça "Seagull" do Kit).
uso: blender -b --python tools/assets/build_seagull.py -- <gull.glb> <saída.glb>"""
import bpy, sys
import numpy as np
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
HEIGHT = 0.45
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in [o for o in bpy.data.objects if o.type == "MESH" and o.parent is None and o.name.startswith("Icosphere")]:
    bpy.data.objects.remove(o, do_unlink=True)  # a esfera que o importador cria para desenhar os ossos
bpy.context.view_layer.update()
pts = []
for o in bpy.data.objects:
    if o.type == "MESH":
        M = o.matrix_world
        pts += [(M @ v.co)[:] for v in o.data.vertices]
pts = np.array(pts)
mn, mx = pts.min(axis=0), pts.max(axis=0)
print("tamanho", (mx - mn).round(3), "min", mn.round(3))
k = HEIGHT / float(mx[2] - mn[2])
holder = bpy.data.objects.new("Seagull", None)
bpy.context.scene.collection.objects.link(holder)
for o in [o for o in bpy.data.objects if o.parent is None and o != holder]:
    o.parent = holder
holder.location = Vector((-(mn[0] + mx[0]) / 2 * k, -(mn[1] + mx[1]) / 2 * k, -mn[2] * k))
holder.scale = (k, k, k)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85)
