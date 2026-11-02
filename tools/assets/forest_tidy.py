"""Arruma a Floresta (data/arenas.json "decor" de forest_01_path): tira o chão de pedra (Floor_UnevenBrick), tira as pedras que ficam no meio da trilha de lama
(Trail_Mud) e as põe ao lado dela, e planta mais folhagem na sala de entrada (a de baixo, à esquerda). build_maps.py ainda gera o chão de pedra, então este script
roda depois dele (é chamado no fim de tools/assets/build_maps.py). Idempotente.
uso: python3 tools/assets/forest_tidy.py   (a partir da raiz do projeto)"""
import json, math, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
decor = forest["decor"]
before = len(decor)
decor[:] = [d for d in decor if d.get("piece") != "Floor_UnevenBrick"]
trail = [d["position"] for d in decor if d.get("piece") == "Trail_Mud"]
keep_away = [e["position"] for e in forest["encounters"]] + [p["position"] for p in forest["props"] if "position" in p]
rooms = forest["rooms"]


def room_of(p):
    for r in rooms:
        cx, cz = r["center"]
        w, h = r["size"]
        if abs(p[0] - cx) <= w / 2 and abs(p[1] - cz) <= h / 2:
            return r
    return None


def off_trail(x, z, margin):
    return all(math.hypot(x - tx, z - tz) >= margin for tx, tz in trail)


rng = random.Random("forest-tidy")
moved = 0
for d in decor:
    piece = str(d.get("piece", ""))
    if not (piece == "Rock_Mossy" or piece.startswith("RockP_")) or "position" not in d:
        continue
    p = d["position"]
    if off_trail(p[0], p[1], 2.7):
        continue
    room = room_of(p)
    if room is None:
        continue
    cx, cz = room["center"]
    w, h = room["size"]
    for _ in range(200):
        x, z = p[0] + rng.uniform(-7, 7), p[1] + rng.uniform(-7, 7)
        if abs(x - cx) > w / 2 - 2.5 or abs(z - cz) > h / 2 - 2.5:
            continue
        if off_trail(x, z, 4.5) and all(math.hypot(x - kx, z - kz) >= 6 for kx, kz in keep_away):
            d["position"] = [round(x, 1), round(z, 1)]
            moved += 1
            break
# mais plantas na sala de entrada (a de baixo, à esquerda): fora da trilha, dos encontros, das portas e das pedras
PLANTS = ["Pl_Bush", "Pl_Shrub1", "Pl_Shrub2", "Pl_Shrub3", "Pl_Shrub4", "Pl_Shrub5", "Pl_Flower", "Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Hemp", "Pl_Swirl"]
decor[:] = [d for d in decor if not d.get("tidy_plant")]
entry = rooms[0]
cx, cz = entry["center"]
w, h = entry["size"]
rocks = [d["position"] for d in decor if str(d.get("piece", "")).startswith("Rock") and "position" in d]
added = 0
for _ in range(600):
    if added >= 45:
        break
    x, z = cx + rng.uniform(-w / 2 + 1.5, w / 2 - 1.5), cz + rng.uniform(-h / 2 + 1.5, h / 2 - 1.5)
    if not off_trail(x, z, 2.2) or any(math.hypot(x - kx, z - kz) < 4 for kx, kz in keep_away) or any(math.hypot(x - rx, z - rz) < 2.5 for rx, rz in rocks):
        continue
    entry_d = {"piece": rng.choice(PLANTS), "position": [round(x, 1), round(z, 1)], "rotation": rng.randrange(0, 360, 15), "scale": round(rng.uniform(0.9, 1.5), 2), "tidy_plant": True}
    decor.append(entry_d)
    added += 1
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK Floresta: chão de pedra removido", before - len(decor) + added, "| pedras tiradas da trilha", moved, "| plantas novas", added)
