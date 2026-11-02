"""Costela de Adão (human-rib-cage-light.glb do autor: caixa torácica humana de 253 mil vértices, 2 texturas de 1024 px; autoria e licença a confirmar): o item que o Leshy larga e que a Taberneira
recebe na missão da Floresta. A malha é reduzida a ~12 mil triângulos, centrada, com o pé no chão, em 0,5 m de altura e deitada de frente para o jogador (assets/models/props/Adam_Rib.glb).
uso: blender -b -P tools/assets/build_adam_rib.py -- <human-rib-cage-light.glb> <saida.glb>"""
import bpy, sys
from mathutils import Vector

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
o = [o for o in bpy.data.objects if o.type == "MESH"][0]
o.data.transform(o.matrix_world)
o.parent = None
bpy.context.view_layer.objects.active = o
dec = o.modifiers.new("dec", "DECIMATE")
dec.ratio = min(1.0, 24000.0 / max(1, len(o.data.polygons)))
bpy.ops.object.modifier_apply(modifier="dec")
pts = [v.co for v in o.data.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
k = 0.5 / (hi.z - lo.z)
for v in o.data.vertices:
    v.co = Vector(((v.co.x - (lo.x + hi.x) / 2) * k, (v.co.y - (lo.y + hi.y) / 2) * k, (v.co.z - lo.z) * k))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85, export_animations=False)
print("OK", out, [round(v, 2) for v in o.dimensions], len(o.data.vertices))
