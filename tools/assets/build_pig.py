"""Porco da Fazenda e de Tortuga (Domestic Pig Male, 2.90, do autor; ~/Downloads/pork.zip): o arquivo não traz
esqueleto, animação nem textura; este script monta um esqueleto simples (corpo + 4 pernas, pesos por região),
as animações "walk" e "idle" e uma textura de pele por ruído. Aplica o Subdivision, remove o esqueleto das pálpebras/córneas, reduz para
1,3 m de comprimento, mantém os pés em y = 0 e a cabeça virada para +Z (o glTF converte -Y do Blender em +Z).
uso: blender -b <DomesticPig_Male_2.90.blend> -P build_pig.py -- <saida.glb> [comprimento_m]"""
import bpy, sys

args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
length = float(args[1]) if len(args) > 1 else 1.3

for name in ("OralCavity", "Tongue", "Tooth"):  # boca fechada: a boca por dentro não aparece
    bpy.data.objects.remove(bpy.data.objects["DomesticPig_Male_" + name], do_unlink=True)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
for o in meshes:
    for m in list(o.modifiers):
        if m.type == "ARMATURE":
            o.modifiers.remove(m)
    o.parent = None
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
for o in meshes:  # aplica o Subdivision do corpo
    bpy.context.view_layer.objects.active = o
    for m in list(o.modifiers):
        if m.type == "SUBSURF":
            m.levels = min(m.levels, 1)
        bpy.ops.object.modifier_apply(modifier=m.name)
    if len(o.data.vertices) > 3000:  # malha muito densa: reduz para ~10 mil vértices
        d = o.modifiers.new("dec", "DECIMATE")
        d.ratio = min(1.0, 10000.0 / len(o.data.vertices))
        bpy.ops.object.modifier_apply(modifier=d.name)
    print("VERTS", o.name, len(o.data.vertices))
for o in list(bpy.data.objects):
    if o.type != "MESH":
        bpy.data.objects.remove(o, do_unlink=True)
body = bpy.data.objects["DomesticPig_Male_Body"]
factor = length / body.dimensions.y
for o in meshes:
    o.scale = (factor,) * 3
    o.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# --- Textura de pele (o .blend não traz imagem): rosa com manchas suaves e sardas, por ruído.
import numpy as np
rng = np.random.default_rng(7)
N = 512


def smooth(res):
    small = rng.random((res, res))
    big = np.kron(small, np.ones((N // res, N // res)))
    k = np.ones(N // res) / (N // res)
    for ax in (0, 1):
        big = np.apply_along_axis(lambda v: np.convolve(np.pad(v, N // res, mode="wrap"), k, "same")[N // res:-N // res], ax, big)
    return big


blot = smooth(8) * 0.6 + smooth(32) * 0.4
fine = rng.random((N, N))
base = np.array([0.7, 0.46, 0.43])
dark = np.array([0.55, 0.33, 0.31])
t = np.clip((blot - 0.3) * 2.2, 0, 1)[..., None]
rgb = base * (1 - t) + dark * t
rgb *= (0.94 + 0.12 * fine)[..., None]
rgb[(fine > 0.995)] = (0.45, 0.28, 0.25)  # sardas
pix = np.dstack([np.clip(rgb, 0, 1), np.ones((N, N))])[::-1].astype(np.float32)
skin = bpy.data.images.new("pig_skin", N, N)
skin.pixels.foreach_set(pix.ravel())
skin.pack()

COLORS = {"Eyelid": (0.8, 0.5, 0.48, 1), "cornea": (0.92, 0.9, 0.85, 1), "Pupil": (0.02, 0.015, 0.01, 1)}
for o in meshes:
    key = o.name.replace("DomesticPig_Male_", "")
    mat = bpy.data.materials.new("pig_" + key)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.85
    if key == "Body":
        tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = skin
        mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = COLORS.get(key, (0.8, 0.5, 0.48, 1))
    o.data.materials.clear()
    o.data.materials.append(mat)

# --- Esqueleto: "Body" e quatro pernas (FL/FR na frente, HL/HR atrás), juntas no alto da perna.
from math import radians
ys = [v.co.y for v in body.data.vertices]
ymid = (min(ys) + max(ys)) / 2.0
TOP = body.dimensions.z * 0.42  # altura da junta (quadril/ombro)
leg_y = {"F": min(ys) + (max(ys) - min(ys)) * 0.22, "H": min(ys) + (max(ys) - min(ys)) * 0.82}
arm_data = bpy.data.armatures.new("PigArmature")
arm = bpy.data.objects.new("PigArmature", arm_data)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
root = arm_data.edit_bones.new("Body")
root.head, root.tail = (0, ymid - 0.2, TOP), (0, ymid + 0.2, TOP)
for fh in "FH":
    for side, sx in (("L", 1), ("R", -1)):
        b = arm_data.edit_bones.new(fh + side)
        b.head, b.tail = (sx * 0.08, leg_y[fh], TOP), (sx * 0.08, leg_y[fh], 0.0)
        b.parent = root
bpy.ops.object.mode_set(mode="OBJECT")
for o in meshes:
    o.vertex_groups.new(name="Body")
    if o == body:
        for n in ("FL", "FR", "HL", "HR"):
            o.vertex_groups.new(name=n)
        for v in o.data.vertices:
            w = max(0.0, min(1.0, (TOP - v.co.z) / (TOP * 0.5)))  # 0 no alto, 1 do meio da perna para baixo
            if w > 0.0:
                name = ("F" if v.co.y < ymid else "H") + ("L" if v.co.x > 0 else "R")
                o.vertex_groups[name].add([v.index], w, "REPLACE")
            if w < 1.0:
                o.vertex_groups["Body"].add([v.index], 1.0 - w, "REPLACE")
    else:
        o.vertex_groups["Body"].add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
    mod = o.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    o.parent = arm

# --- Animações: andar (pernas em diagonal, 1 s) e parado (respiração leve).
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
arm.animation_data_create()
pb = arm.pose.bones
for b in pb:
    b.rotation_mode = "XYZ"
SWING = radians(28)
walk = bpy.data.actions.new("walk")
arm.animation_data.action = walk
phase = {"FL": 0.0, "HR": 0.0, "FR": 0.5, "HL": 0.5}
for f in range(0, 25, 3):
    t = f / 24.0
    for n, ph in phase.items():
        import math
        pb[n].rotation_euler = (SWING * math.sin(2 * math.pi * (t + ph)), 0, 0)
        pb[n].keyframe_insert("rotation_euler", frame=f + 1)
    pb["Body"].location = (0, 0, 0.012 * abs(math.sin(2 * math.pi * t * 2)))
    pb["Body"].keyframe_insert("location", frame=f + 1)
idle = bpy.data.actions.new("idle")
arm.animation_data.action = idle
for f, k in ((1, 0.0), (25, 1.0), (49, 0.0)):
    for n in ("FL", "FR", "HL", "HR"):
        pb[n].rotation_euler = (0, 0, 0)
        pb[n].keyframe_insert("rotation_euler", frame=f)
    pb["Body"].location = (0, 0, 0.006 * k)
    pb["Body"].keyframe_insert("location", frame=f)
arm.animation_data.action = None
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_apply=True, export_animation_mode="ACTIONS",
                          export_yup=True, use_selection=False, export_image_format="WEBP")
print("OK", out, [a.name for a in bpy.data.actions])
