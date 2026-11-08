"""Moça em cima da cama do Bordel de Tortuga ("Bikini Swimsuit V7", Fadly.W na Sketchfab, CC BY 4.0; arquivo trazido pelo autor do projeto): mulher de biquíni
e botas, de quatro, malha parada (sem esqueleto) de 139 mil triângulos num cubo de 1 unidade. Aqui ela é reduzida (~TARGET_TRIS triângulos), a textura vai a
1024 px, fica com HEIGHT m de altura (a da pose), apoiada no chão (z = 0), centrada e olhando para -Y (+Z no glTF). Vira uma peça do kit
(assets/models/props/<nome>.glb), posta em cima da cama por tools/assets/build_brothel.py.
uso: blender -b --python tools/assets/build_bed_pose.py -- <arquivo.glb> <saída.glb>"""
import bpy, sys
import numpy as np
from mathutils import Matrix, Vector

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
TARGET_TRIS = 30000
MAX_TEX = 1024
HEIGHT = 1.1  # altura da pose (de quatro, a cabeça erguida); o comprimento sai igual
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in list(bpy.data.objects):
    if o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
for o in meshes:
    world = o.matrix_world.copy()
    o.parent = None
    o.data.transform(world)
    o.matrix_world = Matrix.Identity(4)
for o in [o for o in bpy.data.objects if o.type != "MESH"]:
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
mod = body.modifiers.new("dec", "DECIMATE")
mod.ratio = min(1.0, TARGET_TRIS / len(body.data.polygons))
bpy.ops.object.modifier_apply(modifier="dec")
pts = np.array([v.co[:] for v in body.data.vertices])
mn, mx = pts.min(0), pts.max(0)
body.data.transform(Matrix.Translation(-Vector(((mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]))))
body.data.transform(Matrix.Scale(HEIGHT / (mx[2] - mn[2]), 4))
for image in bpy.data.images:
    w, h = image.size
    if max(w, h) > MAX_TEX:
        image.scale(max(1, w * MAX_TEX // max(w, h)), max(1, h * MAX_TEX // max(w, h)))
body.name = "Brothel_Bed_Woman"
pts = np.array([v.co[:] for v in body.data.vertices])
print("triângulos", len(body.data.polygons), "tamanho", (pts.max(0) - pts.min(0)).round(2))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_image_format="WEBP", export_image_quality=85)
