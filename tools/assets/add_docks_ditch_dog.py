"""Cão da Vala nas Docas (docks_01_pier): o "Ditch Dog - Rigged and Animated" (Greeble3d, CC BY 4.0; tools/assets/build_ditch_dog.py), bicho de carne anfíbio
que ronda os estaleiros e a peixaria. Água (como todos das Docas), papel "normal". Entra em 4 bandos de 2: Estaleiro, Peixaria, Farol e Armazém, em pontos
livres (longe dos objetos sólidos, dos outros bandos e dos NPCs). Idempotente. Roda no fim de build_maps.py.
uso: python3 tools/assets/add_docks_ditch_dog.py   (a partir da raiz do projeto)"""
import json, math

ARENAS, MONSTERS = "data/arenas.json", "data/monsters.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
mons = json.load(open(MONSTERS, encoding="utf-8"))
docks = arenas["docks_01_pier"]

mons["docks_ditch_dog"] = {
    "name_key": "MONSTER_DITCH_DOG", "max_health": 210, "move_speed": 3.0, "damage": 16, "attack_range": 2.4, "attack_windup": 0.7,
    "attack_cooldown": 1.8, "aggro_range": 40.0, "size": 1.0, "category": "common", "element": "water", "patrol": True, "patrol_radius": 6.0,
    "patrol_speed": 0.7, "look": "ditch_dog", "color": [1.0, 1.0, 1.0], "sound": "beast", "role": "normal",
    "_comment": "Cão da Vala (\"Ditch Dog\", Greeble3d, CC BY 4.0): bicho de carne anfíbio de ~2,3 m que sai das valas do porto; rosna e avança. Água (fraco a Raio)."}

docks["encounters"] = [e for e in docks["encounters"] if not e["id"].startswith("dk_ditch_dog")]
rects = []
for d in docks["decor"]:
    box = d.get("collider") or d.get("solid")
    if box:
        x, z = d["position"]
        rects.append((x - box[0] / 2, z - box[1] / 2, x + box[0] / 2, z + box[1] / 2))
others = [tuple(e["position"]) for e in docks["encounters"]] + [tuple(p["position"]) for p in docks.get("props", [])]
others += [tuple(n["position"]) for n in docks.get("npcs", []) if "position" in n]
rooms = {r["id"]: r for r in docks["rooms"]}


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


PLAN = [("shipyard", (0.3, 0.3)), ("fishery", (-0.3, 0.3)), ("lighthouse", (0.4, -0.2)), ("warehouse", (-0.4, -0.2))]
for i, (room_id, prefer) in enumerate(PLAN):
    pos = spot(room_id, prefer)
    others.append(tuple(pos))
    docks["encounters"].append({"id": "dk_ditch_dog_%s" % "abcd"[i], "position": pos,
                                "monsters": [{"monster": "docks_ditch_dog", "count": 2}], "level": 5})
    print("dk_ditch_dog_%s" % "abcd"[i], room_id, pos)

for path, data in ((MONSTERS, mons), (ARENAS, arenas)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
NAMES = ("Cão da Vala", "Ditch Dog", "Perro de la Zanja")
for idx, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po")):
    text = open(path, encoding="utf-8").read()
    if 'msgid "MONSTER_DITCH_DOG"' not in text:
        open(path, "a", encoding="utf-8").write('\nmsgid "MONSTER_DITCH_DOG"\nmsgstr "%s"\n' % NAMES[idx])
print("OK docas: Cão da Vala em", len(PLAN), "bandos")
