"""Floresta (forest_01_path): o Tio Fungo dá lugar à Boca-de-Flor, criatura magra de ~2,6 m com a cabeça que abre em pétalas ("Demogorgon Rig",
NO DONT EAT ME CASEOH (Ferris wheel), CC BY 4.0; tools/assets/build_demogorgon.py). Só na Floresta: o Tio Fungo (fungus_uncle) continua no Esgoto e na
Floresta Sombria. A Boca-de-Flor (forest_flowermaw) copia os números do Tio Fungo (vida, dano, alcance, papel, Terra) e troca o visual, o tamanho, a voz
e o nome; os bandos da Floresta com fungus_uncle passam a usá-la. Idempotente. Roda no fim de build_maps.py.
uso: python3 tools/assets/forest_demogorgon.py   (a partir da raiz do projeto)"""
import json

ARENAS, MONSTERS = "data/arenas.json", "data/monsters.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
mons = json.load(open(MONSTERS, encoding="utf-8"))
forest = arenas["forest_01_path"]

maw = dict(mons["fungus_uncle"])
maw.update({"name_key": "MONSTER_FLOWERMAW", "look": "demogorgon", "size": 1.0, "sound": "beast", "attack_range": 2.6,
            "_comment": "Boca-de-Flor (\"Demogorgon Rig\", NO DONT EAT ME CASEOH (Ferris wheel), CC BY 4.0): criatura magra de ~2,6 m com a cabeça que abre "
                        "em pétalas; no lugar do Tio Fungo na Floresta, com os mesmos números (corpo a corpo, Terra)."})
mons["forest_flowermaw"] = maw
swapped = 0
for e in forest["encounters"]:
    for m in e["monsters"]:
        if m["monster"] == "fungus_uncle":
            m["monster"] = "forest_flowermaw"
            swapped += m["count"]
for path, data in ((MONSTERS, mons), (ARENAS, arenas)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
NAMES = ("Boca-de-Flor", "Flowermaw", "Boca de Flor")
for idx, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po")):
    text = open(path, encoding="utf-8").read()
    if 'msgid "MONSTER_FLOWERMAW"' not in text:
        open(path, "a", encoding="utf-8").write('\nmsgid "MONSTER_FLOWERMAW"\nmsgstr "%s"\n' % NAMES[idx])
print("OK floresta: Boca-de-Flor no lugar do Tio Fungo,", swapped, "monstros trocados")
