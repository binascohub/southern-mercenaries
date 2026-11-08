"""Troll Blindado nas Ruínas (ruins_01_city): o "Troll (Armored)" de SidewalkNZ (Sketchfab, CC BY 4.0), montado por tools/assets/build_troll_armored.py e preso ao
esqueleto dos heróis por tools/assets/rig_biped.py (perfil troll_armored; assets/models/monsters/troll_armored_animated.glb).
Monstro de Fogo (como todos das Ruínas), lento, resistente e de pancada pesada, com 3 m. Entra em 6 bandos: um em cada Bairro e em cada Praça e dois no Pátio Alto,
em pontos livres (longe das paredes do labirinto, dos objetos sólidos, dos outros bandos, dos NPCs e da entrada).
Idempotente. Roda no fim de build_maps.py (depois de ruins_fire_monsters.py).
uso: python3 tools/assets/add_ruins_armored_troll.py   (a partir da raiz do projeto)"""
import json, math

ARENAS, MONSTERS = "data/arenas.json", "data/monsters.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
mons = json.load(open(MONSTERS, encoding="utf-8"))
ruins = arenas["ruins_01_city"]

mons["ru_armored_troll"] = {
    "name_key": "MONSTER_ARMORED_TROLL", "max_health": 336, "move_speed": 2.3, "damage": 16, "attack_range": 3.0, "attack_windup": 1.0,
    "attack_cooldown": 2.0, "aggro_range": 40.0, "size": 3.0, "category": "common", "element": "fire", "patrol": False, "look": "troll_armored",
    "color": [1.0, 1.0, 1.0], "sound": "ogre", "role": "tank",
    "_comment": "Troll Blindado (\"Troll (Armored)\", SidewalkNZ, CC BY 4.0; tools/assets/build_troll_armored.py + rig_biped.py): bruto de 3 m com armadura de placas, "
                "com os movimentos dos heróis. Monstro das Ruínas: lento, resistente e de pancada pesada. Fogo (fraco a Água)."}

ruins["encounters"] = [e for e in ruins["encounters"] if not e["id"].startswith("r_armored_troll")]
rooms = {r["id"]: r for r in ruins["rooms"]}
rects = []
for d in ruins["decor"]:
    x, z = d["position"]
    if "collider" in d:
        w, h = d["collider"]
    elif "solid" in d:
        w, h = d["solid"]
    else:
        continue
    rects.append((x - w / 2, z - h / 2, x + w / 2, z + h / 2))
others = [tuple(e["position"]) for e in ruins["encounters"]] + [tuple(p["position"]) for p in ruins["props"]]
start = ruins["entries"]["start"]


def clear(x, z):
    for x0, z0, x1, z1 in rects:
        if math.hypot(max(x0 - x, 0, x - x1), max(z0 - z, 0, z - z1)) < 3.0:
            return False
    return all(math.hypot(x - ox, z - oz) >= 9.0 for ox, oz in others) and math.hypot(x - start[0], z - start[1]) >= 25.0


def spot(room_id, prefer):
    """Ponto livre na sala, o mais perto possível de `prefer` (x, z relativos ao centro, em fração da metade do tamanho)."""
    r = rooms[room_id]
    cx, cz = r["center"]
    hw, hh = r["size"][0] / 2 - 3.0, r["size"][1] / 2 - 3.0
    want = (cx + prefer[0] * hw, cz + prefer[1] * hh)
    best = None
    for i in range(-30, 31):
        for j in range(-30, 31):
            x, z = cx + hw * i / 30, cz + hh * j / 30
            if clear(x, z):
                d = math.hypot(x - want[0], z - want[1])
                if best is None or d < best[0]:
                    best = (d, round(x, 1), round(z, 1))
    assert best, room_id
    return [best[1], best[2]]


PLAN = [("bairro_w", (-0.4, 0.3), 1), ("bairro_e", (0.4, 0.3), 1), ("plaza_w", (-0.5, -0.5), 1), ("plaza_e", (0.5, -0.5), 1),
        ("yard", (-0.6, 0.0), 1), ("yard", (0.6, 0.0), 1)]
for i, (room_id, prefer, count) in enumerate(PLAN):
    pos = spot(room_id, prefer)
    others.append(tuple(pos))
    ruins["encounters"].append({"id": "r_armored_troll_%s" % "abcdef"[i], "position": pos,
                                "monsters": [{"monster": "ru_armored_troll", "count": count}], "level": 7})
    print(room_id, pos)

for path, data in ((MONSTERS, mons), (ARENAS, arenas)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
NAMES = ("Troll Blindado", "Armored Troll", "Trol Acorazado")
for idx, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po")):
    text = open(path, encoding="utf-8").read()
    if 'msgid "MONSTER_ARMORED_TROLL"' not in text:
        open(path, "a", encoding="utf-8").write('\nmsgid "MONSTER_ARMORED_TROLL"\nmsgstr "%s"\n' % NAMES[idx])
print("OK ruins: Troll Blindado em", len(PLAN), "bandos")
