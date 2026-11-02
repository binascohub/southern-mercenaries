"""Amplia a sala dos trolls da Floresta (a sala "hub", x de 36 a 60, z de -46 a -8): mais 14 m para a direita (leste) e mais 28 m para baixo (sul, z maior).
O que fica a leste dela (o corredor "cd", a sala do Rei Golem e tudo que está dentro) anda 14 m para leste junto com a parede; as portas continuam nos mesmos pontos
(oeste em z = -17,5, norte em x = 46, leste em z = -27) e as paredes de arbustos ficam nos novos limites, com as mesmas plantas nos trechos novos.
Roda antes de add_forest_king_room.py (é chamado no fim de tools/assets/build_maps.py). Idempotente: se a sala já tem o tamanho novo, não faz nada.
uso: python3 tools/assets/add_forest_troll_room.py   (a partir da raiz do projeto)"""
import json, random
ARENAS = "data/arenas.json"
EX, EZ = 14.0, 28.0
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
hub = next(r for r in forest["rooms"] if r["id"] == "hub")
if hub["size"][0] >= 24 + EX - 1e-6:
    print("OK sala dos trolls já ampliada")
    raise SystemExit
x0, x1 = hub["center"][0] - hub["size"][0] / 2, hub["center"][0] + hub["size"][0] / 2
z0, z1 = hub["center"][1] - hub["size"][1] / 2, hub["center"][1] + hub["size"][1] / 2
east_of_hub = lambda p: p[0] >= x1 + 0.5 and p[1] >= z0 - 0.5      # o corredor cd e a sala do Rei Golem (as salas ao sul da encruzilhada ficam em z < -46)


def shift(node):
    if isinstance(node, list):
        for n in node:
            shift(n)
    elif isinstance(node, dict):
        if isinstance(node.get("position"), list) and len(node["position"]) == 2 and east_of_hub(node["position"]):
            node["position"] = [round(node["position"][0] + EX, 2), node["position"][1]]
            if isinstance(node.get("path"), list) and len(node["path"]) == 2:
                node["path"] = [round(node["path"][0] + EX, 2), node["path"][1]]
        for k, v in node.items():
            if k not in ("position", "path") and isinstance(v, (list, dict)):
                shift(v)


for key in ("encounters", "props", "breakables", "crowd", "decor", "quest_spots", "hazards"):
    shift(forest[key])
for r in forest["rooms"]:
    if r["id"] != "hub" and r["center"][0] - r["size"][0] / 2 >= x1 + 0.5 and r["center"][1] + r["size"][1] / 2 >= z0 - 0.5:
        r["center"][0] = round(r["center"][0] + EX, 2)
hub["size"] = [hub["size"][0] + EX, hub["size"][1] + EZ]
hub["center"] = [round(hub["center"][0] + EX / 2, 2), round(hub["center"][1] + EZ / 2, 2)]
for i, d in enumerate(hub["doors"]):     # as portas ficam nos mesmos pontos: o deslocamento em relação ao novo centro
    side = d.split(":")[0]
    absolute = {"west": -17.5, "east": -27.0, "north": 46.0}[side]
    off = absolute - (hub["center"][0] if side == "north" else hub["center"][1])
    hub["doors"][i] = "%s:%g" % (side, round(off, 2))
rng = random.Random("forest-troll-room")
PIECES = ["Pl_Bamboo"] * 14 + ["Pl_Bush"] * 10 + ["Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Weed4", "Pl_Weed5"] * 6 + ["Pl_Hemp"] * 4 + ["Pl_Flower"] * 3 + \
    ["Pl_Shrub1", "Pl_Shrub2", "Pl_Shrub3", "Pl_Shrub4", "Pl_Shrub5"] * 2
strips = [(x1 + 0.5, x1 + EX - 0.5, z0 + 1.0, z1 - 1.0), (x0 + 1.0, x1 - 0.5, z1 + 0.5, z1 + EZ - 0.5)]   # a faixa leste e a faixa sul
count = 0
for sx0, sx1, sz0, sz1 in strips:
    for _ in range(round((sx1 - sx0) * (sz1 - sz0) * 0.18)):
        pos = [round(rng.uniform(sx0, sx1), 1), round(rng.uniform(sz0, sz1), 1)]
        if abs(pos[1] + 27.0) < 3.0 and pos[0] > x1 - 3.0:     # a porta leste (e o caminho até ela) fica livre
            continue
        forest["decor"].append({"piece": PIECES[count % len(PIECES)], "position": pos, "rotation": rng.randrange(360), "scale": round(rng.uniform(0.9, 1.4), 2)})
        count += 1
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK sala dos trolls ampliada para", hub["size"], "centro", hub["center"], "portas", hub["doors"], "- plantas novas:", count)
