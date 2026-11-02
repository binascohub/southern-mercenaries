"""Suporte de armas (Medieval Weapon Rack, WeaponGuy, CC BY 3.0, opengameart.org/content/medieval-weapon-rack): a malha
com a textura de madeira embutida (1024 px, JPG), em pé, base em y = 0, 2,2 m de largura.
uso: build_weapon_rack.py <weaponrack.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
for o in list(bpy.data.objects):
    if o.name != "Cube":
        bpy.data.objects.remove(o, do_unlink=True)
obj = bpy.data.objects["Cube"]
me = obj.data
me.transform(obj.matrix_world)
obj.matrix_world = Matrix.Identity(4)
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
me.transform(Matrix.Scale(2.2 / (mx.x - mn.x), 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
mat = me.materials[0]
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
t = nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images["WeaponrackWood.jpg"]
links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.85
obj.name = "Weapon_Rack"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK rack")
