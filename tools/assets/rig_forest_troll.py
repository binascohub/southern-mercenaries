"""Troll da Floresta animado como humano: prende a malha de assets/models/monsters/forest_troll.glb (build_forest_troll.py, malha parada de 2,3 m em A-pose)
ao esqueleto dos heróis (assets/models/characters/hero_male.glb), que ganha os movimentos deles (Idle, Walk, Jog_Fwd, Punch_Cross, Hit_Chest e Death01 no Godot).
Mesmo método de build_barbarian_monster.py (pesos de cápsula e braços da A-pose levados à T-pose), mas aqui o esqueleto é que se ajusta ao troll, que é bem
diferente de um humano: pernas curtas (quadril a 0,6 m), tronco alto, ombro a 1,55 m e largo (0,62 m do centro), braços compridos. Cada osso é levado
ao lugar certo no troll sem mudar de direção, então as animações dos heróis continuam valendo. A malha só muda nos braços (para a T-pose).
uso: blender -b -P tools/assets/rig_forest_troll.py -- <forest_troll.glb> <hero_male.glb> <saída.glb>"""
import bpy, sys, math
import numpy as np
from mathutils import Vector

src, hero_path, dst = sys.argv[sys.argv.index("--") + 1:][:3]
KEEP = ("Idle_Loop", "Walk_Loop", "Jog_Fwd_Loop", "Punch_Cross", "Hit_Chest", "Death01")
# Medidas do troll (m, no arquivo): ombro, ângulo do braço abaixo da horizontal (medido na malha: 61 a 65 graus), comprimento do braço até o fim da mão.
SHOULDER = Vector((0.62, 0.0, 1.55))
THETA = math.radians(63.0)
ARM_LEN = 0.87
LEG_X = 0.27
# Altura (z) do herói -> do troll, por trechos: tornozelo, joelho, quadril, ombro, pescoço, cabeça.
Z_HERO = [0.0, 0.104, 0.532, 0.932, 1.441, 1.569, 1.651, 1.8]
Z_TROLL = [0.0, 0.08, 0.30, 0.60, 1.55, 1.95, 2.15, 2.3]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
body = [o for o in bpy.data.objects if o.type == 'MESH'][0]
body.parent = None
bpy.context.view_layer.update()
body.data.transform(body.matrix_world)
body.matrix_world.identity()
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


def chain(root_name):
    root = arm.data.bones[root_name]
    return {root.name} | {b.name for b in root.children_recursive}


ARM_BONES = {1: chain("upperarm_l"), -1: chain("upperarm_r")}
LEG_BONES = {1: chain("thigh_l"), -1: chain("thigh_r")}
hero_sh = arm.data.bones["upperarm_l"].head_local.copy()
hero_hand = arm.data.bones["hand_l"].tail_local.copy()
arm_k = ARM_LEN / (hero_hand.x - hero_sh.x + 0.15)  # + os dedos


def to_troll(p, name):
    z = float(np.interp(p.z, Z_HERO, Z_TROLL)) if p.z <= Z_HERO[-1] else Z_TROLL[-1] + (p.z - Z_HERO[-1])
    for side in (1, -1):
        if name in ARM_BONES[side]:
            return Vector((side * (SHOULDER.x + (side * p.x - hero_sh.x) * arm_k), p.y, SHOULDER.z + (p.z - hero_sh.z)))
        if name in LEG_BONES[side]:
            return Vector((side * (LEG_X + (side * p.x - 0.089) * 1.5), p.y * 1.5, z))
    return Vector((p.x * 1.5, p.y, z))


bpy.context.view_layer.objects.active = arm
for o in bpy.data.objects:
    o.select_set(o is arm)
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones
spots = {b.name: (to_troll(b.head, b.name), to_troll(b.tail, b.name)) for b in eb}
for side, name in ((1, "clavicle_l"), (-1, "clavicle_r")):  # a clavícula vai do tronco até o ombro do troll
    spots[name] = (spots[name][0], Vector((side * (SHOULDER.x - 0.02), eb[name].tail.y, SHOULDER.z)))
for b in eb:
    b.use_connect = False
for b in eb:
    roll = b.roll
    b.head, b.tail = spots[b.name]
    b.roll = roll
bpy.ops.object.mode_set(mode='OBJECT')
bones = {b.name: (Vector(b.head_local), Vector(b.tail_local)) for b in arm.data.bones}


def a_pose(p, side):
    """Ponto da T-pose levado à A-pose do troll (gira em volta do ombro)."""
    dx = (p.x - side * SHOULDER.x) * side
    dz = p.z - SHOULDER.z
    c, s = math.cos(THETA), math.sin(THETA)
    return Vector((side * (SHOULDER.x + dx * c + dz * s), p.y, SHOULDER.z - dx * s + dz * c))


RAD = {"pelvis": .42, "spine_01": .42, "spine_02": .45, "spine_03": .45, "neck_01": .22, "Head": .22, "clavicle": .2, "upperarm": .17, "lowerarm": .16,
       "hand": .15, "thigh": .17, "calf": .14, "foot": .14, "ball": .12}
caps = []
for name in list(bones):
    base = name.rsplit("_", 1)[0] if name.endswith(("_l", "_r")) else name
    if base not in RAD:
        continue
    h, t = bones[name]
    if base == "hand":
        t = h + (t - h).normalized() * 0.25
    if base in ("upperarm", "lowerarm", "hand"):
        side = 1 if name.endswith("_l") else -1
        h, t = a_pose(h, side), a_pose(t, side)
    caps.append((name, h, t, RAD[base]))
P = np.array([tuple(x.co) for x in body.data.vertices])
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
# Braços para a T-pose (o que pesa no braço gira em volta do ombro).
c, s = math.cos(THETA), math.sin(THETA)
for side, chain_names in ((1, ("upperarm_l", "lowerarm_l", "hand_l")), (-1, ("upperarm_r", "lowerarm_r", "hand_r"))):
    idx = [names.index(n) for n in chain_names]
    wa = W[:, idx].sum(axis=1)
    dx = (P[:, 0] - side * SHOULDER.x) * side
    dz = P[:, 2] - SHOULDER.z
    nx = dx * c - dz * s
    nz = dx * s + dz * c
    P[:, 0] = np.where(wa > 0, P[:, 0] * (1 - wa) + (side * SHOULDER.x + side * nx) * wa, P[:, 0])
    P[:, 2] = np.where(wa > 0, P[:, 2] * (1 - wa) + (SHOULDER.z + nz) * wa, P[:, 2])
for i, vert in enumerate(body.data.vertices):
    vert.co = Vector(P[i])
for nme in names:
    body.vertex_groups.new(name=nme)
for i in range(len(P)):
    for j in np.nonzero(W[i])[0]:
        body.vertex_groups[names[j]].add([i], float(W[i, j]), 'REPLACE')
body.name = "Forest_Troll_Body"
body.parent = arm
md = body.modifiers.new("Armature", 'ARMATURE')
md.object = arm
for o in bpy.data.objects:
    o.select_set(o in (body, arm))
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
                          export_animation_mode='NLA_TRACKS', export_skins=True, use_selection=True)
print("OK", dst)
