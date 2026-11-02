"""Portal-poço: o Well of Lost Souls (bobjh, CC-BY 4.0 / CC0, opengameart.org/content/well-of-lost-souls: poço sombrio de pedra e ferro, cor, metal e normal
de 2048 -> 512 px) em Portal_Well.glb (1,3 m de largura, base em y = 0), e o Light crystal (U.R.U. project / Pompei2, CC-BY 3.0,
opengameart.org/content/light-crystal; textura de 256 px, azul e brilhante) em Portal_Crystal.glb (0,5 m de altura, base em y = 0), que flutua e gira dentro do poço
(montado no jogo, em prototype_arena.gd "exit"). O brilho e a luz azul do cristal ficam no código.
uso: build_portal_well.py <pasta well extraída> <crystals.blend> <pasta de saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
well_dir, crystal_blend, out = sys.argv[sys.argv.index("--") + 1:]


def finish(me, name, width=None, height=None, material=None):
    pts = [v.co for v in me.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    k = (width / max(mx.x - mn.x, mx.y - mn.y)) if width else (height / (mx.z - mn.z))
    me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    me.materials.clear()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", export_image_format="JPEG", use_selection=True)
    bpy.data.objects.remove(ob, do_unlink=True)
    print("OK", name, [round(x * k, 2) for x in (mx - mn)])


def principled(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial"); b = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(b.outputs["BSDF"], o_node.inputs["Surface"])
    return m, nodes, links, b


# Poço
bpy.ops.wm.open_mainfile(filepath=os.path.join(well_dir, "well.blend"))
o = bpy.data.objects["well"]
deps = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
me.transform(o.matrix_world)
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
m, nodes, links, b = principled("PortalWell")
def tex(fname, cs="sRGB"):
    t = nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(well_dir, fname)); t.image.scale(512, 512)
    t.image.colorspace_settings.name = cs
    return t
links.new(tex("well_color.png").outputs["Color"], b.inputs["Base Color"])
nm = nodes.new("ShaderNodeNormalMap"); links.new(tex("well_normal.png", "Non-Color").outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], b.inputs["Normal"])
links.new(tex("well_metal.png", "Non-Color").outputs["Color"], b.inputs["Metallic"])
b.inputs["Roughness"].default_value = 0.7
finish(me, "Portal_Well", width=1.3, material=m)
# Cristal
bpy.ops.wm.open_mainfile(filepath=crystal_blend)
o = bpy.data.objects["crystals"]
deps = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
me.transform(o.matrix_world)
img = bpy.data.images["crystals.png"]
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
m, nodes, links, b = principled("PortalCrystal")
t = nodes.new("ShaderNodeTexImage"); t.image = img
links.new(t.outputs["Color"], b.inputs["Base Color"]); links.new(t.outputs["Color"], b.inputs["Emission Color"])
b.inputs["Emission Strength"].default_value = 1.5
b.inputs["Roughness"].default_value = 0.1
finish(me, "Portal_Crystal", height=0.5, material=m)
