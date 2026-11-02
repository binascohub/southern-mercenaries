"""Chefe do Cemitério a partir de "Undead male" (TiZeta, OpenGameArt, CC BY): o .blend (Blender 2.4x) traz um
nobre morto-vivo de casaco roxo (corpo e cabeça, casaco, cabelo/capuz) com esqueleto de 36 ossos, mas sem animações.
Aqui o modelo é normalizado (altura, pés em z = 0, centro em x/y, frente em -Y do Blender = +Z no Godot), as
texturas são ligadas de novo aos materiais e as animações do jogo (idle, walk, run, attack, hit, die) são feitas
à mão girando os ossos.
uso: blender -b undead.blend --python build_undead.py -- <saida.glb> [pasta_de_previa]
(as texturas text_corpoV.png e vestiti-capelliV.png ficam ao lado do .blend)"""
import bpy, sys, os, math
from mathutils import Matrix, Vector, Euler

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
PREVIEW = args[1] if len(args) > 1 else ""
HEIGHT = 1.8
SRC = os.path.dirname(bpy.data.filepath)
bpy.context.scene.render.fps = 30

MESHES = {"Plane.001": "text_corpoV.png", "suite": "vestiti-capelliV.png", "capelli1": "vestiti-capelliV.png"}
arm = bpy.data.objects["Armature"]
for o in list(bpy.data.objects):
    if o.name not in MESHES and o != arm:
        bpy.data.objects.remove(o, do_unlink=True)
meshes = [bpy.data.objects[n] for n in MESHES]

# --- Transformações dentro dos dados (o exportador perde a escala/rotação dos objetos) ---------------------
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
pts = []
for o in meshes:
    ev = o.evaluated_get(deps)
    pts += [ev.matrix_world @ v.co for v in ev.to_mesh().vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
f = HEIGHT / (mx.z - mn.z)
T = Matrix.Scale(f, 4) @ Matrix.Translation(Vector(((mn.x + mx.x) / -2, (mn.y + mx.y) / -2, -mn.z)))
arm_world = arm.matrix_world.copy()
for o in meshes:
    o.parent = None
    o.matrix_world = o.matrix_world            # solta do esqueleto mantendo o lugar
mesh_world = {o.name: o.matrix_world.copy() for o in meshes}
arm.data.transform(T @ arm_world)
arm.matrix_world = Matrix.Identity(4)
for o in meshes:
    M = T @ mesh_world[o.name]
    o.data.transform(M)
    if M.determinant() < 0:
        o.data.flip_normals()                    # escala negativa em x espelhou a malha
    o.matrix_world = Matrix.Identity(4)
    o.parent = arm
    o.matrix_parent_inverse = Matrix.Identity(4)
    for mod in o.modifiers:
        if mod.type == "ARMATURE":
            mod.object = arm
bpy.context.view_layer.update()
print("ALTURA", HEIGHT, "fator", round(f, 4))

# --- Materiais -----------------------------------------------------------------------------------------
for name, tex in MESHES.items():
    o = bpy.data.objects[name]
    img = bpy.data.images.load(os.path.join(SRC, tex), check_existing=True)
    for slot in o.material_slots:
        mat = slot.material
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        nodes.clear()
        out_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        node = nodes.new("ShaderNodeTexImage")
        node.image = img
        bsdf.inputs["Roughness"].default_value = 0.85
        links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

if False:
    for b in arm.data.bones:
        print("BONE", b.name, b.parent.name if b.parent else None, tuple(round(v, 2) for v in b.head_local), tuple(round(v, 2) for v in b.tail_local))


# --- Animações: giros dos ossos (cinemática direta) -----------------------------------------------------------
for a in list(bpy.data.actions):            # as duas ações do arquivo são só uma pose parada
    bpy.data.actions.remove(a)
if arm.animation_data:
    arm.animation_data_clear()
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
pose = arm.pose.bones
for pb in pose:
    pb.rotation_mode = "QUATERNION"
REST = {pb.name: pb.bone.matrix_local.copy() for pb in pose}
HEAD = {pb.name: pb.bone.head_local.copy() for pb in pose}
ORDER = []                                   # pai antes do filho
for b in arm.data.bones:
    chain = []
    while b:
        chain.append(b)
        b = b.parent
    for c in reversed(chain):
        if c.name not in ORDER:
            ORDER.append(c.name)
PARENT = {b.name: b.parent.name if b.parent else None for b in arm.data.bones}
PELVIS = Vector((0.0, 0.05, 0.9))
ROOT_FOLLOW = ("bacino", "gamba.R", "gamba.L", "gonna.R", "gonna.L")   # raízes que seguem o corpo todo


def rx(a): return Matrix.Rotation(math.radians(a), 4, "X")
def ry(a): return Matrix.Rotation(math.radians(a), 4, "Y")
def rz(a): return Matrix.Rotation(math.radians(a), 4, "Z")
def about(p, R): return Matrix.Translation(p) @ R @ Matrix.Translation(-p)


def pose_at(frame, move=(0, 0, 0), body=None, rots=None):
    """move/body: deslocamento e giro do corpo todo em volta da pélvis (x lado, y para trás, z altura; o Blender
    olha para -Y). rots: osso -> matriz de giro (eixos do esqueleto, em volta da cabeça do osso)."""
    rots = rots or {}
    G = Matrix.Translation(Vector(move)) @ about(PELVIS, body if body is not None else Matrix.Identity(4))
    D = {}
    for name in ORDER:
        parent = PARENT[name]
        base = D[parent] if parent else (G if name in ROOT_FOLLOW else Matrix.Identity(4))
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


# A direita do modelo é +X; o braço pende girando em volta de Y (positivo no lado direito, negativo no esquerdo).
SIDE = {"R": 1.0, "L": -1.0}


def arm_rots(side, drop=35, fwd=0, out=0, elbow=0, twist=0):
    """Braço: `drop` baixa desde a pose de T, `fwd` levanta para a frente (graus), `elbow` dobra o antebraço."""
    sg = SIDE[side]
    return {"bicipite." + side: rx(-fwd) @ rz(sg * out) @ ry(sg * drop), "avambraccio." + side: rx(-elbow) @ rz(sg * twist),
            "mano." + side: rx(-elbow * 0.2)}


def leg_rots(side, thigh, knee, skirt=0.0):
    return {"gamba." + side: rx(-thigh), "polpaccio." + side: rx(knee), "piede." + side: rx(thigh - knee),
            "gonna." + side: rx(skirt)}


def merge(*ds):
    out = {}
    for d in ds:
        out.update(d)
    return out


def torso(lean=0.0, twist=0.0, head=(0, 0, 0), side=0.0):
    return {"addome": rx(lean * 0.4) @ rz(twist * 0.4), "schiena": rx(lean * 0.6) @ rz(twist * 0.6) @ ry(side),
            "colloSu": rx(head[0]) @ rz(head[2]) @ ry(head[1]), "testa": rx(head[0] * 0.5) @ rz(head[2] * 0.5)}


# Idle: respira, balança de leve, os braços pendem e as mãos pendem moles (60 quadros, ciclo).
new_action("idle")
for fr in (0, 15, 30, 45, 60):
    sn = math.sin(fr / 60 * 2 * math.pi)
    pose_at(fr, move=(0, 0, 0.006 * sn),
            rots=merge(torso(lean=1.5 * sn, twist=2 * sn, head=(-3 * sn, 0, 4 * sn)),
                       arm_rots("R", drop=38, fwd=3 * sn, elbow=10 + 3 * sn), arm_rots("L", drop=38, fwd=-3 * sn, elbow=10 - 3 * sn)))


def gait(name, frames, steps, thigh, knee, lean, arm_swing, elbow, bob, twist):
    new_action(name)
    for i in range(steps + 1):
        fr = round(i * frames / steps)
        ph = i / steps * 2 * math.pi
        tR, tL = thigh * math.sin(ph), -thigh * math.sin(ph)
        kR, kL = knee * max(0.0, -math.cos(ph)), knee * max(0.0, math.cos(ph))
        pose_at(fr, move=(0.015 * math.sin(ph), 0, bob * (math.cos(2 * ph) - 1)),
                body=rz(twist * 0.4 * math.sin(ph)),
                rots=merge(leg_rots("R", tR, kR, skirt=tR * 0.4), leg_rots("L", tL, kL, skirt=tL * 0.4),
                           torso(lean=lean, twist=-twist * math.sin(ph), head=(-lean * 0.6, 0, 0)),
                           arm_rots("R", drop=38, fwd=-arm_swing * math.sin(ph) * 1.0 + 0, elbow=elbow + arm_swing * 0.3 * max(0, math.sin(ph))),
                           arm_rots("L", drop=38, fwd=arm_swing * math.sin(ph) * 1.0, elbow=elbow + arm_swing * 0.3 * max(0, -math.sin(ph)))))


gait("walk", 36, 8, thigh=24, knee=34, lean=3, arm_swing=16, elbow=14, bob=0.03, twist=8)
gait("run", 22, 8, thigh=44, knee=78, lean=14, arm_swing=40, elbow=70, bob=0.05, twist=10)

# Attack: recua, levanta o braço direito e desce a mão num golpe em arco, a esquerda aberta para a frente (34 quadros).
new_action("attack")
pose_at(0, rots=merge(torso(), arm_rots("R", 38, elbow=10), arm_rots("L", 38, elbow=10)))
pose_at(10, move=(0, 0.06, -0.03), body=rx(-4) @ rz(14),
        rots=merge(leg_rots("R", -10, 10), leg_rots("L", 12, 14), torso(lean=-8, twist=24, head=(-6, 0, -10)),
                   arm_rots("R", drop=20, fwd=140, elbow=70, out=0), arm_rots("L", drop=20, fwd=60, elbow=30)))
pose_at(15, move=(0, 0.08, -0.04), body=rx(-6) @ rz(18),
        rots=merge(leg_rots("R", -12, 10), leg_rots("L", 14, 16), torso(lean=-10, twist=28, head=(-8, 0, -12)),
                   arm_rots("R", drop=20, fwd=155, elbow=80), arm_rots("L", drop=20, fwd=70, elbow=30)))
pose_at(21, move=(0, -0.2, -0.08), body=rx(10) @ rz(-18),
        rots=merge(leg_rots("R", 20, 30), leg_rots("L", -24, 18), torso(lean=24, twist=-26, head=(8, 0, 12)),
                   arm_rots("R", drop=30, fwd=45, elbow=20), arm_rots("L", drop=30, fwd=20, elbow=20)))
pose_at(27, move=(0, -0.18, -0.07), body=rx(8) @ rz(-14),
        rots=merge(leg_rots("R", 18, 26), leg_rots("L", -22, 16), torso(lean=20, twist=-22, head=(6, 0, 10)),
                   arm_rots("R", drop=32, fwd=38, elbow=18), arm_rots("L", drop=32, fwd=20, elbow=20)))
pose_at(34, rots=merge(torso(), arm_rots("R", 38, elbow=10), arm_rots("L", 38, elbow=10)))

# Hit: o golpe joga o tronco para trás e ele se recompõe (16 quadros).
new_action("hit")
pose_at(0, rots=merge(torso(), arm_rots("R", 38, elbow=10), arm_rots("L", 38, elbow=10)))
pose_at(4, move=(0, 0.1, -0.03), body=rx(-8),
        rots=merge(leg_rots("R", -6, 10), leg_rots("L", 8, 12), torso(lean=-16, twist=8, head=(-18, 0, -10)),
                   arm_rots("R", drop=30, fwd=30, elbow=40), arm_rots("L", drop=30, fwd=20, elbow=40)))
pose_at(10, move=(0, 0.05, -0.015), body=rx(-4),
        rots=merge(torso(lean=-8, twist=4, head=(-9, 0, -5)), arm_rots("R", 34, fwd=14, elbow=24), arm_rots("L", 34, fwd=10, elbow=24)))
pose_at(16, rots=merge(torso(), arm_rots("R", 38, elbow=10), arm_rots("L", 38, elbow=10)))

# Die: os joelhos cedem, cai de costas e fica estendido no chão, braços abertos (50 quadros).
new_action("die")
pose_at(0, rots=merge(torso(), arm_rots("R", 38, elbow=10), arm_rots("L", 38, elbow=10)))
pose_at(12, move=(0, 0.1, -0.3), body=rx(-8),
        rots=merge(leg_rots("R", 50, 100), leg_rots("L", 40, 90), torso(lean=10, twist=6, head=(14, 0, -8)),
                   arm_rots("R", 24, fwd=20, elbow=40), arm_rots("L", 24, fwd=10, elbow=40)))
pose_at(28, move=(0, 0.35, -0.55), body=rx(-48),
        rots=merge(leg_rots("R", 40, 60), leg_rots("L", 30, 50), torso(lean=-6, twist=4, head=(8, 0, -10)),
                   arm_rots("R", 10, fwd=-20, out=20, elbow=20), arm_rots("L", 10, fwd=-10, out=20, elbow=30)))
pose_at(42, move=(0, 0.6, -0.78), body=rx(-88),
        rots=merge(leg_rots("R", 6, 4), leg_rots("L", 2, 2), torso(lean=0, twist=3, head=(2, 0, -14)),
                   arm_rots("R", 6, fwd=-10, out=30, elbow=10), arm_rots("L", 6, fwd=-5, out=30, elbow=10)))
pose_at(50, move=(0, 0.6, -0.78), body=rx(-89),
        rots=merge(leg_rots("R", 6, 4), leg_rots("L", 2, 2), torso(lean=0, twist=3, head=(2, 0, -14)),
                   arm_rots("R", 6, fwd=-10, out=32, elbow=10), arm_rots("L", 6, fwd=-5, out=32, elbow=10)))

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
    cam.data.ortho_scale = 2.6
    cam.location = (6, 0, 0.9)      # lateral: olha de +X, a frente (-Y) fica à esquerda
    cam.rotation_euler = (math.radians(90), 0, math.radians(90))
    plan = {"idle": (0, 15), "walk": (0, 4, 9, 13, 18), "run": (0, 3, 6, 9, 12),
            "attack": (0, 10, 15, 21, 27), "hit": (0, 4, 10), "die": (0, 12, 28, 42, 50)}
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
    if img.size[0] > 512:
        img.scale(512, max(1, int(img.size[1] * 512 / img.size[0])))
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", export_animation_mode="ACTIONS", export_apply=True,
                          export_force_sampling=True, export_optimize_animation_size=True, export_image_format="WEBP",
                          export_image_quality=85)
print("OK", OUT, [a.name for a in bpy.data.actions])
