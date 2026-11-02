"""Aldeã (villager1.zip do autor, de cg-moon.com; autoria e licença a confirmar): malha em T-pose com uma textura de 256 px, que
substitui a cortesã das ruas de Tortuga. O arquivo vem em dois pedaços (corpo e um adereço pequeno, provavelmente o coque); aqui eles viram UMA malha
"Villager" (com a textura embutida), e depois tools/assets/rig_to_ual.py prende a malha ao esqueleto dos heróis (1,75 m) e ela ganha as animações deles:
  blender -b -P tools/assets/build_villager.py -- <model.blend> <textura.dds> <saida.blend>
  blender -b -P tools/assets/rig_to_ual.py -- assets/models/characters/hero_female.glb <saida.blend> Villager assets/models/characters/villager.glb 1.75"""
import bpy, sys

src, tex_path, out = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.open_mainfile(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "Villager"
img = bpy.data.images.load(tex_path)
img.pack()
mat = bpy.data.materials.new("Villager")
mat.use_nodes = True
nt = mat.node_tree
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = img
bsdf = nt.nodes["Principled BSDF"]
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.85
body.data.materials.clear()
body.data.materials.append(mat)
bpy.ops.wm.save_as_mainfile(filepath=out)
print("OK", out, [round(v, 2) for v in body.dimensions], len(body.data.vertices))
