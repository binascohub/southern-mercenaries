"""Cavaleira nobre ("Female Noble Knight Armor", Meast, CC-BY 4.0, sketchfab.com/3d-models/female-noble-knight-armor-5b40c2e4b40d48378d595268d2db69bb): o arquivo traz
só a armadura (peitoral, saia, braços, cintos e capas, 12 peças, em centímetros e em A-pose), sem corpo. Como em build_woman_dress.py: as peças viram uma
malha, a escala põe a gola na altura do pescoço de hero_female.glb, os braços passam da A-pose para a T-pose dos heróis e a malha é presa ao esqueleto por
posição (da cintura para baixo a saia fica no osso do quadril). Ficam do corpo dos heróis a cabeça, os olhos, as sobrancelhas, o cabelo comprido, a pele das mãos
(de Ranger_Arms), as calças e as botas (Ranger_Legs, Ranger_Feet: a saia acaba no joelho). Todas as animações dos heróis seguem no arquivo.
uso: blender -b -P tools/assets/build_noble_knight.py -- <female_noble_knight_armor.glb> assets/models/characters/noble_knight.glb"""
import bpy, bmesh, sys, math
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath="assets/models/characters/hero_female.glb")
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
KEEP = {"Head", "Eyes", "Eyebrows", "Hair_Long", "Ranger_Arms", "Ranger_Legs", "Ranger_Feet"}
for o in list(bpy.data.objects):
    if o.type == "MESH" and o.name not in KEEP:
        bpy.data.objects.remove(o, do_unlink=True)
# Ranger_Arms: só a pele (as mãos), sem a manga de tecido.
arms_obj = bpy.data.objects["Ranger_Arms"]
skin_slots = [i for i, m in enumerate(arms_obj.data.materials) if m and "Regular" in m.name]
bm = bmesh.new()
bm.from_mesh(arms_obj.data)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index not in skin_slots], context="FACES")
bm.to_mesh(arms_obj.data)
bm.free()
arms_obj.name = "Hands"

# --- Armadura: as 12 peças numa malha só
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=src)
parts = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
for o in parts:
    o.data = o.data.copy()
    o.data.transform(o.matrix_world)
    o.parent = None
    o.matrix_world = Matrix.Identity(4)
for o in list(bpy.data.objects):
    if o not in before and o not in parts:
        bpy.data.objects.remove(o, do_unlink=True)
for o in bpy.context.view_layer.objects:
    o.select_set(False)
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
armor = parts[0]
armor.name = "Noble_Armor"
mesh = armor.data
for image in bpy.data.images:
    if image.size[0] > 1024:
        image.scale(1024, 1024)

bones = arm.data.bones
def bone_head(n):
    return arm.matrix_world @ bones[n].head_local
# Escala e posição: a gola (o ponto mais alto) um pouco acima da base do pescoço; centrada em x/y, a saia no lugar.
pts = [v.co for v in mesh.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
neck = bone_head("neck_01")
k = (neck.z + 0.06) / hi.z
mesh.transform(Matrix.Translation(Vector((neck.x, neck.y, 0))) @ Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2 + 0.0, 0))))
pts = [v.co for v in mesh.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
print("ARMOR", [round(hi[i] - lo[i], 3) for i in range(3)], "k", round(k, 4), "neck", [round(c, 3) for c in neck], len(mesh.vertices))

for side in ("l", "r"):
    shoulder = bone_head("upperarm_" + side)
    hand = bone_head("hand_" + side)
    sx = 1.0 if hand.x > 0 else -1.0
    arm_verts = [v for v in mesh.vertices if v.co.x * sx > abs(shoulder.x) - 0.02 and v.co.z > shoulder.z - 0.55]
    far = sorted(arm_verts, key=lambda v: -v.co.x * sx)[:max(5, len(arm_verts) // 50)]
    tip = sum((v.co for v in far), Vector()) / len(far)
    reach_mesh = Vector((tip.x - shoulder.x, tip.z - shoulder.z))
    reach_bone = Vector((hand.x - shoulder.x, hand.z - shoulder.z)) * 1.1
    angle = math.atan2(reach_bone.y, reach_bone.x) - math.atan2(reach_mesh.y, reach_mesh.x)
    k = reach_bone.length / max(reach_mesh.length, 0.01)
    for v in arm_verts:
        d = Vector((v.co.x - shoulder.x, v.co.z - shoulder.z))
        if d.x * sx <= 0:
            continue
        w = min(1.0, (d.x * sx) / 0.12)
        r = Vector((d.x * math.cos(angle) - d.y * math.sin(angle), d.x * math.sin(angle) + d.y * math.cos(angle))) * k
        new = d.lerp(r, w)
        v.co.x = shoulder.x + new.x
        v.co.z = shoulder.z + new.y
    print("ARM", side, round(math.degrees(angle), 1), round(k, 2))


# --- Pesos, por posição (o automático falha nesta malha: as mangas ficavam paradas): da cintura para baixo, só o quadril; o tronco vai do quadril à
# coluna alta; cada braço (x além do ombro) vai da clavícula ao braço, ao antebraço, com transição suave nas juntas.
for o in bpy.context.view_layer.objects:
    o.select_set(False)
armor.vertex_groups.clear()
armor.parent = arm
armor.matrix_parent_inverse = arm.matrix_world.inverted()
if not any(m.type == "ARMATURE" for m in armor.modifiers):
    mod = armor.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
groups = {}
def group(n):
    if n not in groups:
        groups[n] = armor.vertex_groups.new(name=n)
    return groups[n]
def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)
pelvis_z = bone_head("pelvis").z
chest_z = bone_head("spine_03").z
shoulder_x = abs(bone_head("upperarm_l").x)
elbow_x = abs(bone_head("lowerarm_l").x)
wrist_x = abs(bone_head("hand_l").x)
for v in mesh.vertices:
    x, z = v.co.x, v.co.z
    side = "l" if x > 0 else "r"
    ax = abs(x)
    w = {}
    # tronco (quadril -> coluna alta, pela altura)
    t = smooth((z - (pelvis_z + 0.05)) / (chest_z - pelvis_z))
    torso = {"pelvis": 1.0 - t, "spine_03": t}
    # braço: de 0 (no tronco) a 1 (além do ombro)
    a = smooth((ax - (shoulder_x - 0.06)) / 0.12) if z > pelvis_z + 0.25 else 0.0
    arm_w = {}
    if a > 0.0:
        e = smooth((ax - (elbow_x - 0.05)) / 0.10)
        arm_w = {"upperarm_" + side: 1.0 - e, "lowerarm_" + side: e}
    for n, val in torso.items():
        if val * (1 - a) > 0.001:
            w[n] = w.get(n, 0) + val * (1 - a)
    for n, val in arm_w.items():
        if val * a > 0.001:
            w[n] = w.get(n, 0) + val * a
    if z < pelvis_z + 0.05:
        w = {"pelvis": 1.0}
    for n, val in w.items():
        group(n).add([v.index], val, "REPLACE")
print("GROUPS", len(armor.vertex_groups))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animation_mode="ACTIONS", export_image_format="WEBP", export_image_quality=85)
print("OK", out)
