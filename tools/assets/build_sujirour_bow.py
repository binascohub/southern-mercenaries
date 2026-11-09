"""Arco do Arqueiro na mão ("Bow", sujirour, CC-BY 4.0, sketchfab.com/3d-models/bow-ac9202b135f9479796be43735b7d9b24): o modelo vem com esqueleto e
a animação de puxar a corda; aqui fica só a malha na pose de descanso, sem esqueleto, como peça do Kit (Weapon_Bow.glb):
de pé (eixo Z do Blender = Y do Godot), 1,3 m de altura, empunhadura (o meio) na origem e a barriga do arco para +X, textura de cor em 1024 px.
uso: blender -b -P tools/assets/build_sujirour_bow.py -- <bow.glb> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for arm in [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]:
    if arm.animation_data:
        arm.animation_data.action = None  # pose de descanso: corda solta
    for bone in arm.pose.bones:
        bone.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
bpy.context.view_layer.objects.active = obj
for mod in list(obj.modifiers):
    bpy.ops.object.modifier_apply(modifier=mod.name)
obj.vertex_groups.clear()
me = obj.data
me.transform(obj.matrix_world)
obj.parent = None
obj.matrix_world = Matrix.Identity(4)
for o in list(bpy.context.scene.objects):
    if o is not obj:
        bpy.data.objects.remove(o, do_unlink=True)

def bounds():
    pts = [v.co for v in me.vertices]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])

# Comprimento no Z; a curva (o segundo maior eixo) no X.
mn, mx = bounds()
dims = [mx[i] - mn[i] for i in range(3)]
order = sorted(range(3), key=lambda i: -dims[i])
basis = Matrix.Identity(3)
cols = [Vector((0, 0, 0))] * 3
axes = [Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))]
target = {order[0]: 2, order[1]: 0, order[2]: 1}
rot = Matrix([[0.0] * 3 for _ in range(3)])
for src_axis, dst_axis in target.items():
    rot[dst_axis][src_axis] = 1.0
if rot.determinant() < 0:
    rot[1] = -rot[1]
me.transform(rot.to_4x4())
mn, mx = bounds()
k = 1.3 / (mx.z - mn.z)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(-(mn + mx) / 2))
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
obj.name = me.name = "Weapon_Bow"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animations=False, export_skins=False, export_image_format="WEBP")
print("ok", [round(d, 3) for d in (mx - mn)])
