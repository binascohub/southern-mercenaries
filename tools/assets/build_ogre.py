"""Ogro (Ogre lowpoly, nubux / rudy85, CC-BY 3.0, opengameart.org/content/ogre-lowpoly): o arquivo é uma malha sem esqueleto, em T-pose,
com três texturas (corpo, pernas, cabeça); os braços são baixados aqui girando os vértices em torno do ombro (peso suave) e no jogo
o corpo todo balança, avança e cai por código (`static` em MonsterModel, como o Demônio da Noite). Pés em y = 0, 1 m de altura,
frente em +Z, texturas em 512 px (JPG).
uso: blender -b -P build_ogre.py -- <pasta com Ogre.blend e as texturas> <saída.glb>"""
import bpy, sys, os, math
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "Ogre.blend"))
o = bpy.data.objects["ogre"]
me = o.data
me.transform(o.matrix_world)
o.matrix_world = Matrix.Identity(4)
SHOULDER_X, SHOULDER_Z = 1.0, 3.2     # ombro (unidades do arquivo); a partir dele o braço desce
BLEND_X = 0.7                          # distância até o peso chegar a 1 (junta suave)
ARM_DOWN = math.radians(68)
for v in me.vertices:
    ax = abs(v.co.x)
    if ax <= SHOULDER_X or v.co.z < 2.2:
        continue
    w = min((ax - SHOULDER_X) / BLEND_X, 1.0)
    side = 1.0 if v.co.x > 0 else -1.0
    pivot = Vector((side * SHOULDER_X, 0.0, SHOULDER_Z))
    rot = Matrix.Rotation(-side * ARM_DOWN * w, 4, "Y")
    v.co = pivot + rot @ (v.co - pivot)
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 1.0 / (mx.z - mn.z)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
TEX = {"corps": "Corps.tga", "jambes": "Jambes.tga", "visage": "Tete.tga"}
for slot, mat in enumerate(me.materials):
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = 0.8
    t = nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(os.path.join(src, TEX[mat.name]), check_existing=True)
    links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
o.name = "Ogre"
for other in list(bpy.data.objects):
    if other is not o:
        bpy.data.objects.remove(other, do_unlink=True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK ogre", [round(x * k, 2) for x in (mx - mn)])
