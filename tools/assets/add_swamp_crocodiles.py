"""Crocodilos no Pântano das Cobras (sala bog_w da Floresta Sombria, dark_forest_01_woods):
 - Crocodilo do Pântano ("Jungle Water Crocodile", vanshtandon321, CC BY 4.0; tools/assets/build_swamp_crocodile.py): rente ao chão, nada até a presa;
 - Crocodilo Espinhoso ("fantasy crocodile animation", hino, CC BY 4.0; tools/assets/build_fantasy_crocodile.py): de patas esticadas, mais forte.
Os dois são de Água (fracos a Raio), do papel "normal" como os do mapa. Entram em 3 bandos em pontos livres do pântano
(longe dos objetos sólidos, dos outros bandos e dos NPCs). Idempotente. Roda no fim de build_maps.py.
uso: python3 tools/assets/add_swamp_crocodiles.py   (a partir da raiz do projeto)"""
import json, math

ARENAS, MONSTERS = "data/arenas.json", "data/monsters.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
mons = json.load(open(MONSTERS, encoding="utf-8"))
woods = arenas["dark_forest_01_woods"]

mons["fd_swamp_croc"] = {
    "name_key": "MONSTER_SWAMP_CROC", "max_health": 210, "move_speed": 2.6, "damage": 16, "attack_range": 2.4, "attack_windup": 0.6,
    "attack_cooldown": 1.8, "aggro_range": 40.0, "size": 1.0, "category": "common", "element": "water", "patrol": True, "patrol_radius": 5.0,
    "patrol_speed": 0.6, "look": "swamp_crocodile", "color": [1.0, 1.0, 1.0], "sound": "beast", "role": "normal",
    "_comment": "Crocodilo do Pântano (\"Jungle Water Crocodile\", vanshtandon321, CC BY 4.0): 2,4 m, rente ao chão; ronda devagar no Pântano das Cobras "
                "e dá o bote em quem chega perto. Água (fraco a Raio)."}
mons["fd_spiked_croc"] = {
    "name_key": "MONSTER_SPIKED_CROC", "max_health": 210, "move_speed": 3.0, "damage": 16, "attack_range": 2.6, "attack_windup": 0.7,
    "attack_cooldown": 2.0, "aggro_range": 40.0, "size": 1.0, "category": "common", "element": "water", "patrol": True, "patrol_radius": 6.0,
    "patrol_speed": 0.8, "look": "fantasy_crocodile", "color": [1.0, 1.0, 1.0], "sound": "beast", "role": "normal",
    "_comment": "Crocodilo Espinhoso (\"fantasy crocodile animation\", hino, CC BY 4.0): 2,6 m, de espinhos nas costas e patas esticadas; anda mais rápido "
                "que o do pântano. Água (fraco a Raio)."}

woods["encounters"] = [e for e in woods["encounters"] if not e["id"].startswith("fd_bog_croc")]
room = next(r for r in woods["rooms"] if r["id"] == "bog_w")
rects = []
for d in woods["decor"]:
    box = d.get("collider") or d.get("solid")
    if box:
        x, z = d["position"]
        rects.append((x - box[0] / 2, z - box[1] / 2, x + box[0] / 2, z + box[1] / 2))
others = [tuple(e["position"]) for e in woods["encounters"]] + [tuple(p["position"]) for p in woods.get("props", [])]
others += [tuple(n["position"]) for n in woods.get("npcs", []) if "position" in n]


def clear(x, z):
    for x0, z0, x1, z1 in rects:
        if math.hypot(max(x0 - x, 0, x - x1), max(z0 - z, 0, z - z1)) < 2.5:
            return False
    return all(math.hypot(x - ox, z - oz) >= 8.0 for ox, oz in others)


def spot(prefer):
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
    assert best, "sem lugar no pântano"
    return [best[1], best[2]]


PLAN = [((-0.3, 0.6), [("fd_swamp_croc", 2)]), ((0.5, 0.1), [("fd_spiked_croc", 2)]), ((-0.6, -0.6), [("fd_swamp_croc", 1), ("fd_spiked_croc", 1)])]
for i, (prefer, group) in enumerate(PLAN):
    pos = spot(prefer)
    others.append(tuple(pos))
    woods["encounters"].append({"id": "fd_bog_croc_%s" % "abc"[i], "position": pos,
                                "monsters": [{"monster": m, "count": n} for m, n in group], "level": 20})
    print("fd_bog_croc_%s" % "abc"[i], pos, group)

for path, data in ((MONSTERS, mons), (ARENAS, arenas)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
NAMES = {"MONSTER_SWAMP_CROC": ("Crocodilo do Pântano", "Swamp Crocodile", "Cocodrilo del Pantano"),
         "MONSTER_SPIKED_CROC": ("Crocodilo Espinhoso", "Spiked Crocodile", "Cocodrilo Espinoso")}
for idx, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po")):
    text = open(path, encoding="utf-8").read()
    for key, names in NAMES.items():
        if 'msgid "%s"' % key not in text:
            text += '\nmsgid "%s"\nmsgstr "%s"\n' % (key, names[idx])
    open(path, "w", encoding="utf-8").write(text)
print("OK floresta sombria: crocodilos em", len(PLAN), "bandos no Pântano das Cobras")
