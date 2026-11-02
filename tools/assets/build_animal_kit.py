"""Crocodilo e pombo do Animal Kit 1.0 (britdawgmasterfunk, Sketchfab, CC Attribution 4.0 — o título diz CC0, mas a licença registrada é CC-BY 4.0, então o
crédito vai no CREDITS.md): o pacote é um .blend de esculturas sem textura nem animação (só esqueletos de pose). Aqui os dois bichos que o Invocador usa
saem com os modificadores aplicados (subdivisão, deslocamento e esqueleto em repouso), reduzidos de polígonos (Decimate) e em cor lisa:
Animal_Alligator.glb (1,3 m de comprimento, cabeça para +Z, verde-musgo) e Animal_Pigeon.glb (0,32 m de corpo, de asas abertas, azul-acinzentado). Pés em y = 0.
uso: build_animal_kit.py <animal_kit_1_0.blend> <pasta de saída> [alligator_flip pigeon_flip]   (flip = 1 vira o bicho de frente para trás)"""
import bpy, sys, math
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
ROT = {"ALLIGATOR": -90.0, "pigeon": 90.0}  # graus em torno de Z
flips = {"ALLIGATOR": int(args[2]) if len(args) > 2 else 0, "pigeon": int(args[3]) if len(args) > 3 else 0}
bpy.ops.wm.open_mainfile(filepath=src)
TARGETS = {"ALLIGATOR": ("Animal_Alligator", 1.3, (0.16, 0.24, 0.11, 1.0), 7000, 0), "pigeon": ("Animal_Pigeon", 0.32, (0.42, 0.45, 0.55, 1.0), 4500, 1)}  # (nome, comprimento do corpo, cor, faces, eixo do corpo: 0 = X, 1 = Y; o pombo está de asas abertas ao longo de X)
deps = bpy.context.evaluated_depsgraph_get()
built = {}
for name, (out_name, length, color, faces, body_axis) in TARGETS.items():
    o = bpy.data.objects[name]
    me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=False, depsgraph=deps)
    me.transform(o.matrix_world)
    print("FACES evaluated", name, len(me.polygons))
    built[name] = (out_name, length, color, faces, body_axis, me)
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for name, (out_name, length, color, faces, body_axis, me) in built.items():
    ob = bpy.data.objects.new(out_name, me)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    mod = ob.modifiers.new("Decimate", "DECIMATE")
    mod.ratio = min(1.0, faces / max(len(me.polygons), 1))
    bpy.ops.object.modifier_apply(modifier=mod.name)
    me = ob.data
    pts = [v.co for v in me.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    # gira em torno do vertical para a cabeça ficar para -Y do Blender (= +Z do glTF): o jacaré tem a cabeça em +X (-90 graus); o pombo, em +Y... (ver o ângulo do pombo na linha de comando)
    me.transform(Matrix.Rotation(math.radians(ROT[name] + (180.0 if flips[name] else 0.0)), 4, "Z"))
    pts = [v.co for v in me.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    k = length / (mx.y - mn.y)
    me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    for poly in me.polygons:
        poly.use_smooth = True
    mat = bpy.data.materials.new(out_name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = 0.7
    me.materials.clear()
    me.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=out + "/" + out_name + ".glb", export_format="GLB", use_selection=True)
    print("OK", out_name, len(me.polygons), "faces", [round(x * k, 2) for x in (mx - mn)])
