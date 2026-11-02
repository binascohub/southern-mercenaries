"""Samurai (samurai.glb enviado pelo autor do projeto: samurai de armadura vermelha, 1,75 m, rigado no estilo Mixamo com 54 ossos e só as animações walk e run,
295 mil polígonos, autor/licença a confirmar), companheiro de Fogo do Invocador. A malha é reduzida (Decimate, ~90 mil triângulos) e as texturas vão a 1024 px.
Como é bípede, ele usa os movimentos dos humanos: as animações dos heróis (Universal Animation Library, assets/models/characters/hero_male.glb) são retargetadas para o
esqueleto dele quadro a quadro: idle (Idle_Loop), walk (Walk_Loop), run (Jog_Fwd_Loop) e attack (Sword_Attack). Tronco, quadril, pescoço, cabeça e pernas copiam a rotação relativa
ao repouso; os braços copiam a direção absoluta (o samurai está em A-pose e o herói em T-pose, então a rotação relativa cruzaria os braços); o quadril copia o deslocamento
(na proporção da altura). Gera assets/models/props/Samurai.glb.
uso: blender -b -P tools/assets/build_samurai_companion.py -- <samurai.glb> <hero_male.glb> <saida.glb>"""
import bpy, sys, math
import numpy as np
from mathutils import Vector, Quaternion, Matrix

src, hero_path, dst = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
sam = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
body = max((o for o in bpy.data.objects if o.type == 'MESH'), key=lambda o: len(o.data.polygons))
for o in list(bpy.data.objects):
    if o not in (sam, body):
        bpy.data.objects.remove(o, do_unlink=True)
sam.name = "SamuraiArmature"
for a in list(bpy.data.actions):  # as walk/run do Mixamo saem: o samurai passa a usar os movimentos dos heróis
    bpy.data.actions.remove(a)
for im in bpy.data.images:
    if im.size[0] > 1024:
        im.scale(1024, 1024)
for o in bpy.data.objects:
    o.select_set(o is body)
bpy.context.view_layer.objects.active = body
mod = body.modifiers.new("dec", 'DECIMATE')
mod.ratio = 90000 / max(1, len(body.data.polygons))
bpy.ops.object.modifier_move_to_index(modifier="dec", index=0)
bpy.ops.object.modifier_apply(modifier="dec")
print("POLYS", len(body.data.polygons))

# herói: só o esqueleto e as animações
bpy.ops.import_scene.gltf(filepath=hero_path)
hero = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and o is not sam)
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o is not body:
        bpy.data.objects.remove(o, do_unlink=True)
hero.name = "HeroArmature"
scene = bpy.context.scene
scene.render.fps = 24
body.hide_viewport = True  # sem a malha na avaliação, cada atualização da pose é barata

MAP = {"Hips": "pelvis", "Spine": "spine_01", "Spine01": "spine_02", "Spine02": "spine_03", "neck": "neck_01", "Head": "Head"}
for side, s in (("Left", "l"), ("Right", "r")):
    MAP.update({f"{side}Shoulder": f"clavicle_{s}", f"{side}Arm": f"upperarm_{s}", f"{side}ForeArm": f"lowerarm_{s}", f"{side}Hand": f"hand_{s}",
                f"{side}UpLeg": f"thigh_{s}", f"{side}Leg": f"calf_{s}", f"{side}Foot": f"foot_{s}", f"{side}ToeBase": f"ball_{s}"})
DIRECTION_ONLY = {"LeftArm", "RightArm", "LeftForeArm", "RightForeArm", "LeftHand", "RightHand"}
CLIPS = {"idle": "Idle_Loop", "walk": "Walk_Loop", "run": "Jog_Fwd_Loop", "attack": "Sword_Attack"}

spb, hpb = sam.pose.bones, hero.pose.bones
for p in spb:
    p.rotation_mode = 'QUATERNION'
sam.animation_data_create()
hero.animation_data_create()
sRw = sam.matrix_world.to_3x3().normalized()
sM = sam.matrix_world
hRw = hero.matrix_world.to_3x3().normalized()


def rot_rest_world(arm, bone):
    return (arm.matrix_world @ bone.matrix_local).to_3x3().normalized()


def dir_rest_world(arm, bone):
    return (arm.matrix_world.to_3x3() @ (bone.tail_local - bone.head_local)).normalized()


def dir_pose_world(arm, pb):
    return (arm.matrix_world.to_3x3() @ (pb.tail - pb.head)).normalized()


def depth_order(arm):
    order = []

    def rec(b):
        order.append(b.name)
        for c in b.children:
            rec(c)
    for b in arm.data.bones:
        if b.parent is None:
            rec(b)
    return order


ORDER = [n for n in depth_order(sam) if n in MAP]
sam_h = (sM @ sam.data.bones["Hips"].head_local).z
hero_h = (hero.matrix_world @ hero.data.bones["pelvis"].head_local).z
K = sam_h / hero_h
sam_hips_rest = sM @ sam.data.bones["Hips"].head_local
hero_pelvis_rest = hero.matrix_world @ hero.data.bones["pelvis"].head_local
print("HIPS", round(sam_h, 3), round(hero_h, 3), "K", round(K, 3))


def retarget_frame():
    bpy.context.view_layer.update()
    for name in ORDER:
        sb = sam.data.bones[name]
        pb = spb[name]
        hb = hero.data.bones[MAP[name]]
        hp = hpb[MAP[name]]
        if sb.parent:
            parent_pb = spb[sb.parent.name]
            base = parent_pb.matrix @ (sb.parent.matrix_local.inverted() @ sb.matrix_local)
        else:
            base = sb.matrix_local.copy()
        if name in DIRECTION_ONLY:
            q = dir_rest_world(sam, sb).rotation_difference(dir_pose_world(hero, hp))
            target = q.to_matrix() @ rot_rest_world(sam, sb)
        else:
            pose_rot = (hero.matrix_world @ hp.matrix).to_3x3().normalized()
            delta = pose_rot @ rot_rest_world(hero, hb).inverted()
            target = delta @ rot_rest_world(sam, sb)
        local_rot = sRw.inverted() @ target
        loc = base.to_translation()
        if name == "Hips":
            disp = (hero.matrix_world @ hp.head) - hero_pelvis_rest
            loc = sM.inverted() @ (sam_hips_rest + disp * K)
        m = Matrix.Translation(loc) @ local_rot.to_4x4()
        pb.matrix = m
        bpy.context.view_layer.update()


def key_frame(frame):
    for p in spb:
        p.keyframe_insert("rotation_quaternion", frame=frame)
        if p.name == "Hips":
            p.keyframe_insert("location", frame=frame)


for out_name, src_name in CLIPS.items():
    action_src = bpy.data.actions[src_name]
    f0, f1 = int(action_src.frame_range[0]), int(action_src.frame_range[1])
    hero.animation_data.action = action_src
    if hasattr(hero.animation_data, "action_slot") and action_src.slots:
        hero.animation_data.action_slot = action_src.slots[0]
    for p in spb:
        p.rotation_quaternion = Quaternion((1, 0, 0, 0))
        p.location = Vector((0, 0, 0))
    new = bpy.data.actions.new(out_name)
    new.use_fake_user = True
    sam.animation_data.action = new
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        retarget_frame()
        key_frame(f - f0 + 1)
    print("CLIP", out_name, "<-", src_name, "frames", f1 - f0 + 1)

for p in spb:
    p.rotation_quaternion = Quaternion((1, 0, 0, 0))
    p.location = Vector((0, 0, 0))
hero.animation_data.action = None
for a in list(bpy.data.actions):
    if a.name not in CLIPS:
        bpy.data.actions.remove(a)
bpy.data.objects.remove(hero, do_unlink=True)
body.hide_viewport = False
print("ACTIONS", [(a.name, tuple(round(x) for x in a.frame_range)) for a in bpy.data.actions])
for o in bpy.data.objects:
    o.select_set(o in (sam, body))
bpy.context.view_layer.objects.active = sam
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
                          export_animation_mode='ACTIONS', export_skins=True, use_selection=True, export_force_sampling=True)
print("OK", dst)
