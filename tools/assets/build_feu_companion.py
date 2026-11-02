"""Feu (feu.glb enviado pelo autor do projeto: diabinho de fogo bípede, cabeça grande, em A-pose de 0,45 m, malha parada de 24 mil vértices, autor/licença a confirmar),
companheiro de Fogo do Invocador: ligado ao esqueleto e às animações dos heróis (assets/models/characters/hero_male.glb), então anda, corre e luta com os mesmos movimentos dos homens.
Gera assets/models/props/Feu.glb: uma peça só (Feu_Body, textura original) mais o esqueleto e as animações do herói (sem as peças do herói).
As proporções dele (pernas curtas, cabeça enorme) não são as do esqueleto: a altura é remapeada em trechos (pés, quadril, ombro, topo da cabeça) e a largura ampliada 4x;
o braço sai da A-pose (55 graus) para a T-pose do esqueleto. O jogo reduz o corpo até o tamanho do Feu (model_scale em data/companions.json). Mesmo método de build_werefeu_companion.py.
uso: blender -b -P tools/assets/build_feu_companion.py -- <feu.glb> <hero_male.glb> <saida.glb>"""
import bpy, bmesh, sys, math
import numpy as np
from mathutils import Vector

src, hero_path, dst = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
# 1) o Feu (malha estática); aplica a transformação do arquivo na malha
bpy.ops.import_scene.gltf(filepath=src)
feu = [o for o in bpy.data.objects if o.type == 'MESH'][0]
feu.parent = None
bpy.context.view_layer.update()
feu.data.transform(feu.matrix_world)
feu.matrix_world = feu.matrix_world.__class__.Identity(4)
# 2) o herói: só o esqueleto e as animações ficam
bpy.ops.import_scene.gltf(filepath=hero_path)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o is not feu:
        bpy.data.objects.remove(o, do_unlink=True)
bones = {b.name: (Vector(b.head_local), Vector(b.tail_local)) for b in arm.data.bones}
bpy.context.view_layer.objects.active = feu
feu.select_set(True)
bm = bmesh.new(); bm.from_mesh(feu.data); bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.to_mesh(feu.data); bm.free()
for im in bpy.data.images:
    if im.size[0] > 2048 or im.size[1] > 2048:
        im.scale(2048, 2048)
# 3) pés em z = 0, braço: eixo do braço (PCA) dá o ângulo da A-pose; a escala põe o ombro na altura do esqueleto
v = np.array([tuple(x.co) for x in feu.data.vertices])
v[:, 2] -= v[:, 2].min()
sh = bones["upperarm_l"][0]
theta = math.radians(55.0)  # o braço pende ~55° abaixo da horizontal (A-pose)
# altura em trechos: pés 0, quadril 0,13, ombro 0,29, topo 0,45 (m, no arquivo) -> 0, 0,85, 1,42, 1,86 (m, no esqueleto); largura e profundidade x4
top = float(v[:, 2].max())
v[:, 2] = np.interp(v[:, 2], [0.0, 0.13, 0.29, top], [0.0, 0.85, 1.42, 1.86])
v[:, 0] *= 4.0
v[:, 1] *= 4.0
print("HEIGHT", v[:, 2].max(), "arm reach", v[:, 0].max())
torso = (v[:, 2] > 0.9) & (v[:, 2] < 1.3) & (abs(v[:, 0]) < 0.2)
v[:, 1] -= np.median(v[torso, 1]) - bones["spine_02"][0].y


def a_pose(p, side):
    d = p - Vector((side * sh.x, sh.y, sh.z))
    c, sn = math.cos(theta), math.sin(theta)
    return Vector((side * sh.x + side * (d.x * side * c + d.z * sn), p.y, sh.z + (-d.x * side * sn + d.z * c)))


RAD = {"pelvis": .35, "spine_01": .33, "spine_02": .33, "spine_03": .3, "neck_01": .2, "Head": .4, "clavicle": .12, "upperarm": .13, "lowerarm": .12,
       "hand": .12, "thigh": .2, "calf": .15, "foot": .13, "ball": .1}
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
for i, vert in enumerate(feu.data.vertices):
    vert.co = Vector(P[i])
for n in names:
    feu.vertex_groups.new(name=n)
for i in range(len(P)):
    for j in np.nonzero(W[i])[0]:
        feu.vertex_groups[names[j]].add([i], float(W[i, j]), 'REPLACE')
feu.name = "Feu_Body"
feu.parent = arm
md = feu.modifiers.new("Armature", 'ARMATURE'); md.object = arm
bpy.ops.object.select_all(action='DESELECT')
for o in (feu, arm):
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
                          export_animation_mode='NLA_TRACKS', export_skins=True, use_selection=True)
print("OK", dst)
