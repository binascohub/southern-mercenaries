"""Casa da Fazenda (Old Medieval Shack House, Spiral, CC0): assets/models/maps/Pr_Farmhouse.glb.
Importa o small_shack.FBX, refaz os materiais (cor com alfa dos .png: o recorte da palha do telhado; os "Slot"
vazios ficam em madeira cinza), põe o chão em y = 0, centra em x/z e vira a porta para +Z (frente do jogo).
uso: blender -b -P tools/assets/build_farmhouse.py -- <pasta do pacote extraído> <saida.glb> [rotacao_graus]"""
import bpy, sys, os, math
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
spin = float(args[2]) if len(args) > 2 else 0.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(src, "small_shack.FBX"))
house = next(o for o in bpy.data.objects if o.type == "MESH")
IMAGES = {"shack_main_tex": "shack_main_diff.png", "shack_details_tex": "shack_details_diff.png"}
for mat in house.data.materials:
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.95
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    if mat.name in IMAGES:
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(os.path.join(src, IMAGES[mat.name]))
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
        mat.blend_method = "CLIP"
    else:
        bsdf.inputs["Base Color"].default_value = (0.3, 0.28, 0.25, 1)
house.data.transform(house.matrix_world)
house.matrix_world = Matrix.Identity(4)
if spin:
    house.data.transform(Matrix.Rotation(math.radians(spin), 4, "Z"))
pts = [v.co for v in house.data.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
house.data.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
house.name = house.data.name = "Pr_Farmhouse"
bpy.ops.object.select_all(action="DESELECT")
house.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=85)
print("OK", out, "caixa %.2f x %.2f x %.2f m" % tuple(mx[i] - mn[i] for i in range(3)))
