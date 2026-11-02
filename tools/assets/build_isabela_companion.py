"""Isabela (isabela.glb enviado pelo autor do projeto: artista marcial de quimono, 71 peças soltas com cor de vértice e sem esqueleto, 3,4 m, em T-pose,
deitada no eixo Y do Blender, autor/licença a confirmar), companheira de Fogo do Invocador: ligada ao esqueleto e às animações dos heróis
(assets/models/characters/hero_male.glb), então anda, corre e luta com os mesmos movimentos dos homens.
O quimono sai preto (faixa cinza e camiseta azul ficam como são). As peças viram uma malha só (Isabela_Body) com a cor de vértice num material próprio; o corpo é endireitado (pés em z = 0, olhando para -Y do Blender = +Z do glTF)
e reduzido para o ombro cair a 1,44 m (o esqueleto do herói); o jogo reduz de novo até o tamanho dela (model_scale em data/companions.json).
Gera assets/models/props/Isabela.glb. Mesmo método de build_werewolf_companion.py (aqui sem o ajuste da A-pose: ela já está em T).
uso: blender -b -P tools/assets/build_isabela_companion.py -- <isabela.glb> <hero_male.glb> <saida.glb>"""
import bpy, sys, math
import numpy as np
from mathutils import Vector, Matrix

src, hero_path, dst = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
# 1) as peças: cada uma leva a transformação do arquivo e vira uma só malha
bpy.ops.import_scene.gltf(filepath=src)
parts = [o for o in bpy.data.objects if o.type == 'MESH']
bpy.context.view_layer.update()
for o in parts:
    world = o.matrix_world.copy()
    o.parent = None
    o.data.transform(world)
    o.matrix_world = Matrix.Identity(4)
for o in list(bpy.data.objects):
    if o.type != 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)
# o quimono (casaco, lapelas, mangas, punhos e calça) vira preto: a cor de vértice vai para um tom quase preto que ainda guarda um pouco do sombreado original
KIMONO = {"gi_torso", "upper_gi", "left_lapel", "right_lapel", "lapel_edge_l", "lapel_edge_r", "left_sleeve", "right_sleeve", "left_cuff", "right_cuff",
          "rear_pant_lower", "rear_pant_upper", "front_pant_lower", "front_pant_upper"}
for o in parts:
    if o.name.split(".")[0] in KIMONO and o.data.color_attributes:
        attr = o.data.color_attributes[0]
        n = len(attr.data)
        col = np.zeros(n * 4, dtype=np.float32)
        attr.data.foreach_get("color", col)
        col = col.reshape(n, 4)
        lum = col[:, :3].mean(axis=1)
        col[:, :3] = (0.02 + 0.07 * lum)[:, None] * np.array([1.0, 1.0, 1.15], dtype=np.float32)[None, :]
        attr.data.foreach_set("color", col.ravel())
bpy.ops.object.select_all(action='DESELECT')
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "Isabela_Body"
# endireita: no arquivo a cabeça fica em -Y e o rosto olha para -Z; gira -90 graus em X (y' = z, z' = -y), de modo que a frente vai para -Y e o topo para +Z
body.data.transform(Matrix.Rotation(math.radians(-90), 4, "X"))
v = np.array([tuple(x.co) for x in body.data.vertices])
print("RAW HEIGHT", v[:, 2].max() - v[:, 2].min(), "front check (nose y should be < head y):")
v[:, 2] -= v[:, 2].min()
# 2) o herói: só o esqueleto e as animações ficam
bpy.ops.import_scene.gltf(filepath=hero_path)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o is not body:
        bpy.data.objects.remove(o, do_unlink=True)
bones = {b.name: (Vector(b.head_local), Vector(b.tail_local)) for b in arm.data.bones}
k = 0.6  # o ombro dela fica a ~2,4 m dos 3,4 m: reduzido para cair nos 1,44 m do esqueleto do herói
v *= k
v[:, 2] -= v[:, 2].min()
torso = (v[:, 2] > 0.9) & (v[:, 2] < 1.3) & (abs(v[:, 0]) < 0.2)
v[:, 1] -= np.median(v[torso, 1]) - bones["spine_02"][0].y
print("HEIGHT", v[:, 2].max(), "arm reach", v[:, 0].max())
RAD = {"pelvis": .25, "spine_01": .22, "spine_02": .22, "spine_03": .2, "neck_01": .1, "Head": .3, "clavicle": .09, "upperarm": .1, "lowerarm": .09,
       "hand": .09, "thigh": .15, "calf": .12, "foot": .1, "ball": .08}
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
for i, vert in enumerate(body.data.vertices):
    vert.co = Vector(P[i])
for n in names:
    body.vertex_groups.new(name=n)
for i in range(len(P)):
    for j in np.nonzero(W[i])[0]:
        body.vertex_groups[names[j]].add([i], float(W[i, j]), 'REPLACE')
# 3) material que usa a cor de vértice
mesh = body.data
color_name = mesh.color_attributes[0].name if mesh.color_attributes else None
print("COLOR ATTR", color_name)
mat = bpy.data.materials.new("Isabela_Mat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.8
if color_name:
    attr = mat.node_tree.nodes.new("ShaderNodeVertexColor")
    attr.layer_name = color_name
    mat.node_tree.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
mesh.materials.clear()
mesh.materials.append(mat)
body.parent = arm
md = body.modifiers.new("Armature", 'ARMATURE'); md.object = arm
bpy.ops.object.select_all(action='DESELECT')
for o in (body, arm):
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
kw = dict(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
          export_animation_mode='NLA_TRACKS', export_skins=True, use_selection=True)
try:
    bpy.ops.export_scene.gltf(export_vertex_color='ACTIVE', **kw)
except TypeError:
    bpy.ops.export_scene.gltf(export_colors=True, **kw)
print("OK", dst)
