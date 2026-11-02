"""Gorila (Gorilla (male), Micket, CC0, opengameart.org/content/gorilla-male): a malha baixa poli, sem esqueleto nem
textura, com o espelho aplicado, numa cor de pelo escuro; frente para +Z (glTF), pés em y = 0, 1,5 m de altura.
É o Urso Guardião (companheiro "bear" do Invocador) trocado por um gorila.
uso: build_gorilla.py <gorilla_male.blend> <saída.glb>"""
import bpy, sys, math
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
for o in list(bpy.data.objects):
    if o.type != "MESH":
        bpy.data.objects.remove(o, do_unlink=True)
obj = bpy.data.objects["Crocodile"]  # o nome do objeto no arquivo é errado: é o gorila
deps = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(obj.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)  # com o espelho aplicado
me.transform(obj.matrix_world)
bpy.data.objects.remove(obj, do_unlink=True)
obj = bpy.data.objects.new("Gorilla", me)
bpy.context.scene.collection.objects.link(obj)
FRONT_YAW = float(sys.argv[sys.argv.index("--") + 3]) if len(sys.argv) > sys.argv.index("--") + 3 else 0.0
me.transform(Matrix.Rotation(math.radians(FRONT_YAW), 4, "Z"))
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 1.5 / (mx.z - mn.z)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
for poly in me.polygons:
    poly.use_smooth = True
mat = bpy.data.materials.new("Fur")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.035, 0.03, 0.027, 1.0)
bsdf.inputs["Roughness"].default_value = 0.95
me.materials.clear()
me.materials.append(mat)
obj.name = "Gorilla"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB")
print("OK gorilla", [round(x * k, 2) for x in (mx - mn)])
