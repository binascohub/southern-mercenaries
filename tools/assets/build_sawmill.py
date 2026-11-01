"""Serraria movida a água (Medieval waterpowered sawmill, Daniel Andersson / hreikin, CC0): assets/models/maps/Pr_Sawmill.glb.
Pega a pose do primeiro quadro (a roda, a manivela e a serra ficam paradas, sem esqueleto), junta tudo numa malha só
com os materiais refeitos (as imagens vêm embutidas no .blend), em pé com o topo da fundação em y = 0, centrada em x/z
e de frente para +Z (a roda d'água do lado de -X no arquivo fica para o lado esquerdo de quem olha).
uso: blender -b -P tools/assets/build_sawmill.py -- <WaterPoweredSawmillUpload.blend> <saida.glb> [escala] [pasta do Old Medieval Shack House extraído: a palha do telhado]"""
import bpy, sys
from mathutils import Vector, Matrix
import os
import numpy as np
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from farm_palette import unify_wood

args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
scale = float(args[2]) if len(args) > 2 else 0.7
bpy.ops.wm.open_mainfile(filepath=src)
bpy.context.scene.frame_set(1)
deps = bpy.context.evaluated_depsgraph_get()
IMAGES = {"RoofTiles": "RoofTiles.jpg", "RustedMetal": "Rusted Metal.jpg", "StoneWall": "StoneWall1.jpg",
          "TreeLogEdgeWeathered": "TreeLogEdgeWeathered.jpg", "Wood": "Wood.jpg"}
# Cobertura de palha (a mesma da casa da Fazenda): recorta o telhado do atlas do Old Medieval Shack House (argumento 4, pasta do pacote).
thatch_dir = args[3] if len(args) > 3 else ""
thatch = None
if thatch_dir:
    atlas = bpy.data.images.load(os.path.join(thatch_dir, "shack_main_diff.png"))
    aw, ah = atlas.size
    px = np.array(atlas.pixels[:], dtype=np.float32).reshape(ah, aw, 4)
    crop = px[int(ah * 0.09):int(ah * 0.63), int(aw * 0.30):int(aw * 0.95)].copy()  # linhas de baixo para cima: o telhado fica na metade de baixo do atlas
    crop[:, :, 3] = 1.0
    thatch = bpy.data.images.new("Thatch", crop.shape[1], crop.shape[0], alpha=False)
    thatch.pixels = crop.ravel().tolist()
    thatch.pack()
for name in ("Wood.jpg", "TreeLogEdgeWeathered.jpg"):
    unify_wood(bpy.data.images[name])  # tom único de madeira da Fazenda (farm_palette.py)
for mat in bpy.data.materials:
    img = thatch if (mat.name == "RoofTiles" and thatch) else bpy.data.images.get(IMAGES.get(mat.name, ""))
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.9
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    if img:
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = img
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
meshes = []
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    mesh.transform(o.matrix_world)
    obj = bpy.data.objects.new("part_" + o.name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    meshes.append(obj)
for o in [o for o in bpy.data.objects if o not in meshes]:
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
whole = bpy.context.view_layer.objects.active
whole.name = whole.data.name = "Pr_Sawmill"
pts = [v.co for v in whole.data.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
foundation_top = bpy.data.objects.get("Foundation")
ground = -0.7  # topo da fundação de pedra (Foundation: z central -2,22, altura 3,04)
whole.data.transform(Matrix.Scale(scale, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -ground))))
bpy.ops.object.select_all(action="DESELECT")
whole.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=85)
print("OK", out, "caixa %.1f x %.1f x %.1f m" % tuple((mx[i] - mn[i]) * scale for i in range(3)))
