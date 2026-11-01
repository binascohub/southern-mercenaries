"""Peças do mapa Docas (Modular Wooden Docks, loafbrr, CC0, opengameart.org/content/modular-wooden-docks): do WoodenDockSet.glb
do pacote, uma peça por arquivo em assets/models/maps/docks/ (Dock_<nome>.gltf), com a textura compartilhada.
Piso com o topo em y = 0,12 (acima da água do mapa); as outras peças com a base em y = 0; origem no centro em x e z.
uso: build_docks_assets.py <WoodenDockSet.glb> <saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
PIECES = ["Floor_Dock_Half", "Floor_Dock", "Fence_Plane_Half", "Fence_Plane", "Fence_Post", "Dock_Bollard_1", "Boat_A_1", "Boat_A_2", "Boat_B_1",
          "Boat_Stand", "Props_Barrel", "Props_Crate", "Props_Box", "Props_Table_1", "Props_Rack_Fish", "Props_Rack", "Props_Bench", "Support_Post"]
for name in PIECES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=src)
    keep = bpy.data.objects[name]
    for o in list(bpy.data.objects):
        if o != keep and o.parent != keep and o.type != "EMPTY":
            bpy.data.objects.remove(o, do_unlink=True)
    for o in [o for o in bpy.data.objects if o.name.endswith("-colonly") or o.type == "EMPTY"]:
        bpy.data.objects.remove(o, do_unlink=True)
    keep.parent = None
    me = keep.data
    me.transform(keep.matrix_world)
    keep.matrix_world = Matrix.Identity(4)
    pts = [v.co for v in me.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    top = name.startswith("Floor_")
    lift = Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, (-mx.z + 0.12) if top else -mn.z))
    me.transform(Matrix.Translation(lift))
    keep.name = "Dock_" + name
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Dock_" + name + ".gltf"), export_format="GLTF_SEPARATE", export_image_format="JPEG")
    print("OK", name, [round(x, 2) for x in (mx - mn)])
