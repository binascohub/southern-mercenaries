"""Guerreiro saxão (Saxon warrior, Blend Swap #83828, CC0): o NPC Guardiã da Pira da Floresta (o "pyre_keeper"), de camisa, calça, capa, escudo, lança e seax.
O arquivo é do Blender 2.72 (materiais antigos com texturas): cada material vira um Principled com a imagem, as malhas saem na pose do arquivo (sem esqueleto nem
animação; o cabelo em partículas é descartado, fica a base do cabelo), juntas num só objeto, de pé em y = 0 e com o corpo de 1,85 m (a lança passa disso).
uso: blender -b --disable-autoexec saxon1.blend --python build_saxon_warrior.py -- <saída.glb>"""
import bpy, sys
import numpy as np
from mathutils import Vector, Matrix

out = sys.argv[sys.argv.index("--") + 1]
HEIGHT = 1.85
# Sem a subdivisão (49 mil polígonos): a malha base já é lisa o bastante para um NPC de cenário.
for o in bpy.data.objects:
    for m in o.modifiers:
        if m.type == "SUBSURF":
            m.show_viewport = False
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()


def texture_of(mat):
    if mat is None:
        return None
    for slot in getattr(mat, "texture_slots", []) or []:
        if slot and slot.texture and getattr(slot.texture, "image", None):
            return slot.texture.image
    if mat.use_nodes:
        for n in mat.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.image:
                return n.image
    return None


parts = []
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.name in ("Plane",) or o.name.startswith("gwallt.0") and o.name != "gwallt.001":
        continue
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    mesh.transform(o.matrix_world)
    obj = bpy.data.objects.new(o.name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for i, mat in enumerate(o.data.materials):
        if mat is None:
            continue
        img = texture_of(mat)
        nm = bpy.data.materials.new(mat.name)
        nm.use_nodes = True
        bsdf = nm.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Roughness"].default_value = 0.85
        if img:
            t = nm.node_tree.nodes.new("ShaderNodeTexImage")
            t.image = img
            nm.node_tree.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
        else:
            bsdf.inputs["Base Color"].default_value = (mat.diffuse_color[0], mat.diffuse_color[1], mat.diffuse_color[2], 1.0)
        if i < len(mesh.materials):
            mesh.materials[i] = nm
    parts.append(obj)
for o in list(bpy.data.objects):
    if o not in parts:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action="DESELECT")
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "NPC_Saxon"
pts = np.array([v.co[:] for v in body.data.vertices])
# Altura do corpo: o mais alto sem a lança (a lança é a parte que passa do resto).
z = pts[:, 2]
lo = z.min()
head = np.percentile(z, 97)  # (a lança e o cabelo são poucos vértices)
scale = HEIGHT / (head - lo)
body.data.transform(Matrix.Translation(-Vector(((pts[:, 0].min() + pts[:, 0].max()) / 2, (pts[:, 1].min() + pts[:, 1].max()) / 2, lo))))
body.data.transform(Matrix.Scale(scale, 4))
for poly in body.data.polygons:
    poly.use_smooth = True
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=82)
print("OK saxon", len(body.data.polygons), "polys, escala", round(scale, 4), "bbox", [round(float(v), 2) for v in (pts.max(axis=0) - pts.min(axis=0)) * scale])
