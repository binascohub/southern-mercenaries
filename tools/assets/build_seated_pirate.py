"""Pirata sentado (Seated pirate with poor rig, pre, CC-BY 3.0 / GPL 2.0 / GPL 3.0, opengameart.org/content/seated-pirate-with-poor-rig): só o pirata
(a cena do arquivo traz mesa, cadeira, talheres e parede), na pose final da animação de sentar (quadro 26), como malha única parada
(Pirate_Seated.glb), com as cores dos materiais do arquivo (pele, couro, panos), 1,2 m de altura sentado, pés/assento em y = 0, de frente para +Z.
É o NPC da missão do mapa das Docas, sentado na taverna.
uso: build_seated_pirate.py <seatedPirate12_0.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
bpy.context.scene.frame_set(26)
o = bpy.data.objects["Pirate.001"]
deps = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
me.transform(o.matrix_world)
colors = {}
for m in o.data.materials:
    c = list(m.diffuse_color)
    if m.use_nodes and m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                c = list(n.inputs["Base Color"].default_value)
            elif n.type == "BSDF_DIFFUSE":
                c = list(n.inputs["Color"].default_value)
    colors[m.name] = c
print("COLORS", {k: [round(x, 2) for x in v[:3]] for k, v in colors.items()})
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
print("DIMS", [round(x, 2) for x in (mx - mn)])
k = 1.2 / (mx.z - mn.z)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
# Troca cada material no lugar (limpar a lista zeraria o índice de material dos polígonos).
for i, slot in enumerate(list(me.materials)):
    name = slot.name
    m = bpy.data.materials.new("Pirate_" + name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = colors[name]
    b.inputs["Roughness"].default_value = 0.6 if "Cornea" in name or "Iris" in name else 0.85
    me.materials[i] = m
ob = bpy.data.objects.new("Pirate_Seated", me)
bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB")
print("OK pirate", [round(x * k, 2) for x in (mx - mn)])
