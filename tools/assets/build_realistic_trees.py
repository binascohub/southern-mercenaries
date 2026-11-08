"""Árvores realistas para a Floresta e os mapas com carvalhos: "Realistic Trees Collection" (Jungle Jim na Sketchfab, CC BY 4.0; arquivo trazido
pelo autor). O arquivo traz sete árvores lado a lado (3 grandes, 3 médias e um arbusto) com 15 a 43 mil triângulos cada, pesado demais para
centenas de árvores na placa integrada. Cada uma vira uma peça do Kit (assets/models/maps/<nome>.glb):
- galhos reduzidos a BRANCH_TRIS triângulos (de cima quase não aparecem);
- folhas: são cartões soltos; ficam LEAF_TRIS triângulos, sorteando cartões inteiros, e os que ficam crescem um pouco para a copa não abrir;
  o material vira recorte (alpha scissor) em vez de mistura (sem problema de ordem de desenho e mais leve);
- de pé em y = 0, tronco no centro, com a altura de TREES (o Carvalho do jogo tem 7 m); texturas em no máximo MAX_TEX px.
uso: blender -b --python tools/assets/build_realistic_trees.py -- <realistic_trees_collection.glb> <pasta de saída>"""
import bpy, bmesh, sys, os, random
from mathutils import Matrix, Vector
src, out_dir = sys.argv[sys.argv.index("--") + 1:][:2]
BRANCH_TRIS, LEAF_TRIS, MAX_TEX = 1200, 2600, 512
TREES = {   # objeto-pai no arquivo: (peça, altura em m)
    "Tree EZTree0.Large": ("Tree_Large_A", 7.5),
    "Tree EZTree1.Large001": ("Tree_Large_B", 7.0),
    "Tree EZTree1.Large009": ("Tree_Large_C", 7.5),
    "Tree EZTree0.Medium010": ("Tree_Medium_A", 6.0),
    "Tree EZTree0.Medium011": ("Tree_Medium_B", 5.0),
    "Tree EZTree1.Medium002": ("Tree_Medium_C", 5.0),
    "Tree EZTree1.Bush006": ("Tree_Bush", 1.4),
}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for mat in bpy.data.materials:
    if mat.name.startswith("leaves") or mat.blend_method == "BLEND":
        mat.blend_method = "CLIP"
        mat.alpha_threshold = 0.4
for image in bpy.data.images:
    w, h = image.size
    if max(w, h) > MAX_TEX:
        s = MAX_TEX / max(w, h)
        image.scale(max(1, int(w * s)), max(1, int(h * s)))


def thin_leaves(mesh: bpy.types.Mesh, target: int, seed: str) -> None:
    """Sorteia cartões inteiros (ilhas ligadas) até ~target triângulos e aumenta os que ficam."""
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    seen, islands = set(), []
    for face in bm.faces:
        if face.index in seen:
            continue
        stack, island = [face], []
        seen.add(face.index)
        while stack:
            f = stack.pop()
            island.append(f)
            for e in f.edges:
                for g in e.link_faces:
                    if g.index not in seen:
                        seen.add(g.index)
                        stack.append(g)
        islands.append(island)
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    if tris > target:
        keep = target / tris
        rng = random.Random(seed)
        grow = min(1.6, (1.0 / keep) ** 0.35)
        dead = []
        for island in islands:
            if rng.random() > keep:
                dead += island
            else:
                verts = {v for f in island for v in f.verts}
                c = sum((v.co for v in verts), Vector()) / len(verts)
                for v in verts:
                    v.co = c + (v.co - c) * grow
        bmesh.ops.delete(bm, geom=dead, context="FACES")
    bm.to_mesh(mesh)
    bm.free()


for parent_name, (piece, height) in TREES.items():
    parent = bpy.data.objects[parent_name]
    parts = []
    for child in [c for c in parent.children_recursive if c.type == "MESH"]:
        mesh = child.data.copy()
        mesh.transform(child.matrix_world)
        obj = bpy.data.objects.new(piece, mesh)
        bpy.context.scene.collection.objects.link(obj)
        leafy = any(m and m.name.startswith("leaves") for m in mesh.materials)
        if leafy:
            thin_leaves(mesh, LEAF_TRIS // max(1, sum(1 for c in parent.children_recursive if c.type == "MESH" and any(
                m and m.name.startswith("leaves") for m in c.data.materials))), piece + child.name)
        else:
            tris = sum(len(p.vertices) - 2 for p in mesh.polygons)
            if tris > BRANCH_TRIS:
                bpy.context.view_layer.objects.active = obj
                mod = obj.modifiers.new("dec", "DECIMATE")
                mod.ratio = BRANCH_TRIS / tris
                bpy.ops.object.select_all(action="DESELECT")
                obj.select_set(True)
                bpy.ops.object.modifier_apply(modifier="dec")
        parts.append(obj)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    if len(parts) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = piece
    vs = [v.co for v in obj.data.vertices]
    mn = Vector([min(v[i] for v in vs) for i in range(3)])
    mx = Vector([max(v[i] for v in vs) for i in range(3)])
    # Centro no tronco: o meio dos vértices perto do chão (a copa nem sempre fica em cima do pé).
    base = [v for v in vs if v.z < mn.z + (mx.z - mn.z) * 0.05] or vs
    cx = sum(v.x for v in base) / len(base)
    cy = sum(v.y for v in base) / len(base)
    k = height / (mx.z - mn.z)
    obj.data.transform(Matrix.Scale(k, 4) @ Matrix.Translation(-Vector((cx, cy, mn.z))))
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    print("árvore", piece, sum(len(p.vertices) - 2 for p in obj.data.polygons), "tri", [round((mx - mn)[i] * k, 1) for i in range(3)], "m")
    bpy.ops.export_scene.gltf(filepath=os.path.join(out_dir, piece + ".glb"), export_format="GLB", use_selection=True,
                              export_image_format="WEBP", export_image_quality=80)
