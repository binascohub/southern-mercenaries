"""Rochas musgosas (Mossy Rock, hooded_kian, CC0) espalhadas pela Floresta e pelo Cemitério (data/arenas.json "decor", peça Rock_Mossy com colisão): umas
poucas por sala, longe das portas, dos encontros e dos baús. Idempotente; chamado no fim de tools/assets/build_maps.py.
uso: python3 tools/assets/add_mossy_rocks.py   (a partir da raiz do projeto)"""
import json, math, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
DOOR = 6.0
total = 0
for area, per_room in {"forest_01_path": 1 / 170.0, "cemetery_01_yard": 1 / 220.0}.items():
    a = arenas[area]
    r = random.Random("mossy-" + area)
    a["decor"] = [d for d in a["decor"] if d.get("piece") != "Rock_Mossy"]
    keep_away = [e["position"] for e in a["encounters"]] + [p["position"] for p in a["props"] if "position" in p]
    for room in a["rooms"]:
        cx, cz = room["center"]
        w, h = room["size"]
        if min(w, h) < 9:
            continue
        doors = []
        for d in room.get("doors", []):
            side, off = (d.split(":")[0], float(d.split(":")[1])) if ":" in d else (d, 0.0)
            doors.append({"north": (cx + off, cz - h / 2), "south": (cx + off, cz + h / 2), "east": (cx + w / 2, cz + off), "west": (cx - w / 2, cz + off)}[side])
        count = max(1, round(w * h * per_room))
        for _ in range(count):
            for _try in range(30):
                x, z = cx + r.uniform(-w / 2 + 2.5, w / 2 - 2.5), cz + r.uniform(-h / 2 + 2.5, h / 2 - 2.5)
                if any(math.hypot(x - dx, z - dz) < DOOR + 2 for dx, dz in doors):
                    continue
                if any(math.hypot(x - kx, z - kz) < 6 for kx, kz in keep_away):
                    continue
                s = round(r.uniform(0.7, 1.5), 2)
                a["decor"].append({"piece": "Rock_Mossy", "position": [round(x, 1), round(z, 1)], "rotation": r.randrange(0, 360, 15), "scale": s,
                                   "solid": [round(2.2 * s, 1), round(1.9 * s, 1)]})
                total += 1
                break
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK mossy rocks", total)
