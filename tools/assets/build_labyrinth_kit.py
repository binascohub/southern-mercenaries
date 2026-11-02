"""Peças do Labirinto para o Forte (3D Walls & Props, deadkir, CC0): arcos, paredes (com janela e porta), colunas, caixão,
escada, barril, caixote, escudo com espada e porta, como .gltf em assets/models/maps/fort/ (Lab_<nome>). Cada peça fica em pé,
base em y = 0, centrada em x/z. Arquitetura sai a 0,65 (4 m do pacote -> 2,6 m, a altura da pedra do Forte); os objetos
pequenos (caixão, barril, caixote, escudo e espada) ficam no tamanho do pacote. As texturas ficam uma vez só na pasta.
uso: blender -b -P tools/assets/build_labyrinth_kit.py -- <Labyrinth_all.FBX> assets/models/maps/fort"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
ARCH, PROP = 0.65, 1.0
PIECES = {  # peça -> (objetos do FBX, escala)
    "ArcBig": (["arc_big"], ARCH), "Arc2": (["arc_2"], ARCH), "ArcCorner": (["arc_corner"], ARCH), "ArcCross": (["arc_cross"], ARCH),
    "ArcTriple": (["arc_triple"], ARCH), "Wall": (["wall"], ARCH), "WallWindow": (["wall_windowed"], ARCH), "WallDoor": (["wall_doored"], ARCH),
    "WallLong": (["wall_long"], ARCH), "WallBroken": (["wall_long_broken"], ARCH), "Column": (["column"], ARCH),
    "ColumnBig": (["column_big"], ARCH), "ColumnSmall": (["column_small"], ARCH), "ColumnBroken": (["column_broken"], ARCH),
    "ColumnArc": (["column_arc_full"], ARCH), "Stair": (["Stair"], ARCH), "Door": (["Door"], ARCH),
    "Coffin": (["coffin", "coffin_cover"], PROP), "ShieldSword": (["shield", "sword"], PROP),
    "Barrel": (["Cylinder001"], PROP), "Crate": (["Box001"], PROP),
}


def world_bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=src)
srcobj = {o.name: o for o in bpy.data.objects}
for name, (names, scale) in PIECES.items():
    copies = []
    for n in names:
        o = srcobj[n]
        c = o.copy(); c.data = o.data.copy(); c.parent = None
        c.matrix_world = o.matrix_world.copy()
        c.animation_data_clear()  # o FBX traz uma "take" por objeto, que o exportador gravaria como animação
        bpy.context.scene.collection.objects.link(c)
        copies.append(c)
    bpy.ops.object.select_all(action="DESELECT")
    for c in copies:
        c.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    if len(copies) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = "Lab_" + name
    mn, mx = world_bbox([obj])
    print("DIMS", name, [round(v * scale, 2) for v in (mx - mn)])
    obj.data.transform(Matrix.Scale(scale, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))) @ obj.matrix_world)
    obj.parent = None
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location, obj.scale, obj.rotation_euler = (0, 0, 0), (1, 1, 1), (0, 0, 0)
    obj.delta_location, obj.delta_scale, obj.delta_rotation_euler = (0, 0, 0), (1, 1, 1), (0, 0, 0)  # o FBX traz a escala/posição aqui
    obj.rotation_mode = "XYZ"
    bpy.context.view_layer.update()
    for mat in obj.data.materials:
        if mat:
            mat.use_backface_culling = False
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Roughness"].default_value = 0.9
                bsdf.inputs["Specular IOR Level"].default_value = 0.1
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Lab_" + name + ".gltf"), export_format="GLTF_SEPARATE",
                              export_image_format="JPEG", use_selection=True, export_animations=False)
    bpy.data.objects.remove(obj)
print("OK", len(PIECES))
