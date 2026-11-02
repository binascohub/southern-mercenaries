"""Itachi (itachi.blend enviado pelo autor do projeto: malha estática "RogueShadowNinja" do Mixamo, em T-pose, 146 mil polígonos, 1 m de altura no arquivo e SEM a textura, que
ficou fora do arquivo; autor/licença a confirmar), NPC do Caçador de Pragas do Esgoto: preso ao esqueleto dos heróis (assets/models/characters/hero_male.glb) por pesos de cápsula,
então fala e espera com os movimentos dos humanos (Idle_Loop, Idle_Talking_Loop, Idle_FoldArms_Loop, Walk_Loop).
Sem a textura original, a cor vem de uma pintura por vértice feita aqui, pela posição no corpo: capa preta da Akatsuki com nuvens vermelhas de borda clara, pele nas mãos e no rosto,
cabelo preto, sandálias escuras. A malha é reduzida (Decimate, ~40 mil polígonos), de frente para -Y do Blender (+Z do glTF), com 1,82 m (o ombro cai a 1,44 m, o do esqueleto) e os pés em z = 0.
Gera assets/models/characters/itachi.glb.
uso: blender -b -P tools/assets/build_itachi_npc.py -- <itachi.blend> <hero_male.glb> <saida.glb>"""
import bpy, sys, math
import numpy as np
from mathutils import Vector, Matrix

src, hero_path, dst = sys.argv[sys.argv.index("--") + 1:][:3]
HEIGHT = 1.82
KEEP_ANIMS = ("Idle_Loop", "Idle_Talking_Loop", "Idle_FoldArms_Loop", "Walk_Loop")
bpy.ops.wm.open_mainfile(filepath=src)
body = next(o for o in bpy.data.objects if o.type == 'MESH')
for o in list(bpy.data.objects):
    if o is not body:
        bpy.data.objects.remove(o, do_unlink=True)
body.parent = None
body.modifiers.clear()
bpy.context.view_layer.update()
body.data.transform(body.matrix_world)
body.matrix_world = Matrix.Identity(4)
while body.data.color_attributes:
    body.data.color_attributes.remove(body.data.color_attributes[0])
for im in list(bpy.data.images):
    bpy.data.images.remove(im)

# Mixamo: a frente é +X depois da conversão do arquivo; gira -90 graus em Z para a frente ir para -Y (os braços ficam ao longo de X, como no esqueleto dos heróis)
body.data.transform(Matrix.Rotation(math.radians(-90), 4, "Z"))
v = np.array([tuple(p.co) for p in body.data.vertices])
feet = v[v[:, 2] < 0.03]
ankle = v[(v[:, 2] > 0.07) & (v[:, 2] < 0.12)]
print("FRENTE (dedos devem estar em y menor que o tornozelo):", round(float(feet[:, 1].mean()), 3), "<", round(float(ankle[:, 1].mean()), 3))
if feet[:, 1].mean() > ankle[:, 1].mean():
    body.data.transform(Matrix.Rotation(math.radians(180), 4, "Z"))
    v = np.array([tuple(p.co) for p in body.data.vertices])
v[:, 0] -= (v[:, 0].min() + v[:, 0].max()) / 2
v[:, 1] -= (v[:, 1].min() + v[:, 1].max()) / 2
v[:, 2] -= v[:, 2].min()
v *= HEIGHT / v[:, 2].max()
for i, p in enumerate(body.data.vertices):
    p.co = Vector(v[i])

# malha mais leve
for o in bpy.data.objects:
    o.select_set(o is body)
bpy.context.view_layer.objects.active = body
mod = body.modifiers.new("dec", 'DECIMATE')
mod.ratio = 40000 / max(1, len(body.data.polygons))
bpy.ops.object.modifier_apply(modifier="dec")
print("POLYS", len(body.data.polygons), "VERTS", len(body.data.vertices))
v = np.array([tuple(p.co) for p in body.data.vertices])
print("ALTURA", round(float(v[:, 2].max()), 3), "ALCANCE DOS BRAÇOS", round(float(abs(v[:, 0]).max()), 3))


# --- pintura por vértice -------------------------------------------------------------------------------------------------------------------------
def _hash(ix, iy, iz):
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def vnoise(p):
    base = np.floor(p).astype(np.int64)
    f = p - base
    f = f * f * (3 - 2 * f)
    out = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                out = out + w * _hash(base[:, 0] + dx, base[:, 1] + dy, base[:, 2] + dz)
    return out


def fbm(p, octaves=3):
    total, amp, freq, norm = 0.0, 0.5, 1.0, 0.0
    for _ in range(octaves):
        total = total + amp * vnoise(p * freq)
        norm += amp
        amp *= 0.5
        freq *= 2.1
    return total / norm


x, y, z = v[:, 0], v[:, 1], v[:, 2]
n = len(v)
cloak = np.tile(np.array([0.028, 0.028, 0.036]), (n, 1))
cloak *= (0.75 + 0.5 * fbm(v * 9.0 + 2.0))[:, None]  # dobras do tecido
# nuvens vermelhas da Akatsuki: blobs onde o ruído passa de um nível; borda clara em volta
cloud_noise = fbm(v * 6.0 + 7.3, 2)
on_cloak = (z > 0.30) & (z < 1.38) & (np.abs(x) < 0.80)  # nuvens só no tecido da capa (nem na gola, nem na barra, nem nas mãos)
cloud = (cloud_noise > 0.60) & on_cloak
rim = (cloud_noise > 0.575) & ~cloud & on_cloak
col = cloak.copy()
col[rim] = np.array([0.80, 0.78, 0.74])
col[cloud] = np.array([0.62, 0.035, 0.05]) * (0.8 + 0.4 * fbm(v * 14.0)[cloud])[:, None]
# gola alta e barra da capa lisas e escuras (sem nuvens), para parecer bainha
plain = ~on_cloak
col[plain] = cloak[plain]
skin = np.array([0.88, 0.70, 0.60])
hair = np.array([0.025, 0.02, 0.025])
# mãos: ponta dos braços
hands = np.abs(x) > 0.80
col[hands] = skin * (0.9 + 0.2 * fbm(v[hands] * 20.0))[:, None]
# cabeça: rosto na frente (y < 0), cabelo no resto; pescoço escondido pela gola
head = z > 1.52
face = head & (y < -0.01) & (z < 1.73) & (np.abs(x) < 0.10)
col[head] = hair
col[face] = skin
# faixa da testa (protetor) e olhos: linha escura na altura dos olhos, só no rosto
eyes = face & (z > 1.615) & (z < 1.635)
col[eyes] = np.array([0.12, 0.02, 0.03])
band = head & (z > 1.665) & (z < 1.69) & (y < 0.02)
col[band] = np.array([0.10, 0.12, 0.16])
# sandálias
feet_zone = z < 0.07
col[feet_zone] = np.array([0.05, 0.04, 0.035])
layer = body.data.color_attributes.new("Col", 'FLOAT_COLOR', 'POINT')
flat = np.ones((n, 4), dtype=np.float32)
flat[:, :3] = np.clip(col, 0, 1)
layer.data.foreach_set("color", flat.ravel())

# --- esqueleto dos heróis -----------------------------------------------------------------------------------------------------------------------
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
print("ANIMAÇÕES", [a.name for a in bpy.data.actions])
bones = {b.name: (Vector(b.head_local), Vector(b.tail_local)) for b in arm.data.bones}
RAD = {"pelvis": .2, "spine_01": .19, "spine_02": .19, "spine_03": .19, "neck_01": .09, "Head": .15, "clavicle": .09, "upperarm": .11, "lowerarm": .1,
       "hand": .07, "thigh": .13, "calf": .1, "foot": .08, "ball": .06}
caps = []
for name in list(bones):
    base = name.rsplit("_", 1)[0] if name.endswith(("_l", "_r")) else name
    if base not in RAD:
        continue
    h, t = bones[name]
    if base == "hand":
        t = h + (t - h).normalized() * 0.2
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
for nme in names:
    body.vertex_groups.new(name=nme)
for i in range(len(P)):
    for j in np.nonzero(W[i])[0]:
        body.vertex_groups[names[j]].add([i], float(W[i, j]), 'REPLACE')
mat = bpy.data.materials.new("Itachi")
mat.use_nodes = True
nt = mat.node_tree
bsdf = nt.nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.85
vc = nt.nodes.new("ShaderNodeVertexColor")
vc.layer_name = "Col"
nt.links.new(vc.outputs["Color"], bsdf.inputs["Base Color"])
body.data.materials.clear()
body.data.materials.append(mat)
body.name = "Itachi_Body"
body.parent = arm
md = body.modifiers.new("Armature", 'ARMATURE')
md.object = arm
for o in bpy.data.objects:
    o.select_set(o in (body, arm))
bpy.context.view_layer.objects.active = arm
kw = dict(filepath=dst, export_format='GLB', export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True, use_selection=True)
try:
    bpy.ops.export_scene.gltf(export_vertex_color='ACTIVE', **kw)
except TypeError:
    bpy.ops.export_scene.gltf(export_colors=True, **kw)
print("OK", dst)
