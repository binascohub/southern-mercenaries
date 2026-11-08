"""Chafariz da praça central da Capital ("fountain water simulation", UJJWAL CHAUHAN na Sketchfab, CC BY 4.0; arquivo trazido pelo autor).
O original tem 69 MB: a água (e até a pedra) é animada por 60 alvos de morph, quadro a quadro. Aqui:
- a pedra (h_1Shape) fica parada, no quadro 0, reduzida a ~16 mil triângulos;
- a grama quadrada de 20 m embaixo (hShape) sai: o piso é o da cidade;
- a água (fShape, a coluna que cai, e f_1/f_2/f_3, os espelhos das bacias) vira uma malha só, mais leve (WATER_RATIO dos
  triângulos), que copia o movimento da original com o modificador Surface Deform; ela ganha um alvo de morph a cada STEP
  quadros (12 no ciclo) e a animação "Flow" passa de um para o outro em loop.
Escala: DIAMETER metros de largura, de pé em z = 0, centro em x = y = 0. Texturas no máximo MAX_TEX px (WebP).
uso: blender -b --python tools/assets/build_fountain.py -- <fountain_water_simulation.glb> <saída.glb>"""
import bpy, sys
from mathutils import Matrix, Vector
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
DIAMETER = 4.6
STONE_TRIS = 16000
STEP = 4
MAX_TEX = 512
WATER = ["fShape", "f_1Shape", "f_2Shape", "f_3Shape"]
WATER_RATIO = {"fShape": 0.2, "f_1Shape": 0.2, "f_2Shape": 1.0, "f_3Shape": 1.0}  # as bacias de cima já são leves (e o Surface Deform não prende nelas)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene = bpy.context.scene
action = bpy.data.actions[0]
first, last = (int(f) for f in action.frame_range)
stone_src = bpy.data.objects["h_1Shape"]
mn = [min((stone_src.matrix_world @ Vector(c))[i] for c in stone_src.bound_box) for i in range(3)]
mx = [max((stone_src.matrix_world @ Vector(c))[i] for c in stone_src.bound_box) for i in range(3)]
k = DIAMETER / max(mx[0] - mn[0], mx[1] - mn[1])
fit = Matrix.Scale(k, 4) @ Matrix.Translation(Vector(((mn[0] + mx[0]) / -2, (mn[1] + mx[1]) / -2, -mn[2])))


def snapshot(names: list, frame: int, label: str) -> bpy.types.Object:
    """As malhas avaliadas (com o morph do quadro) juntas num objeto novo, já na escala do jogo."""
    scene.frame_set(frame)
    dg = bpy.context.evaluated_depsgraph_get()
    parts = []
    for name in names:
        src_obj = bpy.data.objects[name]
        mesh = bpy.data.meshes.new_from_object(src_obj.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        mesh.transform(fit @ src_obj.matrix_world)
        obj = bpy.data.objects.new(label, mesh)
        scene.collection.objects.link(obj)
        parts.append(obj)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    if len(parts) > 1:
        bpy.ops.object.join()
    return bpy.context.view_layer.objects.active


def apply_decimate(obj: bpy.types.Object, **kw) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("dec", "DECIMATE")
    for key, value in kw.items():
        setattr(mod, key, value)
    bpy.ops.object.modifier_apply(modifier="dec")


stone = snapshot(["h_1Shape"], first, "Fountain_Stone")
tris = sum(len(p.vertices) - 2 for p in stone.data.polygons)
apply_decimate(stone, ratio=min(1.0, STONE_TRIS / tris))
# Para cada água: uma cópia leve do quadro 0, no mesmo lugar da original, presa a ela pelo Surface Deform.
scene.frame_set(first)
dg = bpy.context.evaluated_depsgraph_get()
light = []
for name in WATER:
    src_obj = bpy.data.objects[name]
    if WATER_RATIO[name] >= 1.0:
        light.append(name)
        continue
    low = bpy.data.objects.new(name + "_low", bpy.data.meshes.new_from_object(src_obj.evaluated_get(dg), depsgraph=dg))
    scene.collection.objects.link(low)
    low.matrix_world = src_obj.matrix_world
    apply_decimate(low, ratio=WATER_RATIO[name])
    mod = low.modifiers.new("follow", "SURFACE_DEFORM")
    mod.target = src_obj
    bpy.ops.object.surfacedeform_bind(modifier="follow")
    assert mod.is_bound, "Surface Deform não prendeu " + name
    light.append(low.name)
frames = list(range(first, last, STEP))
water_frames = [snapshot(light, frame, "Fountain_Water_%d" % frame) for frame in frames]
counts = {len(o.data.vertices) for o in water_frames}
assert len(counts) == 1, "quadros da água com vértices diferentes: %s" % counts
water = water_frames[0]
water.name = "Fountain_Water"
water.shape_key_add(name="Basis")
for obj in water_frames[1:]:
    key = water.shape_key_add(name="f%d" % frames[water_frames.index(obj)], from_mix=False)
    for v, src_v in zip(key.data, obj.data.vertices):
        v.co = src_v.co
# Ciclo: o alvo i vale 1 no quadro i*STEP e 0 nos vizinhos; no fim volta à base (o quadro 0), fechando o loop.
keys = water.data.shape_keys
keys.animation_data_create()
flow = bpy.data.actions.new("Flow")
keys.animation_data.action = flow
for i, block in enumerate(keys.key_blocks[1:], start=1):
    for t, value in ((i - 1, 0.0), (i, 1.0), (i + 1, 0.0)):
        block.value = value
        block.keyframe_insert("value", frame=t * STEP)
for obj in water_frames[1:]:
    bpy.data.objects.remove(obj, do_unlink=True)
for obj in [o for o in bpy.data.objects if o not in (stone, water)]:
    bpy.data.objects.remove(obj, do_unlink=True)
for obj in (stone, water):
    for poly in obj.data.polygons:
        poly.use_smooth = True
for image in bpy.data.images:
    w, h = image.size
    if max(w, h) > MAX_TEX:
        s = MAX_TEX / max(w, h)
        image.scale(max(1, int(w * s)), max(1, int(h * s)))
scene.frame_start, scene.frame_end = 0, len(frames) * STEP
print("pedra", sum(len(p.vertices) - 2 for p in stone.data.polygons), "tri; água", len(water.data.vertices), "vért x", len(keys.key_blocks), "formas")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_image_format="WEBP", export_image_quality=80,
                          export_morph_tangent=False, export_animation_mode="ACTIONS")
