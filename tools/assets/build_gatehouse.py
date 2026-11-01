"""Portão do Forte (Medieval Gatehouse, Daniel Andersson / Daniel74, CC0, opengameart.org/content/medieval-gatehouse):
assets/models/maps/Gatehouse.glb, a entrada do Forte no fim da Floresta Escura. O .blend traz o portão e as peças soltas
(grades, portas, alçapões, bandeira) com texturas embutidas: tudo vai junto numa malha só. Em pé, base em y = 0,
centrado em x/z, 0,7 da escala do arquivo (29 m -> ~20 m de largura) e com a frente (a grade de entrada) para +Z.
uso: blender -b -P tools/assets/build_gatehouse.py -- <GateHouse2Upload.blend> <saída.glb> [render.png]"""
import bpy, sys, math
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
preview = args[2] if len(args) > 2 else None
SCALE = 0.7
bpy.ops.wm.open_mainfile(filepath=src)
objs = [o for o in bpy.data.objects if o.type == "MESH"]
sc = bpy.context.scene
for o in objs:
    if o.name not in sc.collection.all_objects:
        sc.collection.objects.link(o)
    o.hide_set(False) if o.name in bpy.context.view_layer.objects else None
    o.hide_render = False
    for mod in list(o.modifiers):
        o.modifiers.remove(mod)
pts = [o.matrix_basis @ Vector(c) for o in objs for c in o.bound_box]   # sem pais: matrix_basis = mundo
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
# frente do arquivo = +Y do Blender (grade da frente, bandeira); gira 180° em Z para a frente ficar em -Y (= +Z no glTF)
flip = Matrix.Rotation(math.pi, 4, "Z")
shift = Matrix.Scale(SCALE, 4) @ flip @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
for o in objs:
    o.data.transform(o.matrix_basis)
    o.matrix_basis = Matrix.Identity(4)
    o.data.transform(shift)
bpy.ops.object.select_all(action="DESELECT")
for o in objs:
    o.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="JPEG", export_apply=False)
print("OK largura %.1f x profundidade %.1f x altura %.1f m" % ((mx.x - mn.x) * SCALE, (mx.y - mn.y) * SCALE, (mx.z - mn.z) * SCALE))
if preview:
    for o in list(bpy.data.objects):
        if o.type in ("CAMERA", "LIGHT"):
            bpy.data.objects.remove(o, do_unlink=True)
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam)
    cam.data.clip_end = 1000
    cam.location = (14, -26, 7); cam.rotation_euler = (math.radians(78), 0, math.radians(28)); sc.camera = cam
    sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"
    sc.render.resolution_x = 800; sc.render.resolution_y = 600; sc.render.filepath = preview
    bpy.ops.render.render(write_still=True)
