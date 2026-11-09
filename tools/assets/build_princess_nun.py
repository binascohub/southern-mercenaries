"""Princesa-freira (rainha) que anda pela Capital ("Princess Nun Royal Queen", Prozone, CC-BY 4.0, sketchfab.com/3d-models/princess-nun-royal-queen-74b7fd7e20db45438ca7516911257c89;
ATENÇÃO: os nós do arquivo vêm com o nome "desirefx.me", site que redistribui modelos pagos: confirmar a origem antes de publicar). O arquivo é estático, em A-pose,
vestido longo até os tornozelos, com corpo e cabeça próprios. Como em build_noble_knight.py / build_woman_dress.py: as peças viram uma malha de 1,72 m presa ao esqueleto de
hero_female.glb por posição: o vestido no quadril, o tronco e os braços (parados na pose do arquivo, ao longo do corpo: as mangas largas espetavam quando os braços
dos heróis desciam) do quadril à coluna alta, a cabeça e o véu no osso da cabeça.
Todas as animações dos heróis seguem no arquivo.
uso: blender -b -P tools/assets/build_princess_nun.py -- <princess_nun_royal_queen.glb> assets/models/characters/princess_nun.glb"""
import bpy, bmesh, sys, math
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath="assets/models/characters/hero_female.glb")
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
for o in list(bpy.data.objects):
    if o.type == "MESH":
        bpy.data.objects.remove(o, do_unlink=True)

# --- A princesa: as peças numa malha só
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
bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
armor = parts[0]
armor.name = "Princess_Nun"
mesh = armor.data
for image in bpy.data.images:
    if image.size[0] > 1024:
        image.scale(1024, 1024)

bones = arm.data.bones
def bone_head(n):
    return arm.matrix_world @ bones[n].head_local
# Escala e posição: 1,72 m (a altura do esqueleto dos heróis), pés no chão, centrada em x/y.
pts = [v.co for v in mesh.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
k = 1.72 / (hi.z - lo.z)
neck = bone_head("neck_01")
mesh.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z))))
pts = [v.co for v in mesh.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
print("PRINCESS", [round(hi[i] - lo[i], 3) for i in range(3)], "k", round(k, 4), "neck", [round(c, 3) for c in neck], len(mesh.vertices))

# Os braços ficam na pose do arquivo (A-pose, ao longo do corpo), presos ao tronco: as mangas largas não acompanham os braços dos heróis.



# --- Pesos por posição: do quadril para baixo, o quadril (o vestido longo esconde as pernas); o tronco e os braços vão do quadril à coluna alta, pela altura;
# do pescoço para cima, a cabeça (com a transição no pescoço, abaixo do queixo: misturar tronco e cabeça no rosto o deformava).
bpy.ops.object.select_all(action="DESELECT")
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
neck_z = bone_head("neck_01").z
for v in mesh.vertices:
    z = v.co.z
    t = smooth((z - (pelvis_z + 0.05)) / (chest_z - pelvis_z))
    w = {"pelvis": 1.0 - t, "spine_03": t}
    h = smooth((z - (neck_z - 0.06)) / 0.05)
    if h > 0.0:
        w = {n: val * (1 - h) for n, val in w.items()}
        w["head"] = h
    for n, val in w.items():
        if val > 0.001:
            group(n).add([v.index], val, "REPLACE")
print("GROUPS", len(armor.vertex_groups))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animation_mode="ACTIONS", export_image_format="WEBP", export_image_quality=85)
print("OK", out)
