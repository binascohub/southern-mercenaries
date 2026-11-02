"""Adereços da aldeia da Floresta (Medieval Props Pack 3, Daniel Andersson, CC0): uma .glb por peça em assets/models/maps/Vl_*.glb
(porão, varal de peixes, escada, latrina, lenha, curtume, cepo com machado), em metros, base em y = 0, centrada em x/z, de frente para +Z.
O .blend perdeu as ligações de textura (formato antigo): as imagens são ligadas de novo aos materiais por nome.
uso: blender -b -P tools/assets/build_village_props.py -- <pasta do pacote extraído> assets/models/maps"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
PROPS = {"Celler": "Vl_Cellar", "HangDriedFishes": "Vl_FishRack", "Ladder": "Vl_Ladder", "Outhouse": "Vl_Outhouse",
         "PileOfLogs": "Vl_Logs", "TanningStand": "Vl_TanningStand", "WoodChop": "Vl_ChoppingBlock"}
IMAGES = {"Stone Wall2": "Stone Wall2.jpg", "Door": "Door.jpg", "Rope2": "Rope2.jpg", "Trout": "Trout.jpg", "Bark": "Bark.jpg",
          "Wood2": "wood floor 2.png", "WoodenRings": "Tree_rings.jpg", "Hide": "Deer Hide.jpg", "HideBackside": "Deer Hide.jpg",
          "Rope": "Rope.jpg", "Wood": "Wood.jpg", "AxeHead": "AxeHead.jpg"}
SMALL = {"Tree_rings.jpg": 1024, "Wood.jpg": 1024}  # texturas enormes: reduzidas
# Giro (graus, em volta de Z) para a frente da peça (a porta, o lado de uso) ficar para +Z no Godot; ajustado olhando as imagens.
TURN = {"Celler": 0, "HangDriedFishes": 0, "Ladder": 0, "Outhouse": 0, "PileOfLogs": 0, "TanningStand": 0, "WoodChop": 0}
for name, out_name in PROPS.items():
    bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "Props3.blend"))
    for o in list(bpy.data.objects):
        if o.name != name:
            bpy.data.objects.remove(o, do_unlink=True)
    obj = bpy.data.objects[name]
    for mat in obj.data.materials:
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        nodes.clear()
        out_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
        bsdf.inputs["Roughness"].default_value = 0.9
        image = bpy.data.images.get(IMAGES.get(mat.name, ""))
        if image:
            if image.name in SMALL and max(image.size) > SMALL[image.name]:
                image.scale(SMALL[image.name], SMALL[image.name])
            tex = nodes.new("ShaderNodeTexImage")
            tex.image = image
            links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        else:
            print("SEM IMAGEM", name, mat.name)
    obj.rotation_euler[2] = obj.rotation_euler[2] + TURN[name] * 3.14159265 / 180
    bpy.context.view_layer.update()
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    obj.parent = None
    obj.data.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    obj.data.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, out_name + ".glb"), export_format="GLB", use_selection=True,
                              export_image_format="JPEG", export_apply=True)
    print("OK", out_name, [round(v, 2) for v in (mx - mn)])
