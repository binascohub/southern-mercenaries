"""Lobo (werewolf.glb enviado pelo autor do projeto, lobisomem bípede em A-pose de 2,2 m, autor/licença a confirmar), companheiro de Água do Invocador:
ligado ao esqueleto e às animações dos heróis (assets/models/characters/hero_male.glb), então anda, corre e ataca com os mesmos movimentos dos homens.
Gera assets/models/props/Werewolf.glb: uma peça só (Werewolf_Body, ~45 mil triângulos, textura original) mais o esqueleto e as animações do herói (sem as peças do herói).
A malha é reduzida (Decimate), o braço sai da A-pose para a T-pose do esqueleto e o corpo é dimensionado para o ombro cair no do esqueleto (1,44 m);
o jogo reduz o corpo até o tamanho do lobo (model_scale em data/companions.json). Mesmo método de build_goblin_hero.py.
uso: blender -b -P tools/assets/build_werewolf_companion.py -- <werewolf.glb> <hero_male.glb> <saida.glb>"""
import bpy, bmesh, sys, math
import numpy as np
from mathutils import Vector

src, hero_path, dst = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
# 1) o lobo (malha estática); aplica a transformação do arquivo na malha
bpy.ops.import_scene.gltf(filepath=src)
wolf = [o for o in bpy.data.objects if o.type == 'MESH'][0]
wolf.parent = None
bpy.context.view_layer.update()
wolf.data.transform(wolf.matrix_world)
wolf.matrix_world = wolf.matrix_world.__class__.Identity(4)
# 2) o herói: só o esqueleto e as animações ficam
bpy.ops.import_scene.gltf(filepath=hero_path)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o is not wolf:
        bpy.data.objects.remove(o, do_unlink=True)
bones = {b.name: (Vector(b.head_local), Vector(b.tail_local)) for b in arm.data.bones}
bpy.context.view_layer.objects.active = wolf
wolf.select_set(True)
mod = wolf.modifiers.new("d", 'DECIMATE')
mod.ratio = 45000 / max(1, len(wolf.data.polygons))
bpy.ops.object.modifier_apply(modifier="d")
bm = bmesh.new(); bm.from_mesh(wolf.data); bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.to_mesh(wolf.data); bm.free()
for im in bpy.data.images:
    if im.size[0] > 2048 or im.size[1] > 2048:
        im.scale(2048, 2048)
# 3) pés em z = 0, braço: eixo do braço (PCA) dá o ângulo da A-pose; a escala põe o ombro na altura do esqueleto
v = np.array([tuple(x.co) for x in wolf.data.vertices])
v[:, 2] -= v[:, 2].min()
sh = bones["upperarm_l"][0]
arm_sel = (v[:, 0] > 0.52) & (v[:, 2] > 0.6) & (v[:, 2] < 1.5)  # só o antebraço e a mão (sem ombro nem juba)
pts = v[arm_sel][:, [0, 2]]
mean = pts.mean(axis=0)
d = np.linalg.svd(pts - mean)[2][0]
if d[0] < 0:
    d = -d
theta = math.radians(70.0)  # o braço de cima pende ~70° abaixo da horizontal (o antebraço, ~80°: medido por PCA no antebraço: ver o log)
measured = math.degrees(math.atan2(-d[1], d[0]))
k = 0.82  # o ombro do lobo fica a ~1,75 m dos 2,2 m: ampliado/reduzido para cair nos 1,44 m do esqueleto do herói
print("ARM ANGLE", measured, "scale", k, "arm verts", int(arm_sel.sum()))
v *= k
v[:, 2] -= v[:, 2].min()
torso = (v[:, 2] > 0.9) & (v[:, 2] < 1.3) & (abs(v[:, 0]) < 0.2)
v[:, 1] -= np.median(v[torso, 1]) - bones["spine_02"][0].y


def a_pose(p, side):
    d = p - Vector((side * sh.x, sh.y, sh.z))
    c, sn = math.cos(theta), math.sin(theta)
    return Vector((side * sh.x + side * (d.x * side * c + d.z * sn), p.y, sh.z + (-d.x * side * sn + d.z * c)))


RAD = {"pelvis": .22, "spine_01": .2, "spine_02": .2, "spine_03": .19, "neck_01": .09, "Head": .15, "clavicle": .08, "upperarm": .09, "lowerarm": .075,
       "hand": .06, "thigh": .13, "calf": .09, "foot": .07, "ball": .06}
caps = []
for name in list(bones):
    base = name.rsplit("_", 1)[0] if name.endswith(("_l", "_r")) else name
    if base not in RAD:
        continue
    h, t = bones[name]
    if base == "hand":
        t = h + (t - h).normalized() * 0.2
    if base in ("upperarm", "lowerarm", "hand"):
        side = 1 if name.endswith("_l") else -1
        h, t = a_pose(h, side), a_pose(t, side)
    caps.append((name, h, t, RAD[base]))
P = v
D = np.zeros((len(P), len(caps)))
for i, (name, h, t, r) in enumerate(caps):
    ab = np.array(t - h); L2 = float(ab @ ab) + 1e-9
    u = np.clip(((P - np.array(h)) @ ab) / L2, 0, 1)
    dist = np.linalg.norm(P - (np.array(h) + u[:, None] * ab), axis=1)
    D[:, i] = np.maximum(dist - r, 0) + 0.004
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
for i, vert in enumerate(wolf.data.vertices):
    vert.co = Vector(P[i])
for n in names:
    wolf.vertex_groups.new(name=n)
for i in range(len(P)):
    for j in np.nonzero(W[i])[0]:
        wolf.vertex_groups[names[j]].add([i], float(W[i, j]), 'REPLACE')
wolf.name = "Werewolf_Body"
wolf.parent = arm
md = wolf.modifiers.new("Armature", 'ARMATURE'); md.object = arm
bpy.ops.object.select_all(action='DESELECT')
for o in (wolf, arm):
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
                          export_animation_mode='NLA_TRACKS', export_skins=True, use_selection=True)
print("OK", dst)
