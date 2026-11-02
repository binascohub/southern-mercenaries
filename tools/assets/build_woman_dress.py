"""Mulher de vestido (z-h Fantasy Outfit 21 FREE, woman1.zip do autor; autoria e licença a confirmar): o pacote traz só a roupa (vestido longo bordô com mangas
bufantes transparentes), sem corpo. Aqui o vestido (versão THIN WELD, 437 mil vértices) é reduzido para ~30 mil, as mangas passam da A-pose para a T-pose
dos heróis (como em rig_to_ual.py), as texturas de 4096 px caem para 1024 (cor com a opacidade das mangas e da corrente no alfa, e normal) e a malha é presa ao
esqueleto de hero_female.glb (pesos automáticos; da cintura para baixo a saia fica toda no osso do quadril, pois as pernas não aparecem). Ficam do corpo dos
heróis a cabeça, os olhos, as sobrancelhas, o cabelo comprido e a pele das mãos (de Ranger_Arms). Todas as animações dos heróis seguem no arquivo.
uso: blender -b -P tools/assets/build_woman_dress.py -- "<pasta>/z-h_Fantasy Outfit 21-THIN WELD.fbx" "<pasta>/Textures/PBR Metallic Roughness" assets/models/characters/woman_dress.glb"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

fbx, tex_dir, out = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath="assets/models/characters/hero_female.glb")
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
KEEP = {"Head", "Eyes", "Eyebrows", "Hair_Long", "Ranger_Arms"}
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

# --- Vestido
before = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=fbx)
dress = [o for o in bpy.data.objects if o not in before and o.type == "MESH"][0]
for o in list(bpy.data.objects):
    if o not in before and o is not dress:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.objects.active = dress
mesh = dress.data
mesh.transform(dress.matrix_world)
dress.matrix_world = dress.matrix_world.__class__.Identity(4)
dress.parent = None
dress.rotation_euler = (0, 0, 0)
dress.scale = (1, 1, 1)
tris = len(mesh.polygons)
dec = dress.modifiers.new("dec", "DECIMATE")
dec.ratio = min(1.0, 30000.0 / tris)
bpy.ops.object.modifier_apply(modifier="dec")
mesh = dress.data
pts = [v.co for v in mesh.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
mesh.transform(__import__("mathutils").Matrix.Translation(Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z))))
print("DRESS", [round(hi[i] - lo[i], 3) for i in range(3)], len(mesh.vertices), len(mesh.polygons))

bones = arm.data.bones
def bone_head(n):
    return arm.matrix_world @ bones[n].head_local
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

# --- Materiais: cor (+ opacidade no alfa) e normal, a 1024 px
def load(name, cs):
    img = bpy.data.images.load(os.path.join(tex_dir, "z-h_Fantasy Outfit 21-" + name + ".png"))
    img.colorspace_settings.name = cs
    img.scale(1024, 1024)
    return img
color = load("BaseColor", "sRGB")
opacity = load("Opacity", "Non-Color")
normal = load("Normal", "Non-Color")
cp = list(color.pixels)
op = list(opacity.pixels)
for i in range(0, len(cp), 4):
    cp[i + 3] = op[i]
color.pixels.foreach_set(cp)
color.colorspace_settings.name = "sRGB"
color.pack()
normal.pack()


def make(name, blend):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    o_node = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.8
    nt.links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = color
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    ntex = nt.nodes.new("ShaderNodeTexImage")
    ntex.image = normal
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(ntex.outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    if blend:
        nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
        mat.surface_render_method = "BLENDED"
    mat.use_backface_culling = False
    return mat

solid, sheer = make("DressSolid", False), make("DressSheer", True)
names = [m.name for m in mesh.materials]
print("SLOTS", names)
mesh.materials.clear()
mesh.materials.append(solid)
mesh.materials.append(sheer)
for p in mesh.polygons:
    p.material_index = 1 if ("Opacity" in names[p.material_index]) else 0

# --- Pesos, por posição (o automático falha nesta malha: as mangas ficavam paradas): da cintura para baixo, só o quadril; o tronco vai do quadril à
# coluna alta; cada braço (x além do ombro) vai da clavícula ao braço, ao antebraço, com transição suave nas juntas.
for o in bpy.context.view_layer.objects:
    o.select_set(False)
dress.vertex_groups.clear()
dress.parent = arm
dress.matrix_parent_inverse = arm.matrix_world.inverted()
if not any(m.type == "ARMATURE" for m in dress.modifiers):
    mod = dress.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
groups = {}
def group(n):
    if n not in groups:
        groups[n] = dress.vertex_groups.new(name=n)
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
print("GROUPS", len(dress.vertex_groups))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animation_mode="ACTIONS", export_image_format="WEBP", export_image_quality=85)
print("OK", out)
