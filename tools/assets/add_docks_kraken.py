"""Kraken, chefe final das Docas (docks_01_pier), no lugar do Capitão Afogado: dez tentáculos saem do Convés em anel em volta do centro e acordam juntos
quando o grupo chega ao meio. Nenhum sai do lugar: cada um vira para o herói, marca o chão onde ele está e bate ali com o tentáculo (o aviso de 1,2 s
dá tempo de sair); quem é pego é arrastado até perto do tentáculo, e quem encosta na base leva o pisão em volta, que joga longe. Um deles, o maior, é o próprio Kraken (o chefe: barra de vida, baú, diário do capitão
e a vitória do mapa vem de vencer o anel inteiro); ele chama ondas de Polvos do Kraken, que rastejam até os heróis e somem quando ele cai.
Modelos: tools/assets/build_kraken_tentacle.py ("Tentacle riged", defiat11) e tools/assets/build_kraken_octopus.py ("Octopus", kenchoo), CC BY 4.0.
Os números partem do Capitão Afogado já equilibrado (5630 de vida, 40 de dano): o anel soma ~6000 de vida, e cada tentáculo bate menos que ele.
Também troca os textos que diziam que é o Capitão que luta no Convés (o portão continua sendo "do Capitão Afogado": o Kraken é o monstro dele).
Idempotente. Roda no fim de build_maps.py (depois de balance_monsters.py).
uso: python3 tools/assets/add_docks_kraken.py   (a partir da raiz do projeto)"""
import json

ARENAS, MONSTERS = "data/arenas.json", "data/monsters.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
mons = json.load(open(MONSTERS, encoding="utf-8"))
docks = arenas["docks_01_pier"]

TENTACLE = {"move_speed": 0.0, "aggro_range": 40.0, "element": "water", "ai": "ranged", "keep_distance": 0.0, "look": "kraken_tentacle",
            "color": [1.0, 1.0, 1.0], "sound": "slime", "attack_windup": 1.2}
mons["kraken"] = dict(TENTACLE, **{
    "name_key": "MONSTER_KRAKEN", "max_health": 2600, "damage": 36, "attack_range": 11.0, "attack_cooldown": 3.0, "size": 2.5,
    "category": "boss", "role": "normal", "aggressive": False, "chest_loot": "chest", "quest_drop": "captain_log",
    "_comment": "Chefe final das Docas: o Kraken, o monstro do Capitão Afogado, sobe pelo Convés; este é o tentáculo maior (~10 m). Bate no chão onde o herói está e o arrasta, "
                "pisa em volta de si e chama ondas de Polvos do Kraken. Os outros nove tentáculos do anel são kraken_tentacle.",
    "spit": {"_comment": "Tentáculo que agarra: marca o chão onde o herói está, bate ali e arrasta quem pegou para perto dele.", "radius": 2.6, "damage_mult": 1.0,
             "pull": 6.0, "push_time": 0.45},
    "slam": {"_comment": "Varre a base: quem encosta no tentáculo leva o golpe em volta dele e é jogado longe.", "interval": 7.0, "radius": 5.0, "windup": 1.0,
             "damage_mult": 0.9, "push": 5.0},
    "waves": {"first": 8.0, "interval": 18.0, "radius": 6.0, "toast": "TOAST_KRAKEN_WAVE",
              "list": [[{"monster": "kraken_octopus", "count": 2}], [{"monster": "kraken_octopus", "count": 3}], [{"monster": "kraken_octopus", "count": 3}],
                       [{"monster": "kraken_octopus", "count": 4}], [{"monster": "kraken_octopus", "count": 4}]]}})
mons["kraken_tentacle"] = dict(TENTACLE, **{
    "name_key": "MONSTER_KRAKEN_TENTACLE", "max_health": 380, "damage": 24, "attack_range": 9.0, "attack_cooldown": 3.6, "size": 2.0,
    "category": "elite", "role": "tank",
    "_comment": "Tentáculo do Kraken (~8 m): nove deles fazem o anel do chefe final das Docas com o Kraken. Não sai do lugar; bate no chão onde o herói está.",
    "spit": {"_comment": "Tentáculo que agarra: marca o chão onde o herói está, bate ali e arrasta quem pegou para perto dele.", "radius": 2.2, "damage_mult": 1.0,
             "pull": 5.0, "push_time": 0.4},
    "slam": {"_comment": "Varre a base: quem encosta leva o golpe em volta dele.", "interval": 8.0, "radius": 4.0, "windup": 1.0, "damage_mult": 0.8, "push": 4.0}})
mons["kraken_octopus"] = {
    "name_key": "MONSTER_KRAKEN_OCTOPUS", "max_health": 120, "move_speed": 3.2, "damage": 12, "attack_range": 1.8, "attack_windup": 0.6,
    "attack_cooldown": 1.4, "aggro_range": 40.0, "size": 1.3, "category": "common", "element": "water", "ai": "melee", "look": "kraken_octopus",
    "color": [1.0, 1.0, 1.0], "sound": "slime", "role": "swarm",
    "_comment": "Polvo do Kraken (\"Octopus\", kenchoo, CC BY 4.0): só vem pelas ondas do Kraken, no Convés das Docas; rasteja até o herói e morde."}

# o anel: 7 tentáculos, o Kraken (fica no lado da proa, ao norte) e mais 2; raio 9 m em volta do meio do Convés
docks["encounters"] = [e for e in docks["encounters"] if e["id"] not in ("dk_captain", "dk_kraken")]
docks["encounters"].append({"id": "dk_kraken", "position": [0.0, -176.0], "spread": 9.0, "level": 6,
                            "monsters": [{"monster": "kraken_tentacle", "count": 7}, {"monster": "kraken", "count": 1},
                                         {"monster": "kraken_tentacle", "count": 2}]})
docks["victory_groups"] = ["dk_kraken"]

for path, data in ((MONSTERS, mons), (ARENAS, arenas)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")

T = {
    "MONSTER_KRAKEN": ("Kraken", "Kraken", "Kraken"),
    "MONSTER_KRAKEN_TENTACLE": ("Tentáculo do Kraken", "Kraken Tentacle", "Tentáculo del Kraken"),
    "MONSTER_KRAKEN_OCTOPUS": ("Polvo do Kraken", "Kraken Octopus", "Pulpo del Kraken"),
    "TOAST_KRAKEN_WAVE": ("O Kraken chama as crias: a onda {n} de polvos sobe ao convés!", "The Kraken calls its brood: octopus wave {n} climbs onto the deck!",
                          "El Kraken llama a sus crías: ¡la oleada {n} de pulpos sube a la cubierta!"),
    "QUEST_DOCKS_SMUGGLERS_DESC": (
        "Capitão Pirata quer Diário do Capitão Afogado, que o Kraken do Capitão Afogado guarda no Convés, no fundo do mapa. Consiga os livros com os moradores, desperte os mini-chefes no altar, troque os itens deles pelas chaves, abra o portão com o guardião e derrote o Kraken e seus tentáculos. Entregue Diário do Capitão Afogado a Capitão Pirata por uma recompensa em ouro.",
        "Pirate Captain wants Drowned Captain's Log, which the Drowned Captain's Kraken guards on the Deck, at the bottom of the map. Get the books from the locals, wake the mini-bosses at the altar, trade their items for the keys, open the gate with the guardian and defeat the Kraken and its tentacles. Hand Drowned Captain's Log to Pirate Captain for a gold reward.",
        "Capitán Pirata quiere Diario del Capitán Ahogado, que el Kraken del Capitán Ahogado guarda en la Cubierta, en el fondo del mapa. Consigue los libros con los lugareños, despierta a los minijefes en el altar, cambia sus objetos por las llaves, abre el portón con el guardián y derrota al Kraken y sus tentáculos. Entrega Diario del Capitán Ahogado a Capitán Pirata por una recompensa en oro."),
    "DLG_DOCKGUARD_1": (
        "Parem aí. Este portão fecha o Convés, e no Convés mora o Kraken do Capitão Afogado. O capitão foi para o fundo do mar e mandou a fera de volta no lugar dele.",
        "Stop there. This gate closes the Deck, and on the Deck lives the Drowned Captain's Kraken. The captain went to the bottom of the sea and sent the beast back in his place.",
        "Alto ahí. Este portón cierra la Cubierta, y en la Cubierta vive el Kraken del Capitán Ahogado. El capitán se fue al fondo del mar y mandó a la bestia en su lugar."),
    "DLG_DOCKGUARD_DONE": (
        "As duas chaves! O portão está aberto. Cuidado: quando pisarem no meio do Convés, os dez tentáculos do Kraken sobem todos de uma vez.",
        "Both keys! The gate is open. Beware: when you step into the middle of the Deck, all ten of the Kraken's tentacles rise at once.",
        "¡Las dos llaves! El portón está abierto. Cuidado: cuando pisen el centro de la Cubierta, los diez tentáculos del Kraken suben a la vez."),
}


def po_set(path, key, value):
    """Troca o msgstr de `key` (ou acrescenta a entrada no fim)."""
    lines = open(path, encoding="utf-8").read().split("\n")
    target = 'msgid "%s"' % key
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    if target in lines:
        i = lines.index(target)
        j = i + 1
        while j < len(lines) and lines[j].startswith('"'):
            j += 1  # (sem msgid de várias linhas aqui)
        k = j
        while k + 1 < len(lines) and lines[k + 1].startswith('"'):
            k += 1  # msgstr de várias linhas: some junto
        lines[j:k + 1] = ['msgstr "%s"' % escaped]
    else:
        if lines and lines[-1] == "":
            lines.pop()
        lines += ["", target, 'msgstr "%s"' % escaped, ""]
    open(path, "w", encoding="utf-8").write("\n".join(lines))


for idx, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po")):
    for key, values in T.items():
        po_set(path, key, values[idx])
for key in T:
    po_set("locale/messages.pot", key, "")
print("OK docas: Kraken (1 + 9 tentáculos em anel) no Convés, ondas de Polvos do Kraken")
