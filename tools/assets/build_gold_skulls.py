"""Pilha de caveiras de ouro, decoração das Catacumbas e do Cemitério: "A bunch of gold skull" (IIAdantII na Sketchfab, CC BY 4.0; arquivo
trazido pelo autor). As partes viram uma malha só, reduzida a no máximo MAX_TRIS triângulos, de pé em z = 0, centrada, com HEIGHT de altura;
texturas em no máximo MAX_TEX px. O metal do material é fixado em METALLIC (metal puro sai preto no renderizador do jogo, sem reflexo do céu)
e a cor vira GOLD.
Vai para assets/models/maps/Gold_SkullPile.glb (peça do Kit). uso: blender -b --python tools/assets/build_gold_skulls.py -- <skulls.glb> <saída.glb>"""
import bpy, sys
from mathutils import Matrix, Vector
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
HEIGHT, MAX_TRIS, MAX_TEX, METALLIC = 1.2, 12000, 512, 0.5
GOLD = (0.85, 0.58, 0.16, 1.0)   # a textura de cor é bege claro (o ouro vinha do reflexo do metal): fica a cor lisa, com o mapa de relevo
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = []
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    mesh = o.data.copy()
    mesh.transform(o.matrix_world)
    obj = bpy.data.objects.new("Gold_SkullPile", mesh)
    bpy.context.scene.collection.objects.link(obj)
    meshes.append(obj)
for o in [o for o in bpy.data.objects if o not in meshes]:
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active
tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
if tris > MAX_TRIS:
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.ratio = MAX_TRIS / tris
    bpy.ops.object.modifier_apply(modifier="dec")
vs = [v.co for v in obj.data.vertices]
mn = Vector([min(v[i] for v in vs) for i in range(3)])
mx = Vector([max(v[i] for v in vs) for i in range(3)])
k = HEIGHT / (mx.z - mn.z)
obj.data.transform(Matrix.Scale(k, 4) @ Matrix.Translation(-Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))))
for mat in bpy.data.materials:
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if mat.node_tree else None
    if bsdf:
        for name in ("Metallic", "Base Color", "Roughness", "Emission Color"):
            for link in list(bsdf.inputs[name].links):
                mat.node_tree.links.remove(link)
        bsdf.inputs["Metallic"].default_value = METALLIC
        bsdf.inputs["Base Color"].default_value = GOLD
        bsdf.inputs["Roughness"].default_value = 0.35
        bsdf.inputs["Emission Color"].default_value = GOLD
        bsdf.inputs["Emission Strength"].default_value = 0.08
for image in bpy.data.images:
    w, h = image.size
    if max(w, h) > MAX_TEX:
        s = MAX_TEX / max(w, h)
        image.scale(max(1, int(w * s)), max(1, int(h * s)))
print("pilha", sum(len(p.vertices) - 2 for p in obj.data.polygons), "tri", [round((mx - mn)[i] * k, 2) for i in range(3)], "m")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=80)
