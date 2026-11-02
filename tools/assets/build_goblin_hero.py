"""Roupa do Invocador (goblin.glb enviado pelo autor do projeto, goblin estático em A-pose de 1,1 m, autor/licença a confirmar), ligada ao esqueleto e às
animações do herói masculino (assets/models/characters/hero_male.glb): gera assets/models/characters/hero_goblin.glb, uma peça só (Goblin_Body) com 2 materiais por recorte de alfa:
 0 o que é amarelo/laranja (o casaco): textura em tons de cinza, tingida no jogo pela cor do elemento;
 1 o resto (couro, calça, remendos azuis, pele, orelhas, óculos): textura original, sem tingir.
O modelo é ampliado ~2,05x para o ombro cair no do esqueleto do herói; o jogo reduz o corpo (HeroModel.SUIT_SCALE) para o goblin voltar ao tamanho dele.
Mesmo método de build_dwarf_hero.py.
uso: blender -b -P tools/assets/build_goblin_hero.py -- <goblin.glb> <hero_male.glb> <saida.glb>"""
import bpy, bmesh, sys, math, os
import numpy as np
from mathutils import Vector

args = [a for a in sys.argv[sys.argv.index("--") + 1:] if a != "--debug"]
src, hero_path, dst = args
debug = "--debug" in sys.argv
tmp = os.path.expanduser("~/.cache/sm-animalkit/ninja")
bpy.ops.wm.read_factory_settings(use_empty=True)
# 1) o modelo da elfa (malha estática)
bpy.ops.import_scene.gltf(filepath=src)
elf_obj = [o for o in bpy.data.objects if o.type == 'MESH'][0]
elf_obj.parent = None
nin = elf_obj
img = [i for i in bpy.data.images if i.size[0] > 0][0]
# 2) o herói: fica o Camponês, o rosto e os cabelos
bpy.ops.import_scene.gltf(filepath=hero_path)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
keep = []
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o is not nin and o.name != nin.name:
        if o.name in ("Head", "Eyes", "Eyebrows") or o.name.startswith(("Hair", "Peasant_")):
            keep.append(o)
        else:
            bpy.data.objects.remove(o, do_unlink=True)
bones = {b.name: (Vector(b.head_local), Vector(b.tail_local)) for b in arm.data.bones}
bpy.context.view_layer.objects.active = nin
nin.select_set(True)
mod = nin.modifiers.new("d", 'DECIMATE'); mod.ratio = 45000 / max(1, len(nin.data.polygons)); bpy.ops.object.modifier_apply(modifier="d")
bm = bmesh.new(); bm.from_mesh(nin.data); bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.to_mesh(nin.data); bm.free()
img.scale(2048, 2048)
# alinha: altura = a do topo da cabeça do herói, pés no chão
v = np.array([tuple(x.co) for x in nin.data.vertices])
s = 2.05  # o ombro do goblin fica a ~0,7 m: ampliado para os 1,44 m do esqueleto do herói
v = v * s
v[:, 2] -= v[:, 2].min()
torso = (v[:, 2] > 0.9) & (v[:, 2] < 1.3) & (abs(v[:, 0]) < 0.2)
v[:, 1] -= np.median(v[torso, 1]) - bones["spine_02"][0].y
arm_sel = (v[:, 0] > 0.5) & (v[:, 2] > 0.85) & (v[:, 2] < 1.4)
slope = np.polyfit(v[arm_sel, 0], v[arm_sel, 2], 1)[0]
theta = math.atan(-slope)
print("ARM ANGLE", math.degrees(theta), "scale", s, "arm verts", arm_sel.sum())
sh = bones["upperarm_l"][0]
def a_pose(p, side):
    d = p - Vector((side * sh.x, sh.y, sh.z))
    c, sn = math.cos(theta), math.sin(theta)
    return Vector((side * sh.x + side * (d.x * side * c + d.z * sn), p.y, sh.z + (-d.x * side * sn + d.z * c)))
RAD = {"pelvis": .17, "spine_01": .15, "spine_02": .15, "spine_03": .14, "neck_01": .05, "Head": .1, "clavicle": .05, "upperarm": .05, "lowerarm": .04,
       "hand": .035, "thigh": .09, "calf": .06, "foot": .05, "ball": .04}
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
# faces roxas: pela cor da textura no centro da face (a textura é um mosaico de retalhos de uma cor só)
px = np.array(img.pixels[:], dtype=np.float32).reshape(2048, 2048, 4)[:, :, :3]
mesh = nin.data
# máscara por pixel do roxo (a textura é um mosaico de retalhos e as faces cruzam os retalhos): duas superfícies sobre as mesmas faces,
# cada uma com recorte de alfa; a de tecido (tons de cinza, tingida no jogo) só aparece onde é roxo, a outra (cores originais) no resto
_srgb = np.clip(px, 0, 1)  # (os pixels já vêm em sRGB)
_mx = _srgb.max(axis=2); _mn = _srgb.min(axis=2)
_sat = (_mx - _mn) / (_mx + 1e-6)
_d = np.maximum(_mx - _mn, 1e-6)
_hue = np.where(_mx == _srgb[..., 0], ((_srgb[..., 1] - _srgb[..., 2]) / _d) % 6, np.where(_mx == _srgb[..., 1], (_srgb[..., 2] - _srgb[..., 0]) / _d + 2, (_srgb[..., 0] - _srgb[..., 1]) / _d + 4)) * 60
purple = (_mx > 0.5) & (_sat > 0.68) & (_hue > 28) & (_hue < 41)  # amarelo/laranja vivo (o casaco); o couro marrom é mais escuro e a pele mais pálida
print("YELLOW PIXELS", float(purple.mean()))
def dilate(m):
    o = m.copy()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        o |= np.roll(m, (dy, dx), axis=(0, 1))
    return o
grey = np.dot(px, [0.299, 0.587, 0.114])
grey = np.clip(grey / (np.percentile(grey[purple], 70) + 1e-6) * 0.8, 0, 1)  # claro o bastante: o azul original é escuro
def save_image(name, rgb, alpha):
    im = bpy.data.images.new(name, 2048, 2048, alpha=True)
    im.pixels = np.dstack([rgb, alpha.astype(np.float32)]).astype(np.float32).ravel().tolist()
    im.alpha_mode = 'STRAIGHT'
    im.filepath_raw = os.path.join(tmp, name + ".png"); im.file_format = 'PNG'; im.save()
    return im
D = dilate(purple)
imgA = save_image("goblin_rest", px, ~D)
imgB = save_image("goblin_cloth", np.dstack([grey, grey, grey]), D)
def material(name, image, rough=0.85):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
    t = m.node_tree.nodes.new("ShaderNodeTexImage"); t.image = image
    m.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"])
    m.node_tree.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
    try:
        m.blend_method = 'CLIP'
    except Exception:
        pass
    m.alpha_threshold = 0.5
    return m
mesh.materials.clear()
for m in (material("Goblin_Cloth", imgB), material("Goblin_Rest", imgA, 0.7)):
    mesh.materials.append(m)
# as faces em dobro: a primeira cópia com o tecido, a segunda com o resto
bm = bmesh.new(); bm.from_mesh(mesh)
orig = bm.faces[:]
dup = bmesh.ops.duplicate(bm, geom=orig)
for f in dup["geom"]:
    if isinstance(f, bmesh.types.BMFace):
        f.material_index = 1
for f in orig:
    f.material_index = 0
bm.to_mesh(mesh); bm.free()
nin.name = "Goblin_Body"
nin.parent = arm
md = nin.modifiers.new("Armature", 'ARMATURE'); md.object = arm
bpy.ops.object.select_all(action='DESELECT')
for o in [nin] + keep + [arm]:
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
                          export_animation_mode='NLA_TRACKS', export_skins=True, use_selection=True)
print("OK", dst)
