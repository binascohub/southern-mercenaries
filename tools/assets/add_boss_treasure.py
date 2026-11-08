"""Tesouro dos chefes: joias de ouro (Gold_*, tools/assets/build_gold_treasure.py; "gold assets", Pranav 3d, CC BY 4.0) jogadas no chão em volta
do chefe final de cada mapa (os monstros "boss" dos encontros e o Leshy da Floresta). Cada joia cai num anel de RING_MIN a RING_MAX metros do
chefe, dentro da sala dele e longe das peças sólidas, dos objetos e das portas; nada é sólido (dá para pisar). Idempotente: as entradas antigas
(marcadas com "boss_gold": true) são refeitas. Roda no fim de tools/assets/build_maps.py.
uso: python3 tools/assets/add_boss_treasure.py   (a partir da raiz do projeto)"""
import json, math, random
ARENAS, MONSTERS = "data/arenas.json", "data/monsters.json"
JEWELS = ["Gold_Necklace", "Gold_Bangle", "Gold_Brooch", "Gold_Band", "Gold_Plate", "Gold_Orb", "Gold_Medallion", "Gold_Ring", "Gold_Medallion", "Gold_Ring", "Gold_Orb"]
EXTRA_BOSSES = {"leshy"}            # chefe final da Floresta, marcado como mini-chefe nos dados
RING_MIN, RING_MAX = 4.0, 8.5
arenas = json.load(open(ARENAS, encoding="utf-8"))
monsters = json.load(open(MONSTERS, encoding="utf-8"))
bosses = {k for k, v in monsters.items() if isinstance(v, dict) and v.get("category") == "boss"} | EXTRA_BOSSES


def room_of(arena, x, z):
    for r in arena.get("rooms", []):
        (cx, cz), (w, h) = r["center"], r["size"]
        if abs(x - cx) <= w / 2 and abs(z - cz) <= h / 2:
            return r
    return None


def blocked(arena, x, z, placed):
    for d in arena.get("decor", []):
        s = d.get("solid") or d.get("collider")
        if s and "position" in d:   # caixa da peça (girada de 90 em 90 graus; outros ângulos usam a caixa maior)
            sx, sz = s[0], s[-1]
            rot = int(d.get("rotation", 0)) % 180
            if rot == 90:
                sx, sz = sz, sx
            elif rot != 0:
                sx = sz = max(sx, sz)
            if abs(d["position"][0] - x) < sx / 2 + 0.6 and abs(d["position"][1] - z) < sz / 2 + 0.6:
                return True
    for p in arena.get("props", []):
        if "position" in p and math.hypot(p["position"][0] - x, p["position"][1] - z) < 1.8:
            return True
    return any(math.hypot(px - x, pz - z) < 1.1 for px, pz in placed)


total = 0
for aid, arena in arenas.items():
    if not isinstance(arena, dict) or "decor" not in arena:
        continue
    arena["decor"] = [d for d in arena["decor"] if not d.get("boss_gold")]
    floor_y = 0.13 if str(arena.get("style", {}).get("floor", "")).startswith("Dock_") else 0.0   # tábuas do píer
    for e in arena.get("encounters", []):
        if not any(isinstance(m, dict) and m.get("monster") in bosses for m in e.get("monsters", [])):
            continue
        bx, bz = e["position"]
        room = room_of(arena, bx, bz)
        if room is None:
            continue
        (cx, cz), (w, h) = room["center"], room["size"]
        rng = random.Random("boss-gold-" + aid + e["id"])
        placed = []
        for piece in JEWELS:
            for _ in range(60):
                a, r = rng.uniform(0, 2 * math.pi), rng.uniform(RING_MIN, RING_MAX)
                x, z = bx + r * math.cos(a), bz + r * math.sin(a)
                if abs(x - cx) > w / 2 - 1.8 or abs(z - cz) > h / 2 - 1.8 or blocked(arena, x, z, placed):
                    continue
                placed.append((x, z))
                d = {"piece": piece, "position": [round(x, 2), round(z, 2)], "rotation": rng.randrange(0, 360, 5), "boss_gold": True}
                if floor_y:
                    d["y"] = floor_y
                arena["decor"].append(d)
                break
        total += len(placed)
        print(aid, e["id"], len(placed), "joias")
open(ARENAS, "w", encoding="utf-8").write(json.dumps(arenas, indent=2, ensure_ascii=False) + "\n")
print("OK joias dos chefes:", total)
