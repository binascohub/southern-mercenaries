"""Mais cervos espalhados pela Floresta (breakables "deer_N", tabela "breakable_meat": soltam carne): 1 ou 2 em cada sala grande, em pontos sorteados longe das paredes, da trilha (3 m),
dos bandos, dos adereços, das bolsas de moedas, dos outros cervos (8 m) e do templo, alternando cervo e corça. Roda depois de add_forest_coin_bags.py e antes do espaçamento (é chamado no
fim de tools/assets/build_maps.py). Idempotente: refaz os "deer_N" (os d1..d5, ds e dt ficam).
uso: python3 tools/assets/add_forest_deer.py   (a partir da raiz do projeto)"""
import json, math, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
forest["breakables"] = [b for b in forest["breakables"] if not b["id"].startswith("deer_")]
avoid = [(d["position"][0], d["position"][1], 3.0) for d in forest["decor"] if str(d.get("piece", "")).startswith("Trail_")]
avoid += [(e["position"][0], e["position"][1], 5.0) for e in forest["encounters"]]
avoid += [(p["position"][0], p["position"][1], 7.0) for p in forest["props"] if "position" in p]
avoid += [(b["position"][0], b["position"][1], 8.0 if b["monster"].startswith("deer") else 4.0) for b in forest["breakables"]]
avoid += [(d["position"][0], d["position"][1], 3.5) for d in forest["decor"] if d.get("solid") or d.get("collider") or d.get("light")]
rng = random.Random("forest-more-deer")
placed = []
for room in forest["rooms"]:
    cx, cz = room["center"]
    w, h = room["size"]
    if w * h < 300 or w < 20 or h < 20:      # só as salas grandes
        continue
    want = 2 if w * h >= 600 else 1
    got = 0
    for _ in range(500):
        if got >= want:
            break
        x, z = round(cx + rng.uniform(-w / 2 + 4.0, w / 2 - 4.0), 1), round(cz + rng.uniform(-h / 2 + 4.0, h / 2 - 4.0), 1)
        if any(math.hypot(x - ax, z - az) < ar for ax, az, ar in avoid) or any(math.hypot(x - px, z - pz) < 8.0 for px, pz in placed):
            continue
        placed.append((x, z))
        got += 1
        forest["breakables"].append({"id": "deer_%d" % len(placed), "monster": "deer_buck" if len(placed) % 2 else "deer_doe", "position": [x, z], "table": "breakable_meat"})
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK cervos a mais:", len(placed))
