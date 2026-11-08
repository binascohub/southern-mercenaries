"""Casco Vivo, mini-chefe das Docas, com o modelo novo ("MONSTER", NORBERTO-3D, Sketchfab, CC BY-SA 4.0; arquivo trazido pelo autor): um peixe-pescador
de pé, azul, com crista de espinhos e a isca luminosa na testa.
O arquivo é uma cena: além do monstro (Object_11 + Object_7, a crista, + Object_9, os olhos e a isca, no esqueleto Object_4) traz um inseto voador e um
besouro com esqueletos próprios (Object_120, Object_186), bolhas e peixinhos (cadnav.com*, Object00*) e um chão (Plane001). Aqui só o monstro fica.
A animação do arquivo (Take 001, 1,7 s: balança, avança e morde) vira "idle" e serve para tudo; sem morte (o corpo afunda).
O monstro já olha para -Y no Blender (+Z no glTF, a frente no jogo). O vazio do topo (que nenhuma animação mexe) o deixa com 1 m de altura, pés em y = 0
e centrado: o jogo usa a escala 1,15 (o "size" dos dados vezes 1,15 dá a altura em metros).
uso: blender -b -P tools/assets/build_hull_angler.py -- <monster.glb> <saída: assets/models/monsters/hull_angler.glb>"""
import bpy, sys
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
KEEP = {"Object_11", "Object_7", "Object_9"}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in [o for o in bpy.data.objects if o.type == "MESH" and o.name not in KEEP]:
    bpy.data.objects.remove(o, do_unlink=True)  # extras da cena e as esferas de desenhar ossos
for name in ("Object_120", "Object_186"):
    bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)  # esqueletos do inseto e do besouro
arm = bpy.data.objects["Object_4"]
top = arm
while top.parent:
    top = top.parent
meshes = [bpy.data.objects[n] for n in KEEP]
for img in bpy.data.images:
    if img.size[0] > 512:
        img.scale(512, 512)
for img in [i for i in bpy.data.images if i.users == 0]:
    bpy.data.images.remove(img)
act = bpy.data.actions[0]
act.name = "idle"
act.use_fake_user = True
bpy.context.scene.frame_set(0)
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
pts = [o.matrix_world @ v.co for o in meshes for v in o.evaluated_get(deps).to_mesh().vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 1.0 / (mx.z - mn.z)
top.matrix_world = Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))) @ top.matrix_world
bpy.context.view_layer.update()
print("OK hull angler: %.2f x %.2f x %.2f no arquivo -> 1 m de altura, %d triângulos" % (mx.x - mn.x, mx.y - mn.y, mx.z - mn.z,
                                                                                    sum(len(o.data.polygons) for o in meshes)))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85,
                          export_animation_mode="ACTIONS", export_force_sampling=True)
