"""Templo no meio da sala do Rei Golem da Floresta (a sala "reptiles" depois da troca de move_forest_village.py): o templo em ruínas (Ruin_Temple1, do pacote de
ruínas das Ruínas) no centro da sala, como um adereço que se clica (NPC "forest_temple" com a peça do kit no lugar do corpo, como a estátua do Cemitério).
Ao clicar, depois de uns segundos, o Rei Golem de Pedra (viper_queen, mini-chefe) acorda com o Guardião do Túmulo, e o Rei invoca ondas de golens dos elementos
(Fogo, Gelo, Pedra: dados "waves" do viper_queen em data/monsters.json, tratados por Enemy._update_waves). O encontro f_viper_queen deixa de existir no mapa (só o
templo o invoca; o grupo da invocação mantém o mesmo id). Luz fria sobre o templo, chão de dentro limpo de plantas e pedras (a trilha fica), miolo de 6 x 6 m que bloqueia.
Roda depois de add_forest_king_room.py e antes de add_forest_trees.py (os carvalhos ficam longe dele) e depois de build_maps.py gravar monsters.json. Idempotente.
uso: python3 tools/assets/add_forest_temple.py   (a partir da raiz do projeto)"""
import json, math
ARENAS, MON = "data/arenas.json", "data/monsters.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
room = next(r for r in forest["rooms"] if r["id"] == "reptiles")
cx, cz = room["center"]
R = 6.8     # raio do templo (a base tem 11 m)
forest["decor"] = [d for d in forest["decor"]
                   if d.get("piece") != "Ruin_Temple1" and not d.get("temple_light") and not d.get("temple_block")
                   and (str(d.get("piece", "")).startswith("Trail_") or "position" not in d
                        or math.hypot(d["position"][0] - cx, d["position"][1] - cz) > R)]
forest["decor"].append({"collider": [6.0, 6.0], "position": [cx, cz], "temple_block": True})
forest["decor"].append({"light": [0.6, 0.75, 1.0], "position": [cx, cz], "y": 3.0, "range": 12.0, "energy": 1.1, "temple_light": True})
forest["encounters"] = [e for e in forest["encounters"] if e["id"] != "f_viper_queen"]
forest["props"] = [p for p in forest["props"] if p["id"] != "forest_temple"]
forest["props"].append({"id": "forest_temple", "kind": "npc", "npc": "forest_temple", "kit": "Ruin_Temple1", "rotation": 0, "position": [cx, cz],
                        "summon": {"id": "f_viper_queen", "position": [cx, cz + 9.0], "spread": 3.0, "toast": "TOAST_TEMPLE_AWAKENS",
                                   "monsters": [{"monster": "viper_queen", "count": 1}, {"monster": "forest_tomb_guardian", "count": 1}]}})
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
mons = json.load(open(MON, encoding="utf-8"))
mons["viper_queen"]["waves"] = {
    "first": 8.0, "interval": 24.0, "radius": 6.0, "toast": "TOAST_VIPER_WAVE",
    "list": [[{"monster": "golem_fire", "count": 2}], [{"monster": "golem_ice", "count": 2}], [{"monster": "golem_stone", "count": 2}],
             [{"monster": "golem_fire", "count": 1}, {"monster": "golem_ice", "count": 1}, {"monster": "golem_stone", "count": 1}]]}
json.dump(mons, open(MON, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(MON, "a").write("\n")
print("OK templo em", [cx, cz], "(invoca o Rei Golem; 4 ondas de golens)")
