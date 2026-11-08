"""Explosão de chão na morte dos chefes finais ("Bomb Crack_Ground_00 (Free)", paulyang na Sketchfab, CC BY 4.0; arquivo trazido pelo autor do projeto):
simulação do tyFlow de uma laje de concreto (500 unidades de lado) que estoura no meio, com 2 131 pedaços animados cada um como objeto (22 MB; no Godot
seriam 2 131 chamadas de desenho). Aqui fica só o entulho que se move (a laje parada sairia quadrada sobre o chão dos mapas): os MAX_PIECES pedaços maiores
viram uma malha só, presa a um esqueleto com um osso por pedaço (o movimento de cada um vira o do osso, um quadro a cada STEP). Sai com ~1/80 do tamanho
(a área do estouro com ~6 m de lado; o entulho voa até ~4 m de altura e cai espalhado), 2 materiais (lado e face do concreto), texturas de no máximo 512 px.
A animação "burst" tem 3,3 s. Vai para assets/fx/boss_crack.glb (game/combat/fx.gd, Fx.boss_crack).
uso: blender -b --python tools/assets/build_boss_crack.py -- <bomb_crack_ground_00_free.glb> <saída.glb>"""
import bpy, sys
from mathutils import Matrix, Vector

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
MAX_PIECES = 360
STEP = 2
SCALE = 0.012
MAX_TEX = 512
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in list(bpy.data.objects):
    if o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
action = bpy.data.actions[0]
f0, f1 = int(action.frame_range[0]), int(action.frame_range[1])
frames = list(range(f0, f1 + 1, STEP))
if frames[-1] != f1:
    frames.append(f1)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
track = {o: [] for o in meshes}
for f in frames:
    scene.frame_set(f)
    for o in meshes:
        track[o].append(o.matrix_world.copy())


def size(o):
    return (Vector(o.dimensions)).length


moving = [o for o in meshes if (track[o][0].to_translation() - track[o][-1].to_translation()).length > 1.0 or
          max(abs(a - b) for a, b in zip(track[o][0].to_quaternion(), track[o][-1].to_quaternion())) > 0.01]
moving.sort(key=size, reverse=True)
moving = [o for o in moving if size(o) < 200.0][:MAX_PIECES]  # a laje (inteira ou em placas grandes) não entra
print("pedaços", len(meshes), "em movimento", len(moving))
paths = [track[o] for o in moving]  # os objetos somem depois do join

# Esqueleto: um osso por pedaço, na posição de repouso = o primeiro quadro.
arm_data = bpy.data.armatures.new("crack_rig")
rig = bpy.data.objects.new("crack_rig", arm_data)
scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
names = []
for i, o in enumerate(moving):
    b = arm_data.edit_bones.new("p%03d" % i)
    b.head = track[o][0].to_translation()
    b.tail = b.head + Vector((0, 0, 5.0))
    names.append(b.name)
bpy.ops.object.mode_set(mode="OBJECT")

# Malha única: cada pedaço vai para o mundo no primeiro quadro, com peso 1 no próprio osso.
parts = []
for i, o in enumerate(moving):
    me = o.data.copy()
    me.transform(track[o][0])
    part = bpy.data.objects.new("part%03d" % i, me)
    scene.collection.objects.link(part)
    group = part.vertex_groups.new(name=names[i])
    group.add(range(len(me.vertices)), 1.0, "REPLACE")
    parts.append(part)
for o in list(bpy.data.objects):
    if o not in parts and o is not rig:
        bpy.data.objects.remove(o, do_unlink=True)
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)
bpy.ops.object.select_all(action="DESELECT")
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "boss_crack"
body.parent = rig
mod = body.modifiers.new("rig", "ARMATURE")
mod.object = rig

# Animação: a pose de cada osso = movimento do pedaço desde o primeiro quadro.
burst = bpy.data.actions.new("burst")
rig.animation_data_create()
rig.animation_data.action = burst
rest = {n: rig.data.bones[n].matrix_local.copy() for n in names}
for k, f in enumerate(frames):
    for i, path in enumerate(paths):
        pb = rig.pose.bones[names[i]]
        delta = path[k] @ path[0].inverted()
        pb.matrix = delta @ rest[names[i]]
    bpy.context.view_layer.update()
    for n in names:
        pb = rig.pose.bones[n]
        pb.keyframe_insert("location", frame=f - f0)
        pb.keyframe_insert("rotation_quaternion", frame=f - f0)
        pb.keyframe_insert("scale", frame=f - f0)
rig.matrix_world = Matrix.Scale(SCALE, 4)
for image in bpy.data.images:
    w, h = image.size
    if max(w, h) > MAX_TEX:
        image.scale(max(1, w * MAX_TEX // max(w, h)), max(1, h * MAX_TEX // max(w, h)))
print("triângulos", sum(len(p.vertices) - 2 for p in body.data.polygons), "quadros", len(frames))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_animations=True, export_animation_mode="ACTIONS",
                          export_image_format="WEBP", export_image_quality=80)
