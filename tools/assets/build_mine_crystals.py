"""Cristais da Mina (Lowpoly Crystals Pack, iPoly3D, CC0, opengameart.org/content/lowpoly-crystals-pack):
assets/models/maps/Crystal_B_1..28.glb (textura azul) e Crystal_P_1..28.glb (textura roxa). Cada cristal fica em pé,
base em y = 0, centrado em x/z, com a maior dimensão de 1 m (a escala vem do mapa).
uso: blender -b -P tools/assets/build_mine_crystals.py -- <pasta do pacote extraído> assets/models/maps"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
TEX = {"B": "texture_1.png", "P": "texture_2.png"}
for n in range(1, 29):
    for tag, tex_name in TEX.items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.wm.obj_import(filepath=os.path.join(src, "OBJ", "crystal_%d.obj" % n), forward_axis="NEGATIVE_Z", up_axis="Y")
        objs = [o for o in bpy.data.objects if o.type == "MESH"]
        mat = bpy.data.materials.new("Crystal_%s_%d" % (tag, n))
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        img = mat.node_tree.nodes.new("ShaderNodeTexImage")
        img.image = bpy.data.images.load(os.path.join(src, "Textures", tex_name))
        mat.node_tree.links.new(img.outputs["Color"], bsdf.inputs["Base Color"])
        mat.node_tree.links.new(img.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 0.6   # brilham no escuro da mina
        bsdf.inputs["Roughness"].default_value = 0.25
        for o in objs:
            o.data.materials.clear()
            o.data.materials.append(mat)
        pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
        mn = Vector([min(p[i] for p in pts) for i in range(3)])
        mx = Vector([max(p[i] for p in pts) for i in range(3)])
        s = 1.0 / max(mx - mn)
        shift = Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
        for o in objs:
            o.data.transform(o.matrix_world)
            o.matrix_world = Matrix.Identity(4)
            o.data.transform(shift)
        bpy.ops.object.select_all(action="DESELECT")
        for o in objs:
            o.select_set(True)
        bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Crystal_%s_%d.glb" % (tag, n)), export_format="GLB", use_selection=True)
        if tag == "B":
            print("OK crystal_%d  %.2f x %.2f x %.2f m" % (n, (mx.x - mn.x) * s, (mx.y - mn.y) * s, (mx.z - mn.z) * s))
