"""Placas de cruzamento nos mapas ao ar livre: um poste Signpost_Medieval (Medieval Signs, AnyRPG, CC0) ao lado do meio de cada sala com várias portas
(3 ou mais; 4 ou mais no Cemitério, que tem muitas), em data/arenas.json "decor". Idempotente; chamado no fim de tools/assets/build_maps.py.
uso: python3 tools/assets/add_signposts.py   (a partir da raiz do projeto)"""
import json, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
MAPS = {"forest_01_path": 3, "cemetery_01_yard": 4, "dark_forest_01_woods": 3, "desert_01_canyon": 3, "docks_01_pier": 3, "mine_01_crystal_vein": 3}
total = 0
for area, min_doors in MAPS.items():
    a = arenas[area]
    r = random.Random("signs-" + area)
    a["decor"] = [d for d in a["decor"] if d.get("piece") != "Signpost_Medieval"]
    for room in a["rooms"]:
        if len(room.get("doors", [])) < min_doors:
            continue
        cx, cz = room["center"]
        w, h = room["size"]
        dx = min(3.0, w / 2 - 1.5) * r.choice((-1, 1))
        dz = min(2.5, h / 2 - 1.5) * r.choice((-1, 1))
        a["decor"].append({"piece": "Signpost_Medieval", "position": [round(cx + dx, 1), round(cz + dz, 1)], "rotation": r.randrange(0, 360, 15), "solid": [0.6, 0.6]})
        total += 1
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK signposts", total)
