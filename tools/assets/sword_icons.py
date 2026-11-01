"""Ícones de inventário das espadas do Cavaleiro por rank (128 px, fundo transparente) a partir do 3D Swords Pack
(mehrasaur / Inborn Ninja, CC0, opengameart.org/content/3d-swords-pack). Só aparecem no inventário (não no herói).
uso: sword_icons.py <pasta obj_mtl do pacote> <pasta de saída>"""
import bpy, sys, math, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
# rank: (modelo, cor do metal, metálico, cor do punho)
PICK = {"D": ("sword_8", (0.45, 0.45, 0.47), 0.6, (0.25, 0.15, 0.08)),
        "C": ("sword_6", (0.74, 0.77, 0.82), 0.85, (0.28, 0.13, 0.08)),
        "B": ("sword_7", (0.8, 0.47, 0.25), 0.85, (0.5, 0.08, 0.08)),
        "A": ("sword_3", (0.9, 0.93, 1.0), 0.95, (0.1, 0.2, 0.5)),
        "S": ("sword_9", (0.97, 0.76, 0.22), 1.0, (0.07, 0.05, 0.08))}
FLIP = {"C", "A"}  # a detecção automática do punho erra nestes dois (ponta mais estreita que o pomo)
os.makedirs(out, exist_ok=True)


def material(name, color, metal, rough):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    return mat


for rank, (model, blade, metal, grip) in PICK.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=os.path.join(src, model + ".obj"))
    obj = [o for o in bpy.data.objects if o.type == "MESH"][0]
    me = obj.data
    me.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    pts = [v.co for v in me.vertices]
    ext = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    axis = ext.index(max(ext))
    to_z = {0: Matrix(((0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 0, 1))), 1: Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1))), 2: Matrix.Identity(4)}[axis]
    me.transform(to_z)
    pts = [v.co for v in me.vertices]
    lo, hi = min(p.z for p in pts), max(p.z for p in pts)
    def width(end):
        near = [p for p in pts if abs(p.z - end) < (hi - lo) * 0.12]
        return max(max(p.x for p in near) - min(p.x for p in near), max(p.y for p in near) - min(p.y for p in near)) if near else 0
    if (width(hi) > width(lo)) != (rank in FLIP):  # a lâmina (parte larga) fica para cima, o punho embaixo
        me.transform(Matrix.Rotation(math.pi, 4, "X"))
        pts = [v.co for v in me.vertices]
        lo, hi = min(p.z for p in pts), max(p.z for p in pts)
    me.materials.clear()
    me.materials.append(material("Blade", blade, metal, 0.3))
    me.materials.append(material("Grip", grip, 0.0, 0.7))
    for poly in me.polygons:
        z = sum(me.vertices[i].co.z for i in poly.vertices) / len(poly.vertices)
        poly.material_index = 1 if z < lo + (hi - lo) * 0.2 else 0
    # Blade para cima e para a direita (45°), vista de frente.
    obj.rotation_euler = (0, math.radians(45), 0)
    bpy.context.view_layer.update()
    wp = [obj.matrix_world @ v.co for v in me.vertices]
    mid = Vector([(max(p[i] for p in wp) + min(p[i] for p in wp)) / 2 for i in range(3)])
    size = max(max(p[i] for p in wp) - min(p[i] for p in wp) for i in (0, 2))
    sc = bpy.context.scene
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = size * 1.12
    cam.location = (mid.x, mid.y - 20, mid.z)
    cam.rotation_euler = (math.pi / 2, 0, 0)
    sc.camera = cam
    for ang, e in ((50, 3.5), (-30, 1.2)):
        l = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); l.data.energy = e
        l.rotation_euler = (math.radians(ang), math.radians(-15), math.radians(30)); sc.collection.objects.link(l)
    w = bpy.data.worlds.new("w"); w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.5, 0.5, 0.52, 1)
    sc.world = w
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = 128
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.filepath = os.path.join(out, "sword_%s.png" % rank)
    bpy.ops.render.render(write_still=True)
    print("OK", rank, model)
