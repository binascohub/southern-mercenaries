"""O navio do autor (gerado com trimesh, Z para cima): põe de pé (Y para cima no
glTF), aplica a rotação e marca os materiais como dupla face (as velas são planos)."""
import bpy, sys, math
args = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args[0])
for o in bpy.data.objects:
    if o.parent is None:
        o.rotation_mode = "XYZ"
        o.rotation_euler.x += math.radians(-90)
bpy.context.view_layer.update()
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = [o for o in bpy.data.objects if o.type == "MESH"][0]
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
for m in bpy.data.materials:
    m.use_backface_culling = False
bpy.ops.export_scene.gltf(filepath=args[1], export_format="GLB")
print("OK", args[1])
