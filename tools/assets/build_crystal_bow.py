"""Arco do Arqueiro de terra ("Elder Crystal Bow [PolyPaint]", Xillute | Dev, CC-BY 4.0,
sketchfab.com/3d-models/elder-crystal-bow-polypaint-e3b58d6553f14f1eb353a311734cec1a): madeira escura com cristais verdes. As duas malhas viram uma peça do Kit
(Weapon_Bow_Earth.glb), no mesmo formato de Weapon_Bow.glb (tools/assets/build_sujirour_bow.py): de pé (Z do Blender = Y do Godot), 1,3 m de altura,
empunhadura na origem, barriga para +X, textura de cor em 1024 px.
Também serve ao arco de água ("Stylized Ice Bow", Sinyata, CC-BY 4.0, sketchfab.com/3d-models/stylized-ice-bow-d73bf916ae1c4ed09c5c63f60639bd3f) com o nome
da peça no 3º argumento: Weapon_Bow_Water.
E ao arco de fogo ("Thundering Pulse - Bow", ndnguyen3d, CC-BY 4.0, sketchfab.com/3d-models/thundering-pulse-bow-40d3f938287d4fdf85dbcf9520476eb7): Weapon_Bow_Fire,
sem a flecha solta (4º argumento: começos de nome das malhas que saem, separados por vírgula: BezierCurve.003,BezierCurve.004,BezierCurve.005).
uso: blender -b -P tools/assets/build_crystal_bow.py -- <arco.glb> <saída.glb> [nome da peça, padrão Weapon_Bow_Earth] [malhas que saem]"""
import bpy, sys
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
piece = args[2] if len(args) > 2 else "Weapon_Bow_Earth"
drop = tuple(name for name in args[3].split(",") if name) if len(args) > 3 else ()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and not (drop and o.name.startswith(drop))]
for o in meshes:
    o.data = o.data.copy()
    o.data.transform(o.matrix_world)
    o.parent = None
    o.matrix_world = Matrix.Identity(4)
for o in list(bpy.context.scene.objects):
    if o not in meshes:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
obj = meshes[0]
me = obj.data

def bounds():
    pts = [v.co for v in me.vertices]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])

# Comprimento no Z; a curva (o segundo maior eixo) no X.
mn, mx = bounds()
dims = [mx[i] - mn[i] for i in range(3)]
order = sorted(range(3), key=lambda i: -dims[i])
rot = Matrix([[0.0] * 3 for _ in range(3)])
for src_axis, dst_axis in {order[0]: 2, order[1]: 0, order[2]: 1}.items():
    rot[dst_axis][src_axis] = 1.0
if rot.determinant() < 0:
    rot[1] = -rot[1]
me.transform(rot.to_4x4())
mn, mx = bounds()
me.transform(Matrix.Scale(1.3 / (mx.z - mn.z), 4) @ Matrix.Translation(-(mn + mx) / 2))
# Barriga para +X: o meio do arco (a empunhadura) fica à frente das pontas.
mid = [v.co.x for v in me.vertices if abs(v.co.z) < 0.08]
tips = [v.co.x for v in me.vertices if abs(v.co.z) > 0.55]
if sum(mid) / len(mid) < sum(tips) / len(tips):
    me.transform(Matrix.Rotation(3.14159265, 4, "Z"))
mn, mx = bounds()
me.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, 0))))
for image in bpy.data.images:
    if image.size[0] > 1024:
        image.scale(1024, 1024)
obj.name = me.name = piece
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animations=False, export_skins=False, export_image_format="WEBP")
mn, mx = bounds()
print("ok", [round(d, 3) for d in (mx - mn)])
