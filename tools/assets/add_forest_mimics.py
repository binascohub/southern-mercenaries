"""Baús Monstro (chest_mimic) espalhados pela Floresta toda: 1 em cada sala (2 nas salas grandes), menos na aldeia da partida. São os únicos monstros agressivos do mapa
("aggressive" em data/monsters.json: acordam por proximidade; os outros só revidam), como no Esgoto. Encontros "f_mimic_N" de 1 monstro, em pontos sorteados longe das paredes,
dos outros bandos (5 m), dos adereços (6 m), das bolsas de moedas e cervos (4 m) e uns dos outros (8 m). Idempotente: refaz os "f_mimic_N".
uso: python3 tools/assets/add_forest_mimics.py   (a partir da raiz do projeto)"""
import json, math, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
forest["encounters"] = [e for e in forest["encounters"] if not e["id"].startswith("f_mimic_")]
avoid = [(e["position"][0], e["position"][1], 5.0) for e in forest["encounters"]]
avoid += [(p["position"][0], p["position"][1], 6.0) for p in forest["props"] if "position" in p]
avoid += [(b["position"][0], b["position"][1], 4.0) for b in forest["breakables"]]
avoid += [(d["position"][0], d["position"][1], 3.5) for d in forest["decor"] if d.get("solid") or d.get("collider") or d.get("light")]
avoid += [(d["position"][0], d["position"][1], 2.5) for d in forest["decor"] if str(d.get("piece", "")).startswith("Trail_")]
rng = random.Random("forest-mimics")
placed = []
count = 0
for room in forest["rooms"]:
    if room["id"] == "village":
        continue
    cx, cz = room["center"]
    w, h = room["size"]
    want = 2 if w * h >= 600 else 1
    got = 0
    for _ in range(600):
        if got >= want:
            break
        x, z = round(cx + rng.uniform(-w / 2 + 2.5, w / 2 - 2.5), 1), round(cz + rng.uniform(-h / 2 + 2.5, h / 2 - 2.5), 1)
        if any(math.hypot(x - ax, z - az) < ar for ax, az, ar in avoid) or any(math.hypot(x - px, z - pz) < 8.0 for px, pz in placed):
            continue
        placed.append((x, z))
        count += 1
        got += 1
        forest["encounters"].append({"id": "f_mimic_%d" % count, "position": [x, z], "monsters": [{"monster": "chest_mimic", "count": 1}]})
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("baús monstro:", count)
