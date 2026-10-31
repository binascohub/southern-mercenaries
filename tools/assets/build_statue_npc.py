"""Brigand (anthonymyers, CC BY 3.0) como guarda parado (pose do próprio modelo,
com a alabarda e o machado): malhas juntas, pés em y = 0, 1,85 m de altura do
corpo, textura do corpo e das armas.
uso: build_statue_npc.py <DonePose.blend> <pasta Dude> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, folder, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
keep = ["mesh02.020", "mesh02.007", "RoadKillOut.000", "RoadKillOut.001", "RoadKillOut.002"]
deps = bpy.context.evaluated_depsgraph_get()
objs = []
for name in keep:
    o = bpy.data.objects[name]
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    mesh.transform(o.matrix_world)
    new = bpy.data.objects.new("Brigand_" + name.replace(".", "_"), mesh)
    objs.append(new)
for o in [o for o in bpy.data.objects if o not in objs]:
    bpy.data.objects.remove(o, do_unlink=True)
for o in objs:
    bpy.context.scene.collection.objects.link(o)
body = objs[0]
pts = [v.co for v in body.data.vertices]
feet = min(p.z for p in pts)
top = max(p.z for p in pts)
cx = sum(p.x for p in pts) / len(pts)
cy = sum(p.y for p in pts) / len(pts)
fix = Matrix.Scale(1.85 / (top - feet), 4) @ Matrix.Translation(Vector((-cx, -cy, -feet)))
tex = {"___default___.001": "Done3.png", "___default___": "Done3.png", "None.001": "DoneWeps.png"}
images = {}
for o in objs:
    o.data.transform(fix)
    for mat in o.data.materials:
        if mat is None:
            continue
        file = tex.get(mat.name, "Done3.png")
        if file not in images:
            images[file] = bpy.data.images.load(os.path.join(folder, file))
            if images[file].size[0] > 1024:
                images[file].scale(1024, 1024)
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        nodes.clear()
        o_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = 0.55
        node = nodes.new("ShaderNodeTexImage")
        node.image = images[file]
        links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85)
print("OK", out)
