"""Anjo (angel_1.glb enviado pelo autor do projeto, gerado por IA/Tripo: uma anja de asas brancas, vestido de penas e auréola, de lado, andando, em 9 pedaços de malha com ~830 mil polígonos e uma textura de
alta resolução; sem esqueleto nem animação; autor/licença a confirmar): NPC do Esgoto, no lugar do Catador (Homem-Aranha). Aqui os pedaços viram uma malha só, reduzida a ~60 mil polígonos (Decimate), a textura vai a
1024 px, a frente (+X no arquivo) vira -Y do Blender (+Z do glTF), com 1,75 m, centrada em x/z e com os pés em z = 0. Fica parada na pose do arquivo (um passo à frente), como a Guardiã de pedra e o Saxão antigos, mas bate as asas (animação "flap", dois ossos de asa);
o jogo a faz flutuar e girar de leve por código (NpcModel "float").
Gera assets/models/characters/angel.glb.
uso: blender -b -P tools/assets/build_angel.py -- <angel_1.glb> <saida.glb>"""
import bpy, sys, math
import numpy as np
from mathutils import Vector, Matrix

src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
HEIGHT = 2.4  # era 1,75 m; a anja ficava pequena ao lado dos heróis
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
mod = body.modifiers.new("d", 'DECIMATE')
mod.ratio = min(1.0, 60000 / max(1, len(body.data.polygons)))
bpy.ops.object.modifier_apply(modifier="d")
print("POLÍGONOS depois", len(body.data.polygons))
for im in bpy.data.images:
    if im.size[0] > 1024 or im.size[1] > 1024:
        im.scale(1024, 1024)
# frente (+X) -> -Y; centro em x/z; pés em z = 0; altura 1,75 m
body.data.transform(Matrix.Rotation(math.radians(-90), 4, "Z"))
v = np.array([tuple(p.co) for p in body.data.vertices])
zmin, zmax = float(v[:, 2].min()), float(v[:, 2].max())
k = HEIGHT / (zmax - zmin)
cx = (v[:, 0].min() + v[:, 0].max()) / 2
cy = (v[:, 1].min() + v[:, 1].max()) / 2
body.data.transform(Matrix.Scale(k, 4) @ Matrix.Translation((-cx, -cy, -zmin)))
print("TAMANHO", [round(x, 2) for x in body.dimensions], "escala", round(k, 3))
# Esqueleto de duas asas (ossos que saem dos ombros) e a animação "flap": as asas sobem e descem devagar, em ciclo.
# Os vértices ganham peso de asa só longe do corpo (|x| > 0,3 m) e acima da cintura (z > 0,55 da altura), para os braços e o vestido ficarem parados.
def ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)
v = np.array([tuple(p.co) for p in body.data.vertices])
H = HEIGHT
wing_w = ss(0.3 * H / 1.75, 0.5 * H / 1.75, np.abs(v[:, 0])) * ss(0.55 * H, 0.66 * H, v[:, 2])
bpy.ops.object.select_all(action='DESELECT')
arm_data = bpy.data.armatures.new("AngelArm")
arm = bpy.data.objects.new("AngelArm", arm_data)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
sh_z, sh_x, sh_y = 0.77 * H, 0.2 * H / 1.75, 0.05 * H / 1.75
for name, sign in (("wing_L", 1), ("wing_R", -1)):
    b = arm_data.edit_bones.new(name)
    b.head = (sign * sh_x, sh_y, sh_z)
    b.tail = (sign * (sh_x + 0.5 * H / 1.75), sh_y, sh_z)
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
