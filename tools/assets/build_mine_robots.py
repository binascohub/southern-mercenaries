"""Os dois robôs da Mina (assets/models/monsters/mine_automaton.glb e mine_scout.glb), dos modelos do autor (~/Downloads/pixellabs-glb-3393.glb, o autômato enferrujado, e
pixellabs-glb-3347.glb, o robozinho amarelo de antenas; malhas estáticas de ~38 mil vértices, sem esqueleto; autoria e licença a confirmar).
Reduz a malha (~20 mil), monta um esqueleto simples (corpo, braços, pernas e, no robozinho, a cabeça com as antenas) com pesos por região e cria idle, walk, run e attack
(o autômato bate com os dois braços de cima para baixo; o robozinho dá uma cabeçada). Ambos olham para -Y no Blender (+Z no glTF).
uso: blender -b -P tools/assets/build_mine_robots.py -- <automaton|scout|tin|wraith> <modelo.glb> <saida.glb>
Também gera a Sentinela de Lata (vila da Floresta) e o Espectro (Ruínas) com os mesmos passos."""
import bpy, sys, math
from math import radians

kind, src, out = sys.argv[sys.argv.index("--") + 1:][:3]
CFG = {
    "automaton": dict(z_hip=0.38, z_sh=0.70, x_leg=0.12, x_arm=0.29, leg_top=0.42, leg_ramp=0.1, leg_xmax=0.35, arm_xmin=0.20, arm_ramp=0.06, arm_z=(0.28, 0.86), head_z=None,
                      leg_swing=22, arm_swing=18, run_leg=38, run_arm=34, bob=0.012),
    "scout": dict(z_hip=0.2, z_sh=0.46, x_leg=0.09, x_arm=0.21, leg_top=0.2, leg_ramp=0.06, leg_xmax=0.14, arm_xmin=0.13, arm_ramp=0.05, arm_z=(0.14, 0.5), head_z=0.52,
                  leg_swing=30, arm_swing=26, run_leg=46, run_arm=40, bob=0.02),
    # Sentinela de Lata (pixellabs-robot-3332.glb): ovo de lata com braços grandes e pés de sino; olha para -X no arquivo (gira 90 graus para -Y).
    "tin": dict(z_hip=0.3, z_sh=0.65, x_leg=0.13, x_arm=0.33, leg_top=0.3, leg_ramp=0.08, leg_xmax=0.25, arm_xmin=0.26, arm_ramp=0.06, arm_z=(0.2, 0.8), head_z=None,
                leg_swing=20, arm_swing=16, run_leg=34, run_arm=30, bob=0.012, rot=90),
    # Espectro (pixellabs-undead-3417.glb): encapuzado que flutua, sem pernas, com manoplas enormes.
    "wraith": dict(z_hip=0.45, z_sh=0.7, x_leg=0.1, x_arm=0.28, leg_top=0.0, leg_ramp=0.1, leg_xmax=0.1, arm_xmin=0.14, arm_ramp=0.08, arm_z=(0.05, 0.8), head_z=0.8,
                   leg_swing=0, arm_swing=22, run_leg=0, run_arm=38, bob=0.05)}[kind]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
body = [o for o in bpy.data.objects if o.type == "MESH"][0]
for o in list(bpy.data.objects):
    if o is not body:
        bpy.data.objects.remove(o, do_unlink=True)
body.parent = None
body.rotation_euler = (0, 0, radians(CFG.get("rot", 0)))
bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
dec = body.modifiers.new("dec", "DECIMATE")
dec.ratio = min(1.0, 20000.0 / len(body.data.vertices))
bpy.ops.object.modifier_apply(modifier="dec")
print("VERTS", len(body.data.vertices))
C = CFG
arm_data = bpy.data.armatures.new("RobotArmature")
arm = bpy.data.objects.new("RobotArmature", arm_data)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
root = arm_data.edit_bones.new("Body")
root.head, root.tail = (0, 0, C["z_hip"]), (0, 0, C["z_hip"] + 0.3)
if C["head_z"]:
    hb = arm_data.edit_bones.new("Head")
    hb.head, hb.tail = (0, 0, C["head_z"]), (0, 0, 0.95)
    hb.parent = root
for side, sx in (("L", 1), ("R", -1)):
    leg = arm_data.edit_bones.new("Leg" + side)
    leg.head, leg.tail = (sx * C["x_leg"], 0, C["z_hip"]), (sx * C["x_leg"], 0, 0.0)
    leg.parent = root
    a = arm_data.edit_bones.new("Arm" + side)
    a.head, a.tail = (sx * C["x_arm"], 0, C["z_sh"]), (sx * (C["x_arm"] + 0.04), 0, C["arm_z"][0] + 0.1)
    a.parent = root
bpy.ops.object.mode_set(mode="OBJECT")
groups = ["Body", "LegL", "LegR", "ArmL", "ArmR"] + (["Head"] if C["head_z"] else [])
for n in groups:
    body.vertex_groups.new(name=n)
for v in body.data.vertices:
    c = v.co
    leg = max(0.0, min(1.0, (C["leg_top"] - c.z) / C["leg_ramp"])) if (c.z < C["leg_top"] and abs(c.x) < C["leg_xmax"]) else 0.0
    arm_w = 0.0
    if C["head_z"] and c.z > C["head_z"]:
        head = max(0.0, min(1.0, (c.z - C["head_z"]) / 0.06))
        body.vertex_groups["Head"].add([v.index], head, "REPLACE")
        if head < 1.0:
            body.vertex_groups["Body"].add([v.index], 1.0 - head, "REPLACE")
        continue
    if abs(c.x) > C["arm_xmin"] and C["arm_z"][0] < c.z < C["arm_z"][1]:
        arm_w = max(0.0, min(1.0, (abs(c.x) - C["arm_xmin"]) / C["arm_ramp"])) * (1.0 - leg)
    if leg > 0.0:
        body.vertex_groups["Leg" + ("L" if c.x > 0 else "R")].add([v.index], leg, "REPLACE")
    if arm_w > 0.0:
        body.vertex_groups["Arm" + ("L" if c.x > 0 else "R")].add([v.index], arm_w, "REPLACE")
    rest = 1.0 - min(1.0, leg + arm_w)
    if rest > 0.0:
        body.vertex_groups["Body"].add([v.index], rest, "REPLACE")
mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm
body.parent = arm
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
arm.animation_data_create()
pb = arm.pose.bones
for b in pb:
    b.rotation_mode = "XYZ"
HEAD = "Head" in pb


def put_pose(frame, legs=(0, 0), arms=(0, 0), body_rot=(0, 0, 0), lift=0.0, head_rot=(0, 0, 0), arm_roll=(0, 0)):
    pb["LegL"].rotation_euler = (legs[0], 0, 0)
    pb["LegR"].rotation_euler = (legs[1], 0, 0)
    pb["ArmL"].rotation_euler = (arms[0], 0, arm_roll[0])
    pb["ArmR"].rotation_euler = (arms[1], 0, arm_roll[1])
    pb["Body"].rotation_euler = body_rot
    pb["Body"].location = (0, 0, lift)
    names = ["LegL", "LegR", "ArmL", "ArmR", "Body"]
    if HEAD:
        pb["Head"].rotation_euler = head_rot
        names.append("Head")
    for n in names:
        pb[n].keyframe_insert("rotation_euler", frame=frame)
    pb["Body"].keyframe_insert("location", frame=frame)


def cycle(name, frames, leg_swing, arm_swing, bob, roll):
    arm.animation_data.action = bpy.data.actions.new(name)
    for f in range(0, frames + 1, 2):
        t = f / frames
        s = math.sin(2 * math.pi * t)
        put_pose(f + 1, legs=(leg_swing * s, -leg_swing * s), arms=(-arm_swing * s, arm_swing * s), body_rot=(0, roll * s, 0),
                 lift=bob * abs(s), head_rot=(radians(5) * math.sin(4 * math.pi * t), radians(6) * s, 0))


cycle("walk", 36, radians(C["leg_swing"]), radians(C["arm_swing"]), C["bob"], radians(3))
cycle("run", 20, radians(C["run_leg"]), radians(C["run_arm"]), C["bob"] * 2.5, radians(4))
arm.animation_data.action = bpy.data.actions.new("idle")
for f, k in ((1, 0.0), (31, 1.0), (61, 0.0)):
    put_pose(f, arms=(radians(6) * k, radians(6) * (1 - k)), body_rot=(0, radians(1.5) * (k - 0.5), 0), lift=0.006 * k,
             head_rot=(radians(4) * (k - 0.5), radians(16) * (k - 0.5), 0), arm_roll=(radians(-3) * k, radians(3) * k))
arm.animation_data.action = bpy.data.actions.new("attack")
if kind in ("automaton", "tin", "wraith"):
    frames = ((1, 0.0, 0.0, 0.0), (7, -2.4, -0.12, 0.0), (13, 0.5, 0.2, 0.0), (22, 0.0, 0.0, 0.0))
    for f, up, lean, head in frames:
        put_pose(f, arms=(up, up), body_rot=(lean, 0, 0))
else:  # cabeçada do robozinho: recua e se joga para a frente com a cabeça
    for f, lean, head, arms in ((1, 0.0, 0.0, 0.0), (6, 0.25, 0.35, 0.6), (11, -0.45, -0.5, -0.8), (20, 0.0, 0.0, 0.0)):
        put_pose(f, arms=(arms, arms), body_rot=(lean, 0, 0), head_rot=(head, 0, 0), lift=0.03 if f == 11 else 0.0)
arm.animation_data.action = None
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_apply=True, export_animation_mode="ACTIONS", export_yup=True, use_selection=False, export_image_format="WEBP")
print("OK", out, [a.name for a in bpy.data.actions])
