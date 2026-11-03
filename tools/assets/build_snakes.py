"""Cobras de cenário feitas do zero (sem pacote de terceiros) para a Floresta Escura, em três cores (Green, Dark, Red) e duas poses:
  Snake_Coil_<cor>.glb      cobra enroscada, com o pescoço levantado e a cabeça de frente (~0,7 m de largura, 0,55 m de altura)
  Snake_Slither_<cor>.glb   cobra deslizando em S (~1,5 m de comprimento), com a cabeça voltada para +Z do jogo (o decor "swim" a faz deslizar em círculos)
O corpo é uma fileira de esferas que afinam até a cauda, em faixas de duas tonalidades; olhos amarelos e língua vermelha na cabeça.
uso: blender -b -P tools/assets/build_snakes.py -- <pasta de saída, ex.: assets/models/maps>"""
import bpy, math, os, sys
from mathutils import Vector, Matrix

out_dir = sys.argv[sys.argv.index("--") + 1]
COLORS = {"Green": ((0.12, 0.35, 0.1, 1), (0.04, 0.16, 0.05, 1)), "Dark": ((0.09, 0.09, 0.1, 1), (0.2, 0.17, 0.08, 1)), "Red": ((0.55, 0.1, 0.06, 1), (0.1, 0.07, 0.05, 1))}


def make_mat(name, rgba, rough=0.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Roughness"].default_value = rough
    return m


def sphere(at, radius, mat, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=at, segments=12, ring_count=8)
    o = bpy.context.active_object
    o.scale = scale
    o.data.materials.append(mat)
    return o


def build(points, radii, head_dir, mats, eye_mat, tongue_mat):
    """Esferas ao longo de `points` (cabeça no último ponto), com raio por ponto; faixas alternadas; olhos e língua."""
    for i, (p, r) in enumerate(zip(points, radii)):
        sphere(p, r, mats[(i // 5) % 2])
    hp, hr = points[-1], radii[-1]
    d = Vector(head_dir).normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-4:
        side = Vector((1, 0, 0))
    side.normalize()
    sphere(hp + d * hr * 0.6, hr * 1.15, mats[0], (1.0, 1.0, 0.8))            # cabeça mais larga
    for s in (-1, 1):
        sphere(hp + d * hr * 1.0 + side * s * hr * 0.55 + Vector((0, 0, hr * 0.45)), hr * 0.22, eye_mat)
    sphere(hp + d * hr * 2.0, hr * 0.12, tongue_mat, (0.5, 0.5, 2.2))


def export(name):
    bpy.ops.object.select_all(action="DESELECT")
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    whole = bpy.context.view_layer.objects.active
    whole.name = whole.data.name = name
    pts = [whole.matrix_world @ v.co for v in whole.data.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    whole.data.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    bpy.ops.object.select_all(action="DESELECT")
    whole.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out_dir, name + ".glb"), export_format="GLB", use_selection=True)
    print("OK", name, "caixa %.2f x %.2f x %.2f m" % tuple(mx[i] - mn[i] for i in range(3)))


for cname, (c1, c2) in COLORS.items():
    # --- enroscada: espiral de 2,3 voltas que sobe um pouco e termina num pescoço em S com a cabeça de frente (-Y do Blender = +Z do jogo)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mats = [make_mat("A", c1), make_mat("B", c2)]
    eye, tongue = make_mat("Eye", (0.95, 0.8, 0.1, 1), 0.2), make_mat("Tongue", (0.8, 0.05, 0.1, 1), 0.5)
    pts, rads = [], []
    n = 100
    for i in range(n):
        t = i / (n - 1)
        if t < 0.78:
            u = t / 0.78
            a = u * 2.3 * math.tau
            rad = 0.3 - 0.1 * u
            pts.append(Vector((math.cos(a) * rad, math.sin(a) * rad, 0.05 + 0.1 * u + 0.03 * math.sin(u * 20))))
        else:
            u = (t - 0.78) / 0.22
            pts.append(Vector((0.2 * math.cos(2.3 * math.tau) * (1 - u), -0.18 * u, 0.15 + 0.4 * u)))
        rads.append(0.07 * (0.35 + 0.65 * (1 - abs(t - 0.45) * 1.1)) if t < 0.9 else 0.055)
    build(pts, rads, (0, -1, 0), mats, eye, tongue)
    export("Snake_Coil_" + cname)
    # --- deslizando: S ao longo de -Y (a cabeça no -Y), cauda em +Y
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mats = [make_mat("A", c1), make_mat("B", c2)]
    eye, tongue = make_mat("Eye", (0.95, 0.8, 0.1, 1), 0.2), make_mat("Tongue", (0.8, 0.05, 0.1, 1), 0.5)
    pts, rads = [], []
    n = 90
    for i in range(n):
        t = i / (n - 1)
        y = 0.75 - 1.5 * t
        x = 0.16 * math.sin(t * 3.2 * math.pi) * (0.4 + 0.6 * t)
        pts.append(Vector((x, y, 0.045)))
        rads.append(0.045 * (0.25 + 0.75 * min(1.0, t * 3.0)) if t < 0.95 else 0.05)
    # a cabeça (último ponto) está no -Y; a cauda afina em +Y
    pts = pts
    build(pts, rads, (0, -1, 0), mats, eye, tongue)
    export("Snake_Slither_" + cname)
