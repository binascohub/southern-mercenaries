"""Mutante (Rigged, textured Mutant, OpenGameArt, CC-BY-SA 3.0 / GPL 2.0, opengameart.org/content/rigged-textured-mutant; o rig vem do de Julius para o OGA): humanoide de
armadura em A-pose, 1,8 m, com esqueleto de deformação de 55 ossos (o de controle, de 111, e as restrições saem), as malhas leves body_LOW (1,5 mil vértices) e armor_LOW (700), texturas de
1024 px (corpo e armadura) e nenhuma animação de andar. Aqui os materiais são refeitos (cor, e a normal da armadura) e as animações dos heróis (Universal Animation Library,
assets/models/characters/hero_male.glb) são retargetadas para o esqueleto dele, quadro a quadro: idle (Idle_Loop), walk (Walk_Loop), run (Jog_Fwd_Loop), attack (Punch_Cross), hit (Hit_Chest)
e die (Death01). Tronco, pernas e cabeça copiam a rotação relativa ao repouso; os braços copiam a direção absoluta (ele está em A-pose); o quadril copia o deslocamento (mesmo método de
build_troll_mauler.py). Gera assets/models/monsters/mutant.glb.
uso: blender -b -P tools/assets/build_mutant.py -- <mutant_final.blend> <hero_male.glb> <saida.glb>"""
import bpy, sys, os
from mathutils import Vector, Quaternion, Matrix

src, hero_path, dst = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.open_mainfile(filepath=src)
tro = bpy.data.objects["Deform_armature"]
tro.name = "MutantArmature"
KEEP = {"body_LOW": "body", "armor_LOW": "armor"}
meshes = [bpy.data.objects[n] for n in KEEP]
for o in list(bpy.data.objects):
    if o is not tro and o not in meshes:
        bpy.data.objects.remove(o, do_unlink=True)
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)
if tro.animation_data:
    tro.animation_data_clear()
for pb in tro.pose.bones:  # sem IK nem restrições: a pose vem toda das animações retargetadas
    for c in list(pb.constraints):
        pb.constraints.remove(c)
    pb.rotation_mode = 'QUATERNION'


# --- materiais: cor + normal, a 1024 px ----------------------------------------------------------------------------------------------------------
def image(name):
    img = bpy.data.images.get(name)
    if img is None or img.size[0] == 0:
        return None
    if img.size[0] > 1024:
        img.scale(1024, 1024)
    img.pack()
    return img


def make_material(mat_name, base, normal, flat=(0.8, 0.8, 0.8, 1.0)):
    mat = bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.8
    bsdf.inputs["Metallic"].default_value = 0.0
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    base_img = image(base) if base else None
    if base_img:
        tb = nt.nodes.new("ShaderNodeTexImage")
        tb.image = base_img
        nt.links.new(tb.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = flat
    norm_img = image(normal) if normal else None
    if norm_img:
        tn = nt.nodes.new("ShaderNodeTexImage")
        tn.image = norm_img
        tn.image.colorspace_settings.name = "Non-Color"
        nmap = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(tn.outputs["Color"], nmap.inputs["Color"])
        nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


m_body = make_material("m_body", "body_diff_1k.png", None)
m_armor = make_material("m_armor", "armor_diffuse_1k.png", "normal_armor_1k.png")
for o in meshes:
    o.data.materials.clear()
    o.data.materials.append({"body": m_body, "armor": m_armor}[KEEP[o.name]])
    for poly in o.data.polygons:
        poly.material_index = 0  # cada malha tem um material só
    o.select_set(False)
print("MALHAS", [(o.name, len(o.data.polygons), o.data.materials[0].name) for o in meshes])

# --- animações dos heróis -------------------------------------------------------------------------------------------------------------------------
bpy.ops.import_scene.gltf(filepath=hero_path)
hero = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and o is not tro)
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o not in meshes:
        bpy.data.objects.remove(o, do_unlink=True)
hero.name = "HeroArmature"
scene = bpy.context.scene
scene.render.fps = 24
for o in meshes:
    o.hide_viewport = True  # sem as malhas na avaliação, cada atualização da pose é barata

MAP = {"pelvis.cr": "pelvis", "spine.cr.01": "spine_01", "spine.cr.02": "spine_02", "spine.cr.03": "spine_03", "neck.cr": "neck_01", "head.cr": "Head"}
for s_, h_ in (("L", "l"), ("R", "r")):
    MAP.update({"shoulder.cr.%s" % s_: "clavicle_%s" % h_, "upper_arm.cr.%s" % s_: "upperarm_%s" % h_, "forearm.cr.%s" % s_: "lowerarm_%s" % h_, "hand.cr.%s" % s_: "hand_%s" % h_,
                "thigh.cr.%s" % s_: "thigh_%s" % h_, "shin.cr.%s" % s_: "calf_%s" % h_, "toe.cr.%s" % s_: "ball_%s" % h_})
DIRECTION_ONLY = {"upper_arm.cr.L", "upper_arm.cr.R", "forearm.cr.L", "forearm.cr.R", "hand.cr.L", "hand.cr.R"}
CLIPS = {"idle": "Idle_Loop", "walk": "Walk_Loop", "run": "Jog_Fwd_Loop", "attack": "Punch_Cross", "hit": "Hit_Chest", "die": "Death01"}

spb, hpb = tro.pose.bones, hero.pose.bones
tro.animation_data_create()
hero.animation_data_create()
sRw = tro.matrix_world.to_3x3().normalized()
sM = tro.matrix_world


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


ORDER = [n for n in depth_order(tro) if n in MAP]
tro_hips = (sM @ tro.data.bones["thigh.cr.L"].head_local).z  # a altura do quadril é a da junta da coxa
hero_hips = (hero.matrix_world @ hero.data.bones["thigh_l"].head_local).z
K = tro_hips / hero_hips
root_rest = sM @ tro.data.bones["pelvis.cr"].head_local
hero_root_rest = hero.matrix_world @ hero.data.bones["pelvis"].head_local
print("QUADRIL", round(tro_hips, 3), round(hero_hips, 3), "K", round(K, 3), "ossos mapeados", len(ORDER))


def retarget_frame():
    bpy.context.view_layer.update()
    for name in ORDER:
        sb = tro.data.bones[name]
        pb = spb[name]
        hb = hero.data.bones[MAP[name]]
        hp = hpb[MAP[name]]
        base = (spb[sb.parent.name].matrix @ (sb.parent.matrix_local.inverted() @ sb.matrix_local)) if sb.parent else sb.matrix_local.copy()
        if name in DIRECTION_ONLY:
            q = dir_rest_world(tro, sb).rotation_difference(dir_pose_world(hero, hp))
            target = q.to_matrix() @ rot_rest_world(tro, sb)
        else:
            pose_rot = (hero.matrix_world @ hp.matrix).to_3x3().normalized()
            delta = pose_rot @ rot_rest_world(hero, hb).inverted()
            target = delta @ rot_rest_world(tro, sb)
        local_rot = sRw.inverted() @ target
        loc = base.to_translation()
        if name == "pelvis.cr":
            disp = (hero.matrix_world @ hpb["pelvis"].head) - hero_root_rest
            loc = sM.inverted() @ (root_rest + disp * K)
        pb.matrix = Matrix.Translation(loc) @ local_rot.to_4x4()
        bpy.context.view_layer.update()


def key_frame(frame):
    for p in spb:
        p.keyframe_insert("rotation_quaternion", frame=frame)
        if p.name == "pelvis.cr":
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
    tro.animation_data.action = new
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
for o in meshes + [tro]:
    o.hide_viewport = False
    o.hide_set(False)  # o arquivo traz objetos escondidos na vista, e o exportador não edita escondidos
    o.hide_render = False
for o in bpy.data.objects:
    o.select_set(o in meshes or o is tro)
bpy.context.view_layer.objects.active = tro
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
                          export_animation_mode='ACTIONS', export_skins=True, use_selection=True, export_force_sampling=True, export_morph=False)
print("OK", dst)
