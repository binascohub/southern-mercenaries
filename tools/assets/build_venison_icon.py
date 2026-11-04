"""Ícone da Carne de Cervo (assets/ui/icons/venison.png, 128 px): render do modelo do autor (~/Downloads/low-poly_raw_meat.glb, carne crua low-poly; autoria e licença a confirmar)
em fundo transparente, visto de cima e de lado. O modelo também fica em assets/models/props/Raw_Meat.glb (peça de cenário).
uso: blender -b -P tools/assets/build_venison_icon.py -- <low-poly_raw_meat.glb> <venison.png> <Raw_Meat.glb>"""
import bpy, sys, math, mathutils
src, out_png, out_glb = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
for o in meshes:
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
pts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
mn = mathutils.Vector([min(p[i] for p in pts) for i in range(3)])
mx = mathutils.Vector([max(p[i] for p in pts) for i in range(3)])
center = (mn + mx) / 2
size = max(mx - mn)
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"
sc.display.shading.color_type = "TEXTURE"
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = 128
cam_data = bpy.data.cameras.new("c")
cam_data.type = "ORTHO"
cam_data.ortho_scale = size * 1.25
cam = bpy.data.objects.new("c", cam_data)
sc.collection.objects.link(cam)
sc.camera = cam
cam.location = center + mathutils.Vector((0, -size * 2.0, size * 1.6))
cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = out_png
bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(cam, do_unlink=True)
# peça de cenário: base em z = 0, centrada, ~0,45 m de comprimento
k = 0.45 / size
for o in meshes:
    o.data.transform(mathutils.Matrix.Translation((-center.x, -center.y, -mn.z)))
    o.data.transform(mathutils.Matrix.Scale(k, 4))
bpy.ops.export_scene.gltf(filepath=out_glb, export_format="GLB", use_selection=False, export_image_format="WEBP")
print("OK", out_png, out_glb)
