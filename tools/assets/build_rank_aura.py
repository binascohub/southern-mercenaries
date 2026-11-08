"""Brilho do rank dos equipamentos no herói ("MorphageSpace", tamminen na Sketchfab, CC BY 4.0; arquivo trazido pelo autor do projeto): o modelo é uma esfera
de vidro com uma nuvem de ~490 mil triângulos soltos e brilhantes dentro (mais densa no meio), girando. Aqui sai o vidro e ficam 6 000 triângulos
sorteados da nuvem, em 5 malhas de 1 200 ("rank_1" .. "rank_5"): o jogo acende uma malha a mais por rank médio dos equipamentos (game/actors/player.gd).
A nuvem é achatada no formato do herói (elipse de 0,8 m de raio e 2 m de altura, de pé em z = 0) e cada triângulo cresce em volta do
próprio centro até ~4 cm de lado; o miolo fica aberto (o herói aparece dentro), para aparecer de longe. Sem material (o jogo põe o brilho aditivo dourado). Vai para assets/fx/rank_aura.glb.
uso: blender -b --python tools/assets/build_rank_aura.py -- <morphagespace.glb> <saída.glb>"""
import bpy, sys
import numpy as np

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
TIERS = 5
PER_TIER = 1200
RADIUS, HEIGHT = 0.8, 2.0
SPECK = 0.04  # lado médio de cada faísca no jogo (m): os triângulos da nuvem são de milímetros e sumiriam de longe
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
tris = []
for o in [o for o in bpy.data.objects if o.type == "MESH" and o.data.materials and o.data.materials[0].name == "material_1"]:
    me = o.data
    co = np.zeros(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3) @ np.array(o.matrix_world)[:3, :3].T + np.array(o.matrix_world)[:3, 3]
    idx = np.zeros(len(me.polygons) * 3, dtype=np.int64)
    me.polygons.foreach_get("vertices", idx)
    tris.append(co[idx.reshape(-1, 3)])
tris = np.concatenate(tris)
print("triângulos na nuvem", len(tris))
rng = np.random.default_rng(20261108)
pick = tris[rng.choice(len(tris), TIERS * PER_TIER, replace=False)]
center = pick.mean(axis=(0, 1))
pick = pick - center
reach = np.percentile(np.linalg.norm(pick.reshape(-1, 3), axis=1), 97)
# Miolo aberto: o herói fica visível dentro da nuvem (a original é mais densa no meio). O raio relativo r vai a 0,45 + 0,55 r.
mid = pick.mean(axis=1, keepdims=True)
r = np.linalg.norm(mid, axis=2, keepdims=True) / reach
pick = pick + mid * ((0.45 + 0.55 * np.minimum(r, 1.0)) / np.maximum(r, 1e-6) - 1.0)
pick = pick / reach * np.array([RADIUS, RADIUS, HEIGHT / 2]) + np.array([0, 0, HEIGHT / 2])
mid = pick.mean(axis=1, keepdims=True)
side = np.linalg.norm(pick[:, 1] - pick[:, 0], axis=1).mean()
pick = mid + (pick - mid) * (SPECK / side)
print("lado médio antes", round(float(side), 4), "m")
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for t in range(TIERS):
    part = pick[t * PER_TIER:(t + 1) * PER_TIER]
    me = bpy.data.meshes.new("rank_%d" % (t + 1))
    me.from_pydata(part.reshape(-1, 3).tolist(), [], np.arange(len(part) * 3).reshape(-1, 3).tolist())
    obj = bpy.data.objects.new("rank_%d" % (t + 1), me)
    bpy.context.scene.collection.objects.link(obj)
print("malhas", TIERS, "x", PER_TIER, "triângulos")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_materials="NONE")
