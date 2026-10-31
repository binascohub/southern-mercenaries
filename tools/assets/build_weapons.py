"""Armas do Kingdom Weapon Set (pfunked / Clint Bellanger, CC BY-SA 3.0): uma
.glb por arma, de pé (cabeça/lâmina para +Y), com a origem no meio do
comprimento e o tamanho do jogo; prata e couro em cores lisas.
uso: build_weapons.py <weapon_set_kingdom.blend> <saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
LENGTH = {"KingdomAxe": 0.95, "KingdomCrossbow": 0.8, "KingdomHammer": 0.9, "KingdomLongsword": 1.15,
    "KingdomPolearm": 2.4, "KingdomShortsword": 0.6, "KingdomStaff": 1.7}
COLORS = {"Silver": ((0.78, 0.8, 0.84, 1), 0.85, 0.3), "Leather": ((0.16, 0.1, 0.07, 1), 0.0, 0.7)}
for name, length in LENGTH.items():
    bpy.ops.wm.open_mainfile(filepath=src)
    deps = bpy.context.evaluated_depsgraph_get()
    o = bpy.data.objects[name]
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    mesh.transform(o.matrix_world)
    pts = [v.co for v in mesh.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    mesh.transform(Matrix.Scale(length / (mx.z - mn.z), 4) @ Matrix.Translation(-(mn + mx) / 2))
    for mat in mesh.materials:
        color, metal, rough = COLORS.get(mat.name, ((0.5, 0.5, 0.5, 1), 0.0, 0.7))
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        nodes.clear()
        out_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metal
        bsdf.inputs["Roughness"].default_value = rough
        links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    for other in list(bpy.data.objects):
        bpy.data.objects.remove(other, do_unlink=True)
    weapon = bpy.data.objects.new(name.replace("Kingdom", "Weapon_"), mesh)
    bpy.context.scene.collection.objects.link(weapon)
    path = os.path.join(out, weapon.name + ".glb")
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB")
    print("OK", weapon.name, length)
