"""Armas dos heróis a partir do "Weapons - Medieval Pack 1" (Smeagain, CC BY 3.0): cajado, arco, espada longa e adaga,
uma .glb por arma, de pé (ponta/cabeça para +Y), com a origem no meio do comprimento e o tamanho do jogo.
As partes de metal usam o material "Silver" (o jogo as tinge com o material equipado).
uso: blender -b "Weapons - Basic Pack.blend" --python build_smeagain_weapons.py -- <saída: assets/models/props>"""
import bpy, sys, os
import numpy as np
from mathutils import Vector, Matrix

out = sys.argv[sys.argv.index("--") + 1]
# nome: (objetos, comprimento em m, ponta: "thin" = ponta mais fina, "wide" = cabeça mais larga, "any")
WEAPONS = {
    "Weapon_MS_Staff": (["BezierCurve.003"], 1.7, "wide"),
    "Weapon_MS_Bow": (["BezierCurve.001", "BezierCurve.002", "Cylinder.003"], 1.3, "any"),
    "Weapon_MS_Sword": (["Cube", "Cylinder", "Cylinder.001"], 1.15, "thin"),
    "Weapon_MS_Dagger": (["Cube.002", "Cube.003"], 0.45, "thin"),
}
LIGHT = ("Weapon_MS_Sword", "Weapon_MS_Dagger")
SILVER = ("Blade", "Smooth Metal", "Dagger", "Hamer Silver", "Silver", "Decorative Metal")
COLORS = {"Silver": ((0.78, 0.8, 0.84, 1), 0.85, 0.3), "Wood": ((0.32, 0.2, 0.1, 1), 0.0, 0.7),
          "Leather": ((0.16, 0.1, 0.07, 1), 0.0, 0.7), "Gold": ((0.8, 0.62, 0.2, 1), 0.9, 0.35),
          "Cord": ((0.85, 0.82, 0.7, 1), 0.0, 0.8)}


def kind(name):
    if name in SILVER:
        return "Silver"
    if "Leather" in name or "Handle" in name or "Black" in name:
        return "Leather"
    if name in ("Brass", "Copper", "Hamer Gold"):
        return "Gold"
    if "String" in name:
        return "Cord"
    return "Wood"


src = bpy.data.filepath
for name, (objs, length, tip) in WEAPONS.items():
    bpy.ops.wm.open_mainfile(filepath=src)
    deps = bpy.context.evaluated_depsgraph_get()
    parts = []
    for oname in objs:
        o = bpy.data.objects[oname]
        # Sem os modificadores de subdivisão (a espada passaria de 40 mil polígonos).
        m = o.data.copy() if name in LIGHT else bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
        m.transform(o.matrix_world)
        parts.append(m)
    mesh = parts[0]
    bm_objs = []
    for extra in parts[1:]:
        tmp = bpy.data.objects.new("tmp", extra)
        bpy.context.scene.collection.objects.link(tmp)
        bm_objs.append(tmp)
    first = bpy.data.objects.new("first", mesh)
    bpy.context.scene.collection.objects.link(first)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in [first] + bm_objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = first
    if bm_objs:
        bpy.ops.object.join()
    mesh = first.data
    pts = np.array([v.co[:] for v in mesh.vertices])
    c = pts.mean(axis=0)
    _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
    axis = vt[0]
    t = (pts - c) @ axis
    lo, hi = t.min(), t.max()
    span = hi - lo
    side = np.cross(pts - c, axis)
    spread = np.linalg.norm(side, axis=1)
    a = spread[t < lo + span * 0.1].mean()
    b = spread[t > hi - span * 0.1].mean()
    if (tip == "thin" and b > a) or (tip == "wide" and b < a):
        axis = -axis
    z = Vector(axis).normalized()
    rot = z.rotation_difference(Vector((0, 0, 1))).to_matrix().to_4x4()
    mesh.transform(Matrix.Translation(-Vector(c)))
    mesh.transform(rot)
    p2 = np.array([v.co[:] for v in mesh.vertices])
    mn, mx = p2.min(axis=0), p2.max(axis=0)
    mesh.transform(Matrix.Translation(-Vector(((mn + mx) / 2).tolist())))
    mesh.transform(Matrix.Scale(length / (mx[2] - mn[2]), 4))
    for poly in mesh.polygons:
        poly.use_smooth = True
    seen = {}
    for i, mat in enumerate(mesh.materials):
        k = kind(mat.name)
        if k not in seen:
            nm = bpy.data.materials.new(k)
            nm.use_nodes = True
            bsdf = nm.node_tree.nodes["Principled BSDF"]
            col, metal, rough = COLORS[k]
            bsdf.inputs["Base Color"].default_value = col
            bsdf.inputs["Metallic"].default_value = metal
            bsdf.inputs["Roughness"].default_value = rough
            seen[k] = nm
        mesh.materials[i] = seen[k]
    for other in list(bpy.data.objects):
        if other != first:
            bpy.data.objects.remove(other, do_unlink=True)
    first.name = name
    bpy.ops.object.select_all(action="DESELECT")
    first.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", use_selection=True)
    print("OK", name, length, "polys", len(mesh.polygons))
