"""Cajado do Mago por elemento: junta as malhas de um cajado do Sketchfab numa peça do Kit, no formato do Weapon_MS_Staff: de pé (Z do Blender = Y do Godot),
1,7 m de altura, centro na origem e a cabeça (a ponta mais larga: garra, orbe) para cima; texturas em até 1024 px.
Fogo: "Starter Mage Staff" (eduo, CC-BY 4.0, sketchfab.com/3d-models/starter-mage-staff-8e10f6bc38ba411789bb36ec8627a697) -> Weapon_Staff_Fire.
Água: "Ice Staff" (Wasdteq11, CC-BY 4.0, sketchfab.com/3d-models/ice-staff-c3c71276130e42deaa168682a4208966) -> Weapon_Staff_Water.
Ar: "Khajiiti Moon Staff" (Shriker1, CC-BY 4.0, sketchfab.com/3d-models/khajiiti-moon-staff-87cca6fa0b94448b97a3b354843393e1) -> Weapon_Staff_Air.
Terra: "Stylized Wood Staff" (Manuela Reis, CC-BY 4.0, sketchfab.com/3d-models/stylized-wood-staff-be964c8b493041cab15b449c9f966c25) -> Weapon_Staff_Earth.
uso: blender -b -P tools/assets/build_element_staff.py -- <cajado.glb> <saída.glb> <nome da peça>"""
import bpy, sys
from mathutils import Vector, Matrix

src, out, piece = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
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
if len(me.vertices) > 30000:  # o de fogo vem com ~230 mil vértices: reduz para ~20 mil (é uma arma na mão, vista de longe)
    mod = obj.modifiers.new("d", "DECIMATE")
    mod.ratio = 20000 / len(me.vertices)
    bpy.ops.object.modifier_apply(modifier="d")


def bounds():
    pts = [v.co for v in me.vertices]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


# A direção do cajado (o eixo de maior espalhamento dos vértices, que pode vir inclinado no arquivo) vira Z.
pts = [v.co.copy() for v in me.vertices]
mean = sum(pts, Vector()) / len(pts)
cov = Matrix(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
for p in pts:
    d = p - mean
    for i in range(3):
        for j in range(3):
            cov[i][j] += d[i] * d[j]
direction = Vector((1.0, 1.0, 1.0))
for _ in range(60):  # iteração de potência: o autovetor principal
    direction = (cov @ direction).normalized()
me.transform(direction.rotation_difference(Vector((0.0, 0.0, 1.0))).to_matrix().to_4x4() @ Matrix.Translation(-mean))
mn, mx = bounds()
me.transform(Matrix.Scale(1.7 / (mx.z - mn.z), 4) @ Matrix.Translation(-(mn + mx) / 2))


# Cabeça para cima: a ponta mais larga (garra, orbe) fica em +Z.
def spread(sel):
    pts = [v.co for v in me.vertices if sel(v.co.z)]
    if not pts:
        return 0.0
    return max(Vector((p.x, p.y, 0)).length for p in pts)


if spread(lambda z: z < -0.6) > spread(lambda z: z > 0.6):
    me.transform(Matrix.Rotation(3.14159265, 4, "X"))
for image in bpy.data.images:
    if image.size[0] > 1024:
        image.scale(1024, 1024)
obj.name = me.name = piece
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animations=False, export_image_format="AUTO")  # WebP deixava texturas sem "source" (o Godot não importava)
mn, mx = bounds()
print("ok", [round(d, 3) for d in (mx - mn)])
