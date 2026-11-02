"""Afasta as áreas da Floresta (data/arenas.json, forest_01_path): cada caminho de passagem (os corredores entre as salas) fica D = 12 m mais comprido.
As salas grandes só se deslocam (com tudo que está dentro: cenário, adereços, encontros, cervos, bichos, NPCs, pontos de partida); os corredores esticam: o que
está antes do meio fica, o que está depois anda D, e o trecho novo ganha trilha de barro e plantas. A porta de cada corredor continua alinhada com a da sala vizinha.
O deslocamento de cada sala sai da árvore de salas (aldeia -> ... -> Covil do Leshy): dx e dz em múltiplos de D, a partir da sala de partida.
Roda por último entre os scripts da Floresta (é chamado no fim de tools/assets/build_maps.py). Não é idempotente sozinho: grava "_spacing" na área e, se ele já existe, não faz nada
(o build_maps.py regenera os dados e tira a marca).
uso: python3 tools/assets/add_forest_spacing.py   (a partir da raiz do projeto)"""
import json, math, random
ARENAS = "data/arenas.json"
D = 12.0
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
if forest.get("_spacing"):
    print("OK espaçamento já aplicado")
    raise SystemExit
# (x0, z0, z1) da sala original -> ("room", dx, dz) | ("h", dx_esquerda, dx_direita, dz) | ("v", dz_cima, dz_baixo, dx)   (múltiplos de D)
SPEC = {
    (-41, -28, -7): ("room", 0, 0), (-36, -38, -28): ("v", 0, -1, 0), (-41, -60, -38): ("room", 0, -1),
    (-16, -21.5, -13.5): ("h", 0, 1, 0), (0, -28, -7): ("room", 1, 0), (0, -7, 14): ("room", 1, 0), (0, 14, 35): ("room", 1, 0),
    (6, -38, -28): ("v", 0, -1, 1), (-6, -56, -38): ("room", 1, -1), (25, -21.5, -13.5): ("h", 1, 2, 0), (36, -46, 20): ("room", 2, 0),
    (75, -33, -21): ("h", 2, 3, 0), (86, -65, -9): ("room", 3, 0), (40, -56, -46): ("v", 0, -1, 2), (32, -82, -56): ("room", 2, -1),
    (14, -76, -64): ("h", 1, 2, -1), (-12, -90, -60): ("room", 1, -1), (40, -92, -82): ("v", -1, -2, 2), (32, -122, -92): ("room", 2, -2),
}
rects = []
for r in forest["rooms"]:
    x0, x1 = r["center"][0] - r["size"][0] / 2, r["center"][0] + r["size"][0] / 2
    z0, z1 = r["center"][1] - r["size"][1] / 2, r["center"][1] + r["size"][1] / 2
    rects.append((r, x0, x1, z0, z1, SPEC[(round(x0, 1), round(z0, 1), round(z1, 1))]))


def room_of(x, z):
    best, bd = None, 1e9
    for item in rects:
        _, x0, x1, z0, z1, _ = item
        d = math.hypot(max(x0 - x, 0, x - x1), max(z0 - z, 0, z - z1))
        if d < bd:
            best, bd = item, d
    return best


def offset(x, z):
    r, x0, x1, z0, z1, spec = room_of(x, z)
    if spec[0] == "room":
        return spec[1] * D, spec[2] * D
    if spec[0] == "h":
        return (spec[1] if x < (x0 + x1) / 2 else spec[2]) * D, spec[3] * D
    return spec[3] * D, (spec[1] if z > (z0 + z1) / 2 else spec[2]) * D


def move(pt):
    dx, dz = offset(pt[0], pt[1])
    return [round(pt[0] + dx, 2), round(pt[1] + dz, 2)], (dx, dz)


def walk(node):
    """Translada tudo que tem "position" (e o "path" junto, com o mesmo deslocamento) e os pontos de partida."""
    if isinstance(node, list):
        for n in node:
            walk(n)
    elif isinstance(node, dict):
        if isinstance(node.get("position"), list) and len(node["position"]) == 2 and all(isinstance(v, (int, float)) for v in node["position"]):
            node["position"], (dx, dz) = move(node["position"])
            if isinstance(node.get("path"), list) and len(node["path"]) == 2:
                node["path"] = [round(node["path"][0] + dx, 2), round(node["path"][1] + dz, 2)]
        for k, v in node.items():
            if k != "position" and isinstance(v, (list, dict)) and k != "path":
                walk(v)


old = {r["id"]: (x0, x1, z0, z1, spec) for r, x0, x1, z0, z1, spec in rects}
walk(forest["encounters"]); walk(forest["props"]); walk(forest["breakables"]); walk(forest["crowd"]); walk(forest["decor"]); walk(forest["quest_spots"]); walk(forest["hazards"])
for k, pt in forest["entries"].items():
    forest["entries"][k], _ = move(pt)
# As salas: grandes se deslocam; corredores esticam D.
for r, x0, x1, z0, z1, spec in rects:
    if spec[0] == "room":
        r["center"] = [r["center"][0] + spec[1] * D, r["center"][1] + spec[2] * D]
    elif spec[0] == "h":
        nx0, nx1 = x0 + spec[1] * D, x1 + spec[2] * D
        r["center"] = [(nx0 + nx1) / 2, r["center"][1] + spec[3] * D]
        r["size"] = [nx1 - nx0, r["size"][1]]
    else:
        nz0, nz1 = z0 + spec[2] * D, z1 + spec[1] * D
        r["center"] = [r["center"][0] + spec[3] * D, (nz0 + nz1) / 2]
        r["size"] = [r["size"][0], nz1 - nz0]
# Trecho novo de cada corredor: trilha de barro pela linha da porta e plantas dos lados.
rng = random.Random("forest-spacing")
PIECES = ["Pl_Bamboo"] * 4 + ["Pl_Bush"] * 3 + ["Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Weed4", "Pl_Weed5"] * 2 + ["Pl_Hemp", "Pl_Flower", "Pl_Shrub1", "Pl_Shrub2", "Pl_Shrub3"]
n = 0
for r, x0, x1, z0, z1, spec in rects:
    if spec[0] == "room":
        continue
    if spec[0] == "h":
        a, b = (x0 + x1) / 2 + spec[1] * D, (x0 + x1) / 2 + spec[1] * D + D     # intervalo novo em x
        line = r["center"][1]
        half = r["size"][1] / 2
        along = lambda t: [t, line]
        span = lambda t, o: [round(t, 2), round(line + o, 2)]
    else:
        a, b = (z0 + z1) / 2 + spec[2] * D, (z0 + z1) / 2 + spec[2] * D + D     # intervalo novo em z
        line = r["center"][0]
        half = r["size"][0] / 2
        span = lambda t, o: [round(line + o, 2), round(t, 2)]
    # de a até b (em x ou em z, crescendo)
    t = a + 0.55
    while t < b:
        o = rng.uniform(-0.25, 0.25)
        forest["decor"].append({"piece": "Trail_Mud", "rotation": rng.randrange(0, 360, 15), "position": span(t, o), "scale": round(rng.uniform(0.7, 0.9), 2), "y": round(0.012 + 0.002 * (n % 5), 3)})
        n += 1
        t += 1.1
    for _ in range(round(D * half * 2 * 0.16)):
        t = rng.uniform(a, b)
        o = rng.uniform(-half + 1.0, half - 1.0)
        if abs(o) < 2.2:
            continue
        forest["decor"].append({"piece": rng.choice(PIECES), "position": span(t, o), "rotation": rng.randrange(360), "scale": round(rng.uniform(0.9, 1.4), 2)})
# Conferência: nenhuma sala sobre outra.
boxes = [(r["id"], r["center"][0] - r["size"][0] / 2, r["center"][0] + r["size"][0] / 2, r["center"][1] - r["size"][1] / 2, r["center"][1] + r["size"][1] / 2) for r in forest["rooms"]]
for i, a in enumerate(boxes):
    for b in boxes[i + 1:]:
        assert a[2] <= b[1] + 1e-6 or b[2] <= a[1] + 1e-6 or a[4] <= b[3] + 1e-6 or b[4] <= a[3] + 1e-6, ("salas sobrepostas", a, b)
forest["_spacing"] = D
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK espaçamento: corredores %g m mais compridos" % D)
