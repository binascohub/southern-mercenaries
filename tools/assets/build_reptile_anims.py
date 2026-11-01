"""Animações do Réptil (Rigged Textured Reptile, thecubber, OpenGameArt): o arquivo traz o esqueleto com IK nas pernas e nos braços, mas
só um agachamento parado; este script cria os ciclos idle, walk, attack, hit e die movendo os controles (pés, mãos, pélvis, coluna, cabeça)
e grava o .blend de saída, que tools/assets/build_reptile.sh passa pelo build_monsters.py (que exporta o .glb). Frente do modelo: -Y (Blender).
uso: blender -b -P tools/assets/build_reptile_anims.py -- <raptile_rig_fin.blend> <saida.blend>"""
import bpy, sys, math
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
arm = bpy.data.objects["Armature.000"]
arm.animation_data_create()
arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.rotation_mode = "QUATERNION"
FWD = Vector((0, -1, 0))  # frente do réptil
UP = Vector((0, 0, 1))
RIGHT = Vector((1, 0, 0))
TOUCHED = ["pelvis", "spine.01", "spine.02", "spine.03", "head", "foot_control.L", "foot_control.R", "hand_target.L", "hand_target.R"]
RAD = math.radians


def reset():
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.scale = (1, 1, 1)


def move(name, delta):
    """Desloca um controle por `delta` (metros, no mundo)."""
    pb = arm.pose.bones[name]
    pb.location = pb.location + arm.data.bones[name].matrix_local.to_3x3().inverted() @ Vector(delta)


def turn(name, pitch=0.0, yaw=0.0, roll=0.0):
    """Gira o osso em volta dos eixos do mundo: pitch (+ = inclina para a frente), yaw (+ = para a esquerda dele) e roll."""
    basis = arm.data.bones[name].matrix_local.to_3x3()
    world = Matrix.Rotation(RAD(-pitch), 3, "X") @ Matrix.Rotation(RAD(yaw), 3, "Z") @ Matrix.Rotation(RAD(roll), 3, "Y")
    arm.pose.bones[name].rotation_quaternion = (basis.inverted() @ world @ basis).to_quaternion()


def make(name, frames, pose, loop=True):
    """Uma ação: `pose(f)` põe os controles no quadro f (f de 0 a frames), e todos os controles recebem chave."""
    act = bpy.data.actions.new(name)
    arm.animation_data.action = act
    for f in range(frames + 1):
        reset()
        pose(f)
        for bone in TOUCHED:
            pb = arm.pose.bones[bone]
            pb.keyframe_insert("location", frame=f + 1)
            pb.keyframe_insert("rotation_quaternion", frame=f + 1)
    arm.animation_data.action = None
    return act


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


# --- idle: respira e mexe a cabeça (2 s, em laço) ---------------------------------------------------------
def idle(f):
    t = f / 48.0
    s = math.sin(2 * math.pi * t)
    move("pelvis", UP * (0.012 * s))
    turn("spine.02", pitch=2.0 * math.sin(2 * math.pi * t + 0.6))
    turn("spine.03", yaw=2.0 * math.sin(2 * math.pi * t))
    turn("head", pitch=3.0 * math.sin(2 * math.pi * t + 1.4), yaw=7.0 * math.sin(4 * math.pi * t))
    move("hand_target.L", UP * (0.015 * s))
    move("hand_target.R", UP * (-0.015 * s))


# --- walk: passo de 20 quadros (0,83 s), pés digitígrados, tronco inclinado ------------------------------
STRIDE, LIFT = 0.30, 0.14


def foot(t):
    """Deslocamento do pé (y, z) no instante t do ciclo: apoio (anda para trás) e balanço (volta com elevação)."""
    p = t % 1.0
    if p < 0.5:
        return -STRIDE + 2 * STRIDE * (p / 0.5), 0.0
    q = (p - 0.5) / 0.5
    return STRIDE - 2 * STRIDE * smooth(q), LIFT * math.sin(math.pi * q)


def walk(f):
    t = f / 20.0
    for side, phase in (("L", 0.0), ("R", 0.5)):
        y, z = foot(t + phase)
        move("foot_control." + side, Vector((0, y, z)))
        move("hand_target." + side, Vector((0, 0.5 * y + 0.0, 0.0)) * -1.0 * 0.5 + UP * 0.02)  # a mão vai ao contrário do pé
    move("pelvis", UP * (-0.025 * math.cos(4 * math.pi * t)) + FWD * 0.04)
    turn("pelvis", pitch=6.0)
    turn("spine.02", pitch=3.0, yaw=7.0 * math.sin(2 * math.pi * t))
    turn("spine.03", yaw=-5.0 * math.sin(2 * math.pi * t))
    turn("head", pitch=-6.0, yaw=-4.0 * math.sin(2 * math.pi * t))


# --- attack: recua o braço, golpeia com as garras e volta (24 quadros, uma vez) ---------------------------
def attack(f):
    # chaves: (quadro, recuo 0 a 1, golpe 0 a 1)
    if f <= 8:
        wind, strike = smooth(f / 8.0), 0.0
    elif f <= 12:
        wind, strike = 1.0 - smooth((f - 8) / 4.0), smooth((f - 8) / 4.0)
    else:
        wind, strike = 0.0, 1.0 - smooth((f - 12) / 12.0)
    lean = -10.0 * wind + 30.0 * strike
    move("pelvis", FWD * (0.32 * strike - 0.05 * wind) + UP * (-0.12 * strike))
    turn("pelvis", pitch=0.5 * lean)
    turn("spine.01", pitch=0.3 * lean)
    turn("spine.02", pitch=0.3 * lean, yaw=lerp(0.0, 12.0, strike) - 10.0 * wind)
    turn("head", pitch=-0.5 * lean + 8.0 * wind - 10.0 * strike)
    # mão direita: levanta atrás, depois golpeia para a frente e para baixo; a esquerda segue um pouco depois
    move("hand_target.R", UP * (0.80 * wind - 0.30 * strike) + FWD * (-0.35 * wind + 0.85 * strike) - RIGHT * (0.1 * strike))
    move("hand_target.L", UP * (0.35 * wind - 0.15 * strike) + FWD * (-0.15 * wind + 0.55 * strike) + RIGHT * (0.1 * strike))


# --- hit: leva o golpe e se endireita (12 quadros) -------------------------------------------------------
def hit(f):
    k = math.sin(math.pi * f / 12.0)
    move("pelvis", -FWD * (0.10 * k))
    turn("spine.01", pitch=-8.0 * k)
    turn("spine.02", pitch=-10.0 * k)
    turn("head", pitch=-14.0 * k, yaw=8.0 * k)
    move("hand_target.L", UP * (0.12 * k) + RIGHT * (0.08 * k))
    move("hand_target.R", UP * (0.12 * k) - RIGHT * (0.08 * k))


# --- die: cambaleia, cede os joelhos e tomba de lado (22 quadros, uma vez; termina caído) -----------------
# A coluna (spine.01) e a cabeça não herdam a rotação da pélvis no rig: o tronco e a cabeça giram por conta própria.
def die(f):
    a = smooth(f / 22.0)
    b = smooth((f - 3) / 19.0)
    move("pelvis", UP * (-0.52 * b) + RIGHT * (0.30 * b))
    turn("pelvis", pitch=10.0 * a, roll=55.0 * b)
    turn("spine.01", pitch=14.0 * a, roll=80.0 * b)
    turn("spine.02", roll=4.0 * b)
    turn("head", pitch=10.0 * a, roll=80.0 * b, yaw=-25.0 * b)
    move("foot_control.L", UP * (0.04 * b) + FWD * (0.10 * b))
    move("foot_control.R", UP * (0.20 * b) + FWD * (0.30 * b) + RIGHT * (0.30 * b))
    move("hand_target.L", UP * (-0.55 * b) + RIGHT * (0.55 * b) + FWD * (0.25 * b))
    move("hand_target.R", UP * (-0.20 * b) + RIGHT * (0.30 * b) + FWD * (0.55 * b))


# O crouch original e as ações de rolagem do pé (usadas pelas restrições) saem do caminho; as novas ficam com fake user.
for action in list(bpy.data.actions):
    if not action.name.startswith("foot_roll"):
        bpy.data.actions.remove(action)
for name, frames, fn in (("idle", 48, idle), ("walk", 20, walk), ("attack", 24, attack), ("hit", 12, hit), ("die", 22, die)):
    act = make(name, frames, fn)
    act.use_fake_user = True
bpy.ops.wm.save_as_mainfile(filepath=out)
print("OK", out, [a.name for a in bpy.data.actions])
