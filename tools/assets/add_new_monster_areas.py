"""Áreas novas com monstros novos (modelos do Sketchfab, CC BY 4.0, reduzidos por tools/assets/build_decor_prop.py; famílias `static` em game/actors/monster_model.gd):
  Floresta Negra: o Pântano do Musgo, sala nova a leste do Bosque Leste (grove_e ganha a porta leste), com o Moosgreif (elite de terra, corpo a corpo), o Wendigo
  (elite de água, rápido), a Feiticeira do Cajado de Cristal (ataca de longe com cristal que deixa poça) e o Cervo Sombrio (investida).
  Cemitério: o Charco dos Afogados, sala nova a leste da sala r2 (que ganha a porta leste), com a Bruxa Afogada (ataca de longe com água podre) e a Enfermeira
  Enfaixada (elite, corpo a corpo).
A base de cada monstro é copiada de um parecido do mesmo mapa (o nível e a força são acertados depois por balance_monsters.py, que roda no fim de build_maps.py).
Idempotente; chamado no fim de tools/assets/build_maps.py, antes de balance_monsters.py.
uso: python3 tools/assets/add_new_monster_areas.py   (a partir da raiz do projeto)"""
import json

MON, ARENAS = "data/monsters.json", "data/arenas.json"
mons = json.load(open(MON, encoding="utf-8"))


def monster(key, base, **changes):
    m = {k: v for k, v in mons[base].items() if k not in ("visual_pending", "_comment", "patrol", "patrol_radius", "patrol_speed", "charge", "spit")}
    m.update(changes)
    mons[key] = m


CHARGE = {"min": 4.0, "max": 10.0, "windup": 0.9, "speed": 12.0, "time": 0.6, "damage_mult": 1.2, "cooldown": 5.0}
monster("df_moosgreif", "fd_stag", name_key="MONSTER_DF_MOOSGREIF", look="moosgreif", color=[1.0, 1.0, 1.0], category="elite", element="earth", ai="melee",
        size=1.3, max_health=320, move_speed=2.4, damage=22, attack_range=2.8, attack_windup=1.0, attack_cooldown=2.0, sound="ogre",
        _comment="Moosgreif (Der Moosgreif, Brian Trepanier, CC BY 4.0): o grifo de musgo do folclore alemão; elite do Pântano do Musgo.")
monster("df_wendigo", "fd_stag", name_key="MONSTER_DF_WENDIGO", look="wendigo", color=[1.0, 1.0, 1.0], category="elite", element="water", ai="melee",
        size=1.15, max_health=240, move_speed=4.2, damage=18, attack_range=2.4, attack_windup=0.5, attack_cooldown=1.2, sound="beast",
        _comment="Wendigo (Pigcraft, CC BY 4.0): o horror da fome, de chifres; elite rápido do Pântano do Musgo.")
monster("df_sorceress", "fd_stag", name_key="MONSTER_DF_SORCERESS", look="sorceress", color=[1.0, 1.0, 1.0], category="common", element="air", ai="ranged",
        size=1.0, max_health=160, move_speed=2.4, damage=16, attack_range=9.0, attack_windup=1.0, attack_cooldown=2.6, keep_distance=6.0, sound="shade",
        spit={"radius": 1.6, "puddle_time": 4.0, "puddle_dps": 5.0, "glob": [0.62, 0.35, 1.0]},
        _comment="Feiticeira do Cajado de Cristal (Pigcraft, CC BY 4.0): lança cristais que deixam uma poça roxa; mantém distância.")
monster("df_shadow_stag", "fd_stag", name_key="MONSTER_DF_SHADOW_STAG", look="shadow_stag", color=[1.0, 1.0, 1.0], category="common", element="air", ai="charger",
        size=1.2, max_health=220, move_speed=3.6, damage=17, charge=CHARGE, sound="beast",
        _comment="Cervo Sombrio (Shadow Stag, Pigcraft, CC BY 4.0): cervo de chifres de osso que investe de longe.")
monster("ce_drowned_hag", "ce_brute", name_key="MONSTER_CE_DROWNED_HAG", look="drowned_hag", color=[1.0, 1.0, 1.0], category="common", element="water", ai="ranged",
        size=1.0, max_health=110, move_speed=2.2, damage=9, attack_range=8.0, attack_windup=0.9, attack_cooldown=2.4, keep_distance=5.0, sound="shade",
        spit={"radius": 1.6, "puddle_time": 5.0, "puddle_dps": 3.0, "glob": [0.25, 0.36, 0.3]},
        _comment="Bruxa Afogada (Pigcraft, CC BY 4.0): cospe água podre que deixa poça; mantém distância. Charco dos Afogados.")
monster("ce_asylum_matron", "ce_brute", name_key="MONSTER_CE_ASYLUM_MATRON", look="asylum_matron", color=[1.0, 1.0, 1.0], category="elite", element="earth", ai="melee",
        size=1.0, max_health=150, move_speed=3.2, damage=11, attack_range=1.8, attack_windup=0.5, attack_cooldown=1.1, sound="shade",
        _comment="Enfermeira Enfaixada (Bandaged Asylum Matron, Pigcraft, CC BY 4.0): elite de agulhas do Charco dos Afogados.")
json.dump(mons, open(MON, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(MON, "a").write("\n")

arenas = json.load(open(ARENAS, encoding="utf-8"))


def area(map_id, neighbor, room, encounters):
    a = arenas[map_id]
    a["rooms"] = [r for r in a["rooms"] if r["id"] != room["id"]] + [room]
    for r in a["rooms"]:
        if r["id"] == neighbor and "east" not in r.get("doors", []):
            r["doors"] = r.get("doors", []) + ["east"]
    prefix = room["id"] + "_"
    a["encounters"] = [e for e in a["encounters"] if not e["id"].startswith(prefix)] + [dict(e, id=prefix + e["id"]) for e in encounters]


# Floresta Negra: Bosque Leste (52, -36), 48 x 40 -> o pântano encosta no lado leste (x = 76), do mesmo tamanho.
area("dark_forest_01_woods", "grove_e", {"id": "moss_marsh", "center": [100, -36], "size": [48, 40], "doors": ["west"], "wall_height": 0.8}, [
    {"id": "stags", "position": [88, -46], "monsters": [{"monster": "df_shadow_stag", "count": 2}], "level": 20},
    {"id": "sorceresses", "position": [96, -26], "monsters": [{"monster": "df_sorceress", "count": 2}], "level": 20},
    {"id": "wendigos", "position": [108, -46], "monsters": [{"monster": "df_wendigo", "count": 2}], "level": 20},
    {"id": "moosgreif", "position": [114, -28], "monsters": [{"monster": "df_moosgreif", "count": 1}, {"monster": "df_sorceress", "count": 1}], "level": 20},
])
# Cemitério: sala r2 (5, -52), 36 x 26 -> o charco encosta no lado leste (x = 23).
area("cemetery_01_yard", "r2", {"id": "drowned_mire", "center": [41, -52], "size": [36, 26], "doors": ["west"], "wall_height": 0.8}, [
    {"id": "hags", "position": [36, -58], "monsters": [{"monster": "ce_drowned_hag", "count": 2}], "level": 9},
    {"id": "matron", "position": [48, -47], "monsters": [{"monster": "ce_asylum_matron", "count": 1}, {"monster": "ce_drowned_hag", "count": 1}], "level": 9},
])
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK: Pântano do Musgo (Floresta Negra) e Charco dos Afogados (Cemitério) com 6 monstros novos")
