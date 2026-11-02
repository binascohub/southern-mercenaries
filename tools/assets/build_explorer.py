"""A Exploradora (explorer.glb do autor, Sketchfab "Female NPC 06": exploradora de capuz, jaqueta, luvas, bolsa e bermuda, 5 mil vértices, texturas de 128 a 512 px, esqueleto b_MF de 89 ossos e sem
animação; autoria e licença a confirmar) animada com o pacote de animações dos heróis (Universal Animation Library): as 5 partes, na pose do arquivo (A-pose; no modo REPOUSO o Sketchfab pode deitar o
modelo), viram UMA malha "Explorer"; os braços giram para a T-pose dos heróis (pelos pesos de braço do arquivo, em volta do ombro) e os PESOS DO PRÓPRIO ARQUIVO passam para o esqueleto de
hero_female.glb, osso por osso; nos braços os pesos são refeitos por posição (clavícula, braço, antebraço e mão, com transição larga no ombro). 1,72 m (a altura do esqueleto dos heróis).
  blender -b -P tools/assets/build_explorer.py -- ~/Downloads/explorer.glb assets/models/characters/hero_female.glb assets/models/characters/explorer.glb"""
import bpy, sys, math, re
import numpy as np
from mathutils import Vector

src, hero, out = sys.argv[sys.argv.index("--") + 1:][:3]
HEIGHT = 1.72
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
elf_arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
elf_meshes = [o for o in bpy.data.objects if o.type == "MESH" and len(o.data.vertices) > 100]
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()


def pose_head(part):
    for pb in elf_arm.pose.bones:
        if part in pb.name:
            return elf_arm.matrix_world @ pb.head
    return None


SHOULDER = {s: (pose_head("UpperArm_%s" % s), pose_head("Hand_%s_" % s)) for s in ("L", "R")}
SIDE = {s: ("l" if SHOULDER[s][0].x > 0 else "r") for s in ("L", "R")}  # lado do herói de cada lado do Bip001


def hero_bone(n):
    side = SIDE["L"] if re.search(r"_L(_|$)", n) else SIDE["R"] if re.search(r"_R(_|$)", n) else ""
    if "Weapon" in n or "IK_" in n or "Camera" in n or "Attach" in n:
        return "spine_03"
    if "Thumb" in n and side:
        return "thumb_%02d_%s" % (int(re.search(r"Thumb_(\d\d)", n).group(1)), side)
    if "Finger" in n and side:
        return "hand_" + side
    for key, bone in (("Clavicle", "clavicle"), ("UpperArm", "upperarm"), ("Armroll", "upperarm"), ("Forearm", "lowerarm"), ("ForeTwist", "lowerarm"), ("Hand", "hand"),
                      ("Thigh", "thigh"), ("Calf", "calf"), ("Foot", "foot"), ("Toe", "ball")):
        if key in n and side:
            return "%s_%s" % (bone, side)
    for key, bone in (("Spine_03", "spine_03"), ("Spine_02", "spine_02"), ("Spine_01", "spine_01"), ("BackMount", "spine_03"), ("Neck", "neck_01"), ("Pelvis", "pelvis"), ("Crotch", "pelvis")):
        if key in n:
            return bone
    if any(k in n for k in ("Head", "Face", "jaw", "Lip", "Corner", "brow")):
        return "Head"
    return "pelvis"


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


parts = []
for o in elf_meshes:
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    mesh.transform(o.matrix_world)
    names = {g.index: g.name for g in o.vertex_groups}
    weights = []
    for ov in o.data.vertices:
        w = {}
        for g in ov.groups:
            if g.weight > 0.0:
                b = hero_bone(names[g.group])
                w[b] = w.get(b, 0.0) + g.weight
        weights.append(w)
    for side, (sh, hand) in SHOULDER.items():
        sx = 1.0 if hand.x > sh.x else -1.0
        d = hand - sh
        angle = math.atan2(d.z, d.x * sx)
        c, sn = math.cos(-angle), math.sin(-angle)
        arm_len = d.length
        for v, w in zip(mesh.vertices, weights):
            a = min(sum(val for b, val in w.items() if b.endswith("_" + SIDE[side]) and b.split("_")[0] in ("upperarm", "lowerarm", "hand", "thumb", "index", "middle", "ring", "pinky")), 1.0)
            if a <= 0.0:
                continue
            rx, rz = (v.co.x - sh.x) * sx, v.co.z - sh.z
            nx, nz = rx * c - rz * sn, rx * sn + rz * c
            v.co.x = v.co.x * (1 - a) + (sh.x + nx * sx) * a
            v.co.z = v.co.z * (1 - a) + (sh.z + nz) * a
            if a > 0.5:  # braço: pesos por posição ao longo do braço (já na T-pose)
                t = ((v.co.x - sh.x) * sx) / arm_len
                s_ = SIDE[side]
                up = 1.0 - smooth((t - 0.38) / 0.12)
                hd = smooth((t - 0.86) / 0.1)
                w.clear()
                # ombro: transição larga (~18 cm) da clavícula para o braço; antes (2 cm) o ombro rasgava ao baixar o braço
                arm_w = smooth((t + 0.08) / 0.33)
                w["clavicle_" + s_] = 1.0 - arm_w
                w["upperarm_" + s_] = arm_w * up
                w["lowerarm_" + s_] = arm_w * (1.0 - up) * (1.0 - hd)
                w["hand_" + s_] = arm_w * hd
    new = bpy.data.objects.new(o.name, mesh)
    bpy.context.scene.collection.objects.link(new)
    new.vertex_groups.clear()
    for b in sorted({b for w in weights for b in w}):
        new.vertex_groups.new(name=b)
    for i, w in enumerate(weights):
        tot = sum(w.values()) or 1.0
        for b, val in w.items():
            if val > 0.0:
                new.vertex_groups[b].add([i], val / tot, "REPLACE")
    parts.append(new)
for o in list(bpy.data.objects):
    if o not in parts:
        bpy.data.objects.remove(o, do_unlink=True)
for img in bpy.data.images:
    if img.size[0] > 0:
        img.pack()
bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "Explorer"
mesh = body.data
pts = np.array([tuple(v.co) for v in mesh.vertices])
pts *= HEIGHT / (pts[:, 2].max() - pts[:, 2].min())
pts[:, 2] -= pts[:, 2].min()
pts[:, 0] -= (pts[:, 0].max() + pts[:, 0].min()) / 2
bpy.ops.import_scene.gltf(filepath=hero)
hero_arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
for o in list(bpy.data.objects):
    if o.type == "MESH" and o is not body:
        bpy.data.objects.remove(o, do_unlink=True)
torso = (pts[:, 2] > 0.9) & (pts[:, 2] < 1.2) & (np.abs(pts[:, 0]) < 0.1)
pts[:, 1] += (hero_arm.matrix_world @ hero_arm.data.bones["spine_02"].head_local).y - float(np.median(pts[torso, 1]))
for v, p in zip(mesh.vertices, pts):
    v.co = Vector(p)
body.parent = hero_arm
body.matrix_parent_inverse = hero_arm.matrix_world.inverted()
mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = hero_arm
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animation_mode="ACTIONS", export_image_format="WEBP", export_image_quality=85)
print("OK", out, [round(v, 2) for v in body.dimensions], len(mesh.vertices), len(body.vertex_groups))
