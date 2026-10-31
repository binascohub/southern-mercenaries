"""Cabeça do rato (malhas Head, Eyes, Teeth em repouso, sem esqueleto) para a
Rainha de corpo humano. Mantém as coordenadas do rat.glb (frente +Z no Godot).
uso: rat_head.py <rat.glb> <saida.glb>"""
import bpy, sys
args = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args[0])
keep = {"Head", "Eyes", "Teeth"}
for o in list(bpy.data.objects):
    if o.type == "ARMATURE" and o.animation_data:
        o.animation_data.action = None
bpy.context.view_layer.update()
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.name not in keep:
        continue
    deps = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps))
    mesh.transform(o.matrix_world)
    new = bpy.data.objects.new(o.name + "_static", mesh)
    bpy.context.scene.collection.objects.link(new)
for o in list(bpy.data.objects):
    if not o.name.endswith("_static"):
        bpy.data.objects.remove(o, do_unlink=True)
for o in bpy.data.objects:
    o.name = o.name.replace("_static", "")
    pts = [v.co for v in o.data.vertices]
    print("BB", o.name, [round(min(p[i] for p in pts), 3) for i in range(3)], [round(max(p[i] for p in pts), 3) for i in range(3)])
bpy.ops.export_scene.gltf(filepath=args[1], export_format="GLB", export_image_format="WEBP", export_image_quality=85)
print("OK")
