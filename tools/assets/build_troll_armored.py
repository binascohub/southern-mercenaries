"""Troll Blindado das Ruínas ("Troll (Armored)", SidewalkNZ na Sketchfab, CC BY 4.0; arquivo trazido pelo autor do projeto): malha parada em T-pose,
sem esqueleto nem animação, em 4 pedaços (corpo, cinto, armadura) com 3 texturas. Aqui os pedaços viram uma malha só, de pé em z = 0, centrada,
com 3 m de altura, reduzida a ~40 mil triângulos e com texturas de no máximo 1024 px (WebP). Vai para assets/models/monsters/troll_armored.glb;
tools/assets/rig_biped.py (perfil troll_armored) a prende ao esqueleto dos heróis: troll_armored_animated.glb, o que o jogo usa.
uso: blender -b --python tools/assets/build_troll_armored.py -- <troll_armored.glb> <saída.glb>"""
import bpy, sys
import numpy as np
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
HEIGHT = 3.0
TARGET = 40000
MAX_TEX = 1024
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
for obj in meshes:
    world = obj.matrix_world.copy()
    obj.parent = None
    obj.data.transform(world)
    obj.matrix_world = Matrix.Identity(4)
for o in [o for o in bpy.data.objects if o.type != "MESH"]:
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action="DESELECT")
for obj in meshes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active
tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
if tris > TARGET:
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.ratio = TARGET / tris
    bpy.ops.object.modifier_apply(modifier="dec")
pts = np.array([v.co[:] for v in obj.data.vertices])
mn, mx = pts.min(axis=0), pts.max(axis=0)
obj.data.transform(Matrix.Translation(-Vector(((mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]))))
obj.data.transform(Matrix.Scale(HEIGHT / (mx[2] - mn[2]), 4))
for poly in obj.data.polygons:
    poly.use_smooth = True
for image in bpy.data.images:
    w, h = image.size
    if max(w, h) > MAX_TEX:
        k = MAX_TEX / max(w, h)
        image.scale(max(1, int(w * k)), max(1, int(h * k)))
obj.name = "troll_armored"
pts = np.array([v.co[:] for v in obj.data.vertices])
print("triângulos", sum(len(p.vertices) - 2 for p in obj.data.polygons), "tamanho", (pts.max(0) - pts.min(0)).round(2))
# Perfil para o rig_biped: largura e frente/trás por fatia de altura (a T-pose mostra o ombro e a mão; as pernas, a separação).
for z in np.arange(0.0, HEIGHT + 0.01, 0.1):
    sl = pts[(pts[:, 2] >= z) & (pts[:, 2] < z + 0.1)]
    if len(sl):
        legs = sl[np.abs(sl[:, 0]) < 0.8]
        print("z %.1f  x %+.2f..%+.2f  y %+.2f..%+.2f  pernas|x| %.2f" % (z, sl[:, 0].min(), sl[:, 0].max(), sl[:, 1].min(), sl[:, 1].max(),
              np.median(np.abs(legs[:, 0])) if len(legs) else 0))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_image_format="WEBP", export_image_quality=80)
