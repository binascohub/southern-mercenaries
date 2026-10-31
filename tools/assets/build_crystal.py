"""Cristal (Fantasy Crystals, Brett Post-Script, CC BY-SA 4.0): Crystal_003 de pé,
centrado, 0,28 m (ponta do cajado do Mago); e ícones 128 px dos cristais de refino
na cor de cada material.
uso: build_crystal.py <Crystal_003.fbx> <saida.glb> <pasta dos ícones>"""
import bpy, sys, os, math
from mathutils import Vector, Matrix
src, out, icons = sys.argv[sys.argv.index("--") + 1:]
def load():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=src)
    deps = bpy.context.evaluated_depsgraph_get()
    o = [x for x in bpy.data.objects if x.type == "MESH"][0]
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), depsgraph=deps)
    mesh.transform(o.matrix_world)
    for x in list(bpy.data.objects):
        bpy.data.objects.remove(x, do_unlink=True)
    pts = [v.co for v in mesh.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    size = hi - lo
    axis = max(range(3), key=lambda i: size[i])
    fix = Matrix.Translation(-(lo + hi) / 2)
    if axis == 0: fix = Matrix.Rotation(1.5708, 4, "Y") @ fix
    elif axis == 1: fix = Matrix.Rotation(-1.5708, 4, "X") @ fix
    mesh.transform(Matrix.Scale(0.28 / size[axis], 4) @ fix)
    obj = bpy.data.objects.new("Crystal", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj
obj = load()
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB")
COLORS = {"iron": (0.29, 0.30, 0.31), "steel": (0.72, 0.75, 0.78), "copper": (0.75, 0.42, 0.24),
    "silver": (0.93, 0.95, 0.96), "gold": (0.89, 0.70, 0.24)}
os.makedirs(icons, exist_ok=True)
for name, c in COLORS.items():
    obj = load()
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    b = mat.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = 0.15
    b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = 0.35
    obj.data.materials.clear(); obj.data.materials.append(mat)
    obj.rotation_euler = (0.3, 0.2, 0.4)
    sc = bpy.context.scene
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"; cam.data.ortho_scale = 0.36
    cam.location = (0, -1, 0); cam.rotation_euler = (math.radians(90), 0, 0); sc.camera = cam
    for ang, e in ((45, 3.5), (-35, 1.5)):
        l = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); l.data.energy = e
        l.rotation_euler = (math.radians(ang), 0, math.radians(30)); sc.collection.objects.link(l)
    w = bpy.data.worlds.new("w"); w.color = (0.4, 0.4, 0.42); sc.world = w
    sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = 128; sc.render.image_settings.color_mode = "RGBA"
    sc.render.filepath = os.path.join(icons, "crystal_%s.png" % name)
    bpy.ops.render.render(write_still=True)
print("OK")
