"""Galeão pirata de Tortuga, feito em código (Blender como módulo Python), na
linha da referência do autor: casco escuro de tábuas com frisos dourados,
portinholas vermelhas com canhões, castelo de popa com janelas acesas e
lanternas, três mastros com velas carmesim abauladas (emblema de caveira),
gurupé com bujarronas, enxárcia, figura de proa e a bandeira pirata.
uso: build_galleon.py <pasta_texturas> <saida.glb>
Eixos do Blender: X = comprimento (proa em +X), Y = boca, Z = altura."""
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index("--") + 1:]
TEX, OUT = args[0], args[1]
bpy.ops.wm.read_factory_settings(use_empty=True)

L, B, DRAFT = 16.0, 4.6, 1.6
STATIONS = 28


# --- Materiais ----------------------------------------------------------------------
def mat(name, color, image=None, emission=0.0, metallic=0.0, rough=0.7):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    if image:
        tex = m.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(f"{TEX}/{image}")
        m.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if emission > 0:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = emission
    m.use_backface_culling = False
    return m

M_HULL = mat("Casco", (0.2, 0.13, 0.09), "hull_planks.png")
M_DECK = mat("Convés", (0.36, 0.25, 0.15))
M_GOLD = mat("Dourado", (0.78, 0.52, 0.2), metallic=0.8, rough=0.35)
M_RED = mat("Vermelho", (0.45, 0.06, 0.06))
M_IRON = mat("Ferro", (0.08, 0.08, 0.09), metallic=0.7, rough=0.5)
M_WOOD = mat("Mastros", (0.3, 0.2, 0.12))
M_SAIL = mat("Velas", (1, 1, 1), "sail_crimson.png", rough=0.9)
M_FLAG = mat("Bandeira", (1, 1, 1), "jolly_roger.png", rough=0.9)
M_LIGHT = mat("Janelas", (1.0, 0.7, 0.3), emission=3.0)
M_ROPE = mat("Cordas", (0.16, 0.12, 0.08))


def obj(name, bm, material):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(material)
    bpy.context.scene.collection.objects.link(o)
    return o


def box(name, center, size, material, rot_z=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rot_z, 3, "Z"), verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector(center), verts=bm.verts)
    return obj(name, bm, material)


def cyl(name, a, b, radius, material, segments=10, radius2=None):
    """Cilindro de a até b."""
    a, b = Vector(a), Vector(b)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=radius,
                          radius2=radius if radius2 is None else radius2, depth=(b - a).length)
    rot = (b - a).to_track_quat("Z", "Y").to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation((a + b) / 2) @ rot, verts=bm.verts)
    return obj(name, bm, material)


# --- Casco -----------------------------------------------------------------------------
def half_width(t):
    """Meia-boca: popa larga e quadrada (t=0), proa afinando até a roda (t=1)."""
    if t < 0.55:
        return B / 2 * (0.78 + 0.22 * math.sin(min(1.0, t / 0.55) * math.pi / 2))
    return B / 2 * max(0.04, math.cos((t - 0.55) / 0.45 * math.pi / 2) ** 0.8)


def sheer(t):
    """Altura da borda: sobe na popa (castelo) e um pouco na proa."""
    return 1.9 + 1.4 * max(0.0, 0.22 - t) / 0.22 + 0.9 * max(0.0, t - 0.8) / 0.2


def keel(t):
    return -DRAFT + 0.9 * max(0.0, t - 0.85) / 0.15


def section(t):
    """Pontos da seção (de bombordo a boreste, por baixo)."""
    w, top, bottom = half_width(t), sheer(t), keel(t)
    mid = 0.3
    pts = [(w * 0.92, top), (w, mid)]
    for k in range(1, 7):
        a = k / 7 * math.pi / 2
        pts.append((w * math.cos(a) ** 0.7, mid - (mid - bottom) * math.sin(a)))
    pts.append((0.0, bottom))
    right = [(-y, z) for y, z in reversed(pts[:-1])]
    return [(y, z) for y, z in pts] + right


bm = bmesh.new()
uv = bm.loops.layers.uv.new()
rings = []
for i in range(STATIONS + 1):
    t = i / STATIONS
    x = -L / 2 + t * L
    rings.append([bm.verts.new((x, y, z)) for y, z in section(t)])
for i in range(STATIONS):
    for j in range(len(rings[i]) - 1):
        f = bm.faces.new((rings[i][j], rings[i + 1][j], rings[i + 1][j + 1], rings[i][j + 1]))
        for loop in f.loops:
            loop[uv].uv = (loop.vert.co.x * 0.22, loop.vert.co.z * 0.45 + loop.vert.co.y * 0.05)
# Espelho de popa (a popa é reta).
stern = bm.faces.new(list(reversed(rings[0])))
for loop in stern.loops:
    loop[uv].uv = (loop.vert.co.y * 0.22, loop.vert.co.z * 0.45)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
obj("Casco", bm, M_HULL)

# Convés: tira entre as bordas, um pouco abaixo delas.
bm = bmesh.new()
edges = []
for i in range(STATIONS + 1):
    t = i / STATIONS
    x = -L / 2 + t * L
    w = half_width(t) * 0.92
    z = min(sheer(t), 2.0) - 0.35
    edges.append((bm.verts.new((x, -w, z)), bm.verts.new((x, w, z))))
for i in range(STATIONS):
    bm.faces.new((edges[i][0], edges[i + 1][0], edges[i + 1][1], edges[i][1]))
obj("Convés", bm, M_DECK)

# Frisos dourados ao longo do costado (três faixas) e a amurada no alto.
for k, frac in enumerate([0.98, 0.62, 0.3]):
    for side in (1, -1):
        bm = bmesh.new()
        prev = None
        for i in range(STATIONS + 1):
            t = i / STATIONS
            top, w = sheer(t), half_width(t)
            z = 0.3 + (top - 0.3) * frac if frac < 0.9 else top
            y = (w * (0.92 + 0.08 * (1 - frac)) + 0.03) * side
            a = bm.verts.new((-L / 2 + t * L, y, z - 0.06))
            b = bm.verts.new((-L / 2 + t * L, y, z + 0.06))
            if prev:
                bm.faces.new((prev[0], a, b, prev[1]))
            prev = (a, b)
        obj(f"Friso {k} {side}", bm, M_GOLD)

# Portinholas vermelhas com o canhão saindo (duas fileiras).
for row, zf in enumerate([0.95, 1.55]):
    for i in range(7 if row == 0 else 6):
        t = 0.2 + i * 0.085 + row * 0.04
        x = -L / 2 + t * L
        w = half_width(t)
        for side in (1, -1):
            y = (w * 0.97 + 0.05) * side
            box(f"Portinhola {row} {i} {side}", (x, y, zf), (0.42, 0.06, 0.38), M_RED)
            box(f"Boca {row} {i} {side}", (x, y + 0.02 * side, zf), (0.26, 0.06, 0.24), M_IRON)
            cyl(f"Canhão {row} {i} {side}", (x, y, zf), (x, y + 0.45 * side, zf), 0.07, M_IRON, 8)

# Castelo de popa: dois andares de janelas acesas, galeria e lanternas.
sx = -L / 2
for k, (z, h) in enumerate([(2.35, 0.9), (3.2, 0.7)]):
    width = B * (0.78 - 0.08 * k)
    box(f"Castelo {k}", (sx + 1.6, 0, z), (3.2, width, h), M_HULL)
    box(f"Castelo friso {k}", (sx + 1.6, 0, z + h / 2), (3.3, width + 0.1, 0.1), M_GOLD)
    for i in range(4 - k):
        y = (i - (3 - k) / 2) * 0.8
        box(f"Janela popa {k} {i}", (sx - 0.02, y, z), (0.06, 0.42, h * 0.55), M_LIGHT)
    for i in range(3):
        for side in (1, -1):
            box(f"Janela lado {k} {i} {side}", (sx + 0.7 + i * 0.9, (width / 2 + 0.03) * side, z), (0.4, 0.06, h * 0.5), M_LIGHT)
box("Galeria", (sx - 0.25, 0, 2.0), (0.5, B * 0.8, 0.12), M_GOLD)
for side in (1, -1):
    cyl(f"Lanterna haste {side}", (sx + 0.2, 1.4 * side, 3.6), (sx - 0.3, 1.6 * side, 4.3), 0.04, M_GOLD, 6)
    box(f"Lanterna {side}", (sx - 0.3, 1.6 * side, 4.35), (0.3, 0.3, 0.4), M_LIGHT)
box("Brasão", (sx - 0.05, 0, 3.65), (0.05, 0.7, 0.6), M_RED)
box("Brasão friso", (sx - 0.08, 0, 3.65), (0.03, 0.8, 0.7), M_GOLD)

# Castelo de proa baixo e a figura de proa (dragão estilizado, dourado).
box("Castelo de proa", (L / 2 - 2.3, 0, 2.15), (2.2, B * 0.55, 0.5), M_HULL)
bow = Vector((L / 2, 0, 1.7))
cyl("Figura de proa", bow, bow + Vector((1.4, 0, 0.7)), 0.22, M_GOLD, 8, 0.06)
cyl("Figura cabeça", bow + Vector((1.2, 0, 0.6)), bow + Vector((1.7, 0, 0.9)), 0.12, M_GOLD, 8, 0.02)

# Gurupé com duas bujarronas triangulares.
bs_a, bs_b = Vector((L / 2 - 0.8, 0, 2.2)), Vector((L / 2 + 3.6, 0, 3.4))
cyl("Gurupé", bs_a, bs_b, 0.12, M_WOOD, 10, 0.06)

# Mastros, cestos, vergas e velas abauladas.
MASTS = [(-4.6, 9.5, 2), (0.6, 12.0, 3), (4.8, 10.0, 2)]
## Velas braceadas (giradas no mastro), como na referência: o emblema aparece de lado.
BRACE = math.radians(35)


def braced(x, y, z, mast_x):
    """Ponto (x, y, z) girado BRACE em volta do mastro em mast_x."""
    dx = x - mast_x
    return (mast_x + dx * math.cos(BRACE) - y * math.sin(BRACE), dx * math.sin(BRACE) + y * math.cos(BRACE), z)


def square_sail(name, x, z_top, z_bottom, width, belly):
    """Vela redonda: pano curvo (barriga para a frente), textura inteira."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new()
    nx, nz = 6, 6
    grid = []
    for j in range(nz + 1):
        row = []
        for i in range(nx + 1):
            u, v = i / nx, j / nz
            y = (u - 0.5) * width * (1.0 - 0.12 * v)
            z = z_top - (z_top - z_bottom) * v
            bulge = belly * math.sin(u * math.pi) * math.sin(min(1.0, v * 1.2) * math.pi * 0.9)
            row.append(bm.verts.new(braced(x + bulge, y, z, x - 0.15)))
        grid.append(row)
    for j in range(nz):
        for i in range(nx):
            f = bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
            for loop, (uu, vv) in zip(f.loops, [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]):
                loop[uvl].uv = (uu / nx, 1 - vv / nz)
    return obj(name, bm, M_SAIL)


for m, (x, height, sails) in enumerate(MASTS):
    base = 1.6
    cyl(f"Mastro {m}", (x, 0, base), (x, 0, base + height), 0.2, M_WOOD, 12, 0.1)
    cyl(f"Ponteira {m}", (x, 0, base + height), (x, 0, base + height + 0.6), 0.1, M_GOLD, 8, 0.0)
    span = height - 2.0
    for s in range(sails):
        top = base + height - 0.6 - s * span / sails
        bottom = top - span / sails * 0.82
        width = (B * 1.25) * (1.0 - 0.18 * (sails - 1 - s) / max(1, sails - 1)) if sails > 1 else B * 1.1
        end_a, end_b = braced(x, -width / 2 - 0.3, top, x), braced(x, width / 2 + 0.3, top, x)
        cyl(f"Verga {m} {s}", end_a, end_b, 0.07, M_WOOD, 8)
        box(f"Verga ponta {m} {s} a", end_a, (0.16, 0.16, 0.16), M_GOLD)
        box(f"Verga ponta {m} {s} b", end_b, (0.16, 0.16, 0.16), M_GOLD)
        square_sail(f"Vela {m} {s}", x + 0.15, top - 0.05, bottom, width, 0.9 - 0.15 * s)
    # Cesto da gávea.
    box(f"Cesto {m}", (x, 0, base + height * 0.62), (1.0, 1.0, 0.12), M_WOOD)
    # Enxárcia: cabos do topo até a borda, dos dois lados.
    t = (x + L / 2) / L
    for side in (1, -1):
        for k in range(3):
            foot = Vector((x - 0.6 + k * 0.6, half_width(t) * 0.95 * side, sheer(t)))
            cyl(f"Enxárcia {m} {side} {k}", foot, (x, 0.15 * side, base + height * 0.62), 0.025, M_ROPE, 4)

# Estais do gurupé ao mastro de proa e bujarronas.
fore_top = Vector((MASTS[2][0], 0, 1.6 + MASTS[2][1] * 0.9))
cyl("Estai", bs_b, fore_top, 0.03, M_ROPE, 4)
for k, (a, b, c) in enumerate([
        (bs_b + Vector((-0.4, 0, 0.1)), bs_b.lerp(fore_top, 0.55), Vector((L / 2 + 1.2, 0, 2.9))),
        (bs_b + Vector((-1.6, 0, -0.2)), bs_b.lerp(fore_top, 0.75) + Vector((-0.3, 0, -0.6)), Vector((L / 2 - 0.2, 0, 2.5)))]):
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new()
    va, vb, vc = bm.verts.new(a), bm.verts.new(b), bm.verts.new(c)
    f = bm.faces.new((va, vb, vc))
    for loop, coord in zip(f.loops, [(0.03, 0.03), (0.12, 0.3), (0.22, 0.03)]):
        loop[uvl].uv = coord
    obj(f"Bujarrona {k}", bm, M_SAIL)

# Bandeira pirata no topo do mastro grande, flâmulas vermelhas nos outros.
mx, mh = MASTS[1][0], 1.6 + MASTS[1][1]
bm = bmesh.new()
uvl = bm.loops.layers.uv.new()
grid = []
for j in range(3):
    row = []
    for i in range(5):
        u, v = i / 4, j / 2
        row.append(bm.verts.new((mx - u * 2.4, 0.15 * math.sin(u * 4.0), mh - 0.1 - v * 1.4)))
    grid.append(row)
for j in range(2):
    for i in range(4):
        f = bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
        for loop, (uu, vv) in zip(f.loops, [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]):
            loop[uvl].uv = (uu / 4, 1 - vv / 2)
obj("Bandeira pirata", bm, M_FLAG)
for m in (0, 2):
    x, h = MASTS[m][0], 1.6 + MASTS[m][1]
    bm = bmesh.new()
    pts = [bm.verts.new((x, 0, h)), bm.verts.new((x - 2.6, 0.2, h - 0.25)), bm.verts.new((x, 0, h - 0.5))]
    bm.faces.new(pts)
    obj(f"Flâmula {m}", bm, M_RED)

# Corrimão dourado do castelo de popa.
for side in (1, -1):
    cyl(f"Corrimão {side}", (sx + 0.1, (B * 0.39) * side, 3.75), (sx + 3.1, (B * 0.39) * side, 3.75), 0.04, M_GOLD, 6)

bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", export_image_format="WEBP", export_image_quality=85)
tris = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == "MESH")
print("OK", OUT, "faces", tris)
