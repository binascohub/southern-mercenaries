"""Flechas do Arqueiro por elemento ("Arrows", Akshat, CC-BY 4.0, sketchfab.com/3d-models/arrows-2763023886cb4cb2a920b292d7024051): o arquivo traz 5 flechas
(cada uma com haste "handle", penas "arrowL/arrowR" e ponta "head"/"Plane", e um material por flecha). Cada flecha vira uma peça do Kit, deitada com a ponta para +Z
(Y do Blender = -Z do Godot; aqui a ponta vai para -Y do Blender), 0,8 m de comprimento, centro na origem.
uso: blender -b -P tools/assets/build_element_arrows.py -- <arrows.glb> <pasta de saída> <grupo>=<peça> ...
  grupos: gp, gb, gold, blue, redd (ex.: redd=Arrow_Fire blue=Arrow_Water gold=Arrow_Air gp=Arrow_Earth)"""
import bpy, sys, os
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index("--") + 1:]
src, out_dir = args[0], args[1]
wanted = dict(a.split("=", 1) for a in args[2:])
HANDLES = {"handle.001": "gp", "handle.002": "gb", "handle.003": "gold", "handle.004": "blue", "handle.005": "redd"}
HEADS = {"head_": "gp", "head.001": "gb"}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)


def group_of(name: str) -> str:
    for prefix, group in HANDLES.items():
        if name.startswith(prefix):
            return group
    for prefix, group in HEADS.items():
        if name.startswith(prefix):
            return group
    for group in ("gold", "blue", "redd", "gp", "gb"):
        if "_%s_" % group in name:
            return group
    return ""


groups = {}
for o in bpy.context.scene.objects:
    if o.type == "MESH":
        groups.setdefault(group_of(o.name), []).append(o)
for image in bpy.data.images:  # texturas em 512 px: a flecha é pequena na tela
    if image.size[0] > 512:
        image.scale(512, 512)
for group, piece in wanted.items():
    objs = groups.get(group, [])
    if not objs:
        print("sem grupo", group)
        continue
    for o in objs:
        o.data = o.data.copy()
        o.data.transform(o.matrix_world)
        o.parent = None
        o.matrix_world = Matrix.Identity(4)
    for o in objs:  # pontas com dezenas de milhares de vértices: reduz para ~3 mil (projétil pequeno, muitos ao mesmo tempo)
        if len(o.data.vertices) > 5000:
            bpy.context.view_layer.objects.active = o
            mod = o.modifiers.new("d", "DECIMATE")
            mod.ratio = 3000 / len(o.data.vertices)
            bpy.ops.object.modifier_apply(modifier="d")
    pts = [v.co for o in objs for v in o.data.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    axis = max(range(3), key=lambda i: mx[i] - mn[i])
    center = (mn + mx) / 2
    # A ponta é o lado da "head"/"Plane"; as penas ficam no outro.
    tips = [o for o in objs if o.name.startswith(("head", "Plane"))]
    tip_c = sum((v.co for o in tips for v in o.data.vertices), Vector()) / max(1, sum(len(o.data.vertices) for o in tips))
    sign = 1.0 if tip_c[axis] > center[axis] else -1.0
    # Eixo da flecha -> -Y do Blender (vira +Z no Godot), ponta para -Y.
    to_y = {0: Matrix.Rotation(1.5707963, 4, "Z"), 1: Matrix.Identity(4), 2: Matrix.Rotation(-1.5707963, 4, "X")}[axis]
    m = Matrix.Scale(0.8 / (mx[axis] - mn[axis]), 4) @ to_y @ Matrix.Translation(-center)
    for o in objs:
        o.data.transform(m)
    if (to_y @ Vector((sign if axis == 0 else 0, sign if axis == 1 else 0, sign if axis == 2 else 0)))[1] > 0:
        for o in objs:
            o.data.transform(Matrix.Rotation(3.14159265, 4, "Z"))
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    joined.name = joined.data.name = piece
    bpy.ops.export_scene.gltf(filepath=os.path.join(out_dir, piece + ".glb"), export_format="GLB", use_selection=True,
                              export_animations=False, export_image_format="WEBP")
    print("ok", group, piece, len(joined.data.vertices))
