"""Amplia o mapa dos sapos da Floresta (a Praça da Pira, sala "pira") para o sul (z maior): duas salas novas empilhadas abaixo dela, do mesmo tamanho,
"pira_s" (z de -7 a 14) e "pira_t" (z de 14 a 35), ligadas por portas norte/sul. Cada uma ganha as mesmas plantas e dois grupos de sapos ácidos; a "pira_t"
tem também uma lagoa (duas elipses de água) no centro. Também põe peixes nadando nas lagoas grandes (a da praça e a da "pira_t"). Roda depois de add_forest_pond.py (é chamado no fim de tools/assets/build_maps.py). Idempotente.
uso: python3 tools/assets/add_forest_pira_south.py   (a partir da raiz do projeto)"""
import json, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
pira = next(r for r in forest["rooms"] if r["id"] == "pira")
cx, cz = pira["center"]
w, h = pira["size"]
NEW = [("pira_s", 1), ("pira_t", 2)]
forest["rooms"] = [r for r in forest["rooms"] if r["id"] not in ("pira_s", "pira_t")]
forest["encounters"] = [e for e in forest["encounters"] if not e["id"].startswith("f_toads_s")]
forest["props"] = [p for p in forest["props"] if not p["id"].startswith("toad_pond_s")]
forest["breakables"] = [b for b in forest["breakables"] if not b["id"].startswith(("ds", "dt"))]
if "south" not in pira["doors"]:
    pira["doors"].append("south")
PIECES = ["Pl_Bamboo"] * 14 + ["Pl_Bush"] * 10 + ["Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Weed4", "Pl_Weed5"] * 6 + ["Pl_Hemp"] * 4 + ["Pl_Flower"] * 3 + \
    ["Pl_Shrub1", "Pl_Shrub2", "Pl_Shrub3", "Pl_Shrub4", "Pl_Shrub5"] * 2
shift = 0
for idx, (rid, step) in enumerate(NEW):
    sz = cz + h * step
    doors = ["north"] + (["south"] if idx < len(NEW) - 1 else [])
    forest["rooms"].append({"id": rid, "center": [cx, sz], "size": [w, h], "doors": doors, "wall_height": pira.get("wall_height", 0.8)})
    inside = lambda p, sz=sz: abs(p[0] - cx) <= w / 2 and abs(p[1] - sz) <= h / 2
    forest["decor"] = [d for d in forest["decor"] if not inside(d["position"])]
    ponds = []
    if rid == "pira_t":
        ponds = [("toad_pond_s1", [cx, sz], [12.0, 6.5]), ("toad_pond_s2", [cx + 4.5, sz - 1.2], [6.0, 4.0])]
        for pid, at, size in ponds:
            forest["props"].append({"id": pid, "kind": "water", "position": [round(at[0], 1), round(at[1], 1)], "size": size, "round": True, "color": [0.12, 0.3, 0.3]})
    spots = [(-6.0, 3.0), (6.0, 3.0)] if rid == "pira_s" else [(-6.0, -3.0), (6.0, -3.0)]
    for i, (dx, dz) in enumerate(spots):
        forest["encounters"].append({"id": "f_toads_s%d" % (2 * idx + i + 1), "position": [cx + dx, sz + dz], "monsters": [{"monster": "acid_toad", "count": 3}]})
    # Dois cervos por sala, que ao quebrar soltam carne (tabela "breakable_meat").
    for i, (dx, dz) in enumerate([(-8.0, -4.5), (8.5, -4.0)] if rid == "pira_s" else [(-8.0, 5.0), (8.5, 4.5)]):
        forest["breakables"].append({"id": "d%s%d" % (rid[-1], i + 1), "monster": "deer_buck" if i == 0 else "deer_doe", "position": [cx + dx, sz + dz], "table": "breakable_meat"})
    rng = random.Random("forest-%s" % rid)
    for piece in PIECES:
        for _ in range(60):
            x, z = cx + rng.uniform(-w / 2 + 1.5, w / 2 - 1.5), sz + rng.uniform(-h / 2 + 1.5, h / 2 - 1.5)
            if abs(x - cx) < 2.5 and (z < sz - h / 2 + 4.5 or (idx < len(NEW) - 1 and z > sz + h / 2 - 4.5)):
                continue  # as portas ficam livres
            if any(((x - at[0]) / (size[0] / 2 + 0.6)) ** 2 + ((z - at[1]) / (size[1] / 2 + 0.6)) ** 2 < 1.0 for _, at, size in ponds):
                continue
            break
        forest["decor"].append({"piece": piece, "position": [round(x, 1), round(z, 1)], "rotation": rng.randrange(360), "scale": round(rng.uniform(0.9, 1.4), 2)})
# Peixes (Fish_Catfish, a mesma peça da Fazenda) nadando em círculos nas lagoas grandes: a da praça e a da "pira_t".
forest["decor"] = [d for d in forest["decor"] if d.get("piece") != "Fish_Catfish"]
rf = random.Random("forest-fish")
for pid in ("toad_pond", "toad_pond_s1"):
    pond = next(q for q in forest["props"] if q["id"] == pid)
    for radius in (1.2, 2.0, 2.6):
        forest["decor"].append({"piece": "Fish_Catfish", "position": [pond["position"][0], pond["position"][1]], "y": 0.0, "scale": 1.6,
                                "swim": {"radius": radius, "speed": round(rf.uniform(0.5, 0.9), 2), "phase": round(rf.uniform(0, 6.28), 2)}})
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK salas", [r for r, _ in NEW])
