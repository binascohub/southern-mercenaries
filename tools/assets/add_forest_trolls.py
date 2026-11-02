"""Mapa dos trolls da Floresta: a sala "hub" (a leste do corredor onde ficava o guaxinim) vira a Clareira dos Trolls, com 3 bandos de 2 Trolls da Floresta.
O Troll da Floresta (forest_troll) é o Troll Magro com o modelo troll.glb do autor (assets/models/monsters/forest_troll.glb, por build_forest_troll.py), maior e parado
na pose do arquivo (sem animação, como o Rei Golem). Roda depois de build_maps.py gravar os dados (é chamado no fim dele). Idempotente.
uso: python3 tools/assets/add_forest_trolls.py   (a partir da raiz do projeto)"""
import json
MON, ARENAS = "data/monsters.json", "data/arenas.json"
mons = json.load(open(MON, encoding="utf-8"))
troll = dict(mons["troll"])
troll.update({"name_key": "MONSTER_FOREST_TROLL", "look": "forest_troll", "size": 1.2, "max_health": 380, "patrol_radius": 5.0,
              "_comment": "Troll da Floresta (troll.glb do autor, ombros floridos e saia de cascas): o Troll Magro maior e mais resistente, no mapa dos trolls."})
mons["forest_troll"] = troll
json.dump(mons, open(MON, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(MON, "a").write("\n")
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
forest["encounters"] = [e for e in forest["encounters"] if not e["id"].startswith("f_trolls")]
for i, pos in enumerate([[44.0, -38.0], [54.0, -14.0], [55.0, -31.0]]):
    forest["encounters"].append({"id": "f_trolls_%s" % "abc"[i], "position": pos, "monsters": [{"monster": "forest_troll", "count": 2}]})
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK trolls: 3 bandos na sala hub")
