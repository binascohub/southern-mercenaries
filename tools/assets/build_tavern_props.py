"""Peças da Taverna do "Medieval Tavern Props Pack" (System G6, CC0) em .glb, uma por objeto do .blend:
Tv_Fireplace, Tv_Fire (brasas), Tv_Firewood, Tv_Table, Tv_Table_Round, Tv_Stool_Wood, Tv_Stool_Round, Tv_Bench,
Tv_Barrel, Tv_Basket, Tv_Bucket, Tv_Sack, Tv_Sack_2, Tv_Lamp, Tv_Candle, Tv_Tankard, Tv_Plate, Tv_Counter, Tv_Torch.
Em pé, base em y = 0, centro em x/z, na altura (h) ou na maior medida (l) em metros; texturas em WebP de 512 px.
uso: blender -b -P build_tavern_props.py -- <pasta do pacote extraído> <saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
pack, out = sys.argv[sys.argv.index("--") + 1:]
blend = os.path.join(pack, "medieval_tavern_props_pack.blend")
# nome do glb: (objeto, "h" altura | "l" maior medida, metros)
PIECES = {
    "Tv_Fireplace": ("fireplace_2", "h", 3.8), "Tv_Fire": ("firewood_burning", "l", 0.6),
    "Tv_Firewood": ("firewood", "l", 0.55), "Tv_Table": ("table_wood", "h", 0.78),
    "Tv_Table_Round": ("table_wood_round", "h", 0.75), "Tv_Stool_Wood": ("chair_wood", "h", 0.46),
    "Tv_Stool_Round": ("chair_wood_2", "h", 0.45), "Tv_Bench": ("shelf_wood", "h", 0.46),
    "Tv_Barrel": ("barrel", "h", 0.9), "Tv_Basket": ("basket", "h", 0.8), "Tv_Bucket": ("bucket_wood", "h", 0.4),
    "Tv_Sack": ("sack", "l", 0.8), "Tv_Sack_2": ("sack_2", "h", 0.5), "Tv_Lamp": ("lamp_wood", "h", 0.6),
    "Tv_Candle": ("candle_plate", "h", 0.14), "Tv_Tankard": ("tankard_wood", "h", 0.14),
    "Tv_Plate": ("plate_wood", "l", 0.22), "Tv_Counter": ("bar_counter", "l", 4.2), "Tv_Torch": ("torch_2", "h", 0.9),
}
for name, (obj_name, mode, size) in PIECES.items():
    bpy.ops.wm.open_mainfile(filepath=blend)
    for o in list(bpy.data.objects):
        if o.name != obj_name:
            bpy.data.objects.remove(o, do_unlink=True)
    o = bpy.data.objects[obj_name]
    deps = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    mesh.transform(o.matrix_world)
    o.modifiers.clear()
    o.parent = None
    o.matrix_world = Matrix.Identity(4)
    o.data = mesh
    pts = [v.co for v in mesh.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    scale = size / ((mx.z - mn.z) if mode == "h" else max(mx - mn))
    mesh.transform(Matrix.Scale(scale, 4) @ Matrix.Translation(-Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))))
    for image in bpy.data.images:
        if image.size[0] > 512:
            image.scale(512, 512)
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", use_selection=True,
        export_image_format="WEBP", export_image_quality=88)
    print("OK", name, [round(v * scale, 2) for v in (mx - mn)], len(mesh.polygons))
