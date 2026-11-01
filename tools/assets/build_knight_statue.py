"""Estátua do cavaleiro do Cemitério: assets/models/maps/Statue_Knight.glb ("Knight Statue", yd, OpenGameArt, CC0).
O .blend traz um cavaleiro ajoelhado (malha com esqueleto), a espada, o escudo, a coroa do elmo e o pedestal;
aqui a pose é assada na malha, tudo vira uma peça só em pedra cinza, em pé, base em y = 0, centrada em x/z.
(A versão sentada do mesmo pacote tem a espada e o escudo fora do lugar no arquivo e não foi usada.)
uso: blender -b knight_statue.blend --python tools/assets/build_knight_statue.py -- assets/models/maps/Statue_Knight.glb"""
import bpy, sys
from mathutils import Vector, Matrix

out = sys.argv[sys.argv.index("--") + 1]
HEIGHT = 2.4
deps = bpy.context.evaluated_depsgraph_get()
parts = []
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    ev = o.evaluated_get(deps)
    mesh = bpy.data.meshes.new_from_object(ev)       # com o esqueleto na pose do arquivo
    mesh.transform(ev.matrix_world)
    obj = bpy.data.objects.new(o.name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    parts.append(obj)
for o in list(bpy.data.objects):
    if o not in parts:
        bpy.data.objects.remove(o, do_unlink=True)

mat = bpy.data.materials.new("Statue_Stone")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.36, 0.37, 0.36, 1.0)
bsdf.inputs["Roughness"].default_value = 0.92
for o in parts:
    o.data.materials.clear()
    o.data.materials.append(mat)

pts = [Vector(c) for o in parts for c in o.bound_box]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
s = HEIGHT / (mx.z - mn.z)
shift = Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
for o in parts:
    o.data.transform(shift)
bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
bpy.ops.object.shade_smooth()
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_apply=False)
print("OK", out, "pé %.2f x %.2f m" % ((mx.x - mn.x) * s, (mx.y - mn.y) * s))
