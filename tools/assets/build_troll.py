"""Troll do Cemitério a partir de "Skinny Troll" (piacenti, OpenGameArt, CC BY 3.0): o .blend traz o troll (corpo e
olhos, com 68 ossos), uma clava de espinhos presa a um osso da mão e uma saia de couro com caveiras solta no mundo,
com as texturas embutidas, mas sem animações. Aqui tudo vira uma peça só no esqueleto (a clava no osso da mão, a saia
no osso do quadril), o modelo é normalizado (altura, pés em z = 0, frente em -Y do Blender = +Z no Godot), as texturas
são ligadas de novo aos materiais e as animações do jogo (idle, walk, run, attack, hit, die) são feitas à mão girando
os ossos.
uso: blender -b "troll game.blend" --python build_troll.py -- <saida.glb> [pasta_de_previa]"""
import bpy, sys, os, math
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
PREVIEW = args[1] if len(args) > 1 else ""
HEIGHT = 2.4          # do corpo, sem a clava
bpy.context.scene.render.fps = 30

arm = bpy.data.objects["Armature"]
BODY, CLUB, SKIRT = "Group58010", "club_high.002_club_high.003", "Volume97"
TEXTURES = {"None": "test_None_color.png", "material_0.001": "club test_material_0.001_color.png",
            "Material": "skirt test_Volume97_color.png"}
for o in list(bpy.data.objects):
    if o.name not in (BODY, CLUB, SKIRT) and o != arm:
        bpy.data.objects.remove(o, do_unlink=True)
body, club, skirt = (bpy.data.objects[n] for n in (BODY, CLUB, SKIRT))
if arm.animation_data:
    arm.animation_data_clear()
for pb in arm.pose.bones:                    # o arquivo vem com o esqueleto numa pose: volta ao repouso
    pb.location = (0, 0, 0)
    pb.rotation_mode = "QUATERNION"
    pb.rotation_quaternion = (1, 0, 0, 0)
    pb.scale = (1, 1, 1)
bpy.context.view_layer.update()

# --- Transformações dentro dos dados -------------------------------------------------------------------
pts = [body.matrix_world @ v.co for v in body.data.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
f = HEIGHT / (mx.z - mn.z)
T = Matrix.Scale(f, 4) @ Matrix.Translation(Vector(((mn.x + mx.x) / -2, (mn.y + mx.y) / -2, -mn.z)))
worlds = {o.name: o.matrix_world.copy() for o in (body, club, skirt)}
arm_world = arm.matrix_world.copy()
for o in (body, club, skirt):
    o.parent = None
    o.matrix_world = Matrix.Identity(4)
arm.data.transform(T @ arm_world)
arm.matrix_world = Matrix.Identity(4)
for o in (body, club, skirt):
    M = T @ worlds[o.name]
    o.data.transform(M)
    if M.determinant() < 0:
        o.data.flip_normals()
    o.parent = arm
    o.matrix_parent_inverse = Matrix.Identity(4)
for mod in list(body.modifiers):
    if mod.type == "CORRECTIVE_SMOOTH":
        body.modifiers.remove(mod)
    elif mod.type == "ARMATURE":
        mod.object = arm
# Clava no osso da mão, saia no quadril: peso 1 num osso só.
for o, bone in ((club, "Bone.002_L.006"), (skirt, "Bone")):
    vg = o.vertex_groups.new(name=bone)
    vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
    mod = o.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
bpy.context.view_layer.update()
print("ALTURA", HEIGHT, "fator", round(f, 4))

# --- Materiais -----------------------------------------------------------------------------------------
for mat in bpy.data.materials:
    if mat.name in TEXTURES:
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        nodes.clear()
        out_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        node = nodes.new("ShaderNodeTexImage")
        node.image = bpy.data.images[TEXTURES[mat.name]]
        bsdf.inputs["Roughness"].default_value = 0.85
        links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    elif mat.name == "eyes":
        mat.use_nodes = True
        mat.node_tree.nodes.clear()
        out_node = mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
        bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = (0.9, 0.85, 0.7, 1.0)
        mat.node_tree.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

# --- Animações: giros dos ossos (cinemática direta) -----------------------------------------------------------
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
pose = arm.pose.bones
REST = {pb.name: pb.bone.matrix_local.copy() for pb in pose}
HEAD = {pb.name: pb.bone.head_local.copy() for pb in pose}
PARENT = {b.name: b.parent.name if b.parent else None for b in arm.data.bones}
ORDER = []
for b in arm.data.bones:
    chain = []
    while b:
        chain.append(b)
        b = b.parent
    for c in reversed(chain):
        if c.name not in ORDER:
            ORDER.append(c.name)
PELVIS = HEAD["Bone"]


def rx(a): return Matrix.Rotation(math.radians(a), 4, "X")
def ry(a): return Matrix.Rotation(math.radians(a), 4, "Y")
def rz(a): return Matrix.Rotation(math.radians(a), 4, "Z")
def about(p, R): return Matrix.Translation(p) @ R @ Matrix.Translation(-p)


def pose_at(frame, move=(0, 0, 0), body_rot=None, rots=None):
    """move/body_rot: deslocamento e giro do corpo todo em volta da pélvis (x lado, y para trás, z altura; o
    Blender olha para -Y). rots: osso -> matriz de giro (eixos do esqueleto, em volta da cabeça do osso)."""
    rots = rots or {}
    G = Matrix.Translation(Vector(move)) @ about(PELVIS, body_rot if body_rot is not None else Matrix.Identity(4))
    D = {}
    for name in ORDER:
        parent = PARENT[name]
        base = D[parent] if parent else G
        D[name] = base @ about(HEAD[name], rots.get(name, Matrix.Identity(4)))
        pose[name].matrix = D[name] @ REST[name]
        bpy.context.view_layer.update()
    for pb in pose:
        pb.keyframe_insert("location", frame=frame)
        pb.keyframe_insert("rotation_quaternion", frame=frame)


def reset():
    for pb in pose:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
    bpy.context.view_layer.update()


def new_action(name):
    reset()
    act = bpy.data.actions.new(name)
    arm.animation_data_create()
    arm.animation_data.action = act
    if act.slots:
        arm.animation_data.action_slot = act.slots[0]
    act.use_fake_user = True


SIDE = {"L": 1.0, "R": -1.0}       # o lado L do modelo é +X
UPPER = {"L": "Bone.002_L.001", "R": "Bone.002_R.001"}
FORE = {"L": "Bone.002_L.002", "R": "Bone.002_R.002"}
HAND = {"L": "Bone.002_L.003", "R": "Bone.002_R.003"}
LEG = {"L": ("Bone_L.001", "Bone_L.002", "Bone_L.003"), "R": ("Bone_R.001", "Bone_R.002", "Bone_R.003")}


def arm_rots(side, drop=75, fwd=0, out=0, elbow=0, club_up=0):
    """Braço: `drop` baixa desde a pose de T (75 = pendurado), `fwd` levanta para a frente, `elbow` dobra o antebraço, `club_up` gira o osso da clava (um dedo da mão esquerda) para ela apontar para cima."""
    sg = SIDE[side]
    return {UPPER[side]: rx(-fwd) @ rz(sg * out) @ ry(sg * drop), FORE[side]: rx(-elbow), HAND[side]: rx(-elbow * 0.2), "Bone.002_L.006": rx(-club_up)}


def leg_rots(side, thigh, knee):
    t, s, ft = LEG[side]
    return {t: rx(-thigh), s: rx(knee), ft: rx(thigh - knee)}


def merge(*ds):
    out = {}
    for d in ds:
        out.update(d)
    return out


def torso(lean=0.0, twist=0.0, head=(0, 0, 0)):
    return {"Bone.001": rx(lean * 0.4) @ rz(twist * 0.4), "Bone.002": rx(lean * 0.6) @ rz(twist * 0.6),
            "Bone.003": rx(head[0]) @ rz(head[2]) @ ry(head[1])}


def hang(sw=0.0, lean=0.0, twist=0.0):
    return merge(torso(lean, twist), arm_rots("R", fwd=-sw, elbow=14), arm_rots("L", fwd=sw, elbow=22))


# Idle: respira fundo, a cabeça balança, os braços longos pendem (60 quadros, ciclo).
new_action("idle")
for fr in (0, 15, 30, 45, 60):
    sn = math.sin(fr / 60 * 2 * math.pi)
    pose_at(fr, move=(0, 0, 0.012 * sn),
            rots=merge(torso(lean=2 + 2 * sn, twist=3 * sn, head=(-4 * sn, 0, 5 * sn)),
                       arm_rots("R", 72, fwd=4 * sn, elbow=14), arm_rots("L", 72, club_up=55, fwd=-3 * sn, elbow=24)))


def gait(name, frames, steps, thigh, knee, lean, arm_swing, bob, twist):
    new_action(name)
    for i in range(steps + 1):
        fr = round(i * frames / steps)
        ph = i / steps * 2 * math.pi
        tR, tL = thigh * math.sin(ph), -thigh * math.sin(ph)
        kR, kL = knee * max(0.0, -math.cos(ph)), knee * max(0.0, math.cos(ph))
        pose_at(fr, move=(0.02 * math.sin(ph), 0, bob * (math.cos(2 * ph) - 1)), body_rot=rz(twist * 0.4 * math.sin(ph)),
                rots=merge(leg_rots("R", tR, kR), leg_rots("L", tL, kL), torso(lean=lean, twist=-twist * math.sin(ph), head=(-lean * 0.5, 0, 0)),
                           arm_rots("R", 72, fwd=-arm_swing * math.sin(ph), elbow=18 + 0.3 * arm_swing * max(0, math.sin(ph))),
                           arm_rots("L", 72, club_up=55, fwd=arm_swing * math.sin(ph) * 0.5, elbow=30)))   # a esquerda carrega a clava: balança menos


gait("walk", 40, 8, thigh=22, knee=30, lean=6, arm_swing=14, bob=0.04, twist=8)
gait("run", 24, 8, thigh=40, knee=70, lean=16, arm_swing=34, bob=0.07, twist=10)

# Attack: levanta a clava com a mão esquerda por cima da cabeça e a desce numa pancada (40 quadros).
new_action("attack")
pose_at(0, rots=merge(torso(lean=2), arm_rots("R", 72, elbow=14), arm_rots("L", 72, club_up=55, elbow=24)))
pose_at(14, move=(0, 0.1, -0.05), body_rot=rx(-6) @ rz(-10),
        rots=merge(leg_rots("R", -10, 10), leg_rots("L", 12, 14), torso(lean=-10, twist=-14, head=(-8, 0, 8)),
                   arm_rots("L", drop=30, fwd=150, elbow=60), arm_rots("R", drop=40, fwd=40, elbow=30)))
pose_at(20, move=(0, 0.14, -0.06), body_rot=rx(-8) @ rz(-12),
        rots=merge(leg_rots("R", -12, 10), leg_rots("L", 14, 16), torso(lean=-14, twist=-16, head=(-10, 0, 10)),
                   arm_rots("L", drop=30, fwd=165, elbow=70), arm_rots("R", drop=40, fwd=45, elbow=30)))
pose_at(27, move=(0, -0.3, -0.12), body_rot=rx(14) @ rz(12),
        rots=merge(leg_rots("R", 22, 30), leg_rots("L", -26, 18), torso(lean=30, twist=16, head=(10, 0, -10)),
                   arm_rots("L", drop=40, fwd=60, elbow=20), arm_rots("R", drop=50, fwd=20, elbow=20)))
pose_at(34, move=(0, -0.26, -0.1), body_rot=rx(12) @ rz(10),
        rots=merge(leg_rots("R", 20, 26), leg_rots("L", -24, 16), torso(lean=26, twist=14, head=(8, 0, -8)),
                   arm_rots("L", drop=42, fwd=55, elbow=20), arm_rots("R", drop=52, fwd=18, elbow=20)))
pose_at(40, rots=merge(torso(lean=2), arm_rots("R", 72, elbow=14), arm_rots("L", 72, club_up=55, elbow=24)))

# Hit: o golpe joga o tronco para trás e ele se recompõe (18 quadros).
new_action("hit")
pose_at(0, rots=merge(torso(lean=2), arm_rots("R", 72, elbow=14), arm_rots("L", 72, club_up=55, elbow=24)))
pose_at(5, move=(0, 0.12, -0.04), body_rot=rx(-8),
        rots=merge(leg_rots("R", -6, 10), leg_rots("L", 8, 12), torso(lean=-14, twist=8, head=(-20, 0, -10)),
                   arm_rots("R", 55, fwd=20, elbow=40), arm_rots("L", 55, club_up=55, fwd=15, elbow=40)))
pose_at(11, move=(0, 0.06, -0.02), body_rot=rx(-4),
        rots=merge(torso(lean=-6, twist=4, head=(-10, 0, -5)), arm_rots("R", 66, fwd=10, elbow=26), arm_rots("L", 66, club_up=55, fwd=8, elbow=30)))
pose_at(18, rots=merge(torso(lean=2), arm_rots("R", 72, elbow=14), arm_rots("L", 72, club_up=55, elbow=24)))

# Die: os joelhos cedem, cai de costas com os braços abertos (52 quadros).
new_action("die")
pose_at(0, rots=merge(torso(lean=2), arm_rots("R", 72, elbow=14), arm_rots("L", 72, club_up=55, elbow=24)))
pose_at(14, move=(0, 0.12, -0.45), body_rot=rx(-8),
        rots=merge(leg_rots("R", 55, 105), leg_rots("L", 45, 95), torso(lean=12, twist=6, head=(16, 0, -8)),
                   arm_rots("R", 50, fwd=25, elbow=40), arm_rots("L", 50, fwd=15, elbow=40)))
pose_at(30, move=(0, 0.5, -0.8), body_rot=rx(-48),
        rots=merge(leg_rots("R", 40, 60), leg_rots("L", 30, 50), torso(lean=-6, twist=4, head=(8, 0, -10)),
                   arm_rots("R", 35, fwd=-20, out=20, elbow=20), arm_rots("L", 35, fwd=-10, out=20, elbow=30)))
pose_at(44, move=(0, 0.95, -1.18), body_rot=rx(-88),
        rots=merge(leg_rots("R", 6, 4), leg_rots("L", 2, 2), torso(lean=0, twist=3, head=(2, 0, -14)),
                   arm_rots("R", 30, fwd=-10, out=30, elbow=10), arm_rots("L", 30, fwd=-5, out=30, elbow=10)))
pose_at(52, move=(0, 0.95, -1.18), body_rot=rx(-89),
        rots=merge(leg_rots("R", 6, 4), leg_rots("L", 2, 2), torso(lean=0, twist=3, head=(2, 0, -14)),
                   arm_rots("R", 30, fwd=-10, out=32, elbow=10), arm_rots("L", 30, fwd=-5, out=32, elbow=10)))

arm.animation_data.action = None
reset()

# --- Prévia (opcional) ----------------------------------------------------------------------------------
if PREVIEW:
    os.makedirs(PREVIEW, exist_ok=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x, sc.render.resolution_y = 360, 420
    sc.display.shading.light = "FLAT"
    sc.display.shading.color_type = "TEXTURE"
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 3.2
    cam.location = (8, 0, 1.15)      # lateral: olha de +X, a frente (-Y) fica à esquerda
    cam.rotation_euler = (math.radians(90), 0, math.radians(90))
    plan = {"idle": (0, 15), "walk": (0, 5, 10, 15, 20), "run": (0, 3, 6, 9, 12),
            "attack": (0, 14, 20, 27, 34), "hit": (0, 5, 11), "die": (0, 14, 30, 44, 52)}
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
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, max(1, int(img.size[1] * 1024 / img.size[0])))
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", export_animation_mode="ACTIONS", export_apply=True,
                          export_force_sampling=True, export_optimize_animation_size=True, export_image_format="WEBP",
                          export_image_quality=85)
print("OK", OUT, [a.name for a in bpy.data.actions])
