"""Pirata Perna-de-Pau das Docas, no lugar do Jacaré Arrastador ("Pirate clark", photon (that one larry), Sketchfab, CC BY 4.0; arquivo trazido pelo autor).
O arquivo traz esqueleto próprio e seis animações (@idle, @walk, @run, @Attack 1, @Attack 2, @jump), 71 mil triângulos e 14 texturas de 1024 px (22 MB).
Aqui: a esfera de desenhar ossos sai, as malhas são reduzidas (DECIMATE) a ~1/3, as texturas a 512 px (WEBP), as ações ganham nomes curtos
(idle, walk, run, attack, attack2; o pulo sai) e entra uma ação "die" feita aqui (o arquivo não tem morte): a pose do idle e o corpo tombando de costas
(chave no objeto do esqueleto, girando em volta do calcanhar). O modelo virá de frente para +Z no glTF (no arquivo olha para +X do Blender) e os pés vão
a y = 0 (as duas mudanças só no vazio do topo, Sketchfab_model, que nenhuma animação mexe). Altura ~2,73 m com o chapéu: o jogo usa a escala 1/2,73
("size" dos dados dá a altura; família pirate_clark em game/actors/monster_model.gd).
uso: blender -b -P tools/assets/build_pirate_clark.py -- <pirate_clark.glb> <saída: assets/models/monsters/pirate_clark.glb>"""
import bpy, sys, math
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
RATIO = 0.33
RENAME = {"@idle": "idle", "@walk": "walk", "@run": "run", "@Attack 1": "attack", "@Attack 2": "attack2"}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in [o for o in bpy.data.objects if o.type == "MESH" and o.parent is None]:
    bpy.data.objects.remove(o, do_unlink=True)  # a esfera que o importador cria para desenhar os ossos
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
top = bpy.data.objects["Sketchfab_model"]
meshes = [o for o in bpy.data.objects if o.type == "MESH"]

# --- malhas reduzidas (o DECIMATE antes do Armature, para os pesos irem junto)
for o in meshes:
    if o.data.shape_keys:
        continue
    bpy.context.view_layer.objects.active = o
    mod = o.modifiers.new("dec", "DECIMATE")
    mod.ratio = RATIO
    while o.modifiers.find("dec") > 0:
        bpy.ops.object.modifier_move_up(modifier="dec")
    bpy.ops.object.modifier_apply(modifier="dec")
for img in bpy.data.images:
    if img.size[0] > 512:
        img.scale(512, 512)

# --- de frente para -Y do Blender (+Z no glTF) e pés no chão, mexendo só no vazio do topo
bpy.context.scene.frame_set(0)
top.matrix_world = Matrix.Rotation(-math.pi / 2, 4, "Z") @ top.matrix_world
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
pts = [o.matrix_world @ v.co for o in meshes for v in o.evaluated_get(deps).to_mesh().vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
top.matrix_world = Matrix.Translation(Vector((0, 0, -mn.z))) @ top.matrix_world
bpy.context.view_layer.update()
height = mx.z - mn.z

# --- ações: nomes curtos, sem o pulo
for a in list(bpy.data.actions):
    if a.name in RENAME:
        a.name = RENAME[a.name]
    else:
        bpy.data.actions.remove(a)
for obj in bpy.data.objects:  # faixas NLA que apontavam para ações que saíram
    if obj.animation_data:
        for track in list(obj.animation_data.nla_tracks):
            if not any(s.action for s in track.strips):
                obj.animation_data.nla_tracks.remove(track)

# --- corrida e segundo golpe vêm de lado no arquivo (o quadril, spine_78, gira ~90° em relação ao idle e à caminhada): gira o quadril de volta,
# em volta do eixo vertical que passa pelo meio dos pés, quadro a quadro, para ele correr de frente para onde vai
HIPS = "spine_78"
scene = bpy.context.scene
arm.animation_data_create()


def hips_yaw(action, frame):
    arm.animation_data.action = action
    scene.frame_set(frame)
    return (arm.matrix_world @ arm.pose.bones[HIPS].matrix).to_euler().z


ref = hips_yaw(bpy.data.actions["walk"], 0)
for a in [bpy.data.actions[n] for n in ("run", "attack2")]:
    f0, f1 = int(a.frame_range[0]), int(a.frame_range[1])
    turn = sum(math.remainder(hips_yaw(a, f) - ref, math.tau) for f in range(f0, f1 + 1)) / (f1 - f0 + 1)
    if abs(turn) < math.radians(30):
        continue
    fix = Matrix.Rotation(-turn, 4, "Z")
    hips = arm.pose.bones[HIPS]
    poses = []
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        poses.append((f, arm.matrix_world.inverted() @ fix @ arm.matrix_world @ hips.matrix))
    for f, m in poses:
        scene.frame_set(f)
        hips.matrix = m
        bpy.context.view_layer.update()
        hips.keyframe_insert("location", frame=f)
        hips.keyframe_insert("rotation_quaternion", frame=f)
    print("ação %s: quadril girado %.0f° de volta" % (a.name, math.degrees(-turn)))

# --- morte: a pose do idle e o corpo tombando de costas (para +Y, atrás dele), girando em volta do calcanhar
die = bpy.data.actions["idle"].copy()
die.name = "die"
arm.animation_data_create()
slot = arm.animation_data.action_slot if hasattr(arm.animation_data, "action_slot") else None
arm.animation_data.action = die
arm.rotation_mode = "QUATERNION"
base = arm.matrix_world.copy()
back_y = mx.y - 0.35 * (mx.y - mn.y)
pivot = Vector(((mn.x + mx.x) / 2, back_y, 0.0))
FRAMES = [(0, 0.0, 0.0), (6, 0.12, 0.0), (14, 0.75, 0.0), (18, 1.0, 0.04), (21, 0.95, 0.0), (24, 1.0, 0.0), (40, 1.0, 0.0)]
for f, t, bounce in FRAMES:
    ang = -math.radians(84) * t
    rot = Matrix.Translation(pivot) @ Matrix.Rotation(ang, 4, "X") @ Matrix.Translation(-pivot)
    arm.matrix_world = Matrix.Translation(Vector((0, 0, 0.18 * height / 2.73 * t + bounce))) @ rot @ base
    bpy.context.view_layer.update()
    arm.keyframe_insert("location", frame=f)
    arm.keyframe_insert("rotation_quaternion", frame=f)
    arm.keyframe_insert("scale", frame=f)
# corta as chaves dos ossos (do idle) depois do fim da queda
for fc in (die.fcurves if hasattr(die, "fcurves") else [fc for layer in die.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]):
    while len(fc.keyframe_points) > 1 and fc.keyframe_points[-1].co.x > 40:
        fc.keyframe_points.remove(fc.keyframe_points[-1])
arm.matrix_world = base
for a in bpy.data.actions:  # as outras ações ficam no lugar de antes (sem chave de objeto, não mexem no corpo)
    a.use_fake_user = True
arm.animation_data.action = bpy.data.actions["idle"]
bpy.context.scene.frame_set(0)
print("OK pirate clark: altura %.2f m, %d triângulos, ações %s" % (height, sum(len(o.data.polygons) for o in meshes), sorted(a.name for a in bpy.data.actions)))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85,
                          export_animation_mode="ACTIONS", export_force_sampling=True)
