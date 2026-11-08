"""Floresta (forest_01_path): os Sapos Ácidos dão lugar à Planta Carnívora ("Cartoon flesh-eating plant with animations", Jungle Jim, CC BY 4.0;
tools/assets/build_flesh_plant.py). Só na Floresta: o Sapo Ácido (acid_toad) continua no Esgoto e nos outros mapas. A Planta Carnívora
(forest_flesh_plant) copia os números do Sapo Ácido e o cuspe de veneno (marca no chão, poça tóxica), mas fica plantada (não anda nem foge) e
troca o visual, o tamanho, a voz e o nome. Os bandos da Floresta e as ondas do Leshy com acid_toad passam a usá-la. Idempotente.
Roda no fim de build_maps.py.  uso: python3 tools/assets/forest_flesh_plant.py   (a partir da raiz do projeto)"""
import json

ARENAS, MONSTERS = "data/arenas.json", "data/monsters.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
mons = json.load(open(MONSTERS, encoding="utf-8"))
forest = arenas["forest_01_path"]

plant = json.loads(json.dumps(mons["acid_toad"]))
plant.update({"name_key": "MONSTER_FLESH_PLANT", "look": "flesh_plant", "size": 1.3, "sound": "slime", "color": [1.0, 1.0, 1.0],
              "move_speed": 0.0, "keep_distance": 0.0, "attack_range": 9.0,
              "_comment": "Planta Carnívora (\"Cartoon flesh-eating plant\", Jungle Jim, CC BY 4.0): no lugar do Sapo Ácido na Floresta, com os mesmos números. "
                          "Fica plantada e cospe veneno onde o herói está (marca no chão antes) e deixa uma poça tóxica."})
plant["spit"] = dict(plant.get("spit", {}), glob=[0.45, 0.95, 0.2])
mons["forest_flesh_plant"] = plant
swapped = 0
for e in forest["encounters"]:
    for m in e["monsters"]:
        if m["monster"] == "acid_toad":
            m["monster"] = "forest_flesh_plant"
            swapped += m["count"]
for wave in mons.get("leshy", {}).get("waves", {}).get("list", []):
    for m in wave:
        if m["monster"] == "acid_toad":
            m["monster"] = "forest_flesh_plant"
for path, data in ((MONSTERS, mons), (ARENAS, arenas)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
NAMES = ("Planta Carnívora", "Flesh-Eating Plant", "Planta Carnívora")
for idx, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po", "locale/messages.pot")):
    text = open(path, encoding="utf-8").read()
    if 'msgid "MONSTER_FLESH_PLANT"' not in text:
        open(path, "a", encoding="utf-8").write('\nmsgid "MONSTER_FLESH_PLANT"\nmsgstr "%s"\n' % ("" if path.endswith(".pot") else NAMES[idx]))
print("OK floresta: Planta Carnívora no lugar do Sapo Ácido,", swapped, "monstros trocados")
