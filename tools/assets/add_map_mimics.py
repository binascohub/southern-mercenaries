"""Baús Monstro (chest_mimic) em todos os mapas de combate: cada mapa tem pelo menos 6 e ao menos 12% dos encontros (o Esgoto e a Floresta já têm bem mais).
Os novos (ids mm_*) ficam a 3 m de um encontro de sala, longe da partida e do chefe, num ponto livre; o nível é o do mapa (o balance_monsters.py ajusta a força
pela ordem dos mapas, igual aos outros monstros). Idempotente; roda antes do balance_monsters.py."""
import json, math, random

raw = open("data/arenas.json", encoding="utf-8").read()
data = json.loads(raw)
root = data.get("arenas", data)
rng = random.Random("map-mimics")
report = {}
for area_id, arena in root.items():
    if not isinstance(arena, dict) or arena.get("town") or not arena.get("encounters") or area_id == "prototype_arena":
        continue
    encounters = [e for e in arena["encounters"] if not e["id"].startswith("mm_")]
    arena["encounters"] = encounters
    is_mimic = lambda e: any(m["monster"] == "chest_mimic" for m in e["monsters"])
    have = sum(1 for e in encounters if is_mimic(e))
    want = max(6, math.ceil(len(encounters) * 0.12))
    start = arena["entries"].get("start", [0, 0])
    solids = [x["position"] for k in ("decor", "props", "breakables") for x in arena.get(k, []) if k != "decor" or x.get("solid") or x.get("collider")]
    bases = [e for e in encounters if not is_mimic(e) and math.hypot(e["position"][0] - start[0], e["position"][1] - start[1]) > 25 and not any(m["monster"].endswith(("boss", "general")) or "boss" in m["monster"] for m in e["monsters"])]
    rng.shuffle(bases)
    added = 0
    for base in bases:
        if have + added >= want:
            break
        bx, bz = base["position"]
        for dx, dz in ((3, -3), (-3, 3), (3, 3), (-3, -3), (4, 0), (-4, 0), (0, 4), (0, -4)):
            p = [round(bx + dx, 1), round(bz + dz, 1)]
            if any(math.hypot(q[0] - p[0], q[1] - p[1]) < 2.2 for q in solids) or any(math.hypot(e["position"][0] - p[0], e["position"][1] - p[1]) < 3.0 for e in encounters):
                continue
            encounters.append({"id": "mm_%d" % (added + 1), "position": p, "monsters": [{"monster": "chest_mimic", "count": 1}], "level": base.get("level", arena.get("area_level", 1))})
            added += 1
            break
    report[area_id] = "%d (+%d)" % (have + added, added)
open("data/arenas.json", "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent="\t" if raw.startswith("{\n\t") else 2) + ("\n" if raw.endswith("\n") else ""))
print("OK baús monstro por mapa:", report)
