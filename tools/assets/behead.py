"""Tira a cabeça (e cabelo/chifres) de um personagem com esqueleto, para pôr
outra cabeça presa ao osso: apaga as faces dos materiais dados e os vértices
com peso forte nos grupos da cabeça. Salva um .blend novo.
uso: behead.py <entrada.blend> <saida.blend> <objeto> <materiais,...> <grupos,...> [peso]"""
import bpy, bmesh, sys
a = sys.argv[sys.argv.index("--") + 1:]
src, out, obj = a[0], a[1], a[2]
mats = set(a[3].split(",")); groups = set(a[4].split(","))
limit = float(a[5]) if len(a) > 5 else 0.5
bpy.ops.wm.open_mainfile(filepath=src)
o = bpy.data.objects[obj]
index = {g.index for g in o.vertex_groups if g.name in groups}
slots = {i for i, s in enumerate(o.material_slots) if s.material and s.material.name in mats}
gone_v = {v.index for v in o.data.vertices if sum(g.weight for g in v.groups if g.group in index) >= limit}
bm = bmesh.new(); bm.from_mesh(o.data)
bm.verts.ensure_lookup_table()
faces = [f for f in bm.faces if f.material_index in slots or any(v.index in gone_v for v in f.verts)]
bmesh.ops.delete(bm, geom=faces, context="FACES")
loose = [v for v in bm.verts if not v.link_faces]
bmesh.ops.delete(bm, geom=loose, context="VERTS")
bm.to_mesh(o.data); bm.free()
print("FACES LEFT", len(o.data.polygons))
bpy.ops.wm.save_as_mainfile(filepath=out)
