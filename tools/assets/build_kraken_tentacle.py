"""Tentáculo do Kraken, chefe final das Docas ("Tentacle riged", defiat11, Sketchfab, CC BY 4.0; arquivo trazido pelo autor).
O arquivo: um tentáculo de 15 m em pé (base em z = 0), cadeia de 23 ossos, 41 mil triângulos, duas texturas de 1024 px e uma animação (sobe e se enrola).
Aqui: a esfera de desenhar ossos sai, as malhas são reduzidas (DECIMATE) a ~1/5, as texturas a 512 px (WEBP), e as animações são feitas por código,
dobrando a cadeia em volta de um eixo do mundo (cada osso recebe uma parte da curva; como todos giram em volta do mesmo eixo, as partes se somam):
  idle    ondula devagar, para os lados e para a frente (laço de 3 s); serve também de walk e run (o tentáculo não sai do lugar)
  attack  recua e se ergue (0,9 s), desce com tudo para a frente até deitar no chão (0,25 s: bate em ~1,15 s, no fim do aviso de 1,2 s), fica e volta (2,2 s)
  die     amolece e desaba para a frente, deitado (o jogo afunda o corpo)
"Frente" = -Y no Blender = +Z no glTF (o jogo vira +Z para o alvo). O jogo usa a escala 1/15 (o "size" dos dados dá a altura em metros).
uso: blender -b -P tools/assets/build_kraken_tentacle.py -- <tentacle_riged.glb> <saída: assets/models/monsters/kraken_tentacle.glb>"""
import bpy, sys, math
from mathutils import Vector, Quaternion, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
RATIO = 0.2
FPS = 24
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
bpy.context.scene.render.fps = FPS
for o in [o for o in bpy.data.objects if o.type == "MESH" and o.parent is None]:
    bpy.data.objects.remove(o, do_unlink=True)  # a esfera que o importador cria para desenhar os ossos
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    bpy.context.view_layer.objects.active = o
    mod = o.modifiers.new("dec", "DECIMATE")
    mod.ratio = RATIO
    while o.modifiers.find("dec") > 0:
        bpy.ops.object.modifier_move_up(modifier="dec")
    bpy.ops.object.modifier_apply(modifier="dec")
for img in bpy.data.images:
    if img.size[0] > 512:
        img.scale(512, 512)
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)
for obj in bpy.data.objects:
    if obj.animation_data:
        obj.animation_data_clear()

# cadeia da base à ponta (cada osso tem um filho só)
chain = []
b = arm.data.bones["Sceleton_Tentacles_00"]
while b:
    chain.append(b.name)
    b = b.children[0] if b.children else None
N = len(chain)
arm_rot = arm.matrix_world.to_quaternion()
local_axis = {}
for name in chain:
    rest = (arm_rot @ arm.data.bones[name].matrix_local.to_quaternion())
    local_axis[name] = {ax: (rest.inverted() @ Vector(v)).normalized() for ax, v in (("x", (1, 0, 0)), ("y", (0, 1, 0)))}
for pb in arm.pose.bones:
    pb.rotation_mode = "QUATERNION"


def weights(profile):
    """Parte da curva de cada osso (soma 1): "base" pesa mais embaixo (dobra no pé e deita), "even" igual, "tip" mais na ponta (enrola)."""
    w = []
    for i in range(N):
        t = i / (N - 1)
        w.append({"base": (1.0 - t) ** 1.6 + 0.05, "even": 1.0, "tip": 0.2 + t ** 1.5}[profile])
    s = sum(w)
    return [x / s for x in w]


def pose(frame, bends):
    """bends: lista de (eixo do mundo "x"/"y", graus no total, perfil, fase por osso em graus para ondular). Grava uma chave em cada osso."""
    for i, name in enumerate(chain):
        q = Quaternion()
        for axis, total, profile, wave in bends:
            ang = math.radians(total) * weights(profile)[i] * (math.cos(math.radians(wave * i)) if wave else 1.0)
            q = q @ Quaternion(local_axis[name][axis], ang)
        pb = arm.pose.bones[name]
        pb.rotation_quaternion = q
        pb.keyframe_insert("rotation_quaternion", frame=frame)


def action(name):
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data_create()
    arm.animation_data.action = act
    return act


# frente = -Y: giro positivo em volta de +X leva +Z para -Y
action("idle")
LOOP = 3 * FPS
for f in range(0, LOOP + 1, 4):
    ph = 2 * math.pi * f / LOOP
    pose(f, [("x", 14 * math.sin(ph), "even", 0), ("y", 22 * math.sin(ph + 1.3), "tip", 28), ("x", 10 * math.sin(2 * ph + 0.5), "tip", 40)])
action("attack")
pose(0, [("x", 0, "even", 0)])
pose(int(0.5 * FPS), [("x", -22, "base", 0), ("x", -40, "tip", 0)])           # recua e ergue a ponta
pose(int(0.9 * FPS), [("x", -30, "base", 0), ("x", -55, "tip", 0)])
pose(int(1.05 * FPS), [("x", 55, "base", 0), ("x", 10, "tip", 0)])             # desce
pose(int(1.15 * FPS), [("x", 92, "base", 0), ("x", -6, "tip", 0)])             # bate: deitado para a frente
pose(int(1.5 * FPS), [("x", 88, "base", 0), ("x", -4, "tip", 0)])
pose(int(2.2 * FPS), [("x", 0, "even", 0)])
action("die")
pose(0, [("x", 0, "even", 0)])
pose(int(0.3 * FPS), [("x", -15, "base", 0), ("y", 20, "tip", 0)])
pose(int(0.9 * FPS), [("x", 96, "base", 0), ("y", 30, "even", 0), ("x", -10, "tip", 0)])
pose(int(1.1 * FPS), [("x", 90, "base", 0), ("y", 26, "even", 0), ("x", -4, "tip", 0)])
pose(int(1.6 * FPS), [("x", 92, "base", 0), ("y", 28, "even", 0), ("x", -6, "tip", 0)])
arm.animation_data.action = bpy.data.actions["idle"]
bpy.context.scene.frame_set(0)
print("OK kraken tentacle: %d ossos, %d triângulos, ações %s" % (N, sum(len(o.data.polygons) for o in bpy.data.objects if o.type == "MESH"),
                                                               sorted(a.name for a in bpy.data.actions)))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85,
                          export_animation_mode="ACTIONS", export_force_sampling=True)
