"""Relíquias das missões do Padre da Capital: o Coração Humano (Human Heart, Scribe / bart, CC0,
opengameart.org/content/human-heart) e o Crânio Antigo (Old Skull, vrav / Snabisch, CC-BY-SA 3.0,
opengameart.org/content/old-skull) em .glb: Quest_Heart.glb e Quest_Skull.glb, pousados (base em y = 0), o crânio com a
textura de cor e a normal embutidas e o coração em vermelho liso. O coração é a malha na pose de repouso (sem os modificadores de batida).
uso: build_quest_relics.py <pasta do coração (heart.blend, heart0024.png)> <pasta do crânio (skull.obj, texturas)> <pasta de saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
heart_dir, skull_dir, out = sys.argv[sys.argv.index("--") + 1:]


def finish(me, name, height, colour_path, normal_path=None, roughness=0.6, tint=None):
    pts = [v.co for v in me.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    me.transform(Matrix.Scale(height / (mx.z - mn.z), 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = roughness
    if colour_path:
        t = nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(colour_path)
        t.image.scale(512, 512)
        links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = tint
    if normal_path:
        n = nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(normal_path)
        n.image.colorspace_settings.name = "Non-Color"
        n.image.scale(512, 512)
        nm = nodes.new("ShaderNodeNormalMap")
        links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    me.materials.clear()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", export_image_format="JPEG")
    print("OK", name, [round(x, 2) for x in (mx - mn)])


# Coração: a malha "Sphere" com o esqueleto de batida em repouso (sem os modificadores de colisão).
bpy.ops.wm.open_mainfile(filepath=os.path.join(heart_dir, "heart.blend"))
obj = bpy.data.objects["Sphere"]
for mod in list(obj.modifiers):
    if mod.type != "ARMATURE":
        obj.modifiers.remove(mod)
deps = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(obj.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
me.transform(obj.matrix_world)
for other in list(bpy.data.objects):
    bpy.data.objects.remove(other, do_unlink=True)
finish(me, "Quest_Heart", 0.4, None, roughness=0.3, tint=(0.5, 0.04, 0.06, 1.0))  # a textura do arquivo sai escura: cor lisa de carne

# Crânio antigo (sem mandíbula).
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(skull_dir, "skull.obj"))
sk = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = sk.data
me.transform(sk.matrix_world)
bpy.data.objects.remove(sk, do_unlink=True)
finish(me, "Quest_Skull", 0.35, os.path.join(skull_dir, "skull.tga"), os.path.join(skull_dir, "skull_norm.tga"), roughness=0.7)
