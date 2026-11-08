"""Tiro de arco do Arqueiro ("Animation - Bow Shoot", lexferreira89 na Sketchfab, CC BY 4.0; arquivo trazido pelo autor do projeto): um boneco com
esqueleto próprio (nomes em português: Cu, PelvisA, CostaA..D, Ombro/Braco/Antebraco/Mao, Coxa/Perna/PeA/PeB, dedos) e um arco, numa animação de
0,875 s (mira, puxa a corda, solta, volta). Aqui a animação passa para o esqueleto dos heróis (Universal Animation Library, hero_male.glb), quadro a quadro:
 - espelhada: no original o arco fica na mão esquerda; no jogo o arco está preso em hand_r (game/actors/player.gd);
 - cada osso copia a orientação no mundo do osso correspondente; tronco, cabeça e pernas em relação ao repouso (os dois de pé), braços
   depois de alinhar o repouso (o boneco está em A-pose e o herói em T-pose);
 - o punho do arco é dobrado para o arco ficar de pé (ver bow_hand);
 - os dedos do boneco são retos: as mãos do herói ficam fechadas na pegada do Sword_Idle (arco numa, corda na outra);
 - o quadril copia o deslocamento, na proporção da altura do quadril;
 - retemporizada: no jogo a flecha sai no começo do tiro e o próximo vem em ~0,4 s, então a puxada é comprimida em 0,1 s e a soltura e a volta
   ocupam o resto (0,45 s no total).
Sai assets/models/characters/anim_bow_shoot.glb: o esqueleto, uma malha pequena presa a ele (Eyes, só para o Godot montar o Skeleton3D) e a ação
"Bow_Shoot"; game/actors/hero_model.gd a junta às animações do Arqueiro e a usa no "shoot".
uso: blender -b --python tools/assets/build_bow_shoot.py -- <animation_-_bow_shoot.glb> <hero_male.glb> <saída.glb>"""
import bpy, sys
from mathutils import Matrix, Vector

src, hero_path, out = sys.argv[sys.argv.index("--") + 1:][:3]
FPS = 30
# (segundos na saída, quadro do original): puxada rápida, soltura no quadro 12, volta à mira no 21.
TIMING = [(0.0, 5.0), (0.1, 12.0), (0.45, 21.0)]
LENGTH = TIMING[-1][0]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
sk = bpy.data.objects["Esqueleto"]
bpy.ops.import_scene.gltf(filepath=hero_path)
hero = next(o for o in bpy.data.objects if o.type == "ARMATURE" and o.name not in ("Esqueleto", "ArcoArma"))
keep_mesh = next(o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("Eyes") and o.parent == hero)
for o in list(bpy.data.objects):
    if o not in (sk, hero, keep_mesh) and o.type in ("MESH", "ARMATURE", "EMPTY") and o.name not in ("Root", "Sketchfab_model"):
        if o.type != "ARMATURE" or o.name == "ArcoArma":
            bpy.data.objects.remove(o, do_unlink=True)
# Os dedos do boneco são retos (não fecham no arco): as mãos do herói ficam fechadas na pegada do Sword_Idle (as duas).
FINGERS = ("index", "middle", "ring", "pinky", "thumb")
grip_action = next(a for a in bpy.data.actions if a.name.split("|")[-1].startswith("Sword_Idle"))
hero.animation_data_create()
hero.animation_data.action = grip_action
if grip_action.slots:
    hero.animation_data.action_slot = grip_action.slots[0]
bpy.context.scene.frame_set(int(grip_action.frame_range[0]))
GRIP = {p.name: p.rotation_quaternion.copy() for p in hero.pose.bones if p.name.startswith(FINGERS)}
hero.animation_data.action = None

# Mapa herói <- original (lados trocados: espelho).
MAP = {"pelvis": "PelvisA", "spine_01": "CostaA", "spine_02": "CostaB", "spine_03": "CostaD", "neck_01": "Pescoco", "Head": "Cabeca"}
ARM = {}
for hs, ss in (("r", "L"), ("l", "R")):
    MAP.update({"thigh_" + hs: "Coxa_" + ss, "calf_" + hs: "Perna_" + ss, "foot_" + hs: "PeA_" + ss, "ball_" + hs: "PeB_" + ss})
    for h, s in (("clavicle", "Ombro"), ("upperarm", "Braco"), ("lowerarm", "Antebraco"), ("hand", "Mao")):
        ARM[h + "_" + hs] = s + "_" + ss
MAP.update(ARM)
MAP = {h: s + "_Esqueleto" for h, s in MAP.items() if h in hero.data.bones and s + "_Esqueleto" in sk.data.bones}
ORDER = [b.name for b in hero.data.bones if b.name in MAP]  # bones vêm em ordem de hierarquia (pai antes do filho)
MIRROR = Matrix.Diagonal((-1.0, 1.0, 1.0))


def rot_world(obj, m4):
    return (obj.matrix_world @ m4).to_3x3().normalized()


def mirror(r):
    return MIRROR @ r @ MIRROR


def dir_world(obj, bone):
    return (obj.matrix_world.to_3x3() @ (bone.tail_local - bone.head_local)).normalized()


scene = bpy.context.scene
scene.frame_set(1)
bpy.context.view_layer.update()
# Correção fixa por osso: P = R_src_pose · C, com C = R_src_rest⁻¹ · Q⁻¹ · R_hero_rest (Q alinha o repouso do braço do original ao do herói).
CORR = {}
for h, s in MAP.items():
    hb, sb = hero.data.bones[h], sk.data.bones[s]
    rs = mirror(rot_world(sk, sb.matrix_local))
    rh = rot_world(hero, hb.matrix_local)
    if h in ARM:
        q = (MIRROR @ dir_world(sk, sb)).rotation_difference(dir_world(hero, hb)).to_matrix()
    else:
        q = Matrix.Identity(3)
    CORR[h] = rs.inverted() @ q.inverted() @ rh

src_pelvis_rest = sk.matrix_world @ sk.data.bones["Cu_Esqueleto"].head_local
hero_pelvis_rest = hero.matrix_world @ hero.data.bones["pelvis"].head_local
K = hero_pelvis_rest.z / src_pelvis_rest.z
hero_inv = hero.matrix_world.inverted()
hero_rot_inv = hero.matrix_world.to_3x3().normalized().inverted()

action = bpy.data.actions.new("Bow_Shoot")
action.use_fake_user = True
hero.animation_data_create()
hero.animation_data.action = action
for p in hero.pose.bones:
    p.rotation_mode = "QUATERNION"


def source_frame(t):
    for (t0, f0), (t1, f1) in zip(TIMING, TIMING[1:]):
        if t <= t1 + 1e-6:
            return f0 + (f1 - f0) * (t - t0) / (t1 - t0)
    return TIMING[-1][1]


# O jogo prende o arco em hand_r girado 150° no X do osso (player.gd, HAND_GRIP): o arco corre ao longo de A = (0, -0,87, 0,5) no osso,
# quase junto do antebraço. Com o braço esticado para a frente o arco ficaria deitado; o punho então dobra para baixo o bastante para A ficar
# de pé: Y do osso = -0,87·cima + 0,5·frente e Z = 0,5·cima + 0,87·frente (frente = o antebraço, no plano do chão).
GRIP_A = Vector((0.0, -0.866, 0.5))


def bow_hand(lowerarm):
    fwd = hero.matrix_world.to_3x3() @ (lowerarm.tail - lowerarm.head)
    fwd.z = 0.0
    fwd.normalize()
    up = Vector((0.0, 0.0, 1.0))
    y = (-0.866 * up + 0.5 * fwd).normalized()
    z = (0.5 * up + 0.866 * fwd).normalized()
    x = y.cross(z)
    return Matrix((x, y, z)).transposed()


frames = int(round(LENGTH * FPS))
for i in range(frames + 1):
    f = source_frame(i / FPS)
    scene.frame_set(int(f), subframe=f - int(f))
    for p in hero.pose.bones:
        p.rotation_quaternion = (1, 0, 0, 0)
        p.location = (0, 0, 0)
    bpy.context.view_layer.update()
    for h in ORDER:
        s = MAP[h]
        target = mirror(rot_world(sk, sk.pose.bones[s].matrix)) @ CORR[h]
        if h == "hand_r":
            target = bow_hand(hero.pose.bones["lowerarm_r"])
        pb = hero.pose.bones[h]
        head = pb.matrix.to_translation()
        if h == "pelvis":
            disp = MIRROR @ ((sk.matrix_world @ sk.pose.bones["Cu_Esqueleto"].head) - src_pelvis_rest)
            head = hero_inv @ (hero_pelvis_rest + disp * K)
        pb.matrix = Matrix.Translation(head) @ (hero_rot_inv @ target).to_4x4()
        bpy.context.view_layer.update()
    for name, q in GRIP.items():
        hero.pose.bones[name].rotation_quaternion = q
        hero.pose.bones[name].keyframe_insert("rotation_quaternion", frame=i + 1)
    for h in ORDER:
        pb = hero.pose.bones[h]
        pb.keyframe_insert("rotation_quaternion", frame=i + 1)
        if h == "pelvis":
            pb.keyframe_insert("location", frame=i + 1)
print("quadros", frames + 1, "ossos", len(ORDER), "K", round(K, 3))

# Só fica o herói (esqueleto + a malha pequena) e a ação nova.
for o in list(bpy.data.objects):
    if o not in (hero, keep_mesh):
        bpy.data.objects.remove(o, do_unlink=True)
for a in list(bpy.data.actions):
    if a != action:
        bpy.data.actions.remove(a)
for p in hero.pose.bones:
    p.rotation_quaternion = (1, 0, 0, 0)
    p.location = (0, 0, 0)
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, frames + 1
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_animations=True, export_animation_mode="ACTIONS",
                          export_materials="NONE", export_frame_range=False, export_force_sampling=True)
