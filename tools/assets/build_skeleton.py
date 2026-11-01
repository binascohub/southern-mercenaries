"""Esqueleto do Cemitério a partir de "Skeleton with rig" (rudy85, OpenGameArt, CC0):
o arquivo traz a malha (oito peças de ossos) e um rig de controle com IK, mas nenhuma animação.
Aqui o modelo é normalizado (1,8 m de altura, pés em y = 0, centro em x/z = 0, frente +Z no Godot),
ganha um material de osso e as animações do jogo (idle, walk, run, attack, hit, die), feitas à mão
mexendo nos controles do rig (pés, quadril, peito, pescoço e mãos); o exportador assa o resultado
nos ossos.
uso: blender -b fgc_skeleton.blend --python build_skeleton.py -- <saida.glb> [pasta_de_previa]
Com a pasta de prévia, também renderiza alguns quadros de cada animação (PNG) para conferir."""
import bpy, sys, math
from mathutils import Matrix, Vector, Euler

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
PREVIEW = args[1] if len(args) > 1 else ""
HEIGHT = 1.8
FPS = 30
bpy.context.scene.render.fps = FPS

arm = bpy.data.objects["Manny_Armature"]
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
for o in list(bpy.data.objects):
    if o != arm and o not in meshes:
        bpy.data.objects.remove(o, do_unlink=True)

# --- Tamanho e posição: dentro dos dados (o exportador perde a escala do objeto) ---------------------
for m in meshes:
    for mod in m.modifiers:
        if mod.type == "SUBSURF":
            mod.levels = 1
            mod.render_levels = 1
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
pts = []
for o in meshes:
    ev = o.evaluated_get(deps)
    pts += [o.matrix_world @ v.co for v in ev.to_mesh().vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
f = HEIGHT / (mx.z - mn.z)
T = Matrix.Scale(f, 4) @ Matrix.Translation(Vector(((mn.x + mx.x) / -2, (mn.y + mx.y) / -2, -mn.z)))
arm.data.transform(T)
for o in meshes:
    o.data.transform(T)
    o.parent = arm
    o.matrix_parent_inverse = Matrix.Identity(4)
bpy.context.view_layer.update()
print("ALTURA", HEIGHT, "fator", round(f, 4), "pontos", len(pts))

# --- Material de osso ----------------------------------------------------------------------------------
mat = bpy.data.materials["Material"]
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
out_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Base Color"].default_value = (0.78, 0.73, 0.6, 1.0)
bsdf.inputs["Roughness"].default_value = 0.85
links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
for o in meshes:
    o.data.materials.clear()
    o.data.materials.append(mat)
    o.data.polygons.foreach_set("use_smooth", [True] * len(o.data.polygons))

# --- Animação pelos controles do rig -------------------------------------------------------------------
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
pose = arm.pose.bones
REST = {pb.name: pb.bone.matrix_local.copy() for pb in pose}   # repouso, no espaço do esqueleto
CONTROLS = ["CONTROL_FOOT.L", "CONTROL_FOOT.R", "CONTROL_HIPS", "CONTROL_CHEST", "CONTROL_NECK",
            "MCH_armIKtar.L", "MCH_armIKtar.R"]
for pb in pose:
    pb.rotation_mode = "QUATERNION"


def place(bone, move=(0, 0, 0), rot=(0, 0, 0), pivot=None):
    """Põe o controle no repouso + deslocamento (x lado, y frente do Blender = -Y do modelo, z altura)
    e rotação (graus, em torno de x/y/z do esqueleto, em torno do `pivot` ou da base do osso)."""
    base = REST[bone]
    p = Vector(pivot) if pivot is not None else base.translation
    R = Euler([math.radians(a) for a in rot], "XYZ").to_matrix().to_4x4()
    M = Matrix.Translation(Vector(move)) @ Matrix.Translation(p) @ R @ Matrix.Translation(-p) @ base
    pose[bone].matrix = M
    bpy.context.view_layer.update()


def key(frame):
    for name in CONTROLS:
        pb = pose[name]
        pb.keyframe_insert("location", frame=frame)
        pb.keyframe_insert("rotation_quaternion", frame=frame)


def rest_pose():
    for name in CONTROLS:
        pose[name].location = (0, 0, 0)
        pose[name].rotation_quaternion = (1, 0, 0, 0)
    bpy.context.view_layer.update()


FWD = -1.0  # a frente do modelo é -Y no Blender


def new_action(name, frames, loop):
    rest_pose()
    act = bpy.data.actions.new(name)
    arm.animation_data_create()
    arm.animation_data.action = act
    if act.slots:
        arm.animation_data.action_slot = act.slots[0]
    act.use_fake_user = True
    return act


def pose_at(frame, feet=None, hips=(0, 0, 0), hips_rot=(0, 0, 0), chest_rot=(0, 0, 0), neck_rot=(0, 0, 0),
            hands=None, hands_rot=None):
    """Um quadro. feet = ((x, frente, altura) esquerdo, direito); hands idem (deslocamentos do repouso)."""
    rest_pose()
    fl, fr = feet or ((0, 0, 0), (0, 0, 0))
    for side, (x, fw, z) in (("L", fl), ("R", fr)):
        place("CONTROL_FOOT." + side, (x, fw * FWD, z))
    place("CONTROL_HIPS", (hips[0], hips[1] * FWD, hips[2]), hips_rot)
    place("CONTROL_CHEST", (0, 0, 0), chest_rot)
    place("CONTROL_NECK", (0, 0, 0), neck_rot)
    hl, hr = hands or ((0, 0, 0), (0, 0, 0))
    for side, (x, fw, z) in (("L", hl), ("R", hr)):
        rot = (hands_rot or {}).get(side, (0, 0, 0))
        place("MCH_armIKtar." + side, (x, fw * FWD, z), rot)
    key(frame)


def lerp(a, b, t):
    return a + (b - a) * t


# Idle: respira, balança a cabeça e os braços de leve (60 quadros, volta ao começo).
act = new_action("idle", 60, True)
for fr in (0, 15, 30, 45, 60):
    s = math.sin(fr / 60 * 2 * math.pi)
    pose_at(fr, hips=(0, 0, -0.012 * s), chest_rot=(1.5 * s, 0, 1.2 * s), neck_rot=(-2 * s, 0, 3 * s),
            hands=((0, 0.02 * s, 0.01 * s), (0, -0.02 * s, 0.01 * s)))

# Walk: passo curto e duro de morto-vivo (32 quadros, ciclo).
act = new_action("walk", 32, True)
STEPS = 8
for i in range(STEPS + 1):
    fr = round(i * 32 / STEPS)
    ph = i / STEPS * 2 * math.pi
    def foot(phase):
        fw = 0.26 * math.sin(phase)                 # frente e trás
        lift = max(0.0, math.cos(phase)) * 0.14     # sobe enquanto vai para a frente
        return (0, fw, lift)
    sw = math.sin(ph)
    pose_at(fr, feet=(foot(ph), foot(ph + math.pi)),
            hips=(0.02 * sw, 0, -0.025 * abs(math.cos(ph))), hips_rot=(0, 0, 4 * sw),
            chest_rot=(4, 0, -5 * sw), neck_rot=(-3, 0, 2 * sw),
            hands=((0, -0.13 * sw, 0.03), (0, 0.13 * sw, 0.03)))

# Run: passada longa, corpo inclinado para a frente, braços dobrados batendo (20 quadros, ciclo).
act = new_action("run", 20, True)
STEPS = 8
for i in range(STEPS + 1):
    fr = round(i * 20 / STEPS)
    ph = i / STEPS * 2 * math.pi
    def foot(phase):
        fw = 0.45 * math.sin(phase)
        lift = max(0.0, math.cos(phase)) * 0.34
        return (0, fw, lift)
    sw = math.sin(ph)
    pose_at(fr, feet=(foot(ph), foot(ph + math.pi)),
            hips=(0.03 * sw, 0.04, -0.07 + 0.06 * math.cos(2 * ph)), hips_rot=(-8, 0, 7 * sw),
            chest_rot=(-8, 0, -9 * sw), neck_rot=(6, 0, 3 * sw),
            hands=((0, -0.3 * sw, 0.28), (0, 0.3 * sw, 0.28)))

# Attack: recua, levanta o braço direito e desce a garra num golpe em arco (30 quadros, uma vez).
act = new_action("attack", 30, False)
pose_at(0)
pose_at(8, feet=((0, 0.1, 0), (0, -0.15, 0)), hips=(0, -0.08, -0.04), hips_rot=(10, 0, -14),
        chest_rot=(8, 0, 22), neck_rot=(0, 0, -10), hands=((0, 0.05, 0.05), (0.05, -0.25, 0.7)))
pose_at(12, feet=((0, 0.15, 0), (0, -0.2, 0)), hips=(0, -0.1, -0.05), hips_rot=(12, 0, -18),
        chest_rot=(10, 0, 28), neck_rot=(0, 0, -12), hands=((0, 0.05, 0.05), (0.05, -0.3, 0.8)))
pose_at(17, feet=((0, 0.3, 0), (0, -0.1, 0)), hips=(0, 0.22, -0.1), hips_rot=(-18, 0, 20),
        chest_rot=(-22, 0, -24), neck_rot=(6, 0, 10), hands=((0, 0.1, 0.0), (-0.1, 0.55, -0.15)))
pose_at(22, feet=((0, 0.3, 0), (0, -0.05, 0)), hips=(0, 0.2, -0.1), hips_rot=(-15, 0, 16),
        chest_rot=(-18, 0, -20), neck_rot=(5, 0, 8), hands=((0, 0.1, 0.0), (-0.1, 0.5, -0.1)))
pose_at(30)

# Hit: o golpe joga o corpo para trás e ele se recompõe (16 quadros, uma vez).
act = new_action("hit", 16, False)
pose_at(0)
pose_at(4, feet=((0, 0.05, 0), (0, -0.1, 0)), hips=(0, -0.14, -0.04), hips_rot=(12, 0, 6),
        chest_rot=(14, 0, 8), neck_rot=(16, 0, -10), hands=((-0.1, -0.15, 0.2), (0.1, -0.15, 0.2)))
pose_at(10, hips=(0, -0.07, -0.02), hips_rot=(6, 0, 3), chest_rot=(7, 0, 4), neck_rot=(8, 0, -5),
        hands=((-0.05, -0.07, 0.1), (0.05, -0.07, 0.1)))
pose_at(16)

# Die: os joelhos cedem, cai de costas e os ossos ficam espalhados no chão (45 quadros, uma vez).
act = new_action("die", 45, False)
pose_at(0)
pose_at(10, feet=((0, 0.05, 0), (0, 0.0, 0)), hips=(0, -0.1, -0.35), hips_rot=(10, 0, 6),
        chest_rot=(14, 0, 8), neck_rot=(22, 0, -12), hands=((-0.15, -0.1, 0.1), (0.15, -0.2, 0.2)))
pose_at(24, feet=((0.05, 0.3, 0.0), (-0.05, 0.1, 0.0)), hips=(0, -0.55, -0.55), hips_rot=(-48, 0, 10),
        chest_rot=(-10, 0, 8), neck_rot=(10, 0, -14), hands=((-0.35, -0.2, 0.0), (0.3, 0.1, 0.1)))
pose_at(38, feet=((0.12, 0.65, 0.0), (-0.08, 0.5, 0.0)), hips=(0, -0.85, -0.74), hips_rot=(-86, 0, 8),
        chest_rot=(-4, 0, 6), neck_rot=(4, 0, -18), hands=((-0.55, -0.35, -0.05), (0.45, 0.0, -0.05)))
pose_at(45, feet=((0.14, 0.7, 0.0), (-0.1, 0.55, 0.0)), hips=(0, -0.88, -0.76), hips_rot=(-88, 0, 8),
        chest_rot=(-3, 0, 6), neck_rot=(3, 0, -18), hands=((-0.58, -0.38, -0.06), (0.48, 0.02, -0.06)))

arm.animation_data.action = None
rest_pose()

# --- Prévia (opcional) ----------------------------------------------------------------------------------
if PREVIEW:
    import os
    os.makedirs(PREVIEW, exist_ok=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x, sc.render.resolution_y = 360, 420
    sc.display.shading.light = "STUDIO"
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.6
    # lateral (olhando de +X; a frente do modelo fica à esquerda)
    cam.location = (6, 0, 0.9)
    cam.rotation_euler = (math.radians(90), 0, math.radians(90))
    plan = {"idle": (0, 15), "walk": (0, 4, 8, 12, 16), "run": (0, 3, 6, 9, 12),
            "attack": (0, 8, 12, 17, 22), "hit": (0, 4, 10), "die": (0, 10, 24, 38, 45)}
    for act in [a for a in bpy.data.actions if a.name in plan]:
        arm.animation_data.action = act
        if act.slots:
            arm.animation_data.action_slot = act.slots[0]
        for fr in plan[act.name]:
            sc.frame_set(fr)
            sc.render.filepath = f"{PREVIEW}/{act.name}_{fr:02d}.png"
            bpy.ops.render.render(write_still=True)
    arm.animation_data.action = None

# --- Exporta -------------------------------------------------------------------------------------------
bpy.ops.object.mode_set(mode="OBJECT")
for a in bpy.data.actions:
    arm.animation_data.action = a
    if a.slots:
        arm.animation_data.action_slot = a.slots[0]
    track = arm.animation_data.nla_tracks.new()
    track.name = a.name
    track.strips.new(a.name, int(a.frame_range[0]), a)
    track.mute = True
arm.animation_data.action = None
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", export_animation_mode="ACTIONS",
                          export_apply=True, export_force_sampling=True, export_optimize_animation_size=False,
                          export_def_bones=True)
print("OK", OUT, [a.name for a in bpy.data.actions])
