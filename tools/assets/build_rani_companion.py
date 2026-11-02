"""Rani (rani.glb enviado pelo autor do projeto: dançarina de fogo do Character Creator, esqueleto CC_Base com 101 ossos em T-pose, 1,83 m, 9 malhas com ~590 mil
polígonos e 38 texturas de até 4096 px (95 MB), só a animação padrão; autor/licença a confirmar), companheira de Fogo do Invocador. As malhas pesadas são reduzidas
(roupa, cabelo, braceletes e saia por Decimate) e as texturas vão a 1024 px. Como é bípede, ela usa os movimentos dos humanos: as animações dos heróis (Universal Animation
Library, assets/models/characters/hero_male.glb) são retargetadas para o esqueleto dela quadro a quadro (rotação relativa ao repouso, as duas em T-pose): idle (Idle_Loop),
walk (Walk_Loop), run (Jog_Fwd_Loop) e attack (Punch_Jab); o quadril copia o deslocamento na proporção da altura. Ossos de torção, dedos, rosto e acessórios ficam no repouso
e seguem os pais. Mesmo método de build_samurai_companion.py. Gera assets/models/props/Rani.glb.
uso: blender -b -P tools/assets/build_rani_companion.py -- <rani.glb> <hero_male.glb> <saida.glb>"""
import bpy, sys, math
import numpy as np
from mathutils import Vector, Quaternion, Matrix

src, hero_path, dst = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
sam = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
sam.name = "RaniArmature"
for a in list(bpy.data.actions):  # a animação padrão do arquivo sai: ela passa a usar os movimentos dos heróis
    bpy.data.actions.remove(a)
for im in bpy.data.images:
    if im.size[0] > 1024 or im.size[1] > 1024:
        im.scale(min(im.size[0], 1024), min(im.size[1], 1024))
# malhas mais leves: alvo de polígonos por nome (o resto fica como veio)
TARGETS = {"FireDancerOutfit_150196": 45000, "HeatherHair": 30000, "tribalfusionArm": 15000, "FireDancerOutfit_134324": 15000}
for o in meshes:
    for key, target in TARGETS.items():
        if key in o.name and len(o.data.polygons) > target:
            for ob in bpy.data.objects:
                ob.select_set(ob is o)
            bpy.context.view_layer.objects.active = o
            mod = o.modifiers.new("dec", 'DECIMATE')
            mod.ratio = target / len(o.data.polygons)
            bpy.ops.object.modifier_move_to_index(modifier="dec", index=0)
            bpy.ops.object.modifier_apply(modifier="dec")
print("POLYS", sum(len(o.data.polygons) for o in meshes))
body = meshes[0]

# herói: só o esqueleto e as animações
bpy.ops.import_scene.gltf(filepath=hero_path)
hero = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and o is not sam)
hero_meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o not in meshes]
for o in hero_meshes:
    bpy.data.objects.remove(o, do_unlink=True)
hero.name = "HeroArmature"
scene = bpy.context.scene
scene.render.fps = 24
for o in meshes:
    o.hide_viewport = True  # sem as malhas na avaliação, cada atualização da pose é barata

MAP = {"CC_Base_Hip": "pelvis", "CC_Base_Waist": "spine_01", "CC_Base_Spine01": "spine_02", "CC_Base_Spine02": "spine_03", "CC_Base_NeckTwist01": "neck_01", "CC_Base_Head": "Head"}
for side, s_ in (("L", "l"), ("R", "r")):
    MAP.update({f"CC_Base_{side}_Clavicle": f"clavicle_{s_}", f"CC_Base_{side}_Upperarm": f"upperarm_{s_}", f"CC_Base_{side}_Forearm": f"lowerarm_{s_}", f"CC_Base_{side}_Hand": f"hand_{s_}",
                f"CC_Base_{side}_Thigh": f"thigh_{s_}", f"CC_Base_{side}_Calf": f"calf_{s_}", f"CC_Base_{side}_Foot": f"foot_{s_}", f"CC_Base_{side}_ToeBase": f"ball_{s_}"})
DIRECTION_ONLY = set()  # as duas estão em T-pose: a rotação relativa serve em todos os ossos
CLIPS = {"idle": "Idle_Loop", "walk": "Walk_Loop", "run": "Jog_Fwd_Loop", "attack": "Punch_Jab"}

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
sam_h = (sM @ sam.data.bones["CC_Base_Hip"].head_local).z
hero_h = (hero.matrix_world @ hero.data.bones["pelvis"].head_local).z
K = sam_h / hero_h
sam_hips_rest = sM @ sam.data.bones["CC_Base_Hip"].head_local
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
        if name == "CC_Base_Hip":
            disp = (hero.matrix_world @ hp.head) - hero_pelvis_rest
            loc = sM.inverted() @ (sam_hips_rest + disp * K)
        m = Matrix.Translation(loc) @ local_rot.to_4x4()
        pb.matrix = m
        bpy.context.view_layer.update()


def key_frame(frame):
    for p in spb:
        p.keyframe_insert("rotation_quaternion", frame=frame)
        if p.name == "CC_Base_Hip":
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
for o in meshes:
    o.hide_viewport = False
print("ACTIONS", [(a.name, tuple(round(x) for x in a.frame_range)) for a in bpy.data.actions])
for o in bpy.data.objects:
    o.select_set(o in meshes or o is sam)
bpy.context.view_layer.objects.active = sam
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
                          export_animation_mode='ACTIONS', export_skins=True, use_selection=True, export_force_sampling=True, export_morph=False)
print("OK", dst)
