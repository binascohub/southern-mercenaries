"""Escorpião (sunburn, CC BY 3.0): esculpido sem esqueleto e sem textura. As
peças ficam separadas (corpo, 2 pinças, 6 patas) com a origem na junta, para o
jogo animar (patas andando, pinças, cauda); malhas reduzidas (decimate) e casca
escura. Comprimento ~1 m, frente para +Z no Godot (pinças em -Y no Blender).
uso: build_scorpion.py <scorpion.blend> <saida.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
TARGET = {"body": 3500, "claw": 900, "leg": 350}
shell = bpy.data.materials.new("Chitin")
shell.use_nodes = True
bsdf = shell.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.16, 0.11, 0.07, 1)
bsdf.inputs["Roughness"].default_value = 0.35
keep = []
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.name == "Cube":
        bpy.data.objects.remove(o, do_unlink=True)
        continue
    kind = "body" if o.name.startswith("body") else ("claw" if o.name.startswith("claw") else "leg")
    o.data = o.data.copy()
    ratio = min(1.0, TARGET[kind] / max(len(o.data.polygons), 1))
    mod = o.modifiers.new("dec", "DECIMATE")
    mod.ratio = ratio
    bpy.context.view_layer.objects.active = o
    with bpy.context.temp_override(object=o, active_object=o):
        bpy.ops.object.modifier_apply(modifier="dec")
    o.data.materials.clear()
    o.data.materials.append(shell)
    for p in o.data.polygons:
        p.use_smooth = True
    keep.append(o)
    print("DEC", o.name, len(o.data.polygons))
# Escala para ~1 m de comprimento e pés no chão: aplicada nos objetos (raiz comum).
pts = [o.matrix_world @ v.co for o in keep for v in o.data.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
k = 1.0 / (hi.y - lo.y)
root = bpy.data.objects.new("Scorpion", None)
bpy.context.scene.collection.objects.link(root)
root.location = (-(lo.x + hi.x) / 2 * k, -(lo.y + hi.y) / 2 * k, -lo.z * k)
root.scale = (k, k, k)
for o in keep:
    o.parent = root
names = {"body-5": "Body", "claw3": "Claw_R", "claw3.001": "Claw_L"}
legs = 0
for o in keep:
    if o.name in names:
        o.name = names[o.name]
    else:
        side = "R" if o.location.x < 0 else "L"
        o.name = "Leg_%s_%d" % (side, legs)
        legs += 1
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB")
print("OK", out, [round((hi[i] - lo[i]) * k, 2) for i in range(3)])
