"""Homem-Aranha (The Amazing Spider-Man 2 suit, Ugo9p1, modelo comprado; ele pede crédito): o Catador do Esgoto.
O arquivo vem em FBX com texturas UDIM (10 telas 4K do corpo), que viram um atlas 5 x 2 (1024 px cada; tela k na coluna k % 5, linha k // 5 de baixo
para cima); aqui as peças (corpo, teias, dedos, botas, logo, lentes) viram UMA malha
"Spiderman" já na pose do arquivo, e depois tools/assets/rig_to_ual.py prende a malha ao esqueleto dos heróis (altura 1,8 m):
  blender -b -P tools/assets/build_spiderman.py -- <TASM 2.fbx> <saida.blend> <atlas.png>
  blender -b -P tools/assets/rig_to_ual.py -- assets/models/characters/hero_male.glb <saida.blend> Spiderman assets/models/characters/spiderman.glb 1.8
O atlas sai de: python3 -I tools/assets/spiderman_atlas.py "<pasta textures>" <atlas.png>"""
import bpy, sys, os, math
from mathutils import Vector
SRC, OUT_BLEND, ATLAS = sys.argv[-3:]
TEX = os.path.dirname(SRC).rsplit("/", 1)[0] + "/textures"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=SRC)
deps = bpy.context.evaluated_depsgraph_get()
parts = []
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    mesh.transform(o.matrix_world)
    new = bpy.data.objects.new(o.name, mesh)
    bpy.context.scene.collection.objects.link(new)
    if o.name.startswith("Body"):
        uv = mesh.uv_layers.active
        for loop in uv.data:
            u, v = loop.uv
            k = min(max(int(math.floor(u + 1e-6)), 0), 9) if u < 9.999 else 9
            fu = min(max(u - k, 0.002), 0.998)
            fv = min(max(v, 0.002), 0.998)
            loop.uv = ((k % 5 + fu) / 5.0, (k // 5 + fv) / 2.0)
        mat = bpy.data.materials.new("SpiderSuit")
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(ATLAS)
        tex.image.pack()
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.6
        mesh.materials.clear()
        mesh.materials.append(mat)
        for p in mesh.polygons:
            p.material_index = 0
    elif o.name.startswith("Lenses"):
        mat = bpy.data.materials.new("SpiderLens")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.92, 0.95, 1)
        mesh.materials.clear(); mesh.materials.append(mat)
        for p in mesh.polygons: p.material_index = 0
    elif o.name.startswith("Sole") and not mesh.materials:
        mat = bpy.data.materials.new("SpiderSole")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.05, 0.06, 1)
        mesh.materials.append(mat)
    parts.append(new)
    print("PART", new.name, len(mesh.vertices), [m.name for m in mesh.materials][:4])
for o in [o for o in bpy.data.objects if o not in parts]:
    bpy.data.objects.remove(o, do_unlink=True)
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
j = bpy.context.view_layer.objects.active
j.name = "Spiderman"
pts = [v.co for v in j.data.vertices]
lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
print("BBOX", [round(a, 2) for a in lo], [round(a, 2) for a in hi], "verts", len(pts))
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
