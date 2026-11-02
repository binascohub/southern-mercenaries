"""Espadas do Cavaleiro por rank (Low Poly Swords, Lamoot, CC BY 3.0, opengameart.org/content/low-poly-swords):
cinco das seis espadas do pacote (sem textura no original), uma .glb por rank (Sword_D ... Sword_S), de pé (ponta
em +Y), 1 m de comprimento, com o meio na origem. Lâmina e punho levam cores lisas do rank (metal e couro).
uso: build_knight_swords.py <lowpoly swords.blend> <saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
# rank: (modelo, cor do metal, metálico, cor do punho, brilho)
PICK = {"D": ("Sword", (0.42, 0.42, 0.44), 0.6, (0.22, 0.14, 0.08), 0.0),
        "C": ("Dha", (0.72, 0.75, 0.8), 0.85, (0.25, 0.12, 0.08), 0.0),
        "B": ("Falcata", (0.78, 0.46, 0.25), 0.85, (0.45, 0.08, 0.08), 0.0),
        "A": ("Sword 2", (0.88, 0.9, 0.97), 0.95, (0.1, 0.18, 0.4), 0.0),
        "S": ("Weird Sword", (0.95, 0.74, 0.22), 1.0, (0.06, 0.05, 0.07), 1.2)}
LENGTH = 1.0


def material(name, color, metal, rough, glow=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if glow > 0:
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = glow * 0.25
    return mat


for rank, (name, metal_color, metal, grip_color, glow) in PICK.items():
    bpy.ops.wm.open_mainfile(filepath=src)
    for o in list(bpy.data.objects):
        if o.name != name:
            bpy.data.objects.remove(o, do_unlink=True)
    obj = bpy.data.objects[name]
    me = obj.data
    me.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    # Eixo do comprimento: o maior.
    pts = [v.co for v in me.vertices]
    ext = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    axis = ext.index(max(ext))
    # O punho é a ponta mais estreita.
    lo, hi = min(p[axis] for p in pts), max(p[axis] for p in pts)

    def width_near(end):
        near = [p for p in pts if abs(p[axis] - end) < (hi - lo) * 0.15]
        other = [i for i in range(3) if i != axis]
        return max((max(p[i] for p in near) - min(p[i] for p in near)) for i in other) if near else 0
    flip = width_near(lo) > width_near(hi)  # a ponta mais larga (lâmina) deve ir para +Y
    # Gira o eixo do comprimento para +Z (depois o glTF o põe em +Y), com o punho embaixo.
    perm = {0: Matrix(((0, 0, 1, 0), (0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 0, 1))), 1: Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1))), 2: Matrix.Identity(4)}[axis]
    me.transform(perm)
    if flip:
        me.transform(Matrix.Rotation(3.14159265, 4, "X"))
    pts = [v.co for v in me.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    me.transform(Matrix.Scale(LENGTH / (mx.z - mn.z), 4) @ Matrix.Translation(-(mn + mx) / 2))
    me.materials.clear()
    me.materials.append(material("Blade_" + rank, metal_color, metal, 0.35, glow))
    me.materials.append(material("Grip_" + rank, grip_color, 0.0, 0.7))
    for poly in me.polygons:
        z = sum(me.vertices[i].co.z for i in poly.vertices) / len(poly.vertices)
        poly.material_index = 1 if z < -LENGTH * 0.28 else 0
    obj.name = "Sword_" + rank
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Sword_%s.glb" % rank), export_format="GLB", export_image_format="JPEG")
    print("OK", rank, name, "axis", axis, "flip", flip)
