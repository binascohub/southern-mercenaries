"""Necromante (necromanser.rar enviado pelo autor do projeto: "Necromancer", 128 peças de malha já ligadas a um esqueleto de 223 ossos, 11 animações em FBX — uma por arquivo — e
SEM texturas; autor/licença a confirmar): chefe do Esgoto, no lugar do Feiticeiro-Aranha. Aqui as peças viram uma malha só com 8 materiais lisos pintados por peça (pele pálida, manto roxo,
armadura escura, cajado, cabelo, ossos, correntes, couro), e as animações dos FBX entram no mesmo esqueleto: idle (idle1), walk (walk), attack (atack1), attack2 (atack2), cast (spellcast1),
hit (wound), die (death) e roar (roar). Gera assets/models/monsters/necromancer.glb (de frente para -Y do Blender, 2,2 m com o cajado).
uso: blender -b -P tools/assets/build_necromancer.py -- <pasta "Animation FBX"> <saida.glb>"""
import bpy, sys, os
from mathutils import Vector

fbx_dir, dst = sys.argv[sys.argv.index("--") + 1:][:2]
CLIPS = {"idle": "idle1", "walk": "walk", "attack": "atack1", "attack2": "atack2", "cast": "spellcast1", "hit": "wound", "die": "death", "roar": "roar"}
COLORS = {"skin": (0.52, 0.56, 0.48), "robe": (0.17, 0.07, 0.21), "armor": (0.2, 0.2, 0.26), "staff": (0.1, 0.085, 0.11), "hair": (0.1, 0.19, 0.09),
          "bone": (0.78, 0.74, 0.62), "chain": (0.42, 0.42, 0.47), "leather": (0.15, 0.11, 0.09)}
BY_NAME = {"ZBrush_defualt_group": "skin", "Group62658": "robe", "Group32033": "armor", "Group31686": "armor", "default1": "staff", "Group48766": "staff", "RetopoGroup1": "hair"}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(fbx_dir, "Necromancer@%s.fbx" % CLIPS["idle"]))
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
mats = {}
for k, c in COLORS.items():
    m = bpy.data.materials.new("m_" + k)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*c, 1)
    b.inputs["Roughness"].default_value = 0.8
    b.inputs["Metallic"].default_value = 0.35 if k == "chain" else 0.0
    mats[k] = m
for o in meshes:
    short = o.name.split(":")[-1]
    d = sorted(o.dimensions)
    c = o.matrix_world @ sum((Vector(v) for v in o.bound_box), Vector()) / 8
    if short in BY_NAME:
        kind = BY_NAME[short]
    elif d[1] < 0.1 and d[2] > 0.15:
        kind = "chain"
    elif len(o.data.polygons) >= 300 or c.z > 1.5 or (d[2] < 0.45 and d[0] > 0.1):
        kind = "bone"
    else:
        kind = "leather"
    o.data.materials.clear()
    o.data.materials.append(mats[kind])
# uma malha só
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "Necromancer_Body"
print("POLÍGONOS", len(body.data.polygons), "MATERIAIS", len(body.data.materials), "TAMANHO", [round(x, 2) for x in body.dimensions])

# animações: uma por FBX, todas no esqueleto principal
actions = {}
for name, fn in CLIPS.items():
    if name == "idle":
        act = arm.animation_data.action
    else:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=os.path.join(fbx_dir, "Necromancer@%s.fbx" % fn))
        new = [o for o in bpy.data.objects if o not in before]
        a2 = next(o for o in new if o.type == 'ARMATURE')
        act = a2.animation_data.action
        a2.animation_data.action = None
        for o in new:
            bpy.data.objects.remove(o, do_unlink=True)
    act.name = name
    act.use_fake_user = True
    actions[name] = act
    print("CLIPE", name, tuple(round(x) for x in act.frame_range))
arm.animation_data.action = None
for tr in list(arm.animation_data.nla_tracks):
    arm.animation_data.nla_tracks.remove(tr)
for name, act in actions.items():
    tr = arm.animation_data.nla_tracks.new()
    tr.name = name
    tr.strips.new(name, int(act.frame_range[0]), act)
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True)
print("OK", dst)
