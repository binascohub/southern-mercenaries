"""Verme Dourado no Deserto (desert_01_canyon): o "Gold Sandworm" (Fubbi, CC BY 4.0; tools/assets/build_sandworm.py), verme de ~2,5 m que não sai do buraco
na areia e cospe de longe (ai "ranged", velocidade 0: vira para quem chega e cospe areia ácida em arco, que deixa poça). Um por ponto, em 6 pontos livres das
Dunas (2), da Areia Movediça, do Ninho, dos Destroços e da Estrada (longe dos objetos sólidos, dos outros bandos e dos NPCs). Idempotente. Roda no fim de build_maps.py.
uso: python3 tools/assets/add_desert_sandworm.py   (a partir da raiz do projeto)"""
import json, math

ARENAS, MONSTERS = "data/arenas.json", "data/monsters.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
mons = json.load(open(MONSTERS, encoding="utf-8"))
desert = arenas["desert_01_canyon"]

mons["de_sandworm"] = {
    "name_key": "MONSTER_GOLD_SANDWORM", "max_health": 210, "move_speed": 0.0, "damage": 16, "attack_range": 11.0, "attack_windup": 1.0,
    "attack_cooldown": 2.4, "aggro_range": 40.0, "size": 1.0, "category": "common", "element": "earth", "ai": "ranged", "keep_distance": 0.0,
    "spit": {"radius": 1.8, "puddle_time": 4.0, "puddle_dps": 5.0, "glob": [0.95, 0.72, 0.25]}, "look": "gold_sandworm", "color": [1.0, 1.0, 1.0],
    "sound": "slime", "role": "normal",
    "_comment": "Verme Dourado (\"Gold Sandworm\", Fubbi, CC BY 4.0): verme de ~2,5 m que fica no buraco dele na areia (não anda), vira para quem chega e "
                "cospe areia ácida em arco; a bola cai na marca do chão e deixa uma poça. Sozinho em cada ponto, no meio dos bandos do deserto. Terra."}

desert["encounters"] = [e for e in desert["encounters"] if not e["id"].startswith("de_sandworm_")]
rects = []
for d in desert["decor"]:
    box = d.get("collider") or d.get("solid")
    if box:
        x, z = d["position"]
        rects.append((x - box[0] / 2, z - box[1] / 2, x + box[0] / 2, z + box[1] / 2))
others = [tuple(e["position"]) for e in desert["encounters"]] + [tuple(p["position"]) for p in desert.get("props", [])]
others += [tuple(n["position"]) for n in desert.get("npcs", []) if "position" in n]
rooms = {r["id"]: r for r in desert["rooms"]}


def clear(x, z):
    for x0, z0, x1, z1 in rects:
        if math.hypot(max(x0 - x, 0, x - x1), max(z0 - z, 0, z - z1)) < 2.5:
            return False
    return all(math.hypot(x - ox, z - oz) >= 8.0 for ox, oz in others)


def spot(room_id, prefer):
    room = rooms[room_id]
    cx, cz = room["center"]
    hw, hh = room["size"][0] / 2 - 3.0, room["size"][1] / 2 - 3.0
    want = (cx + prefer[0] * hw, cz + prefer[1] * hh)
    best = None
    for i in range(-30, 31):
        for j in range(-30, 31):
            x, z = cx + hw * i / 30, cz + hh * j / 30
            if clear(x, z):
                d = math.hypot(x - want[0], z - want[1])
                if best is None or d < best[0]:
                    best = (d, round(x, 1), round(z, 1))
    assert best, "sem lugar em " + room_id
    return [best[1], best[2]]


PLAN = [("dunes", (-0.5, 0.3)), ("dunes", (0.5, -0.4)), ("quicksand", (0.0, 0.0)), ("nest", (0.3, -0.3)), ("wrecks", (-0.3, 0.4)), ("road", (0.4, -0.5))]
for i, (room_id, prefer) in enumerate(PLAN):
    pos = spot(room_id, prefer)
    others.append(tuple(pos))
    desert["encounters"].append({"id": "de_sandworm_%s" % "abcdef"[i], "position": pos,
                                "monsters": [{"monster": "de_sandworm", "count": 1}], "level": 15})
    print("de_sandworm_%s" % "abcdef"[i], room_id, pos)

for path, data in ((MONSTERS, mons), (ARENAS, arenas)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
NAMES = ("Verme Dourado", "Gold Sandworm", "Gusano Dorado")
for idx, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po")):
    text = open(path, encoding="utf-8").read()
    if 'msgid "MONSTER_GOLD_SANDWORM"' not in text:
        open(path, "a", encoding="utf-8").write('\nmsgid "MONSTER_GOLD_SANDWORM"\nmsgstr "%s"\n' % NAMES[idx])
print("OK deserto: Verme Dourado em", len(PLAN), "pontos")
