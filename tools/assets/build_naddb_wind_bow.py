"""Arco do Arqueiro de vento ("Bow and arrow", naddb, CC-BY 4.0, sketchfab.com/3d-models/bow-and-arrow-ce2c19b57b1b4b9a843c985d2a95c3c0): arco dourado com asas
brancas. Ficam o arco, as pedras, as asas e a corda; saem a flecha solta, a câmera e a luz. Peça do Kit (Weapon_Bow_Wind.glb), no mesmo formato de Weapon_Bow.glb
(tools/assets/build_sujirour_bow.py): de pé (Z do Blender = Y do Godot), 1,5 m de altura com as asas, empunhadura na origem, barriga para +X e a corda em -X.
uso: blender -b -P tools/assets/build_naddb_wind_bow.py -- <bow_and_arrow.glb> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
KEEP = ("Cylinder_gold", "Cylinder.001_diamond", "Cube.009_white", "Cube_Material")  # arco, pedras, asas, corda
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith(KEEP)]
bow = next(o for o in meshes if o.name.startswith("Cylinder_gold"))
string = next(o for o in meshes if o.name.startswith("Cube_Material"))
for o in meshes:
    o.data = o.data.copy()
    o.data.transform(o.matrix_world)
    o.parent = None
    o.matrix_world = Matrix.Identity(4)
for o in list(bpy.context.scene.objects):
    if o not in meshes:
        bpy.data.objects.remove(o, do_unlink=True)

def bounds(objs):
    pts = [v.co for o in objs for v in o.data.vertices]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])

def center(objs):
    pts = [v.co for o in objs for v in o.data.vertices]
    return sum(pts, Vector()) / len(pts)

def apply(m):
    for o in meshes:
        o.data.transform(m)

# O comprimento do arco (sem as asas) vai para Z; o eixo da corda até o arco, para X.
mn, mx = bounds([bow])
dims = [mx[i] - mn[i] for i in range(3)]
tall = max(range(3), key=lambda i: dims[i])
if tall == 0:
    apply(Matrix.Rotation(1.5707963, 4, "Y"))
elif tall == 1:
    apply(Matrix.Rotation(1.5707963, 4, "X"))
side = center([bow]) - center([string])
side.z = 0
if abs(side.y) > abs(side.x):
    apply(Matrix.Rotation(-1.5707963 if side.y > 0 else 1.5707963, 4, "Z"))
elif side.x < 0:
    apply(Matrix.Rotation(3.14159265, 4, "Z"))
# Altura total (com as asas) 1,5 m, empunhadura (o meio do arco) na origem.
mn, mx = bounds([bow])
apply(Matrix.Translation(-(mn + mx) / 2))
mn, mx = bounds(meshes)
k = 1.5 / (mx.z - mn.z)
apply(Matrix.Scale(k, 4))
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = bow
bpy.ops.object.join()
bow.name = bow.data.name = "Weapon_Bow_Wind"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animations=False, export_skins=False)
mn, mx = bounds([bow])
print("ok", [round(d, 3) for d in (mx - mn)], "corda x", round(center([bow]).x, 3))
