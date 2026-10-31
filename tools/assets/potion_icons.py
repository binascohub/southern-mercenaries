"""Ícones do inventário (128 px, fundo transparente) a partir das Potions
(Clint Bellanger, CC BY 3.0): cada consumível com o frasco e a cor do líquido.
uso: potion_icons.py <potions_0.blend> <pasta de saída>"""
import bpy, sys, math, os
src, out = sys.argv[sys.argv.index("--") + 1:]
ICONS = {
    "potion_health": ("HealthPotion", (0.85, 0.08, 0.1)),
    "potion_resource": ("ManaPotion", (0.15, 0.35, 1.0)),
    "elemental_potion_fire": ("HealthElixir", (1.0, 0.45, 0.12)),
    "elemental_potion_water": ("ManaElixir", (0.3, 0.62, 1.0)),
    "elemental_potion_air": ("HealthElixir", (0.82, 0.68, 1.0)),
    "elemental_potion_earth": ("HealthElixir", (0.55, 0.72, 0.3)),
    "return_charm": ("HealthVial", (1.0, 0.8, 0.3)),
}
os.makedirs(out, exist_ok=True)
for icon, (obj, color) in ICONS.items():
    bpy.ops.wm.open_mainfile(filepath=src)
    sc = bpy.context.scene
    keep = bpy.data.objects[obj]
    for o in list(bpy.data.objects):
        if o != keep:
            bpy.data.objects.remove(o, do_unlink=True)
    keep.location = (0, 0, 0)
    for slot in keep.material_slots:
        mat = slot.material.copy()
        slot.material = mat
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        nodes.clear()
        o_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
        if "Liquid" in mat.name:
            bsdf.inputs["Base Color"].default_value = (*color, 1)
            bsdf.inputs["Emission Color"].default_value = (*color, 1)
            bsdf.inputs["Emission Strength"].default_value = 0.6
        elif mat.name.startswith("Glass"):
            bsdf.inputs["Base Color"].default_value = (0.85, 0.92, 0.95, 1)
            bsdf.inputs["Roughness"].default_value = 0.05
            bsdf.inputs["Alpha"].default_value = 0.35
        else:
            bsdf.inputs["Base Color"].default_value = (0.45, 0.3, 0.18, 1)
    bpy.context.view_layer.update()
    pts = [keep.matrix_world @ v.co for v in keep.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    size = max(hi[i] - lo[i] for i in range(3))
    mid = [(lo[i] + hi[i]) / 2 for i in range(3)]
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = size * 1.25
    cam.location = (mid[0] + size * 2, mid[1] - size * 3, mid[2] + size * 1.2)
    direction = (cam.location[0] - mid[0], cam.location[1] - mid[1], cam.location[2] - mid[2])
    from mathutils import Vector
    cam.rotation_euler = Vector(direction).to_track_quat("Z", "Y").to_euler()
    sc.camera = cam
    for ang, e in ((45, 3.5), (-35, 1.5)):
        l = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); l.data.energy = e
        l.rotation_euler = (math.radians(ang), 0, math.radians(30)); sc.collection.objects.link(l)
    w = bpy.data.worlds.new("w"); w.color = (0.4, 0.4, 0.42); sc.world = w
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = 128
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.filepath = os.path.join(out, icon + ".png")
    bpy.ops.render.render(write_still=True)
    print("OK", icon)
