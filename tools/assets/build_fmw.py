"""Fantasy Melee Weapons (Brett Post-Script, CC BY-SA 4.0): uma .glb por arma
(a variante básica de cada uma), de pé (maior medida no eixo vertical), centrada,
no tamanho do jogo; as cores lisas do pacote.
uso: build_fmw.py <pasta dos .fbx> <saida>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
LENGTH = {"Dagger": 0.45, "Long_Sword": 1.1, "Great_Sword": 1.5, "War_Axe": 0.9, "Great_Axe": 1.4, "Hammer": 0.9,
    "Mace": 0.85, "Spiked_Mace": 0.95, "Club": 0.85, "Spear": 2.2, "Polearm": 2.3, "Quarterstaff": 1.8, "Scythe": 1.9}
for name, length in LENGTH.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(src, name + ".fbx"))
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    deps = bpy.context.evaluated_depsgraph_get()
    joined = []
    for o in meshes:
        m = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
        m.transform(o.matrix_world)
        joined.append(m)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    objs = []
    for m in joined:
        o = bpy.data.objects.new("Weapon_" + name, m)
        bpy.context.scene.collection.objects.link(o)
        objs.append(o)
    pts = [v.co for o in objs for v in o.data.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    size = hi - lo
    axis = max(range(3), key=lambda i: size[i])
    fix = Matrix.Translation(-(lo + hi) / 2)
    if axis == 0:
        fix = Matrix.Rotation(1.5708, 4, "Y") @ fix
    elif axis == 1:
        fix = Matrix.Rotation(-1.5708, 4, "X") @ fix
    fix = Matrix.Scale(length / size[axis], 4) @ fix
    for o in objs:
        o.data.transform(fix)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Weapon_FM_" + name + ".glb"), export_format="GLB")
    print("OK", name, [round(x, 2) for x in size], "eixo", axis)
