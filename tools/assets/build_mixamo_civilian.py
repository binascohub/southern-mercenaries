"""Civis do Mixamo (civilian1.glb e civilian3.glb enviados pelo autor do projeto: homens do Mixamo de camisa, calça, sapatos, barba, bigode e cabelo, em T-pose, com o esqueleto do Mixamo de 66 ossos e
7 materiais de textura a 512/1024 px; autor/licença a confirmar): moradores que andam pelas ruas da Capital e de Tortuga. Aqui a malha é lida na pose de repouso (sem a esfera de apoio do arquivo), as peças viram
uma malha só (um material por textura) e prendem-se ao esqueleto dos heróis (assets/models/characters/hero_male.glb) por pesos de cápsula, com os movimentos dos humanos (Idle_Loop, Idle_Talking_Loop,
Walk_Loop). Escala para 1,78 m, pés em z = 0, de frente para -Y do Blender. (Não confundir com tools/assets/build_civilian.py, que faz a Civil de Tortuga com o rig_to_ual.py.)
Gera assets/models/characters/civilian1.glb e civilian3.glb.
uso: blender -b -P tools/assets/build_mixamo_civilian.py -- <civilianN.glb> <hero_male.glb> <saida.glb> [ângulo dos braços abaixo da horizontal em graus (0 = T-pose)] [altura em m] [pose] [animações extras, ex.: Walk_Formal_Loop,Spell_Simple_Idle_Loop]
(pula as peças "_hi_" duplicadas de baixa/alta resolução, como o cabelo do arquivo florest_quest_1.glb)"""
import bpy, sys, math
import numpy as np
from mathutils import Vector

_args = sys.argv[sys.argv.index("--") + 1:]
src, hero_path, dst = _args[:3]
ARM_DEG = float(_args[3]) if len(_args) > 3 else 0.0
HEIGHT = float(_args[4]) if len(_args) > 4 else 1.78
REST = not (len(_args) > 5 and _args[5] == "pose")  # "pose": lê a malha na pose do arquivo em vez da de repouso (alguns rigs de repouso vêm deitados)
KEEP_ANIMS = ("Idle_Loop", "Idle_Talking_Loop", "Walk_Loop") + tuple(a for a in (_args[6].split(",") if len(_args) > 6 else []) if a)  # 7º argumento: mais animações do pacote dos heróis, separadas por vírgula
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for a in bpy.data.objects:
    if a.type == 'ARMATURE':
        if REST:
            a.data.pose_position = 'REST'
        a.animation_data_clear()
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
parts = []
for o in [o for o in bpy.data.objects if o.type == 'MESH' and o.name != "Icosphere" and not any("_hi_" in (m.name if m else "") for m in o.data.materials)]:
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    mesh.transform(o.matrix_world)
    mesh.materials.clear()
    for m in o.data.materials:
        mesh.materials.append(m)
    ob = bpy.data.objects.new("P_" + o.name, mesh)
    bpy.context.scene.collection.objects.link(ob)
    parts.append(ob)
    print("PARTE", o.name, len(mesh.polygons), [m.name for m in o.data.materials])
for o in list(bpy.data.objects):
    if o not in parts:
        bpy.data.objects.remove(o, do_unlink=True)
for o in bpy.data.objects:
    o.select_set(o in parts)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "Civilian_Body"
mesh = body.data
for im in bpy.data.images:
    if im.size[0] > 1024:
        im.scale(1024, 1024)
v = np.array([tuple(p.co) for p in mesh.vertices])
print("VÉRTICES", len(v), "ALTURA", round(float(v[:, 2].max() - v[:, 2].min()), 2), "LARGURA", round(float(v[:, 0].max() - v[:, 0].min()), 2), "SUPERFÍCIES", len(mesh.materials),
      "FRENTE y do bigode/barba", round(float(np.median(v[v[:, 2] > v[:, 2].max() * 0.88][:, 1])), 2))
v[:, 0] -= (v[:, 0].min() + v[:, 0].max()) / 2
v[:, 1] -= np.median(v[:, 1])
v[:, 2] -= v[:, 2].min()
v *= HEIGHT / v[:, 2].max()

bpy.ops.import_scene.gltf(filepath=hero_path)
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o is not body:
        bpy.data.objects.remove(o, do_unlink=True)
if arm.animation_data:
    for track in list(arm.animation_data.nla_tracks):
        if not track.strips or track.strips[0].action.name not in KEEP_ANIMS:
            arm.animation_data.nla_tracks.remove(track)
for a in list(bpy.data.actions):
    if a.name not in KEEP_ANIMS:
        bpy.data.actions.remove(a)
bones = {b.name: (Vector(b.head_local), Vector(b.tail_local)) for b in arm.data.bones}
RAD = {"pelvis": .2, "spine_01": .19, "spine_02": .19, "spine_03": .19, "neck_01": .08, "Head": .14, "clavicle": .08, "upperarm": .075, "lowerarm": .065,
       "hand": .07, "thigh": .13, "calf": .1, "foot": .08, "ball": .06}
sh = bones["upperarm_l"][0]
theta = math.radians(ARM_DEG)


def a_pose(p, side):
    """Leva um ponto do braço da T-pose do esqueleto à pose de braços caídos do modelo (rotação em torno do ombro)."""
    dd = p - Vector((side * sh.x, sh.y, sh.z))
    c, sn = math.cos(theta), math.sin(theta)
    return Vector((side * sh.x + side * (dd.x * side * c + dd.z * sn), p.y, sh.z + (-dd.x * side * sn + dd.z * c)))


caps = []
for name in list(bones):
    base = name.rsplit("_", 1)[0] if name.endswith(("_l", "_r")) else name
    if base not in RAD:
        continue
    h, t = bones[name]
    if base == "hand":
        t = h + (t - h).normalized() * 0.2
    if ARM_DEG > 0 and base in ("upperarm", "lowerarm", "hand"):
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
# Vestido longo (o material "material" abaixo do quadril): pesos mais suaves entre as pernas, para a saia não rasgar ao andar.
dress_mat = [i for i, m in enumerate(mesh.materials) if m and m.name == "material"]
if dress_mat:
    vert_mat = np.full(len(P), -1)
    for poly in mesh.polygons:
        for vi in poly.vertices:
            vert_mat[vi] = poly.material_index
    skirt = np.isin(vert_mat, dress_mat) & (P[:, 2] < 0.85)
    W[skirt] = (D[skirt].min(axis=1, keepdims=True) / D[skirt]) ** 2
    print("VÉRTICES DE SAIA", int(skirt.sum()))
W[W < 0.04] = 0
drop = np.argsort(-W, axis=1)[:, 4:]
np.put_along_axis(W, drop, 0, axis=1)
W /= W.sum(axis=1, keepdims=True)
names = [c[0] for c in caps]
if ARM_DEG > 0:  # os vértices dos braços giram de volta para a T-pose do esqueleto (como o Monstro Bárbaro)
    c, sn = math.cos(theta), math.sin(theta)
    for side, idx in {1: [names.index(n) for n in ("upperarm_l", "lowerarm_l", "hand_l")], -1: [names.index(n) for n in ("upperarm_r", "lowerarm_r", "hand_r")]}.items():
        wa = W[:, idx].sum(axis=1)
        dx = (P[:, 0] - side * sh.x) * side
        dz = P[:, 2] - sh.z
        nx = dx * c - dz * sn
        nz = dx * sn + dz * c
        P[:, 0] = np.where(wa > 0, P[:, 0] * (1 - wa) + (side * sh.x + side * nx) * wa, P[:, 0])
        P[:, 2] = np.where(wa > 0, P[:, 2] * (1 - wa) + (sh.z + nz) * wa, P[:, 2])
for i, vert in enumerate(mesh.vertices):
    vert.co = Vector(P[i])
for nme in names:
    body.vertex_groups.new(name=nme)
for i in range(len(P)):
    for j in np.nonzero(W[i])[0]:
        body.vertex_groups[names[j]].add([i], float(W[i, j]), 'REPLACE')
while mesh.color_attributes:
    mesh.color_attributes.remove(mesh.color_attributes[0])
body.parent = arm
md = body.modifiers.new("Armature", 'ARMATURE')
md.object = arm
for o in bpy.data.objects:
    o.select_set(o in (body, arm))
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True, use_selection=True)
print("OK", dst)
