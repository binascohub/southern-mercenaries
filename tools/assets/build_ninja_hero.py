"""Corpo do Ninja (modelo estático ninja.glb enviado pelo autor do projeto, 434 mil vértices, autor/licença a confirmar) ligado ao esqueleto e às
animações do herói masculino (assets/models/characters/hero_male.glb): gera assets/models/characters/hero_ninja.glb.
 - decima para ~45 mil triângulos e reduz a textura para 2048;
 - pesos por distância às cápsulas dos ossos (braços no A-pose do modelo) e, depois, os braços sobem para o T-pose do esqueleto (o peso decide quanto);
 - separa em 4 peças, uma por slot de equipamento (Ninja_Body, Ninja_Head, Ninja_Hands, Ninja_Feet), cada uma com 2 materiais:
   0 tecido azul (textura em tons de cinza, tingida no jogo pela cor do rank), 1 o resto (botas, luvas, espada, faixa, rosto e mãos: textura original, sem tingir).
Mantém a cabeça, os olhos e os cabelos do herói (a cidade esconde a peça Ninja_Head: capuz e máscara). Rode com o hero_male.glb e com o hero_female.glb.
uso: blender -b -P tools/assets/build_ninja_hero.py -- <ninja.glb> <hero_male.glb> <saida.glb> [--debug]"""
import bpy, bmesh, sys, math, os
import numpy as np
from mathutils import Vector

src, hero_path, dst = sys.argv[-3], sys.argv[-2], sys.argv[-1]
debug = "--debug" in sys.argv
if dst == "--debug":
    src, hero_path, dst = sys.argv[-4], sys.argv[-3], sys.argv[-2]
tmp = os.path.join(os.path.expanduser("~/.cache/sm-animalkit/ninja"))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=hero_path)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
# fica o rosto do herói (Head, Eyes, Eyebrows e os cabelos), que a cidade mostra no lugar do capuz e da máscara
keep = []
for o in list(bpy.data.objects):
    if o.type == 'MESH':
        if o.name in ("Head", "Eyes", "Eyebrows") or o.name.startswith("Hair"):
            keep.append(o)
        else:
            bpy.data.objects.remove(o, do_unlink=True)
hero_top = max(max((o.matrix_world @ Vector(c)).z for c in o.bound_box) for o in keep if o.name == "Head")
bones = {b.name: (Vector(b.head_local), Vector(b.tail_local)) for b in arm.data.bones}
bpy.ops.import_scene.gltf(filepath=src)
nin = [o for o in bpy.data.objects if o.type == 'MESH' and o not in keep][0]
nin.parent = None
bpy.context.view_layer.objects.active = nin
nin.select_set(True)
mod = nin.modifiers.new("d", 'DECIMATE'); mod.ratio = 45000 / max(1, len(nin.data.polygons)); bpy.ops.object.modifier_apply(modifier="d")
bm = bmesh.new(); bm.from_mesh(nin.data); bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.to_mesh(nin.data); bm.free()
img = bpy.data.images[0]
img.scale(2048, 2048)
# alinha: altura = a do herói, pés no chão, tronco no eixo do esqueleto
v = np.array([tuple(x.co) for x in nin.data.vertices])
s = hero_top / (v[:, 2].max() - v[:, 2].min())
v = v * s
v[:, 2] -= v[:, 2].min()
torso = (v[:, 2] > 1.0) & (v[:, 2] < 1.4) & (abs(v[:, 0]) < 0.15)
v[:, 1] -= np.median(v[torso, 1]) - bones["spine_02"][0].y
# ângulo do braço (A-pose) pelos vértices fora do tronco
arm_sel = (v[:, 0] > 0.3) & (v[:, 2] > 0.6) & (v[:, 2] < 1.4)
slope = np.polyfit(v[arm_sel, 0], v[arm_sel, 2], 1)[0]
theta = math.atan(-slope)
print("ARM ANGLE", math.degrees(theta), "scale", s, "arm verts", arm_sel.sum())
sh = bones["upperarm_l"][0]
# cápsulas (cabeça, cauda, raio); braços girados para o A-pose
def a_pose(p, side):
    d = p - Vector((side * sh.x, sh.y, sh.z))
    c, sn = math.cos(theta), math.sin(theta)
    return Vector((side * sh.x + side * (d.x * side * c + d.z * sn), p.y, sh.z + (-d.x * side * sn + d.z * c)))
RAD = {"pelvis": .17, "spine_01": .17, "spine_02": .17, "spine_03": .16, "neck_01": .06, "Head": .1, "clavicle": .05, "upperarm": .06, "lowerarm": .045,
       "hand": .04, "thigh": .1, "calf": .07, "foot": .05, "ball": .04}
caps = []
for name in list(bones):
    base = name.rsplit("_", 1)[0] if name.endswith(("_l", "_r")) else name
    if base not in RAD:
        continue
    h, t = bones[name]
    if base == "hand":
        t = h + (t - h).normalized() * 0.16
    if base in ("upperarm", "lowerarm", "hand"):
        side = 1 if name.endswith("_l") else -1
        h, t = a_pose(h, side), a_pose(t, side)
    caps.append((name, h, t, RAD[base]))
P = v
D = np.zeros((len(P), len(caps)))
for i, (name, h, t, r) in enumerate(caps):
    ab = np.array(t - h); L2 = float(ab @ ab) + 1e-9
    u = np.clip(((P - np.array(h)) @ ab) / L2, 0, 1)
    d = np.linalg.norm(P - (np.array(h) + u[:, None] * ab), axis=1)
    D[:, i] = np.maximum(d - r, 0) + 0.004
W = (D.min(axis=1, keepdims=True) / D) ** 6
W[W < 0.04] = 0
drop = np.argsort(-W, axis=1)[:, 4:]
np.put_along_axis(W, drop, 0, axis=1)
W /= W.sum(axis=1, keepdims=True)
names = [c[0] for c in caps]
# braços do A-pose para o T-pose
arm_idx = {1: [names.index(n) for n in ("upperarm_l", "lowerarm_l", "hand_l")], -1: [names.index(n) for n in ("upperarm_r", "lowerarm_r", "hand_r")]}
c, sn = math.cos(theta), math.sin(theta)
for side, idx in arm_idx.items():
    wa = W[:, idx].sum(axis=1)
    dx = (P[:, 0] - side * sh.x) * side
    dz = P[:, 2] - sh.z
    nx = dx * c - dz * sn
    nz = dx * sn + dz * c
    P[:, 0] = np.where(wa > 0, P[:, 0] * (1 - wa) + (side * sh.x + side * nx) * wa, P[:, 0])
    P[:, 2] = np.where(wa > 0, P[:, 2] * (1 - wa) + (sh.z + nz) * wa, P[:, 2])
for i, vert in enumerate(nin.data.vertices):
    vert.co = Vector(P[i])
for n in names:
    nin.vertex_groups.new(name=n)
for i in range(len(P)):
    for j in np.nonzero(W[i])[0]:
        nin.vertex_groups[names[j]].add([i], float(W[i, j]), 'REPLACE')
# classificação das faces: tecido, pele, faixa (pela cor da textura no centro da face)
px = np.array(img.pixels[:], dtype=np.float32).reshape(2048, 2048, 4)[:, :, :3]
uv = nin.data.uv_layers.active.data
mesh = nin.data
# ilhas de malha (a espada e a alça são peças soltas do corpo)
parent = list(range(len(P)))
def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]; i = parent[i]
    return i
for poly in mesh.polygons:
    vs = list(poly.vertices)
    for q in vs[1:]:
        parent[find(q)] = find(vs[0])
island = [find(i) for i in range(len(P))]
from collections import Counter
isl_size = Counter(island)
if debug:
    for root_i, n in isl_size.most_common(12):
        ids = [i for i in range(len(P)) if island[i] == root_i]
        print("ISLAND", n, np.round(P[ids].min(axis=0), 2), np.round(P[ids].max(axis=0), 2))
_fc = np.array([np.mean(P[list(q.vertices)], axis=0) for q in mesh.polygons])
_sel = (abs(_fc[:, 0]) < 0.25) & (_fc[:, 2] > 0.9)
_bins = {}
for _b in range(18, 36):
    _m = _sel & (_fc[:, 2] >= _b * 0.05) & (_fc[:, 2] < (_b + 1) * 0.05)
    if _m.sum() > 10:
        _bins[_b] = float(np.percentile(_fc[_m, 1], 82))
def back_surface(z):
    k = min(_bins, key=lambda b: abs(b - z / 0.05)) if _bins else 0
    return _bins.get(k, 0.12)
face_class = []
for poly in mesh.polygons:
    u = np.mean([uv[l].uv[0] for l in poly.loop_indices]); w = np.mean([uv[l].uv[1] for l in poly.loop_indices])
    r, g, b = px[min(2047, max(0, int(w * 2048))), min(2047, max(0, int(u * 2048)))]
    sat = (max(r, g, b) - min(r, g, b)) / (max(r, g, b) + 1e-6)
    cx, cy, cz = np.mean(P[list(poly.vertices)], axis=0)
    skin = r > 0.4 and r > g >= b * 0.95 and 0.12 < sat <= 0.62 and (cz < 1.5 or cy < 0)  # (no capuz, só o rosto da frente é pele)
    sash = r > 0.15 and r > g >= b * 0.8 and sat > 0.62 and g < 0.5 * r
    boots = cz < 0.38  # botas e faixas das pernas
    gloves = abs(cx) > 0.52  # faixas, luvas e mãos (a partir do cotovelo)
    sword = abs(cx) < 0.25 and cz > 0.9 and cy > back_surface(cz) + 0.022  # a espada e a alça, soltas atrás das costas
    # só o tecido azul (casaco, calça, capuz e mangas) muda de cor; o resto fica como é no modelo
    face_class.append(1 if (skin or sash or boots or gloves or sword) else 0)
# slot de cada face (peso dominante dos vértices)
def slot_of(poly):
    acc = {}
    for vi in poly.vertices:
        for j in np.nonzero(W[vi])[0]:
            acc[names[j]] = acc.get(names[j], 0) + W[vi, j]
    top = max(acc, key=acc.get)
    base = top.rsplit("_", 1)[0] if top.endswith(("_l", "_r")) else top
    if base in ("Head", "neck_01"):
        return "Head"
    if base in ("lowerarm", "hand"):
        return "Hands"
    if base in ("calf", "foot", "ball"):
        return "Feet"
    return "Body"
face_slot = [slot_of(p) for p in mesh.polygons]

print("CLASSES", {k: face_class.count(k) for k in (0, 1)}, {k: face_slot.count(k) for k in ("Head", "Hands", "Feet", "Body")})
# texturas e materiais
grey = np.dot(px, [0.299, 0.587, 0.114])
grey = np.clip(grey / (np.percentile(grey, 90) + 1e-6) * 0.85, 0, 1)
gimg = bpy.data.images.new("ninja_cloth", 2048, 2048)
gimg.pixels = np.dstack([grey, grey, grey, np.ones_like(grey)]).astype(np.float32).ravel().tolist()
gimg.filepath_raw = os.path.join(tmp, "ninja_cloth.png"); gimg.file_format = 'PNG'; gimg.save()
img.filepath_raw = os.path.join(tmp, "ninja_color.png"); img.file_format = 'PNG'; img.save()
def material(name, image, rough=0.85):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
    t = m.node_tree.nodes.new("ShaderNodeTexImage"); t.image = image
    m.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"])
    return m
mats = [material("Ninja_Cloth", gimg), material("Ninja_Skin", img, 0.7)]
if debug:  # imagem de conferência: tingido em vermelho, o resto em azul, de frente e de costas
    import math as _m
    mesh.materials.clear()
    for col in ((0.9, 0.1, 0.1, 1), (0.1, 0.2, 0.9, 1)):
        dm = bpy.data.materials.new("dbg"); dm.diffuse_color = col; mesh.materials.append(dm)
    for i, p in enumerate(mesh.polygons):
        p.material_index = face_class[i]
    sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.color_type = 'MATERIAL'; sc.display.shading.light = 'FLAT'
    sc.render.resolution_x = 700; sc.render.resolution_y = 900
    cam = bpy.data.cameras.new("c"); co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); sc.camera = co
    cam.type = 'ORTHO'; cam.ortho_scale = 2.4
    for nm, loc, rot in (("back", (0, 6, 0.9), (_m.pi / 2, 0, _m.pi)), ("front", (0, -6, 0.9), (_m.pi / 2, 0, 0)), ("side", (6, 0, 0.9), (_m.pi / 2, 0, _m.pi / 2))):
        co.location = loc; co.rotation_euler = rot
        sc.render.filepath = os.path.join(tmp, "dbg_" + nm + ".png"); bpy.ops.render.render(write_still=True)
    sys.exit(0)
mesh.materials.clear()
for m in mats:
    mesh.materials.append(m)
for i, p in enumerate(mesh.polygons):
    p.material_index = face_class[i]
# cada face leva o slot dela: guarda em um atributo para cortar as peças
attr = mesh.attributes.new("slot", 'INT', 'FACE')
order = ["Body", "Head", "Hands", "Feet"]
for i in range(len(mesh.polygons)):
    attr.data[i].value = order.index(face_slot[i])
parts = []
for k, slot in enumerate(order):
    o = nin.copy(); o.data = nin.data.copy(); o.name = "Ninja_" + slot; bpy.context.collection.objects.link(o)
    b = bmesh.new(); b.from_mesh(o.data)
    lay = b.faces.layers.int.get("slot")
    bmesh.ops.delete(b, geom=[f for f in b.faces if f[lay] != k], context='FACES')
    b.to_mesh(o.data); b.free()
    o.parent = arm
    o.parent_type = 'OBJECT'
    md = o.modifiers.new("Armature", 'ARMATURE'); md.object = arm
    parts.append(o)
bpy.data.objects.remove(nin, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
for o in parts + keep + [arm]:
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='JPEG', export_jpeg_quality=88, export_animations=True,
                          export_animation_mode='NLA_TRACKS', export_skins=True, use_selection=True)
print("OK", dst)
