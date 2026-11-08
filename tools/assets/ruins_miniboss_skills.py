"""Mini-chefes das Ruínas (ruins_01_city): o Guardião das Ruínas (ruin_warden, Praça dos Cavaleiros) e o Campeão Caído (war_champion, Praça dos
Monólitos) eram só investida + golpe. Agora cada um chama 6 ondas de monstros de FOGO (Demônio, Súcubo, Batedor da Mina, Golem de Fogo,
Golem de Magma) e tem duas habilidades no chão com aviso: pisão que empurra e um arremesso que deixa o chão em brasa.
Eles também trocam de alvo entre os heróis (enemy.gd _boss_target: todo chefe e mini-chefe; os animais do Invocador não os prendem mais).
Idempotente. Roda no fim de build_maps.py (depois dos clones do Guardião em outros mapas e do balanceamento).
uso: python3 tools/assets/ruins_miniboss_skills.py   (a partir da raiz do projeto)"""
import json

MONSTERS = "data/monsters.json"
mons = json.load(open(MONSTERS, encoding="utf-8"))

FIRE_WAVES = [
    [{"monster": "demon_twelve", "count": 2}],
    [{"monster": "succubus", "count": 2}],
    [{"monster": "mine_scout", "count": 3}],
    [{"monster": "golem_fire", "count": 1}, {"monster": "demon_twelve", "count": 1}],
    [{"monster": "succubus", "count": 1}, {"monster": "demon_twelve", "count": 2}],
    [{"monster": "mn_magma", "count": 1}, {"monster": "mine_scout", "count": 2}],
]
for wave in FIRE_WAVES:
    for entry in wave:
        assert mons[entry["monster"]]["element"] == "fire", entry

mons["ruin_warden"].update({
    "slam": {"_comment": "Terremoto: o golem bate os punhos no chão; a terra racha em volta dele e quem está dentro leva dano e é jogado longe.",
             "interval": 9.0, "radius": 5.0, "windup": 1.1, "damage_mult": 1.0, "push": 6.0, "push_time": 0.4, "wind": True},
    "fireball": {"_comment": "Pedra em brasa: arranca um bloco do chão, aquece e arremessa onde o herói está; deixa o chão em brasa por alguns segundos.",
                 "min": 4.0, "max": 16.0, "windup": 1.1, "cooldown": 5.0, "radius": 2.4, "damage_mult": 1.1, "element": "fire",
                 "glob": [1.0, 0.45, 0.1], "glob_size": 1.8, "puddle_time": 4.0, "puddle_dps": 6.0},
    "waves": {"_comment": "Chama os demônios presos nas ruínas: a cada intervalo, monstros de fogo brotam em volta dele.",
              "first": 6.0, "interval": 16.0, "radius": 6.0, "toast": "TOAST_WARDEN_WAVE", "list": FIRE_WAVES},
})
mons["war_champion"].update({
    "slam": {"_comment": "Anel de chamas: crava a espada no chão e uma explosão de fogo sai em volta dele; quem está dentro leva dano e é empurrado.",
             "interval": 8.0, "radius": 5.0, "windup": 1.0, "damage_mult": 1.1, "push": 5.0, "push_time": 0.35, "boom": [1.0, 0.5, 0.15]},
    "fireball": {"_comment": "Lança de fogo: arremessa uma chama onde o herói está; o chão fica queimando por alguns segundos.",
                 "min": 4.0, "max": 15.0, "windup": 1.0, "cooldown": 5.0, "radius": 2.2, "damage_mult": 1.1, "element": "fire",
                 "glob": [1.0, 0.35, 0.05], "glob_size": 1.6, "puddle_time": 4.0, "puddle_dps": 7.0},
    "waves": {"_comment": "Chama o exército de fogo da guerra: a cada intervalo, monstros de fogo brotam em volta dele.",
              "first": 6.0, "interval": 15.0, "radius": 6.0, "toast": "TOAST_CHAMPION_WAVE", "list": FIRE_WAVES[1:] + FIRE_WAVES[:1]},
})

json.dump(mons, open(MONSTERS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(MONSTERS, "a").write("\n")

# Avisos das ondas (pt_BR, en e es), só se ainda não existem.
TOASTS = {"TOAST_WARDEN_WAVE": ("O Guardião das Ruínas liberta os demônios: onda {n}!", "The Ruin Warden unleashes the demons: wave {n}!", "¡El Guardián de las Ruinas libera a los demonios: oleada {n}!"),
          "TOAST_CHAMPION_WAVE": ("O Campeão Caído chama o exército de fogo: onda {n}!", "The Fallen Champion calls the army of fire: wave {n}!", "¡El Campeón Caído llama al ejército de fuego: oleada {n}!")}
for path, idx in (("locale/pt_BR.po", 0), ("locale/en.po", 1), ("locale/es.po", 2)):
    text = open(path, encoding="utf-8").read()
    add = "".join('\nmsgid "%s"\nmsgstr "%s"\n' % (key, texts[idx]) for key, texts in TOASTS.items() if 'msgid "%s"' % key not in text)
    if add:
        open(path, "a", encoding="utf-8").write(add)
print("OK ruins: mini-chefes com 6 ondas de fogo, pisão e arremesso em brasa")
