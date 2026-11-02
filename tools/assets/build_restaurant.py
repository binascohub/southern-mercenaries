"""Restaurante medieval (medieval_restaurant.glb do autor: cena do SketchUp de uma estalagem de dois andares de telhado de madeira e base de pedra, com torre, pátio e uma árvore; 44 objetos, 500 mil
vértices, 34 materiais de textura de até 512 px; autoria e licença a confirmar): vira o prédio do Restaurante da Capital. As 5 malhas "BackSide" (as costas das faces, que dobravam os vértices) saem;
o resto (FrontSide) é ENDIREITADO (o prédio estava girado uns graus no SketchUp: o ângulo é o que dá a menor caixa em volta do que toca o chão) e reduzido para a escala dada (a maior dimensão do arquivo ~ 75
unidades; com 0,4 o prédio fica com ~26 x 30 m), pés no chão, centrado em x/y, e vira UMA malha de vários materiais ("Restaurant"). O lado da frente fica para +Z no Godot (depois da rotação em
build_restaurant.py: argumento --front-deg).
uso: blender -b -P tools/assets/build_restaurant.py -- <medieval_restaurant.glb> <saida.glb> [escala=0.4] [giro_extra_graus=0]"""
import bpy, sys, math
import numpy as np
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
scale = float(args[2]) if len(args) > 2 else 0.4
extra = float(args[3]) if len(args) > 3 else 0.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("BackSide")]
for o in list(bpy.data.objects):
    if o.type == "MESH" and o.name.startswith("BackSide"):
        bpy.data.objects.remove(o, do_unlink=True)
for o in meshes:
    mesh = o.data
    mesh.transform(o.matrix_world)
    o.parent = None
    o.matrix_world = Matrix.Identity(4)
for o in list(bpy.data.objects):
    if o.type != "MESH":
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "Restaurant"
mesh = body.data
P = np.array([tuple(v.co) for v in mesh.vertices])
# ângulo que dá a menor caixa em volta dos pontos baixos (o chão do prédio)
low = P[P[:, 2] < 6.0][:, :2]
best = (1e18, 0.0)
for deg in np.arange(0.0, 90.0, 0.25):
    r = math.radians(deg)
    R = np.array([[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]])
    q = low @ R.T
    area = float(np.ptp(q[:, 0]) * np.ptp(q[:, 1]))
    if area < best[0]:
        best = (area, deg)
ang = math.radians(best[1] + extra)
print("ANGLE", best[1], "extra", extra)
R = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
P[:, :2] = P[:, :2] @ R.T
P *= scale
P[:, 2] -= P[:, 2].min()
body_pts = P[P[:, 2] < 3.0]
P[:, 0] -= (body_pts[:, 0].min() + body_pts[:, 0].max()) / 2
P[:, 1] -= (body_pts[:, 1].min() + body_pts[:, 1].max()) / 2
for v, p in zip(mesh.vertices, P):
    v.co = Vector(p)
mesh.update()
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=80, export_animations=False)
print("OK", out, [round(v, 1) for v in body.dimensions], len(mesh.vertices))
