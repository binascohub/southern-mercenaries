"""Peças do castelo para o Forte (3D Castle Dungeon Tileset Extended, rubberduck, CC0): colunas, arcos de portão com as
portas abertas, paredes com tocha / janela / decoração, o altar decorativo e o piso de lajotas, como .gltf em
assets/models/maps/fort/ (Castle_<nome>). Cada peça fica em pé, base em y = 0, centrada em x/z, escalada para a mesma
altura da pedra do Forte (SCALE: 4 m do pacote -> 2,6 m). As texturas ficam uma vez só na pasta (nomes do próprio pacote).
uso: blender -b <pasta>/3d-tileset-1-1.blend -P tools/assets/build_castle_kit.py -- assets/models/maps/fort"""
import bpy, sys, os, math
from mathutils import Vector, Matrix
out = sys.argv[sys.argv.index("--") + 1]
SCALE = 0.65
# nome da peça -> objetos do .blend; portas: (objeto, lado da dobradiça) abertas em ~90 graus
PIECES = {
    "Column": ["castle-column"], "ColumnB": ["column"], "EdgeColumn": ["edge-column-1"],
    "Wall": ["castle-wall"], "WallTorch1": ["caslte-wall-w-torch-1"], "WallTorch2": ["caslte-wall-w-torch-2"],
    "WallWindow": ["castle-wall-w-window"], "WallWindowBig": ["castle-wall-w-window-big"], "WallDeco": ["castle-wall-w-deco-1"],
    "WallThing": ["caslte-wall-w-thing"],
    "GateBig": ["caslte-wall-w-gate-big", "gate-big-part-1", "gate-big-part-2"],
    "GateSmall": ["caslte-wall-w-gate-small", "gate-small-part-1", "gate-small-part-2"],
    "GateNew": ["castle-wall-gate-new", "gate-new-left", "gate-new-right"],
    "Altar": ["decorative-1"], "Dais": ["decorative-2"], "Tiles": ["ground-tile-2-4"], "Mug": ["mug"],
}
DOORS = {"gate-new-left": 1, "gate-new-right": -1}


def world_bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


src = {o.name: o for o in bpy.data.objects}
for name, names in PIECES.items():
    copies = []
    for n in names:
        o = src[n]
        c = o.copy(); c.data = o.data.copy(); c.parent = None
        c.matrix_world = o.matrix_world.copy()
        bpy.context.scene.collection.objects.link(c)
        if n in DOORS:  # porta aberta: gira em torno da borda de fora
            mn, mx = world_bbox([c])
            side = DOORS[n]
            hinge = Vector((mn.x if side > 0 else mx.x, (mn.y + mx.y) / 2, 0))
            c.matrix_world = Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(-90 * side), 4, "Z") @ Matrix.Translation(-hinge) @ c.matrix_world
        copies.append(c)
    bpy.ops.object.select_all(action="DESELECT")
    for c in copies:
        c.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = "Castle_" + name
    mn, mx = world_bbox([obj])
    obj.data.transform(Matrix.Scale(SCALE, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))) @ obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    for mat in obj.data.materials:
        if mat:
            mat.use_backface_culling = False
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Castle_" + name + ".gltf"), export_format="GLTF_SEPARATE",
                              export_image_format="JPEG", use_selection=True)
    bpy.data.objects.remove(obj)
print("OK", len(PIECES))
