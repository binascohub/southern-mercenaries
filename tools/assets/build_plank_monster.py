"""Monstro de Tábuas (Monster_4, minib1.rar enviado pelo autor do projeto: corpo e 6 tábuas, esqueleto de 67 ossos no estilo do Unreal, 1,87 m, sem animações, texturas 4K;
autor/licença a confirmar): mini-chefe do Esgoto (no lugar do Rei dos Sapos). Monta os materiais (cor, emissão e normal, a 1024 px), reduz nada na malha e retargeta as animações dos
heróis (Universal Animation Library, assets/models/characters/hero_male.glb) para o esqueleto dele, quadro a quadro: idle (Idle_Loop), walk (Walk_Loop), run (Jog_Fwd_Loop), attack (Punch_Cross),
hit (Hit_Chest) e die (Death01). Os ossos têm os mesmos nomes dos heróis (cabeça: head/Head); tronco, pescoço, cabeça e pernas copiam a rotação relativa ao repouso e os braços a direção
absoluta (o monstro está em A-pose e o herói em T-pose); o quadril copia o deslocamento. Mesmo método de build_samurai_companion.py.
Gera assets/models/monsters/plank_monster.glb.
uso: blender -b -P tools/assets/build_plank_monster.py -- <pasta do pacote extraído (com model/ e textures/)> <hero_male.glb> <saida.glb>"""
import bpy, sys, os
from mathutils import Vector, Quaternion, Matrix

pack, hero_path, dst = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(pack, "model", "sk_monster_4.fbx"))
mon = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
mon.name = "MonsterArmature"
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)


# --- materiais: cor + emissão (corpo) + normal, a 1024 px -------------------------------------------------------------------------------------------
def load(name):
    path = os.path.join(pack, "textures", name)
    img = bpy.data.images.load(path)
    img.scale(1024, 1024)
    img.pack()
    return img


def make_material(mat_name, base, emissive, normal):
    mat = bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.8
    bsdf.inputs["Metallic"].default_value = 0.0
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tb = nt.nodes.new("ShaderNodeTexImage")
    tb.image = load(base)
    nt.links.new(tb.outputs["Color"], bsdf.inputs["Base Color"])
    if emissive:
        te = nt.nodes.new("ShaderNodeTexImage")
        te.image = load(emissive)
        te.image.colorspace_settings.name = "sRGB"
        nt.links.new(te.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 1.5
    tn = nt.nodes.new("ShaderNodeTexImage")
    tn.image = load(normal)
    tn.image.colorspace_settings.name = "Non-Color"
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(tn.outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


m_body = make_material("m_body", "t_body_Base_color.png", "t_body_Emissive.png", "t_body_Normal_OpenGL.png")
m_plank = make_material("m_plank", "t_plank_Base_color.png", None, "t_plank_Normal_OpenGL.png")
for o in meshes:
    o.data.materials.clear()
    o.data.materials.append(m_body if o.data.name.startswith("1_low") or "body" in o.name.lower() or o.name.startswith("1_low") else m_plank)
print("MALHAS", [(o.name, o.data.materials[0].name) for o in meshes])

# --- animações dos heróis ----------------------------------------------------------------------------------------------------------------------
bpy.ops.import_scene.gltf(filepath=hero_path)
hero = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and o is not mon)
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o not in meshes:
        bpy.data.objects.remove(o, do_unlink=True)
hero.name = "HeroArmature"
scene = bpy.context.scene
scene.render.fps = 24
for o in meshes:
    o.hide_viewport = True  # sem as malhas na avaliação, cada atualização da pose é barata

MAP = {"pelvis": "pelvis", "spine_01": "spine_01", "spine_02": "spine_02", "spine_03": "spine_03", "neck_01": "neck_01", "head": "Head"}
for s_ in ("l", "r"):
    for b in ("clavicle", "upperarm", "lowerarm", "hand", "thigh", "calf", "foot"):
        MAP["%s_%s" % (b, s_)] = "%s_%s" % (b, s_)
    MAP["ball_%s" % s_] = "ball_%s" % s_
DIRECTION_ONLY = {"upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r", "hand_l", "hand_r"}
CLIPS = {"idle": "Idle_Loop", "walk": "Walk_Loop", "run": "Jog_Fwd_Loop", "attack": "Punch_Cross", "hit": "Hit_Chest", "die": "Death01"}

spb, hpb = mon.pose.bones, hero.pose.bones
for p in spb:
    p.rotation_mode = 'QUATERNION'
mon.animation_data_create()
hero.animation_data_create()
sRw = mon.matrix_world.to_3x3().normalized()
sM = mon.matrix_world


def rot_rest_world(arm, bone):
    return (arm.matrix_world @ bone.matrix_local).to_3x3().normalized()


# No FBX o "rabo" do osso não aponta para o membro: a direção de repouso de cada osso dos braços vai até a cabeça do osso filho.
CHILD_OF = {"upperarm_l": "lowerarm_l", "lowerarm_l": "hand_l", "hand_l": "middle_01_l", "upperarm_r": "lowerarm_r", "lowerarm_r": "hand_r", "hand_r": "middle_01_r"}


def dir_rest_world(arm, bone):
    child = arm.data.bones[CHILD_OF[bone.name]]
    return (arm.matrix_world.to_3x3() @ (child.head_local - bone.head_local)).normalized()


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


ORDER = [n for n in depth_order(mon) if n in MAP]
sam_h = (sM @ mon.data.bones["pelvis"].head_local).z
hero_h = (hero.matrix_world @ hero.data.bones["pelvis"].head_local).z
K = sam_h / hero_h
sam_hips_rest = sM @ mon.data.bones["pelvis"].head_local
hero_pelvis_rest = hero.matrix_world @ hero.data.bones["pelvis"].head_local
print("HIPS", round(sam_h, 3), round(hero_h, 3), "K", round(K, 3), "ossos mapeados", len(ORDER))


def retarget_frame():
    bpy.context.view_layer.update()
    for name in ORDER:
        sb = mon.data.bones[name]
        pb = spb[name]
        hb = hero.data.bones[MAP[name]]
        hp = hpb[MAP[name]]
        base = (spb[sb.parent.name].matrix @ (sb.parent.matrix_local.inverted() @ sb.matrix_local)) if sb.parent else sb.matrix_local.copy()
        if name in DIRECTION_ONLY:
            q = dir_rest_world(mon, sb).rotation_difference(dir_pose_world(hero, hp))
            target = q.to_matrix() @ rot_rest_world(mon, sb)
        else:
            pose_rot = (hero.matrix_world @ hp.matrix).to_3x3().normalized()
            delta = pose_rot @ rot_rest_world(hero, hb).inverted()
            target = delta @ rot_rest_world(mon, sb)
        local_rot = sRw.inverted() @ target
        loc = base.to_translation()
        if name == "pelvis":
            disp = (hero.matrix_world @ hp.head) - hero_pelvis_rest
            loc = sM.inverted() @ (sam_hips_rest + disp * K)
        pb.matrix = Matrix.Translation(loc) @ local_rot.to_4x4()
        bpy.context.view_layer.update()


def key_frame(frame):
    for p in spb:
        p.keyframe_insert("rotation_quaternion", frame=frame)
        if p.name == "pelvis":
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
    mon.animation_data.action = new
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        retarget_frame()
        key_frame(f - f0 + 1)
    print("CLIPE", out_name, "<-", src_name, "quadros", f1 - f0 + 1)

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
for o in bpy.data.objects:
    o.select_set(o in meshes or o is mon)
bpy.context.view_layer.objects.active = mon
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
                          export_animation_mode='ACTIONS', export_skins=True, use_selection=True, export_force_sampling=True, export_morph=False)
print("OK", dst)
