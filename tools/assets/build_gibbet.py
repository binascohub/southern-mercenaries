"""Gibbet (gaiola de forca, Gibbet, bobjh / Snabisch, CC-BY 3.0 e CC-BY 4.0, opengameart.org/content/gibbet-0, textura sobre o rusted metal texture pack de p0ss): a gaiola
(hanging_cage), as correntes e a tampa com as texturas do pacote (cor + normal, 512 px) num .glb (Gibbet.glb), pendurada de uma viga de madeira presa a um poste
(feitos aqui com caixas, como o arquivo não os traz). A gaiola fica a 0,5 m do chão; base do poste em y = 0; o poste e a viga ficam para -X (a gaiola no centro).
uso: build_gibbet.py <pasta hanging_cage> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "cage.blend"))
deps = bpy.context.evaluated_depsgraph_get()
parts = []
for name in ("hanging_cage", "hanging_cage_chains", "hanging_cage_hatch"):
    o = bpy.data.objects[name]
    me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    me.transform(o.matrix_world)
    parts.append((name, me))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
pts = [v.co for _, me in parts for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
print("DIMS", [round(x, 2) for x in (mx - mn)])
lift = 0.5 - mn.z
fix = Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, lift)))
metal = bpy.data.materials.new("GibbetMetal")
metal.use_nodes = True
nodes, links = metal.node_tree.nodes, metal.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial"); b = nodes.new("ShaderNodeBsdfPrincipled")
links.new(b.outputs["BSDF"], o_node.inputs["Surface"]); b.inputs["Roughness"].default_value = 0.6
c = nodes.new("ShaderNodeTexImage"); c.image = bpy.data.images.load(os.path.join(src, "hanging_cage.png")); c.image.scale(512, 512)
links.new(c.outputs["Color"], b.inputs["Base Color"])
n = nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(os.path.join(src, "cage_Normal.png")); n.image.scale(512, 512); n.image.colorspace_settings.name = "Non-Color"
nm = nodes.new("ShaderNodeNormalMap")
links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], b.inputs["Normal"])
wood = bpy.data.materials.new("GibbetWood")
wood.use_nodes = True
wb = wood.node_tree.nodes["Principled BSDF"]
wb.inputs["Base Color"].default_value = (0.12, 0.07, 0.04, 1.0); wb.inputs["Roughness"].default_value = 0.9
top = (mx.z - mn.z) + lift
for name, me in parts:
    me.transform(fix)
    me.materials.clear(); me.materials.append(metal)
    ob = bpy.data.objects.new("Gibbet_" + name, me)
    bpy.context.scene.collection.objects.link(ob)
def box(name, size, loc):
    me = bpy.data.meshes.new(name)
    sx, sy, sz = size
    v = [(x * sx / 2, y * sy / 2, z * sz / 2) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    me.from_pydata(v, [], f)
    me.transform(Matrix.Translation(Vector(loc)))
    me.materials.append(wood)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
# poste (para -X) e viga até o centro da gaiola, na altura do topo das correntes
box("Gibbet_post", (0.28, 0.28, top + 0.2), (-1.3, 0, (top + 0.2) / 2))
box("Gibbet_beam", (1.5, 0.2, 0.2), (-0.55, 0, top + 0.05))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK gibbet altura", round(top + 0.2, 2))
