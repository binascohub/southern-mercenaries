"""Bolsas de moedas espalhadas pela Floresta (breakables "coin_bag_N", tabela "coin_bag" de data/loot.json: sempre soltam ouro): 1 ou 2 em cada sala grande (a sala com a
bolsa original da partida e os corredores ficam de fora), em pontos sorteados longe das paredes, da trilha (3 m), dos bandos, dos adereços, dos cervos e umas das outras (6 m).
Roda depois de add_forest_king_room.py e antes do espaçamento (é chamado no fim de tools/assets/build_maps.py). Idempotente: refaz as bolsas "coin_bag_N" (a "coin_bag" fica).
uso: python3 tools/assets/add_forest_coin_bags.py   (a partir da raiz do projeto)"""
import json, math, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
forest["breakables"] = [b for b in forest["breakables"] if not b["id"].startswith("coin_bag_")]
avoid = [(d["position"][0], d["position"][1], 3.0) for d in forest["decor"] if str(d.get("piece", "")).startswith("Trail_")]
avoid += [(e["position"][0], e["position"][1], 5.0) for e in forest["encounters"]]
avoid += [(p["position"][0], p["position"][1], 6.0) for p in forest["props"] if "position" in p]
avoid += [(b["position"][0], b["position"][1], 4.0) for b in forest["breakables"]]
avoid += [(d["position"][0], d["position"][1], 3.5) for d in forest["decor"] if d.get("solid") or d.get("collider") or d.get("light")]
rng = random.Random("forest-coin-bags")
placed = []
for room in forest["rooms"]:
    cx, cz = room["center"]
    w, h = room["size"]
    if w * h < 300 or w < 20 or h < 20:      # só as salas grandes (corredores e salinhas ficam de fora)
        continue
    want = 1 if w * h >= 600 else 0   # segundo mapa do jogo: ouro direto contido (a renda vem das missões e do tesouro)
    if want == 0:
        continue
    got = 0
    for _ in range(400):
        if got >= want:
            break
        x, z = round(cx + rng.uniform(-w / 2 + 3.0, w / 2 - 3.0), 1), round(cz + rng.uniform(-h / 2 + 3.0, h / 2 - 3.0), 1)
        if any(math.hypot(x - ax, z - az) < ar for ax, az, ar in avoid) or any(math.hypot(x - px, z - pz) < 6.0 for px, pz in placed):
            continue
        placed.append((x, z))
        got += 1
        forest["breakables"].append({"id": "coin_bag_%d" % len(placed), "monster": "coin_bag", "position": [x, z], "table": "coin_bag"})
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK bolsas de moedas espalhadas:", len(placed))
