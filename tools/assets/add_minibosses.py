"""Dois mini-chefes por mapa de combate (docs/03-2-areas.md) e os drops das relíquias de missão do Padre da Capital.
Idempotente: roda de novo sem duplicar. Também é chamado no fim de tools/assets/build_maps.py (que regenera os mapas).
  Esgoto   Gator Velho (s3) + Rei dos Sapos (s2)        Floresta  Leshy + Rainha das Víboras
  Ruínas   Guardião do Cofre + Alfa da Matilha (larga a Carne Selvagem)         Cemitério Ogro da Cripta (id crypt_scorpion) + Senhor da Cripta (larga o Coração Humano)
  Forte    Comandante (larga o Crânio Antigo) + Rainha das Súcubos     Mina  Chefe Troll + Guardião do Túmulo
uso: python3 tools/assets/add_minibosses.py   (a partir da raiz do projeto)"""
import json
ARENAS, MONSTERS = "data/arenas.json", "data/monsters.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
monsters = json.load(open(MONSTERS, encoding="utf-8"))


def clone(name, base, **changes):
    m = json.loads(json.dumps(monsters[base]))
    m.pop("_comment", None)
    m.update(changes)
    monsters[name] = m


clone("frog_king", "old_gator", _comment="Mini-chefe do Esgoto (canais): o Rei dos Sapos, um sapo do tamanho de um boi; investidas (os ratos não são mais monstros: só cenário).",
      name_key="MONSTER_FROG_KING", max_health=130, damage=14, size=4.5, element="earth", look="frog", color=[0.32, 0.25, 0.2])
clone("viper_queen", "old_gator", _comment="Mini-chefe da Floresta: a Rainha das Víboras, líder do bando de répteis.",
      name_key="MONSTER_VIPER_QUEEN", max_health=240, damage=17, size=2.2, element="earth", look="reptile", color=[0.7, 1.0, 0.6])
clone("ruin_alpha", "old_gator", _comment="Mini-chefe das Ruínas: o Alfa da Matilha (docs/03-2-areas.md); investidas rápidas.",
      name_key="MONSTER_RUIN_ALPHA", max_health=300, damage=22, size=2.0, element="air", look="stalker", color=[1.0, 1.0, 1.0])
clone("succubus_queen", "succubus", _comment="Mini-chefe do Forte: a Rainha das Súcubos; magia à distância como as súcubas, bem mais forte.",
      name_key="MONSTER_SUCCUBUS_QUEEN", category="miniboss", max_health=480, damage=24, size=1.5, element="fire")
clone("troll_chief", "troll", _comment="Mini-chefe da Mina: o Chefe Troll.",
      name_key="MONSTER_TROLL_CHIEF", category="miniboss", max_health=420, damage=28, size=1.5, element="earth")
# O mini-chefe da praça do Cemitério (id crypt_scorpion) agora é o Ogro da Cripta (build_maps.py ainda o define como escorpião).
monsters["crypt_scorpion"].update({"look": "ogre", "size": 1.6, "color": [1.0, 1.0, 1.0],
                                   "_comment": "Mini-chefe do Cemitério (praça): o Ogro da Cripta (Ogre lowpoly, nubux / rudy85, CC BY 3.0); investidas. O id continua crypt_scorpion (saves e encontros)."})
monsters["crypt_lord"]["quest_drop"] = "human_heart"
monsters["fort_commander"]["quest_drop"] = "old_skull"
monsters["ruin_alpha"]["quest_drop"] = "wild_meat"


def add_encounter(area, enc):
    arenas[area]["encounters"] = [e for e in arenas[area]["encounters"] if e["id"] != enc["id"]] + [enc]


def set_monsters(area, enc_id, mons):
    for e in arenas[area]["encounters"]:
        if e["id"] == enc_id:
            e["monsters"] = mons


add_encounter("sewers_02_canals", {"id": "s2_frog_king", "position": [0, -58], "monsters": [{"monster": "frog_king", "count": 1}]})
add_encounter("forest_01_path", {"id": "f_viper_queen", "position": [-3, -78], "monsters": [{"monster": "viper_queen", "count": 1}]})
add_encounter("ruins_01_city", {"id": "r_alpha", "position": [20, -40], "monsters": [{"monster": "ruin_alpha", "count": 1}]})
set_monsters("fort_01_gate", "fo_succubi_court", [{"monster": "succubus_queen", "count": 1}, {"monster": "succubus", "count": 1}])
set_monsters("mine_01_crystal_vein", "m_troll", [{"monster": "troll_chief", "count": 1}])
set_monsters("mine_01_crystal_vein", "m_golem_stone", [{"monster": "tomb_guardian", "count": 1}])
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False); open(ARENAS, "a").write("\n")
json.dump(monsters, open(MONSTERS, "w", encoding="utf-8"), indent=2, ensure_ascii=False); open(MONSTERS, "a").write("\n")
print("OK minibosses")
