"""Polvo do Kraken, as ondas do chefe final das Docas ("Octopus", kenchoo, Sketchfab, CC BY 4.0; arquivo trazido pelo autor).
O arquivo: polvo com esqueleto (oito braços), 58 mil triângulos, textura de 1024 px e uma animação longa (rasteja e mexe os braços, ~12 s).
Aqui: a esfera de desenhar ossos sai, a malha é reduzida (DECIMATE) a ~1/5, a textura a 512 px (WEBP), sem os dois alvos de forma da respiração; a animação vira "idle" (o jogo a usa também
para andar e atacar). O polvo é virado (só no vazio do topo, que nenhuma animação mexe) com os braços para -Y do Blender = +Z no glTF (a frente no jogo):
a frente é a direção do fim do manto (C_HeadEnd) para a raiz dos braços (C_Root). Base em y = 0, centrado. Largura de ~2,6 m no arquivo:
o jogo usa a escala 1/2,6 (o "size" dos dados dá a largura em metros).
uso: blender -b -P tools/assets/build_kraken_octopus.py -- <octopus.glb> <saída: assets/models/monsters/kraken_octopus.glb>"""
import bpy, sys, math
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
RATIO = 0.2
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in [o for o in bpy.data.objects if o.type == "MESH" and o.parent is None]:
    bpy.data.objects.remove(o, do_unlink=True)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
top = arm
while top.parent:
    top = top.parent
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
for o in meshes:
    bpy.context.view_layer.objects.active = o
    if o.data.shape_keys:  # dois alvos de forma animados (a respiração): saem, senão o DECIMATE não aplica
        o.shape_key_clear()
    mod = o.modifiers.new("dec", "DECIMATE")
    mod.ratio = RATIO
    while o.modifiers.find("dec") > 0:
        bpy.ops.object.modifier_move_up(modifier="dec")
    bpy.ops.object.modifier_apply(modifier="dec")
for img in bpy.data.images:
    if img.size[0] > 512:
        img.scale(512, 512)
act = bpy.data.actions[0]
act.name = "idle"
act.use_fake_user = True
start = int(act.frame_range[0])
bpy.context.scene.frame_set(start)
bpy.context.view_layer.update()
root = arm.matrix_world @ arm.pose.bones["C_Root_Jnt_66"].head
head = arm.matrix_world @ arm.pose.bones["C_HeadEnd_jnt_0"].head
fwd = Vector((root.x - head.x, root.y - head.y, 0.0)).normalized()
turn = math.atan2(fwd.x, -fwd.y)  # ângulo que leva fwd para -Y
top.matrix_world = Matrix.Rotation(turn, 4, "Z") @ top.matrix_world
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
pts = [o.matrix_world @ v.co for o in meshes for v in o.evaluated_get(deps).to_mesh().vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
top.matrix_world = Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))) @ top.matrix_world
bpy.context.view_layer.update()
print("OK kraken octopus: giro %.0f graus, %.2f x %.2f x %.2f m, %d triângulos" % (math.degrees(turn), mx.x - mn.x, mx.y - mn.y, mx.z - mn.z,
                                                                                  sum(len(o.data.polygons) for o in meshes)))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85,
                          export_animation_mode="ACTIONS", export_force_sampling=True)
