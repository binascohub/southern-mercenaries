"""Guardião do Portão (horror-monster-light.glb enviado pelo autor do projeto: monstro de terror magro e bípede, 2,2 m, braços caídos, malha estática de 400 mil polígonos e 2 texturas;
autor/licença a confirmar): o NPC que recebe as duas chaves do Esgoto e faz o portão do Ninho cair. Preso ao esqueleto dos heróis (assets/models/characters/hero_male.glb) por pesos de cápsula, com os
braços (quase verticais, 77 graus abaixo da horizontal) levados à T-pose do esqueleto, então anda, corre e luta com os movimentos dos humanos. Ficam 6 animações dos heróis, que o Godot importa como
Idle, Walk, Jog_Fwd, Punch_Cross, Hit_Chest e Death01. A malha é reduzida (~40 mil triângulos), as texturas vão a 1024 px, o ombro cai a 1,44 m (o do esqueleto) e os pés ficam em z = 0 (no jogo o
NpcModel a amplia de volta para ~2,2 m). Gera assets/models/characters/gate_keeper.glb. Mesmo método de build_barbarian_monster.py.
uso: blender -b -P tools/assets/build_horror_monster.py -- <horror-monster-light.glb> <hero_male.glb> <saida.glb>"""
import bpy, bmesh, sys, math
import numpy as np
from mathutils import Vector, Matrix

src, hero_path, dst = sys.argv[sys.argv.index("--") + 1:][:3]
KEEP = ("Idle_Loop", "Walk_Loop", "Jog_Fwd_Loop", "Punch_Cross", "Hit_Chest", "Death01")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
body = [o for o in bpy.data.objects if o.type == 'MESH'][0]
body.parent = None
bpy.context.view_layer.update()
body.data.transform(body.matrix_world)
body.matrix_world = Matrix.Identity(4)
bpy.ops.import_scene.gltf(filepath=hero_path)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o is not body:
        bpy.data.objects.remove(o, do_unlink=True)
if arm.animation_data:
    for track in list(arm.animation_data.nla_tracks):
        if not track.strips or track.strips[0].action.name not in KEEP:
            arm.animation_data.nla_tracks.remove(track)
for a in list(bpy.data.actions):
    if a.name not in KEEP:
        bpy.data.actions.remove(a)
print("ANIMAÇÕES", sorted(a.name for a in bpy.data.actions))
bones = {b.name: (Vector(b.head_local), Vector(b.tail_local)) for b in arm.data.bones}
for o in bpy.data.objects:
    o.select_set(o is body)
bpy.context.view_layer.objects.active = body
mod = body.modifiers.new("d", 'DECIMATE')
mod.ratio = 40000 / max(1, len(body.data.polygons))
bpy.ops.object.modifier_apply(modifier="d")
bm = bmesh.new(); bm.from_mesh(body.data); bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.to_mesh(body.data); bm.free()
for im in bpy.data.images:
    if im.size[0] > 1024 or im.size[1] > 1024:
        im.scale(1024, 1024)
print("POLÍGONOS", len(body.data.polygons))

# pés em z = 0; o braço (A-pose) é medido na malha; a escala põe o ombro (1,55 m no arquivo) na altura do esqueleto (1,44 m)
v = np.array([tuple(x.co) for x in body.data.vertices])
v[:, 2] -= v[:, 2].min()
sh = bones["upperarm_l"][0]
theta = math.radians(77.0)  # os braços pendem quase na vertical (do ombro à ponta da mão: ~0,2 m para fora e ~0,9 m para baixo)
top = float(np.percentile(v[:, 2], 99.9))
k = 1.44 / (0.795 * top)  # o ombro do monstro fica a ~79% da altura; a escala põe o ombro na altura do esqueleto (1,44 m)
print("ÂNGULO DO BRAÇO", round(math.degrees(theta), 1), "escala", round(k, 3), "altura no arquivo", round(top, 3))
v *= k
v[:, 2] -= v[:, 2].min()
torso = (v[:, 2] > 0.9) & (v[:, 2] < 1.3) & (abs(v[:, 0]) < 0.2)
v[:, 1] -= np.median(v[torso, 1]) - bones["spine_02"][0].y


def a_pose(p, side):
    dd = p - Vector((side * sh.x, sh.y, sh.z))
    c, sn = math.cos(theta), math.sin(theta)
    return Vector((side * sh.x + side * (dd.x * side * c + dd.z * sn), p.y, sh.z + (-dd.x * side * sn + dd.z * c)))


RAD = {"pelvis": .16, "spine_01": .15, "spine_02": .15, "spine_03": .15, "neck_01": .07, "Head": .12, "clavicle": .07, "upperarm": .07, "lowerarm": .06,
       "hand": .06, "thigh": .09, "calf": .07, "foot": .06, "ball": .05}  # o monstro é bem mais magro que os heróis
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
    ab = np.array(t - h)
    L2 = float(ab @ ab) + 1e-9
    u = np.clip(((P - np.array(h)) @ ab) / L2, 0, 1)
    dist = np.linalg.norm(P - (np.array(h) + u[:, None] * ab), axis=1)
    D[:, i] = np.maximum(dist - r, 0) + 0.004
W = (D.min(axis=1, keepdims=True) / D) ** 6
W[W < 0.04] = 0
drop = np.argsort(-W, axis=1)[:, 4:]
np.put_along_axis(W, drop, 0, axis=1)
W /= W.sum(axis=1, keepdims=True)
names = [c[0] for c in caps]
c, sn = math.cos(theta), math.sin(theta)
arm_idx = {1: [names.index(n) for n in ("upperarm_l", "lowerarm_l", "hand_l")], -1: [names.index(n) for n in ("upperarm_r", "lowerarm_r", "hand_r")]}
for side, idx in arm_idx.items():
    wa = W[:, idx].sum(axis=1)
    dx = (P[:, 0] - side * sh.x) * side
    dz = P[:, 2] - sh.z
    nx = dx * c - dz * sn
    nz = dx * sn + dz * c
    P[:, 0] = np.where(wa > 0, P[:, 0] * (1 - wa) + (side * sh.x + side * nx) * wa, P[:, 0])
    P[:, 2] = np.where(wa > 0, P[:, 2] * (1 - wa) + (sh.z + nz) * wa, P[:, 2])
for i, vert in enumerate(body.data.vertices):
    vert.co = Vector(P[i])
for nme in names:
    body.vertex_groups.new(name=nme)
for i in range(len(P)):
    for j in np.nonzero(W[i])[0]:
        body.vertex_groups[names[j]].add([i], float(W[i, j]), 'REPLACE')
body.name = "GateKeeper_Body"
body.parent = arm
md = body.modifiers.new("Armature", 'ARMATURE')
md.object = arm
for o in bpy.data.objects:
    o.select_set(o in (body, arm))
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
                          export_animation_mode='NLA_TRACKS', export_skins=True, use_selection=True)
print("OK", dst)
