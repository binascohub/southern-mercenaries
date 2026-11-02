"""Teias de aranha (Spider Webs, p0ss, CC BY 3.0, opengameart.org/content/spider-webs): assets/models/maps/Web_Round_Up.glb,
Web_Square_Up.glb (de pé, para atravessar corredores e cantos) e as mesmas duas com sufixo _Flat (deitadas no chão; a teia de canto do pacote ficou de fora).
Cada teia é malha de fios (sem UV; as texturas do pacote não servem), então o material é cinza claro, um pouco transparente. Maior dimensão de 1 m,
centradas em x/z, base em y = 0 (a escala vem do mapa); materiais com mistura de alfa, dos dois lados.
uso: blender -b -P tools/assets/build_webs.py -- <pasta do pacote extraído> assets/models/maps"""
import bpy, sys, os, math
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
PARTS = {"Round": "web.blend", "Square": "web-square.blend"}
for name, blend in PARTS.items():
    for pose in ("Up", "Flat"):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        with bpy.data.libraries.load(os.path.join(src, blend)) as (frm, to):
            to.objects = list(frm.objects)
        o = [x for x in to.objects if x is not None and x.type == "MESH"][0]
        bpy.context.scene.collection.objects.link(o)
        mesh = o.data.copy()
        mesh.transform(o.matrix_world)
        mat = bpy.data.materials.new("Web_" + name)
        mat.use_nodes = True
        mat.surface_render_method = "BLENDED"
        mat.use_backface_culling = False
        b = mat.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (0.82, 0.82, 0.8, 1)
        b.inputs["Alpha"].default_value = 0.85
        b.inputs["Roughness"].default_value = 1.0
        mesh.materials.clear()
        mesh.materials.append(mat)
        pts = [v.co for v in mesh.vertices]
        mn = Vector([min(p[i] for p in pts) for i in range(3)])
        mx = Vector([max(p[i] for p in pts) for i in range(3)])
        big = max(mx - mn)
        mesh.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -(mn.z + mx.z) / 2))))
        mesh.transform(Matrix.Scale(1.0 / big, 4))
        if pose == "Up":
            mesh.transform(Matrix.Rotation(math.pi / 2, 4, "X"))   # plano XY -> plano XZ (de pé, de frente para +Z do glTF)
        pts = [v.co for v in mesh.vertices]
        low = min(p.z for p in pts)
        mesh.transform(Matrix.Translation(Vector((0, 0, -low + (0.01 if pose == "Flat" else 0.0)))))
        for x in list(bpy.data.objects):
            bpy.data.objects.remove(x, do_unlink=True)
        obj = bpy.data.objects.new("Web_%s_%s" % (name, pose), mesh)
        bpy.context.scene.collection.objects.link(obj)
        bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Web_%s_%s.glb" % (name, pose)), export_format="GLB", export_image_format="WEBP")
        print("OK Web_%s_%s" % (name, pose), [round(v, 2) for v in (mx - mn) / big])
