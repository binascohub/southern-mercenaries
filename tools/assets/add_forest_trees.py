"""Árvores na Floresta toda: troca um pouco da vegetação (arbustos e bambus) por carvalhos vivos (Oak_Tree; o tronco bloqueia), uns 1 por 110 m² de sala,
longe da trilha, das portas, dos grupos de monstros, dos adereços (NPCs, água, portais), da fogueira e entre si. Roda por último (é chamado no fim de
tools/assets/build_maps.py). Idempotente: tira as árvores anteriores e põe de novo (semente própria).
uso: python3 tools/assets/add_forest_trees.py   (a partir da raiz do projeto)"""
import json, math, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
forest["decor"] = [d for d in forest["decor"] if d.get("piece") != "Oak_Tree"]
decor = forest["decor"]
VEG = ("Pl_Bush", "Pl_Shrub", "Pl_Bamboo")
keep = [(d["position"][0], d["position"][1], 3.0) for d in decor if str(d.get("piece", "")).startswith("Trail_")]
keep += [(e["position"][0], e["position"][1], 5.0) for e in forest["encounters"]]
keep += [(p["position"][0], p["position"][1], max(4.0, max(p.get("size", [0, 0])) / 2 + 2.5)) for p in forest["props"] if "position" in p]
keep += [(b["position"][0], b["position"][1], 3.0) for b in forest.get("breakables", [])]
keep += [(c["position"][0], c["position"][1], 3.0) for c in forest.get("crowd", [])]
keep += [(d["position"][0], d["position"][1], 4.0) for d in decor if d.get("camp") or d.get("light") or d.get("piece") in ("Fire_Flame", "Signpost_Medieval", "Pr_RoadSign", "Pr_LampPost")]
keep += [(d["position"][0], d["position"][1], 11.0) for d in decor if d.get("piece") == "Ruin_Temple1"]   # o templo da sala do Rei Golem (e a peça que fica no adereço dele)
keep += [(p["position"][0], p["position"][1], 11.0) for p in forest["props"] if p.get("kit") == "Ruin_Temple1"]
trees = []
rng = random.Random("forest-living-trees")
for room in forest["rooms"]:
    cx, cz = room["center"]
    w, h = room["size"]
    want = max(1, round(w * h / 110))
    cands = [d for d in decor if str(d.get("piece", "")).startswith(VEG) and abs(d["position"][0] - cx) <= w / 2 - 3.0 and abs(d["position"][1] - cz) <= h / 2 - 3.0]
    rng.shuffle(cands)
    placed = 0
    for c in cands:
        x, z = c["position"]
        if placed >= want:
            break
        if any(math.hypot(x - kx, z - kz) < kr for kx, kz, kr in keep) or any(math.hypot(x - t["position"][0], z - t["position"][1]) < 9.0 for t in trees):
            continue
        scale = round(rng.uniform(0.8, 1.4), 2)
        side = round(1.1 * scale, 1)
        trees.append({"piece": "Oak_Tree", "position": [x, z], "rotation": rng.randrange(360), "scale": scale, "solid": [side, side]})
        placed += 1
# Tira a vegetação que ficaria dentro do tronco e da copa.
gone = lambda d: any(math.hypot(d["position"][0] - t["position"][0], d["position"][1] - t["position"][1]) < 1.6 for t in trees) and str(d.get("piece", "")).startswith("Pl_")
forest["decor"] = [d for d in decor if not gone(d)] + trees
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK árvores:", len(trees))
