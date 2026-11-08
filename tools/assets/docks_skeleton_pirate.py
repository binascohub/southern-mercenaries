"""Docas (docks_01_pier): o Polvo de Tinta dá lugar ao Esqueleto Pirata ("Skeleton Pirate \"The Captin\"", FireGoat, CC BY 4.0;
tools/assets/build_skeleton_pirate.py), esqueleto de casaca e chapéu com sabre e perna de pau, com os movimentos dos heróis (guarda de sabre, corte e volta).
O pirata (docks_skeleton_pirate) é de corpo a corpo: mesma vida, dano e papel do polvo (normal, Água), sem o jato de tinta. Troca o polvo em todos os
bandos das Docas e nas ondas dos chefes (o polvo só existia lá). Idempotente. Roda no fim de build_maps.py.
uso: python3 tools/assets/docks_skeleton_pirate.py   (a partir da raiz do projeto)"""
import json

ARENAS, MONSTERS = "data/arenas.json", "data/monsters.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
mons = json.load(open(MONSTERS, encoding="utf-8"))
docks = arenas["docks_01_pier"]

octo = mons["sea_octopus"]
mons["docks_skeleton_pirate"] = {
    "name_key": "MONSTER_SKELETON_PIRATE", "max_health": octo["max_health"], "move_speed": 3.0, "damage": octo["damage"], "attack_range": 2.4,
    "attack_windup": 0.6, "attack_cooldown": 1.6, "aggro_range": octo["aggro_range"], "size": 1.0, "category": "common", "element": "water",
    "ai": "melee", "patrol": True, "patrol_radius": 5.0, "patrol_speed": 0.6, "look": "skeleton_pirate", "color": [1.0, 1.0, 1.0], "sound": "shade",
    "role": octo.get("role", "normal"),
    "_comment": "Esqueleto Pirata (\"Skeleton Pirate \\\"The Captin\\\"\", FireGoat, CC BY 4.0): esqueleto de casaca e chapéu, sabre e perna de pau; "
                "no lugar do Polvo de Tinta nas Docas, com a mesma vida e dano, mas de corpo a corpo (corte de sabre). Água."}

swapped = 0


def swap(node):
    global swapped
    if isinstance(node, dict):
        if node.get("monster") == "sea_octopus":
            node["monster"] = "docks_skeleton_pirate"
            swapped += int(node.get("count", 1))
        for v in node.values():
            swap(v)
    elif isinstance(node, list):
        for v in node:
            swap(v)


swap(docks["encounters"])
swap(docks.get("props", []))
for mid, m in mons.items():  # ondas dos chefes das Docas (Besta do Casco, Capitão Afogado)
    if isinstance(m, dict) and mid != "docks_skeleton_pirate" and "waves" in m:
        swap(m["waves"])
for path, data in ((MONSTERS, mons), (ARENAS, arenas)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
NAMES = ("Esqueleto Pirata", "Skeleton Pirate", "Esqueleto Pirata")
for idx, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po")):
    text = open(path, encoding="utf-8").read()
    if 'msgid "MONSTER_SKELETON_PIRATE"' not in text:
        open(path, "a", encoding="utf-8").write('\nmsgid "MONSTER_SKELETON_PIRATE"\nmsgstr "%s"\n' % NAMES[idx])
print("OK docas: Esqueleto Pirata no lugar do Polvo de Tinta,", swapped, "trocados")
