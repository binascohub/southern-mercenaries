"""Caixotes e cerâmicas quebráveis em todos os mapas de combate, em grupos nos cantos e nas bordas das salas: 3 caixotes juntos ou 5 a 8 potes e jarros juntos.
Tudo quebra com qualquer golpe (monstros `crate` e `pot` de data/monsters.json) e solta o que a tabela do objeto manda (data/loot.json): nada, ouro, poção de vida ou de recurso, ou um Mímico escondido
(`mimic`, mais comum nos caixotes). Os grupos ficam longe das portas, da entrada e de qualquer coisa que bloqueie. Os barris continuam só decorativos.
Idempotente (os ids `cx_*` e `pt_*` são refeitos); chamado em tools/assets/build_maps.py depois de make_barrels_decor.py.
uso: python3 tools/assets/add_crates_pots.py   (a partir da raiz do projeto)"""
import json, math, random, re
ARENAS, LOOT = "data/arenas.json", "data/loot.json"
MAPS = ["sewers_01_drains", "forest_01_path", "ruins_01_city", "cemetery_01_yard", "fort_01_gate", "catacombs_01_depths", "desert_01_canyon", "docks_01_pier", "mine_01_crystal_vein",
        "bunker_01_entrance", "dark_forest_01_woods"]
BLOCKERS = ("Fort_", "Wall_", "Roof_", "Canyon_Rock", "Bk_", "Ruin_", "Cliff", "Corner_", "Pr_Obelisk", "Gatehouse")
arenas = json.load(open(ARENAS, encoding="utf-8"))
loot = json.load(open(LOOT, encoding="utf-8"))
loot["breakable_crate"] = {"_comment": "Caixotes dos cantos dos mapas: poção de vida ou de recurso, ou um Mímico que estava escondido (data/monsters.json chest_mimic).",
                           "outcomes": {"nothing": 30, "potion_health": 28, "potion_resource": 20, "mimic": 22}}
loot["breakable_pot"] = {"_comment": "Potes e jarros dos cantos dos mapas: moedas, ou raramente um Mímico.",
                         "outcomes": {"nothing": 40, "gold": 54, "mimic": 6}, "gold": {"min": 1, "max": 4, "per_level": 0.6}}
json.dump(loot, open(LOOT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(LOOT, "a").write("\n")


def door_points(room):
    cx, cz = room["center"]
    w, h = room["size"]
    out = []
    for spec in room.get("doors", []):
        side, _, off = str(spec).partition(":")
        off = float(off) if off else 0.0
        out.append({"north": (cx + off, cz - h / 2), "south": (cx + off, cz + h / 2), "west": (cx - w / 2, cz + off), "east": (cx + w / 2, cz + off)}[side])
    return out


total = {}
for name in MAPS:
    area = arenas[name]
    rng = random.Random("crates-" + name)
    area["breakables"] = [b for b in area.get("breakables", []) if not re.match(r"^(cx|pt)_\d+$", str(b.get("id", "")))]
    obstacles = []
    for d in area["decor"]:
        if "position" not in d:
            continue
        if "solid" in d or "collider" in d:
            s = d.get("solid") or d.get("collider")
            obstacles.append((d["position"][0], d["position"][1], max(s) / 2.0 + 1.0))
        elif str(d.get("piece", "")).startswith(BLOCKERS):
            obstacles.append((d["position"][0], d["position"][1], 2.4))
    for p in area["props"]:
        if "position" in p:
            obstacles.append((p["position"][0], p["position"][1], 3.2))
    for e in area["encounters"]:
        obstacles.append((e["position"][0], e["position"][1], 3.0))
    for b in area["breakables"]:
        obstacles.append((b["position"][0], b["position"][1], 1.0))
    starts = list(area.get("entries", {}).values())
    rooms = [r for r in area["rooms"] if min(r["size"]) >= 10]
    spots = []
    for r in rooms:
        cx, cz = r["center"]
        w, h = r["size"]
        doors = door_points(r)
        inset = 1.7
        cand = [(cx + sx * (w / 2 - inset), cz + sz * (h / 2 - inset), sx, sz) for sx in (-1, 1) for sz in (-1, 1)]
        for t in range(1, int(w // 10)):  # bordas: a cada ~10 m ao longo dos lados norte e sul
            x = cx - w / 2 + t * w / int(w // 10)
            cand += [(x, cz - h / 2 + inset, 0, -1), (x, cz + h / 2 - inset, 0, 1)]
        for t in range(1, int(h // 10)):
            z = cz - h / 2 + t * h / int(h // 10)
            cand += [(cx - w / 2 + inset, z, -1, 0), (cx + w / 2 - inset, z, 1, 0)]
        for x, z, sx, sz in cand:
            if any(math.hypot(x - dx, z - dz) < 6.0 for dx, dz in doors) or any(math.hypot(x - ex, z - ez) < 7.0 for ex, ez in starts):
                continue
            spots.append((x, z, sx, sz))
    rng.shuffle(spots)
    want = max(10, min(40, len(rooms) // 2 + 8))
    counters = {"cx": 0, "pt": 0}
    clusters = 0

    def try_cluster(x, z, sx, sz):
        if any(math.hypot(x - ox, z - oz) < r + 0.6 for ox, oz, r in obstacles):
            return False
        crates = rng.random() < 0.4
        items = []
        if crates:  # três caixotes encostados, em L, de frente para o canto
            offs = [(0.0, 0.0), (-sx * 1.05 if sx else 1.05, 0.0), (0.0, -sz * 1.05 if sz else 1.05)] if sx and sz else [(0.0, 0.0), (1.05, 0.0), (0.5, -sz * 1.0 if sz else 1.0)]
            items = [(x + dx, z + dz, "crate") for dx, dz in offs]
        else:
            n = rng.randint(5, 8)
            pts = []
            for _ in range(n * 30):
                if len(pts) >= n:
                    break
                px = x - sx * rng.uniform(0.0, 1.6) + (rng.uniform(-1.6, 1.6) if not sx else 0.0)
                pz = z - sz * rng.uniform(0.0, 1.6) + (rng.uniform(-1.6, 1.6) if not sz else 0.0)
                if all(math.hypot(px - qx, pz - qz) > 0.62 for qx, qz in pts):
                    pts.append((px, pz))
            items = [(px, pz, "pot") for px, pz in pts]
        if any(any(math.hypot(ix - ox, iz - oz) < r for ox, oz, r in obstacles) for ix, iz, _ in items):
            return False
        for ix, iz, kind in items:
            tag = "cx" if kind == "crate" else "pt"
            counters[tag] += 1
            area["breakables"].append({"id": "%s_%d" % (tag, counters[tag]), "monster": kind, "position": [round(ix, 1), round(iz, 1)], "table": "breakable_crate" if kind == "crate" else "breakable_pot"})
            obstacles.append((ix, iz, 0.9))
        return True

    for x, z, sx, sz in spots:
        if clusters >= want:
            break
        clusters += 1 if try_cluster(x, z, sx, sz) else 0
    if clusters < want // 2:  # mapas de uma sala só (Forte, Bunker): as paredes de pedra ficam no meio da sala; pega pontos livres junto de um bloqueio, no chão andável (perto de um encontro)
        blockers = [(o[0], o[1]) for o in obstacles if o[2] >= 2.4]
        walk = [tuple(e["position"]) for e in area["encounters"]] + [tuple(p["position"]) for p in area["props"] if "position" in p]
        for _ in range(6000):
            if clusters >= want:
                break
            bx, bz = rng.choice(blockers) if blockers else (0.0, 0.0)
            a_ = rng.uniform(0, math.tau)
            x, z = bx + math.cos(a_) * rng.uniform(3.2, 4.6), bz + math.sin(a_) * rng.uniform(3.2, 4.6)
            if (walk and min(math.hypot(x - wx, z - wz) for wx, wz in walk) > 12.0) or any(math.hypot(x - ex, z - ez) < 7.0 for ex, ez in starts):
                continue
            clusters += 1 if try_cluster(x, z, rng.choice((-1, 1)), rng.choice((-1, 1))) else 0
    total[name] = "%d grupos (%d caixotes, %d potes)" % (clusters, counters["cx"], counters["pt"])
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK caixotes e cerâmicas:", total)
