"""Polvo Abissal nas Docas (docks_01_pier), no lugar do Espantalho Afogado (docks_scarecrow, de add_pixellabs_content.py): o "Alien Octopus"
(agasherev, CC BY 4.0; tools/assets/build_alien_octopus.py), bípede de ~2 m com cabeça de polvo e armadura. Mesmos números do espantalho (monstro
comum, Água) e os mesmos lugares: o par que ele fazia em 7 bandos das Docas. Idempotente. Roda no fim de build_maps.py.
uso: python3 tools/assets/docks_alien_octopus.py   (a partir da raiz do projeto)"""
import json

ARENAS, MONSTERS = "data/arenas.json", "data/monsters.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
mons = json.load(open(MONSTERS, encoding="utf-8"))
docks = arenas["docks_01_pier"]

base = mons.get("docks_scarecrow") or mons["docks_alien_octopus"]
mons["docks_alien_octopus"] = dict({k: v for k, v in base.items() if k != "_comment"}, **{
    "_comment": "Polvo Abissal das Docas (\"Alien Octopus\", agasherev, CC BY 4.0; tools/assets/build_alien_octopus.py): bípede de ~2 m com cabeça de polvo "
                "e armadura que sobe do porto; agarra com os braços compridos. No lugar do Espantalho Afogado, com os mesmos números. Água.",
    "name_key": "MONSTER_DOCKS_ALIEN_OCTOPUS", "look": "alien_octopus", "size": 2.0, "color": [1.0, 1.0, 1.0], "sound": "slime"})
mons.pop("docks_scarecrow", None)
swapped = 0
for e in docks["encounters"]:
    for m in e["monsters"]:
        if m["monster"] == "docks_scarecrow":
            m["monster"] = "docks_alien_octopus"
            swapped += 1
for path, data in ((MONSTERS, mons), (ARENAS, arenas)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
NAMES = ("Polvo Abissal", "Abyssal Octopus", "Pulpo Abisal")
for idx, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po", "locale/messages.pot")):
    text = open(path, encoding="utf-8").read()
    if 'msgid "MONSTER_DOCKS_ALIEN_OCTOPUS"' not in text:
        open(path, "a", encoding="utf-8").write('\nmsgid "MONSTER_DOCKS_ALIEN_OCTOPUS"\nmsgstr "%s"\n' % (NAMES[idx] if idx < 3 else ""))
print("OK docas: Polvo Abissal no lugar do Espantalho Afogado em", swapped, "bandos")
