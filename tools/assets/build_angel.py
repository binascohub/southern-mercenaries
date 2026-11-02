"""Anjo caído (angel.glb enviado pelo autor do projeto, gerado por IA/Tripo: uma anja esquelética de asas negras abertas, auréola de espinhos e manto rasgado, de frente, em 20 pedaços de malha
com ~2 milhões de polígonos e 3 texturas de 4096 px; sem esqueleto nem animação; autor/licença a confirmar): a Serafina, NPC do Esgoto (substituiu o angel_1.glb, de asas brancas, que
ficava com falhas depois da redução). Aqui os pedaços viram uma malha só, com as emendas soldadas (remove_doubles: sem isso a redução abre buracos entre os blocos) e reduzida a ~150 mil
polígonos (Decimate), as texturas vão a 2048 px, a frente vira -Y do Blender (+Z do glTF), com 2,4 m (com a auréola), centrada em x/z e com os pés em z = 0.
Um esqueleto de dois ossos de asa (nos ombros) e a animação "flap" fazem as asas baterem; o corpo fica parado, e o jogo a faz flutuar e girar de leve por código (NpcModel "float").
Gera assets/models/characters/angel.glb.
uso: blender -b -P tools/assets/build_angel.py -- <angel.glb> <saida.glb> [giro_frente_graus=0] [polígonos=150000] [altura_m=2.4] [luminância_da_pena=0.22]"""
import bpy, sys, math
import numpy as np
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index("--") + 1:]
src, dst = args[:2]
FRONT_DEG = float(args[2]) if len(args) > 2 else 0.0  # giro em Z que leva a frente do arquivo para -Y (o angel.glb já olha para -Y; o antigo angel_1.glb olhava para +X: -90)
TARGET_POLYS = int(args[3]) if len(args) > 3 else 150000
DARK = float(args[5]) if len(args) > 5 else 0.22  # luminância (0 a 1) abaixo da qual a textura é pena preta
SMOOTH = 10  # passadas de suavização do peso pelos vizinhos
HEIGHT = float(args[4]) if len(args) > 4 else 2.4  # era 1,75 m; a anja ficava pequena ao lado dos heróis (5º argumento: outra altura, p.ex. 2.6 para o Azazel)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
dg = bpy.context.evaluated_depsgraph_get()
parts = []
for o in [o for o in bpy.data.objects if o.type == 'MESH' and o.name != "Icosphere"]:
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    mesh.transform(o.matrix_world)
    idx = [p.material_index for p in mesh.polygons]
    mats = list(o.data.materials)
    mesh.materials.clear()
    for m in mats:
        mesh.materials.append(m)
    ob = bpy.data.objects.new("P_" + o.name, mesh)
    bpy.context.scene.collection.objects.link(ob)
    parts.append(ob)
for o in list(bpy.data.objects):
    if o not in parts:
        bpy.data.objects.remove(o, do_unlink=True)
for o in bpy.data.objects:
    o.select_set(o in parts)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "Angel"
print("POLÍGONOS antes", len(body.data.polygons))
# Solda as emendas entre os pedaços (o Tripo corta a malha em blocos): sem isso a redução abre buracos ao longo delas.
import bmesh
bm = bmesh.new()
bm.from_mesh(body.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00005)
bm.to_mesh(body.data)
bm.free()
print("POLÍGONOS soldados", len(body.data.polygons), "vértices", len(body.data.vertices))
mod = body.modifiers.new("d", 'DECIMATE')
mod.ratio = min(1.0, TARGET_POLYS / max(1, len(body.data.polygons)))
mod.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier="d")
print("POLÍGONOS depois", len(body.data.polygons))
for im in bpy.data.images:
    if im.size[0] > 2048 or im.size[1] > 2048:
        im.scale(2048, 2048)
# frente (+X) -> -Y; centro em x/z; pés em z = 0; altura 1,75 m
body.data.transform(Matrix.Rotation(math.radians(FRONT_DEG), 4, "Z"))
v = np.array([tuple(p.co) for p in body.data.vertices])
zmin, zmax = float(v[:, 2].min()), float(v[:, 2].max())
k = HEIGHT / (zmax - zmin)
cx = (v[:, 0].min() + v[:, 0].max()) / 2
cy = (v[:, 1].min() + v[:, 1].max()) / 2
body.data.transform(Matrix.Scale(k, 4) @ Matrix.Translation((-cx, -cy, -zmin)))
print("TAMANHO", [round(x, 2) for x in body.dimensions], "escala", round(k, 3))
# Esqueleto de duas asas (ossos que saem dos ombros) e a animação "flap": as asas sobem e descem devagar, em ciclo.
# As penas são pretas e os ossos e o manto claros: o peso de asa vem da cor da textura no vértice (escura e longe do eixo do corpo), suavizado pelos vizinhos da malha
# (o peso só pela distância ao corpo deformava os braços e deixava agulhas de pena soltas).
def ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)
v = np.array([tuple(p.co) for p in body.data.vertices])
H = HEIGHT
base_image = None
for node in body.data.materials[0].node_tree.nodes:
    if node.type == 'BSDF_PRINCIPLED' and node.inputs["Base Color"].links:
        base_image = node.inputs["Base Color"].links[0].from_node.image
w, h = base_image.size
px = np.empty(w * h * 4, dtype=np.float32)
base_image.pixels.foreach_get(px)
px = px.reshape(h, w, 4)
nloops = len(body.data.loops)
loop_vert = np.empty(nloops, dtype=np.int32)
body.data.loops.foreach_get("vertex_index", loop_vert)
loop_uv = np.empty(nloops * 2, dtype=np.float32)
body.data.uv_layers.active.data.foreach_get("uv", loop_uv)
loop_uv = loop_uv.reshape(-1, 2)
tex = px[np.clip((loop_uv[:, 1] * h).astype(int), 0, h - 1), np.clip((loop_uv[:, 0] * w).astype(int), 0, w - 1), :3]
lum = tex @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
vert_lum = np.zeros(len(v), dtype=np.float32)
count = np.zeros(len(v), dtype=np.float32)
np.add.at(vert_lum, loop_vert, lum)
np.add.at(count, loop_vert, 1.0)
vert_lum /= np.maximum(count, 1.0)
raw = ((vert_lum < DARK) & (np.abs(v[:, 0]) > 0.12 * H)).astype(np.float32)
edges = np.empty(len(body.data.edges) * 2, dtype=np.int32)
body.data.edges.foreach_get("vertices", edges)
edges = edges.reshape(-1, 2)
for _ in range(SMOOTH):
    acc = raw.copy()
    deg = np.ones(len(v), dtype=np.float32)
    np.add.at(acc, edges[:, 0], raw[edges[:, 1]])
    np.add.at(acc, edges[:, 1], raw[edges[:, 0]])
    np.add.at(deg, edges[:, 0], 1.0)
    np.add.at(deg, edges[:, 1], 1.0)
    raw = acc / deg
ax = np.abs(v[:, 0])
# longe do corpo (|x| > 0,26 da altura) tudo é asa; na faixa perto dele (0,10 a 0,26) só a pena escura, para braços, mãos e costelas ficarem parados.
wing_w = np.maximum(ss(0.20 * H, 0.26 * H, ax), ss(0.5, 0.75, raw) * ss(0.10 * H, 0.14 * H, ax))
print("VÉRTICES DE ASA", int((wing_w > 0.5).sum()), "de", len(v))
bpy.ops.object.select_all(action='DESELECT')
arm_data = bpy.data.armatures.new("AngelArm")
arm = bpy.data.objects.new("AngelArm", arm_data)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
sh_z, sh_x, sh_y = 0.74 * H, 0.1 * H, 0.04 * H
for name, sign in (("wing_L", 1), ("wing_R", -1)):
    b = arm_data.edit_bones.new(name)
    b.head = (sign * sh_x, sh_y, sh_z)
    b.tail = (sign * (sh_x + 0.3 * H), sh_y, sh_z)
bpy.ops.object.mode_set(mode='OBJECT')
for name, sign in (("wing_L", 1), ("wing_R", -1)):
    g = body.vertex_groups.new(name=name)
    side = (v[:, 0] * sign) > 0
    for i in np.nonzero(side & (wing_w > 0.001))[0]:
        g.add([int(i)], float(wing_w[i]), 'REPLACE')
body.parent = arm
md = body.modifiers.new("Armature", 'ARMATURE')
md.object = arm
act = bpy.data.actions.new("flap")
arm.animation_data_create().action = act
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
FR, AMP = 40, math.radians(26)
for name, sign in (("wing_L", 1), ("wing_R", -1)):
    pb = arm.pose.bones[name]
    rest = pb.bone.matrix_local.to_3x3()
    pb.rotation_mode = 'QUATERNION'
    for f in range(FR + 1):
        ang = sign * AMP * math.sin(2 * math.pi * f / FR)
        r = Matrix.Rotation(ang, 3, 'Y')
        pb.rotation_quaternion = (rest.inverted() @ r @ rest).to_quaternion()
        pb.keyframe_insert("rotation_quaternion", frame=f + 1)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, FR + 1
if "--frame" in sys.argv:  # só para conferir: congela no pico da batida
    bpy.context.scene.frame_set(int(sys.argv[sys.argv.index("--frame") + 1]))
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
arm.select_set(True)
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', use_selection=True, export_animations=True, export_skins=True)
print("OK", dst)
