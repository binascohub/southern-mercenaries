"""Louça do Dinnerware (Clint Bellanger, CC BY 3.0, opengameart.org/content/dinnerware): uma .glb por peça
(Dw_Plate, Dw_Bowl, Dw_Platter, Dw_Jug, Dw_Pitcher, Dw_Goblet, Dw_Tankard, Dw_Cup, Dw_Bottle, Dw_Fork,
Dw_Knife, Dw_Spoon), de pé, com a base em y = 0, no tamanho real (o original tem uma peça de 2 unidades
para um prato de ~22 cm: escala 0,11), materiais com as texturas do pacote (vidro em cor translúcida).
uso: build_dinnerware.py <dinnerware.blend> <pasta com as texturas> <saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, texdir, out = sys.argv[sys.argv.index("--") + 1:]
PIECES = {"DinnerPlate": "Plate", "DinnerBowl": "Bowl", "Platter": "Platter", "Jug": "Jug", "Pitcher": "Pitcher",
          "Goblet": "Goblet", "Tankard": "Tankard", "Cup": "Cup", "WineBottle": "Bottle", "Fork": "Fork",
          "Knife": "Knife", "Spoon": "Spoon"}
TEXTURES = {"TerraCotta": "terracotta_d.png", "TerraCottaStretch": "terracotta_d.png", "Silver": "silver_d.png",
            "SilverStretch": "silver_d.png", "Wood": "wood_d.png", "WoodStretch": "wood_d.png"}
FLAT = {"Glass": ((0.75, 0.88, 0.9, 0.35), 0.05), "DarkGlass": ((0.05, 0.16, 0.08, 0.9), 0.1), "Cork": ((0.5, 0.36, 0.2, 1), 0.8)}
SCALE = 0.11
for src_name, name in PIECES.items():
    bpy.ops.wm.open_mainfile(filepath=src)
    deps = bpy.context.evaluated_depsgraph_get()
    o = bpy.data.objects[src_name]
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), depsgraph=deps)
    mesh.transform(o.matrix_world)
    pts = [v.co for v in mesh.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    # Base no chão, centro em x/y; talheres ficam deitados (altura pequena).
    mesh.transform(Matrix.Scale(SCALE, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    old = list(mesh.materials)
    mesh.materials.clear()
    for m in old:
        mat = bpy.data.materials.new(m.name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        if m.name in TEXTURES:
            node = mat.node_tree.nodes.new("ShaderNodeTexImage")
            node.image = bpy.data.images.load(os.path.join(texdir, TEXTURES[m.name]))
            mat.node_tree.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
            bsdf.inputs["Metallic"].default_value = 0.8 if "Silver" in m.name else 0.0
            bsdf.inputs["Roughness"].default_value = 0.35 if "Silver" in m.name else 0.7
        else:
            color, rough = FLAT.get(m.name, ((0.5, 0.5, 0.5, 1), 0.6))
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Alpha"].default_value = color[3]
            bsdf.inputs["Roughness"].default_value = rough
            if color[3] < 1:
                mat.blend_method = "BLEND" if hasattr(mat, "blend_method") else None
        mesh.materials.append(mat)
    for other in list(bpy.data.objects):
        bpy.data.objects.remove(other, do_unlink=True)
    piece = bpy.data.objects.new("Dw_" + name, mesh)
    bpy.context.scene.collection.objects.link(piece)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Dw_%s.glb" % name), export_format="GLB", export_image_format="JPEG")
    print("OK", name, [round(x * SCALE, 3) for x in (mx - mn)])
