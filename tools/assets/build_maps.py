"""Gera os mapas da expedição depois do Esgoto (data/arenas.json): Floresta, Ruínas, Cemitério e Forte, na
ordem Tortuga -> Floresta -> Ruínas -> Cemitério -> Forte. As salas, os encontros e o cenário saem daqui
(sorteio com semente fixa), então rodar de novo reproduz o mesmo mapa. Também cria os monstros novos
(data/monsters.json) e o portal de Tortuga para a Floresta.
uso: python3 tools/assets/build_maps.py   (a partir da raiz do projeto)"""
import json, random, math

ARENAS = "data/arenas.json"
MONSTERS = "data/monsters.json"
arenas = json.load(open(ARENAS))
monsters = json.load(open(MONSTERS))


def rng(name):
    return random.Random(name)


def room(rid, cx, cz, w, h, doors, **extra):
    r = {"id": rid, "center": [cx, cz], "size": [w, h], "doors": doors}
    r.update(extra)
    return r


def scatter(r, room_def, pieces, count, margin=2.0, keep=(), scale=(1.0, 1.0), solid=None, avoid=()):
    """Espalha `count` peças (sorteadas de `pieces`) dentro da sala, longe das portas e dos pontos em `avoid`."""
    cx, cz = room_def["center"]
    w, h = room_def["size"]
    out = []
    tries = 0
    while len(out) < count and tries < count * 40:
        tries += 1
        x = cx + r.uniform(-w / 2 + margin, w / 2 - margin)
        z = cz + r.uniform(-h / 2 + margin, h / 2 - margin)
        if any(math.hypot(x - ax, z - az) < ar for ax, az, ar in list(keep) + list(avoid)):
            continue
        piece = r.choice(pieces)
        entry = {"piece": piece, "position": [round(x, 1), round(z, 1)], "rotation": r.randrange(0, 360, 15)}
        sc = r.uniform(*scale)
        if sc != 1.0:
            entry["scale"] = round(sc, 2)
        if solid:
            entry["solid"] = solid
        out.append(entry)
    return out


def ring(r, room_def, pieces, step, inset=0.8, gaps=(), scale=(1.0, 1.0)):
    """Fileira de peças junto às paredes (vegetação de borda), deixando vãos nas portas."""
    cx, cz = room_def["center"]
    w, h = room_def["size"]
    out = []
    for side in ("north", "south", "west", "east"):
        horizontal = side in ("north", "south")
        length = w if horizontal else h
        n = int(length / step)
        for i in range(n):
            t = -length / 2 + step * (i + 0.5) + r.uniform(-0.3, 0.3)
            x, z = (cx + t, cz + (-h / 2 + inset if side == "north" else h / 2 - inset)) if horizontal else \
                (cx + (-w / 2 + inset if side == "west" else w / 2 - inset), cz + t)
            if side in room_def["doors"] or any(d.split(":")[0] == side for d in room_def["doors"]):
                off = [float(d.split(":")[1]) if ":" in d else 0.0 for d in room_def["doors"] if d.split(":")[0] == side][0]
                if abs(t - off) < 3.0:
                    continue
            if any(math.hypot(x - gx, z - gz) < gr for gx, gz, gr in gaps):
                continue
            out.append({"piece": r.choice(pieces), "position": [round(x, 1), round(z, 1)], "rotation": r.randrange(0, 360, 15),
                        "scale": round(r.uniform(*scale), 2)})
    return out


def monster(name, base, **changes):
    m = json.loads(json.dumps(monsters[base]))
    m.pop("_comment", None)
    m.update(changes)
    monsters[name] = m


# --- Monstros novos (placeholders de arte: reaproveitam os modelos existentes) --------------------
monster("leshy", "old_gator", _comment="Mini-chefe da Floresta (04-tortuga-e-missoes.md: o Leshy guarda a árvore anciã): gigante de casca, "
        "investidas e pisões; modelo do Monstro da Floresta (cdmir, CC0).", name_key="MONSTER_LESHY", max_health=220, damage=18, size=2.0,
        element="earth", look="forest", color=[0.8, 0.85, 0.7])
monster("ruin_warden", "old_gator", _comment="Mini-chefe das Ruínas: o guardião do cofre real (substitui Cérbero até haver modelo). Investidas rápidas.",
        name_key="MONSTER_RUIN_WARDEN", max_health=260, damage=20, size=2.2, element="fire", look="lizard", color=[1.0, 0.55, 0.3])
monster("crypt_scorpion", "old_gator", _comment="Mini-chefe do Cemitério: escorpião da cripta, gigante e escuro.",
        name_key="MONSTER_CRYPT_SCORPION", max_health=300, damage=22, size=3.0, element="water", look="scorpion", color=[0.45, 0.5, 0.65])
monster("crypt_lord", "crypt_scorpion", _comment="Chefe do Cemitério: o Senhor da Cripta (Undead male, TiZeta, CC BY), nobre morto-vivo; "
        "investidas como o escorpião que ele substitui.", name_key="MONSTER_CRYPT_LORD", size=1.5, look="undead", color=[1.0, 1.0, 1.0])
monster("fort_commander", "old_gator", _comment="Chefe do Forte: o comandante amaldiçoado (usa o modelo do Feiticeiro-Aranha até haver arte própria).",
        name_key="MONSTER_FORT_COMMANDER", max_health=400, damage=25, size=2.4, element="air", look="demon", color=[0.8, 0.9, 1.0])
monster("succubus", "acid_toad", _comment="Súcubo (docs/03-1-bestiario.md, seção 10; Goth Female \"Fleur du Mal\", tizeta, CC BY 3.0): serva de Lúcifer, ataque de magia à distância: lança uma bola de fogo do inferno (marca no chão antes) que deixa chamas e recua. O encanto dela (mercenário atingido ataca os amigos) ainda não existe.",
        name_key="MONSTER_SUCCUBUS", max_health=110, damage=18, move_speed=2.2, attack_range=10.0, attack_windup=1.2, attack_cooldown=2.6,
        size=1.0, element="fire", look="succubus", color=[1.0, 1.0, 1.0], keep_distance=7.0,
        spit={"radius": 1.8, "puddle_time": 3.0, "puddle_dps": 5.0, "glob": [1.0, 0.35, 0.1]})
monster("night_demon", "skeleton", _comment="Demônio da Noite (Night Demon, nubux / morgan strauss, CC BY 3.0): demônio magro de garras longas, corpo a corpo e rápido; ainda não está em nenhum mapa (pode entrar em qualquer um, é só pôr em um encontro).",
        name_key="MONSTER_NIGHT_DEMON", max_health=140, damage=20, move_speed=3.4, size=1.3, element="air", look="night_demon", color=[1.0, 1.0, 1.0])
monster("dark_elf", "acid_toad", _comment="Elfo Sombrio (Dark Elf, danimal, CC BY-SA 3.0): besteiro do Forte; atira de longe um virote de sombra (marca no chão antes) e recua.",
        name_key="MONSTER_DARK_ELF", max_health=90, damage=14, move_speed=2.4, attack_range=9.0, attack_windup=1.0, attack_cooldown=2.2,
        size=1.0, element="air", look="dark_elf", color=[1.0, 1.0, 1.0], keep_distance=6.0,
        spit={"radius": 1.2, "puddle_time": 1.5, "puddle_dps": 3.0, "glob": [0.45, 0.2, 0.7]})
monster("dark_elf_lord", "dark_elf", _comment="Mini-chefe do Forte (sudoeste): o Senhor Elfo Sombrio, líder dos besteiros; virote de sombra mais forte; despertado pelo Exilado.",
        name_key="MONSTER_DARK_ELF_LORD", category="miniboss", max_health=420, damage=22, size=1.4, color=[0.8, 0.7, 1.0],
        spit={"radius": 1.6, "puddle_time": 2.5, "puddle_dps": 5.0, "glob": [0.45, 0.2, 0.7]})
# Esqueleto (Skeleton with rig, rudy85, CC0; modelo e animações feitos por tools/assets/build_skeleton.py):
# corpo a corpo comum do Cemitério, em grupos.
monsters["skeleton"] = {
    "_comment": "Esqueleto do Cemitério (Skeleton with rig, rudy85, CC0): corpo a corpo, vaga entre as covas até alguém chegar perto. Terra, como os mortos da lenda (fraco a Fogo).",
    "name_key": "MONSTER_SKELETON", "max_health": 90, "move_speed": 3.0, "damage": 14, "attack_range": 2.2,
    "attack_windup": 0.6, "attack_cooldown": 1.4, "aggro_range": 40.0, "size": 1.0, "category": "common", "element": "earth",
    "patrol": True, "patrol_radius": 6.0, "patrol_speed": 0.8, "look": "skeleton", "color": [0.92, 0.86, 0.72],
}
# Zumbi Magro (Thin Zombie, Rosswet Mobile, CC BY 3.0; build_monsters.py): mais lento e resistente que o esqueleto.
monster("zombie", "skeleton", _comment="Zumbi Magro do Cemitério (Thin Zombie, Rosswet Mobile, CC BY 3.0): corpo a corpo, lento e resistente; vaga entre as covas. Terra (fraco a Fogo).",
        name_key="MONSTER_ZOMBIE", max_health=130, damage=12, move_speed=2.2, attack_windup=0.8, attack_cooldown=1.7, look="zombie",
        color=[1.0, 1.0, 1.0])
# Troll Magro (Skinny Troll, piacenti, CC BY 3.0; build_troll.py): elite corpo a corpo do Cemitério, lento, de pancada pesada.
monster("troll", "skeleton", _comment="Troll Magro do Cemitério (Skinny Troll, piacenti, CC BY 3.0): elite corpo a corpo; lento, resistente e de pancada lenta e pesada com a clava. Terra (fraco a Fogo).",
        name_key="MONSTER_TROLL", max_health=320, damage=24, move_speed=2.4, attack_range=3.2, attack_windup=1.1, attack_cooldown=2.2,
        category="elite", size=1.0, look="troll", color=[1.0, 1.0, 1.0], patrol_radius=4.0)
# Guardião do Túmulo: mini-chefe de pedra que a estátua do poste de luz desperta (Praça da Estátua do Cemitério); usa o modelo do
# golem de pedra, escurecido, e investe como o Escorpião da Cripta.
monster("tomb_guardian", "crypt_scorpion", _comment="Guardião do Túmulo (mini-chefe do Cemitério): golem de pedra que a estátua do poste de luz desperta quando se fala com ela; investe como o Escorpião da Cripta. Terra (fraco a Fogo).",
        name_key="MONSTER_TOMB_GUARDIAN", max_health=340, damage=24, size=2.2, element="earth", look="golem_stone", color=[0.78, 0.85, 0.75])
# Jarro e garrafa brancos (Free Mug Pack 1, rubberduck, CC0; build_mugs.py): quebráveis como o pote do Esgoto, com cacos;
# no Cemitério soltam só poção (tabela "breakable_potion").
monster("mug", "pot", _comment="Jarro ou garrafa branca (Free Mug Pack 1, rubberduck, CC0): quebrável parado, como o pote do Esgoto; ao quebrar solta poção (tabela 'breakable_potion' no objeto). O modelo sai da posição.",
        name_key="PROP_MUG", max_health=8, size=0.8, look="mug", pieces=["Mug_Jar", "Mug_Bottle"], shards=True, color=[0.9, 0.86, 0.78])


# Golens da Floresta (umask007, CC BY / CC BY-SA): três elites corpo a corpo lentos e resistentes; o de pedra investe.
GOLEM = dict(move_speed=1.8, attack_range=2.6, aggro_range=40.0, size=1.6, category="elite", color=[1.0, 1.0, 1.0])
monster("golem_fire", "skeleton", _comment="Golem de Fogo da Floresta (Fire/Ice/Stone Golem, umask007, CC BY 3.0 / CC BY-SA 3.0): elite corpo a corpo, rápido e de dano alto.",
        name_key="MONSTER_GOLEM_FIRE", max_health=180, damage=16, attack_windup=0.8, attack_cooldown=1.8, element="fire", look="golem_fire",
        patrol=False, **{**GOLEM, "move_speed": 2.3})
monster("golem_ice", "skeleton", _comment="Golem de Gelo da Floresta (umask007): elite corpo a corpo, o mais lento; Água.",
        name_key="MONSTER_GOLEM_ICE", max_health=220, damage=14, attack_windup=1.0, attack_cooldown=2.2, element="water", look="golem_ice",
        patrol=False, **{**GOLEM, "move_speed": 1.6})
monster("golem_stone", "old_gator", _comment="Golem de Pedra da Floresta (umask007): elite que investe como o Leshy; Terra.",
        name_key="MONSTER_GOLEM_STONE", max_health=260, damage=18, attack_windup=0.9, attack_cooldown=2.0, element="earth", look="golem_stone",
        **{**GOLEM, "move_speed": 1.8})
monsters["golem_stone"].update({"ai": "charger", "charge": {"min": 4.0, "max": 9.0, "windup": 1.0, "speed": 10.0, "time": 0.6, "damage_mult": 1.3, "cooldown": 5.0}})
for _g in ("golem_stone", "golem_ice", "golem_fire"):
    for _k in ("rare_spawn", "no_loot", "flee", "patrol_radius", "patrol_speed"):
        monsters[_g].pop(_k, None)


# Réptil da Floresta (Rigged Textured Reptile, thecubber, CC BY-SA 3.0): corpo a corpo rápido, anda em bando e vaga por perto até alguém chegar.
monster("forest_reptile", "skeleton", _comment="Réptil da Floresta (thecubber, CC BY-SA 3.0): garras rápidas, em bando de três; vaga entre as árvores até alguém chegar perto.",
        name_key="MONSTER_FOREST_REPTILE", max_health=70, move_speed=3.2, damage=10, attack_range=2.0, attack_windup=0.5, attack_cooldown=1.3,
        size=1.1, element="earth", look="reptile", color=[1.0, 1.0, 1.0])


# Besta Quitinosa (Beast 02, Atmostatic, CC BY 3.0 / CC BY-SA 3.0): aranha-besouro de garras, rápida; bando de dois na clareira.
monster("chitin_beast", "skeleton", _comment="Besta Quitinosa da Floresta (Beast 02, Atmostatic, CC BY / CC BY-SA): corpo a corpo rápido e frágil; vaga até alguém chegar. Terra.",
        name_key="MONSTER_CHITIN_BEAST", max_health=80, move_speed=3.4, damage=12, attack_range=2.2, attack_windup=0.5, attack_cooldown=1.3,
        size=1.1, element="earth", look="chitin_beast", color=[1.0, 1.0, 1.0])


# Cervos da Floresta (CDmir e TinyWorlds, CC0): quebráveis como os potes do Esgoto: não atacam, não perseguem, não voltam depois de mortos
# (a campanha guarda os já quebrados) e, ao morrer, soltam só poção (tabela "breakable_potion").
monster("deer_buck", "barrel", _comment="Cervo da Floresta (Old Deer Male, CDmir, CC0): quebrável parado, como o pote do Esgoto; ao morrer solta poção.",
        name_key="PROP_DEER_BUCK", max_health=20, size=1.4, look="deer_buck", color=[1.0, 1.0, 1.0])
monster("deer_doe", "barrel", _comment="Corça da Floresta (Deer Female, CDmir, CC0): igual ao cervo.",
        name_key="PROP_DEER_DOE", max_health=20, size=1.4, look="deer_doe", color=[1.0, 1.0, 1.0])


# --- Trilhas de lajes (usadas pelo Cemitério e pela Floresta) ---------------------------------------------------
def seg_dist(px, pz, a, b):
    ax, az = a
    bx, bz = b
    dx, dz = bx - ax, bz - az
    t = 0.0 if dx == 0 and dz == 0 else max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / (dx * dx + dz * dz)))
    return math.hypot(px - (ax + t * dx), pz - (az + t * dz))


def stone_trail(rng_, points, step=0.9, spread=0.5, scale=(0.42, 0.62)):
    """Trilha de lajes soltas (Floor_UnevenBrick, 2 m, encolhida para ~1 m) ao longo da linha `points`: duas fileiras
    tortas, cada laje girada ao acaso e numa altura um pouco diferente (as que se sobrepõem não brigam no chão)."""
    out = []
    n = 0
    for (x0, z0), (x1, z1) in zip(points, points[1:]):
        length = math.hypot(x1 - x0, z1 - z0)
        if length < 0.01:
            continue
        dx, dz = (x1 - x0) / length, (z1 - z0) / length
        for i in range(max(int(length / step), 1)):
            t = (i + 0.5) * step
            for lane in (-1, 1):
                off = lane * spread * 0.55 + rng_.uniform(-0.18, 0.18)
                along = t + rng_.uniform(-0.2, 0.2) + (step / 2 if lane > 0 else 0)
                out.append({"piece": "Floor_UnevenBrick", "rotation": rng_.randrange(0, 360, 15),
                            "position": [round(x0 + dx * along - dz * off, 2), round(z0 + dz * along + dx * off, 2)],
                            "scale": round(rng_.uniform(*scale), 2), "y": round(0.03 + 0.004 * (n % 7), 3)})
                n += 1
    return out


# --- Floresta ---------------------------------------------------------------------------------------
# Mapa de salas e trilhas no desenho da referência do autor (~/Downloads/map-forest.jpg): a aldeia no canto sudoeste (a partida) e uma rota
# principal até a sala do chefe final (o Leshy, no nordeste, com a saída). Na rota ficam as duas áreas de mini-chefe: cada uma tem uma praça
# no centro com um NPC que conversa, passa a missão do mini-chefe e o invoca (como a estátua do Cemitério):
#   Praça da Pira (a Guardiã, Golem de Fogo) -> encruzilhada -> Praça da Pedra (o Eremita, Golem de Pedra) -> Covil do Leshy.
# Quatro salas de monstros, cada uma com um só tipo, ficam no fim de caminhos sem saída que saem da aldeia e da rota:
#   Clareira dos Sapos (norte da aldeia: sapos ácidos) · Gruta dos Morcegos (norte da Praça da Pira: morcegos da peste)
#   · Toca dos Répteis (oeste da Praça da Pedra: répteis e a Rainha das Víboras) · Covil das Bestas (leste da encruzilhada: bestas quitinosas).
fr = rng("forest")

# id: (x0, x1, z0, z1, {lado: coordenada da porta}). Salas vizinhas no leste-oeste ficam a 1 m uma da outra e as do norte-sul se tocam
# (como no Cemitério); cada lado tem no máximo uma porta, de 6 m.
FOR_ROOMS = {
    "village": (-41, -17, -28, -7, {"north": -30, "east": -17.5}),
    "ca": (-36, -24, -38, -28, {"south": -30, "north": -30}),                            # caminho sem saída 1 (norte da aldeia)
    "toads": (-41, -15, -60, -38, {"south": -30}),                                       # sala de monstros 1
    "c8": (-16, -1, -21.5, -13.5, {"west": -17.5, "east": -17.5}),
    "pira": (0, 24, -28, -7, {"west": -17.5, "east": -17.5, "north": 12}),               # mini-chefe 1 (Praça da Pira)
    "cb": (6, 18, -38, -28, {"south": 12, "north": 12}),                                 # caminho sem saída 2
    "bats": (-6, 30, -56, -38, {"south": 12}),                                           # sala de monstros 2
    "c7": (25, 35, -21.5, -13.5, {"west": -17.5, "east": -17.5}),
    "hub": (36, 60, -46, -8, {"west": -17.5, "north": 46, "east": -27}),                 # encruzilhada
    "cd": (61, 71, -33, -21, {"west": -27, "east": -27}),                                # caminho sem saída 3
    "beasts": (72, 96, -45, -9, {"west": -27}),                                          # sala de monstros 3
    "c6": (40, 52, -56, -46, {"south": 46, "north": 46}),
    "pedra": (32, 62, -82, -56, {"south": 46, "north": 46, "west": -70}),                # mini-chefe 2 (Praça da Pedra)
    "cc": (14, 31, -76, -64, {"east": -70, "west": -70}),                                # caminho sem saída 4
    "reptiles": (-12, 13, -90, -60, {"east": -70}),                                      # sala de monstros 4
    "c4": (40, 52, -92, -82, {"south": 46, "north": 46}),
    "lair": (32, 62, -122, -92, {"south": 46}),                                          # Covil do Leshy (chefe final, saída)
}
FOR_SECTORS = {"toads": "Pr_Obelisk2", "bats": "Pr_BrokenPillar2", "reptiles": "Pr_Obelisk1", "beasts": "Pr_Cross3",
               "pira": "Pr_Cross4", "pedra": "Pr_Cross4", "lair": "Pr_Obelisk3"}


def fr_doors(rid):
    x0, x1, z0, z1, doors = FOR_ROOMS[rid]
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    out = []
    for side, coord in doors.items():
        off = coord - (cx if side in ("north", "south") else cz)
        out.append(side if abs(off) < 1e-6 else "%s:%g" % (side, off))
    return out


f_rooms_out = [room(rid, (x0 + x1) / 2, (z0 + z1) / 2, x1 - x0, z1 - z0, fr_doors(rid), wall_height=0.8)
               for rid, (x0, x1, z0, z1, _) in FOR_ROOMS.items()]
village_room = f_rooms_out[0]
f_rooms = f_rooms_out[1:]
_FOUT = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}
_FFACE = {"north": "south", "south": "north", "west": "east", "east": "west"}
for _rid, (_x0, _x1, _z0, _z1, _doors) in FOR_ROOMS.items():    # conferência: do outro lado de cada porta há uma sala com a porta no mesmo lugar
    for _side, _coord in _doors.items():
        _pt = {"north": (_coord, _z0), "south": (_coord, _z1), "west": (_x0, _coord), "east": (_x1, _coord)}[_side]
        _probe = (_pt[0] + _FOUT[_side][0] * 1.4, _pt[1] + _FOUT[_side][1] * 1.4)
        _hits = [o for o, r in FOR_ROOMS.items() if o != _rid and r[0] <= _probe[0] <= r[1] and r[2] <= _probe[1] <= r[3]]
        assert len(_hits) == 1 and FOR_ROOMS[_hits[0]][4].get(_FFACE[_side]) == _coord, ("porta sem par", _rid, _side, _coord, _hits)
for _a in FOR_ROOMS:                                           # e nenhuma sala sobre outra
    for _b in FOR_ROOMS:
        if _a < _b:
            _ra, _rb = FOR_ROOMS[_a], FOR_ROOMS[_b]
            assert _ra[1] <= _rb[0] or _rb[1] <= _ra[0] or _ra[3] <= _rb[2] or _rb[3] <= _ra[2], ("salas sobrepostas", _a, _b)


def f_rect_in(x, z, rid, margin=0.0):
    x0, x1, z0, z1, _ = FOR_ROOMS[rid]
    return x0 + margin <= x <= x1 - margin and z0 + margin <= z <= z1 - margin


# Quatro salas de monstros, um tipo em cada. Os dois golens (pedra e fogo) são mini-chefes invocados nas praças (`rank`).
f_enc = [
    {"id": "f_toads_a", "position": [-36, -44], "monsters": [{"monster": "acid_toad", "count": 3}]},
    {"id": "f_toads_b", "position": [-20, -44], "monsters": [{"monster": "acid_toad", "count": 3}]},
    {"id": "f_toads_c", "position": [-35, -55], "monsters": [{"monster": "acid_toad", "count": 3}]},
    {"id": "f_toads_d", "position": [-21, -55], "monsters": [{"monster": "acid_toad", "count": 3}]},
    {"id": "f_bats_a", "position": [0, -44], "monsters": [{"monster": "plague_bat", "count": 3}]},
    {"id": "f_bats_b", "position": [24, -44], "monsters": [{"monster": "plague_bat", "count": 3}]},
    {"id": "f_bats_c", "position": [12, -52], "monsters": [{"monster": "plague_bat", "count": 4}]},
    {"id": "f_reptiles", "position": [-6, -66], "monsters": [{"monster": "forest_reptile", "count": 3}]},
    {"id": "f_reptiles_b", "position": [7, -85], "monsters": [{"monster": "forest_reptile", "count": 3}]},
    {"id": "f_reptiles_c", "position": [-7, -85], "monsters": [{"monster": "forest_reptile", "count": 3}]},
    {"id": "f_beasts", "position": [80, -39], "monsters": [{"monster": "chitin_beast", "count": 2}]},
    {"id": "f_beasts_b", "position": [90, -39], "monsters": [{"monster": "chitin_beast", "count": 2}]},
    {"id": "f_beasts_c", "position": [80, -15], "monsters": [{"monster": "chitin_beast", "count": 2}]},
    {"id": "f_beasts_d", "position": [90, -15], "monsters": [{"monster": "chitin_beast", "count": 2}]},
    {"id": "f_leshy", "position": [47, -111], "monsters": [{"monster": "leshy", "count": 1}]},
]
F_PLAZA_R = 6.5
F_PLAZAS = {"stone": (46, -69), "fire": (12, -17.5)}        # a Praça da Pedra (sala `pedra`) e a Praça da Pira (sala `pira`)
f_summons = {
    "stone": {"id": "f_golem_stone", "position": [46, -61.5], "spread": 3.0, "toast": "TOAST_HERMIT_AWAKENS",
              "monsters": [{"monster": "golem_stone", "count": 1, "rank": "miniboss"}]},
    "fire": {"id": "f_golem_fire", "position": [12, -10.0], "spread": 3.0, "toast": "TOAST_PYRE_AWAKENS",
             "monsters": [{"monster": "golem_fire", "count": 1, "rank": "miniboss"}]},
}
f_extra = []

# --- Trilhas de lajes: ligam as portas e os centros dos setores (param na borda das praças, que têm piso próprio) --------------------
f_trails = [
    [(-22.5, -10.5), (-19, -15), (-16, -17.5), (-8, -17.5), (0, -17.5), (5.6, -17.5)],                           # da partida até a Praça da Pira
    [(18.4, -17.5), (24, -17.5), (35, -17.5), (38, -17.5), (43, -24), (49, -32), (47, -40), (46, -46),
     (46, -56), (46, -62.5)],                                                                                    # da Pira, pela encruzilhada, até a Praça da Pedra
    [(46, -75.5), (46, -82), (46, -92), (47, -103)],                                                             # da Praça da Pedra ao Leshy
    [(-30, -28), (-31, -34), (-30, -40), (-27, -46), (-26, -52)],                                                # caminho 1: aldeia -> sapos
    [(12, -24), (12, -28), (12, -38), (14, -44), (12, -50)],                                                     # caminho 2: Pira -> morcegos
    [(49, -32), (55, -28), (60, -27), (71, -27), (80, -27), (86, -27)],                                          # caminho 3: encruzilhada -> bestas
    [(39.5, -69), (36, -70), (32, -70), (14, -70), (4, -70), (0, -73)],                                          # caminho 4: Praça da Pedra -> répteis
]


def f_trail_dist(x, z):
    return min(seg_dist(x, z, a, b) for line in f_trails for a, b in zip(line, line[1:]))


def f_samples(step=2.5, radius=2.2):
    """Pontos (x, z, raio) ao longo de todas as trilhas, para o que é sorteado não ficar em cima delas."""
    out = []
    for line in f_trails:
        for a, b in zip(line, line[1:]):
            n = max(int(math.hypot(b[0] - a[0], b[1] - a[1]) / step), 1)
            out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n, radius) for k in range(n)]
    return out


f_decor = []
plants = ["Pl_Bush", "Pl_Swirl", "Pl_Hemp", "Pl_Flower"]
F_START = (-22.5, -10.5)
f_fixed = [(F_START[0], F_START[1], 3), (-26.5, -9.0, 2), (47, -119, 4), (41, -117, 3), (53, -117, 3), (-38, -57, 3), (28, -53, 3), (-9, -87, 3), (93, -12, 3)]
f_keep = [(e["position"][0], e["position"][1], 3) for e in f_enc] + [(cx, cz, F_PLAZA_R + 3.0) for cx, cz in F_PLAZAS.values()] + f_fixed
for rd in f_rooms:
    f_decor += ring(fr, rd, ["Pl_Bamboo", "Pl_Bamboo", "Pl_Bush"], 2.4, scale=(0.9, 1.5))
    f_decor += scatter(fr, rd, plants, int(rd["size"][0] * rd["size"][1] / 22), margin=2.0, avoid=f_keep)
# Pedras (Rocks, Nobiax, CC0 + Low Poly Rocks, para, CC0): semente própria. As grandes bloqueiam, as pequenas são só enfeite.
ROCK_FOOTPRINT = {"Rock_1": 0.9, "Rock_2": 0.75, "Rock_3": 1.2, "Rock_4": 1.0, "Rock_5": 0.75,
                  "RockP_1": 0.9, "RockP_2": 1.1, "RockP_3": 1.0, "RockP_4": 1.0, "RockP_5": 1.0, "RockP_6": 0.95}
rkr = rng("forest_rocks")
for rd in f_rooms:
    for rock in scatter(rkr, rd, list(ROCK_FOOTPRINT), int(rd["size"][0] * rd["size"][1] / 70), margin=3.0, scale=(0.6, 2.2), avoid=f_keep):
        if rock["scale"] >= 1.2:
            side = round(ROCK_FOOTPRINT[rock["piece"]] * rock["scale"] * 0.85, 1)
            rock["solid"] = [side, side]
        f_decor.append(rock)
# Arbustos tropicais (Tropical Shrubs, Nobiax, CC0): também com semente própria; só enfeite, sem colisão.
shr = rng("forest_shrubs")
for rd in f_rooms:
    f_decor += scatter(shr, rd, ["Pl_Shrub%d" % i for i in range(1, 6)], int(rd["size"][0] * rd["size"][1] / 30), margin=2.5,
                       scale=(0.8, 1.6), avoid=f_keep)
# Ervas daninhas (Tiny Weeds, Nobiax, CC0): tufos pequenos pelo chão, semente própria, sem colisão.
wdr = rng("forest_weeds")
for rd in f_rooms:
    f_decor += scatter(wdr, rd, ["Pl_Weed%d" % i for i in range(1, 6)], int(rd["size"][0] * rd["size"][1] / 8), margin=1.5,
                       scale=(1.0, 2.0), avoid=f_keep)
# Árvores mortas (Dead Tree, piacenti, CC BY 3.0): troncos secos com raízes à mostra, semente própria; o tronco bloqueia (colisor pequeno).
dtr = rng("forest_dead_trees")
for rd in f_rooms:
    for tree in scatter(dtr, rd, ["Dead_Tree"], int(rd["size"][0] * rd["size"][1] / 110), margin=4.0, scale=(0.6, 1.1), avoid=f_keep):
        side = round(0.9 * tree["scale"], 1)
        tree["solid"] = [side, side]
        f_decor.append(tree)
# Carvalhos velhos (Old oak tree, Julius Krischan Makowka, GPL / CC BY-SA 3.0; build_oak.py): copas grandes, semente própria; o tronco bloqueia.
oakr = rng("forest_oaks")
for rd in f_rooms:
    for tree in scatter(oakr, rd, ["Oak_Tree"], int(rd["size"][0] * rd["size"][1] / 150), margin=5.0, scale=(0.8, 1.4), avoid=f_keep):
        side = round(1.1 * tree["scale"], 1)
        tree["solid"] = [side, side]
        f_decor.append(tree)
# Peças postas à mão: placa e poste na partida, obeliscos e pilares no Covil do Leshy.
f_decor += [{"piece": "Pr_RoadSign", "position": [-19.0, -9.5], "rotation": 200}, {"piece": "Pr_LampPost", "position": [-24.0, -8.2], "rotation": 0, "solid": [0.6, 0.6]},
            {"piece": "Pr_Obelisk3", "position": [47, -119], "solid": [1.4, 1.4]}, {"piece": "Pr_Obelisk2", "position": [41, -117], "solid": [1.0, 1.0]},
            {"piece": "Pr_Obelisk2", "position": [53, -117], "solid": [1.0, 1.0]}, {"piece": "Pr_BrokenPillar2", "position": [36, -100], "solid": [1.2, 1.2]},
            {"piece": "Pr_BrokenPillar1", "position": [58, -100], "solid": [1.2, 1.2]}]
# Poucos cervos: semente própria, longe das portas, dos baús, dos grupos de monstros, das praças, das trilhas e uns dos outros.
f_deer = []
dr_ = rng("forest_deer")
for rid, count in (("hub", 2), ("toads", 1), ("bats", 1), ("reptiles", 1)):
    rd = f_rooms_out[list(FOR_ROOMS).index(rid)]
    for spot in scatter(dr_, rd, ["deer"], count, margin=4.0, avoid=f_keep + f_samples() + [(d["position"][0], d["position"][1], 10) for d in f_deer]):
        f_deer.append({"id": "d%d" % (len(f_deer) + 1), "monster": "deer_buck" if len(f_deer) % 2 == 0 else "deer_doe",
                       "position": spot["position"], "table": "breakable_potion"})
# --- Aldeia de Ferncroft (Medieval Props Pack 3, Daniel Andersson, CC0; casas do kit de Tortuga) ---------------------------------------------
# A aldeia é a sala da partida (canto sudoeste): portas ao norte (Clareira dos Sapos) e a leste (corredor até o Covil das Bestas).


def cabin(cx, cz, windows_first=True):
    """Casa 4 x 4 m com a fachada para o sul (+Z): paredes do kit com colisão, cantos, piso de tábua e telhado."""
    front = ["Wall_Plaster_Door_Round", "Wall_Plaster_Window_Wide_Round"] if windows_first else ["Wall_Plaster_Window_Thin_Round", "Wall_Plaster_Door_Round"]
    walls = [(front[0], cx - 1, cz + 2, 0), (front[1], cx + 1, cz + 2, 0),
             ("Wall_Plaster_Straight", cx - 1, cz - 2, 180), ("Wall_Plaster_Straight", cx + 1, cz - 2, 180),
             ("Wall_Plaster_Window_Wide_Round", cx + 2, cz - 1, 90), ("Wall_Plaster_Straight", cx + 2, cz + 1, 90),
             ("Wall_Plaster_Straight", cx - 2, cz - 1, 270), ("Wall_Plaster_Window_Thin_Round", cx - 2, cz + 1, 270)]
    out = [{"piece": w, "position": [x, z], "rotation": r, "solid": [2.0, 0.5]} for w, x, z, r in walls]
    out += [{"piece": "Corner_Exterior_Wood", "position": [cx + sx, cz + sz]} for sx in (-2, 2) for sz in (-2, 2)]
    out += [{"piece": "Floor_WoodDark", "position": [cx + fx, cz + fz], "y": 0.03} for fx in (-1, 1) for fz in (-1, 1)]
    out.append({"piece": "Roof_RoundTiles_4x4", "position": [cx, cz], "y": 3.2})
    return out


v_decor = cabin(-35, -23) + cabin(-26, -23.5, False)
v_decor += [
    {"piece": "Vl_Cellar", "position": [-36.5, -10.6], "solid": [2.4, 2.3]},
    {"piece": "Vl_Outhouse", "position": [-38.3, -14.6], "solid": [1.4, 1.5]},
    {"piece": "Vl_Logs", "position": [-38.5, -19.9], "rotation": 90, "solid": [2.2, 0.8]},
    {"piece": "Vl_ChoppingBlock", "position": [-37.0, -17.4], "rotation": 30, "solid": [0.5, 0.5]},
    {"piece": "Vl_TanningStand", "position": [-23.0, -27.0], "solid": [2.2, 0.5]},
    {"piece": "Vl_FishRack", "position": [-21.0, -22.0], "solid": [2.1, 0.4]},
    {"piece": "Vl_Ladder", "position": [-33.2, -25.2], "rotation": 0, "y": 0.0},
    {"piece": "Well_Covered", "position": [-27.5, -15.5], "solid": [1.8, 1.8]},
    {"piece": "Cart_Wood", "position": [-30.0, -9.6], "rotation": 15, "solid": [2.4, 1.3]},
    {"piece": "Wheelbarrow", "position": [-34.5, -12.3], "rotation": 340, "solid": [1.0, 0.8]},
    {"piece": "Barrel", "position": [-37.6, -26.3], "solid": [0.9, 0.9]},
    {"piece": "Barrel", "position": [-19.6, -26.0], "solid": [0.9, 0.9]},
    {"piece": "Crate_Wooden", "position": [-38.8, -26.4], "rotation": 20, "solid": [0.9, 0.9]},
    {"piece": "Bucket_Wooden_1", "position": [-26.2, -16.9]},
    {"piece": "Stool_Wood", "position": [-35.9, -17.2]},
    {"piece": "Bench_Wood", "position": [-22.6, -19.4], "rotation": 0},
    {"piece": "Mushroom_Cluster", "position": [-40.0, -25.2]}, {"piece": "Mushroom_Tall", "position": [-39.4, -25.8]},
    {"piece": "Mushroom_Flat", "position": [-39.0, -7.9]},
]
vr = rng("forest_village")
v_keep = [(-35, -23, 4.6), (-26, -23.5, 4.6), (-36.5, -10.6, 2.2), (-38.3, -14.6, 1.6), (-27.5, -15.5, 2.0), (-30, -9.6, 2.2),
          (-19, -17.5, 4.0), (-34.5, -19, 2.0), (-30.2, -21.2, 2.0), (-23, -27, 2.0), (-24, -10, 3.0), (-26.5, -9, 2.0), (-21, -22, 2.0), (-38.5, -19.9, 2.0), (-37.0, -17.4, 1.5)]
v_decor += ring(vr, village_room, ["Pl_Bamboo", "Pl_Bamboo", "Pl_Bush"], 2.4, scale=(0.9, 1.5))
v_decor += scatter(vr, village_room, ["Pl_Bush", "Pl_Flower", "Pl_Swirl", "Pl_Shrub1", "Pl_Shrub3"], 10, margin=2.5, scale=(0.8, 1.4), avoid=v_keep)
v_decor += scatter(vr, village_room, ["Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Weed4", "Pl_Weed5"], 60, margin=1.5, scale=(1.0, 2.0), avoid=v_keep)
f_decor += v_decor

# Praças (centro dos setores 2 e 5): piso de lajes em disco, anel de peças em volta (sem tapar as trilhas) e o NPC no meio.
def f_plaza(kind, cx, cz):
    pr = random.Random("forest_plaza_%s" % kind)
    out = []
    for gx in range(-8, 9, 2):
        for gz in range(-8, 9, 2):
            if math.hypot(gx, gz) < F_PLAZA_R + 0.8:
                out.append({"piece": "Floor_UnevenBrick", "position": [cx + gx, cz + gz], "rotation": pr.choice((0, 90, 180, 270)), "y": 0.03})
    pieces = ["Pr_Obelisk2", "Pr_BrokenPillar1"] if kind == "stone" else ["Pr_LampPost", "Pr_BrokenPillar2"]
    for k in range(12):
        a = math.tau * (k + 0.5) / 12
        x, z = cx + (F_PLAZA_R + 1.0) * math.cos(a), cz + (F_PLAZA_R + 1.0) * math.sin(a)
        if f_trail_dist(x, z) < 2.4 or not any(f_rect_in(x, z, r, 1.0) for r in ("pedra", "pira")):
            continue
        out.append({"piece": pieces[k % 2], "position": [round(x, 1), round(z, 1)], "rotation": pr.randrange(0, 360, 15), "solid": [0.8, 0.8]})
    if kind == "fire":
        out.append({"light": [1.0, 0.55, 0.22], "position": [cx, cz + 0.5], "y": 2.4, "range": 12.0, "energy": 1.6})
    return out


f_plaza_decor = f_plaza("stone", *F_PLAZAS["stone"]) + f_plaza("fire", *F_PLAZAS["fire"])

# Marcos de pedra em cada porta de cada setor: um par, um de cada lado da abertura (um tipo por setor, como as divisas do Cemitério).
f_markers = []
for rid, piece in FOR_SECTORS.items():
    x0, x1, z0, z1, doors = FOR_ROOMS[rid]
    for side, coord in doors.items():
        for off in (-3.6, 3.6):
            x, z = {"north": (coord + off, z0 + 1.2), "south": (coord + off, z1 - 1.2), "west": (x0 + 1.2, coord + off), "east": (x1 - 1.2, coord + off)}[side]
            f_markers.append({"piece": piece, "position": [round(x, 1), round(z, 1)], "solid": [1.4, 1.4]})
# Nada sorteado (plantas, pedras, árvores) em cima das trilhas, das praças e dos marcos.
f_decor = [d for d in f_decor if not (d["piece"].startswith(("Pl_", "Rock", "Dead_", "Oak_")) and (
    f_trail_dist(*d["position"]) < (3.4 if d["piece"].startswith("Oak_") else 2.6 if d["piece"].startswith(("Rock", "Dead_")) else 1.9)
    or any(math.hypot(d["position"][0] - cx, d["position"][1] - cz) < F_PLAZA_R + 1.5 for cx, cz in F_PLAZAS.values())
    or any(math.hypot(d["position"][0] - m["position"][0], d["position"][1] - m["position"][1]) < 2.2 for m in f_markers)))]
f_decor += f_plaza_decor + f_markers
ft = random.Random("forest_trails")
for line in f_trails:
    f_decor += [s for s in stone_trail(ft, line) if all(math.hypot(s["position"][0] - cx, s["position"][1] - cz) > F_PLAZA_R + 0.6 for cx, cz in F_PLAZAS.values())]
v_props = [
    {"id": "village_hunter", "kind": "npc", "npc": "village_hunter", "position": [-34.5, -19.0]},
    {"id": "village_wife", "kind": "npc", "npc": "village_wife", "position": [-30.2, -21.2]},
    {"id": "elf_archer", "kind": "npc", "npc": "elf_archer", "position": [-32.0, -16.6], "rotation": 200},
    {"id": "village_sign", "kind": "sign", "name_key": "PROP_VILLAGE_SIGN", "position": [-19.5, -14.6], "text_key": "PROP_VILLAGE_SIGN_TEXT"},
]
arenas["forest_01_path"] = {
    "_comment": "Floresta (04-tortuga-e-missoes.md, missão 3 na ordem do mapa: Tortuga -> Floresta -> Ruínas -> Cemitério -> Forte). Mapa de salas e trilhas no desenho de ~/Downloads/map-forest.jpg: a aldeia na partida (sudoeste) e uma rota principal (Praça da Pira, encruzilhada, Praça da Pedra) até o Covil do Leshy (chefe final, com a saída, no nordeste). As duas praças são as áreas de mini-chefe: o NPC de cada uma passa a missão e invoca um golem. Quatro caminhos sem saída terminam em salas de monstros (Clareira dos Sapos, Gruta dos Morcegos, Covil das Bestas, Toca dos Répteis); marcos de pedra nas portas e trilhas de lajes. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_FOREST", "player_class": "mage", "map_id": "map_forest", "area_level": 3, "outdoor": True,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": f_rooms_out, "encounters": f_enc + f_extra, "hazards": [],
    "entries": {"start": [F_START[0], -12.0], "forest": [F_START[0], -12.0]},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-26.5, -9.0], "to": "tortuga", "entry": "forest", "expedition_end": True},
        {"id": "to_ruins", "kind": "exit", "name_key": "PROP_TO_RUINS", "position": [47, -119.5], "to": "ruins_01_city", "entry": "start", "group": True},
        {"id": "forest_chest_1", "kind": "chest", "position": [-38, -57], "loot": "chest"},
        {"id": "forest_chest_2", "kind": "chest", "position": [28, -53], "loot": "chest"},
        {"id": "forest_chest_3", "kind": "chest", "position": [-9, -87], "loot": "chest"},
        {"id": "forest_chest_4", "kind": "chest", "position": [93, -12], "loot": "chest"},
        {"id": "forest_hermit", "kind": "npc", "npc": "forest_hermit", "position": list(F_PLAZAS["stone"]), "rotation": 0, "summon": f_summons["stone"]},
        {"id": "forest_pyre_keeper", "kind": "npc", "npc": "forest_pyre_keeper", "position": list(F_PLAZAS["fire"]), "rotation": 0, "summon": f_summons["fire"]},
    ] + v_props,
    "quest_spots": [], "breakables": f_deer,
    "style": {"_comment": "Floresta: sem piso do kit (chão de grama), cerca viva de arbustos nas bordas; o chão de fora das salas é quase preto (o vazio do desenho).", "walls": [""], "floor": "Ground_Grass", "low": "Pl_Bush",
              "ground": [0.02, 0.035, 0.02]},
    "decor": f_decor, "passive": True,
}

# --- Ruínas -------------------------------------------------------------------------------------------
rr = rng("ruins")
colliders = json.load(open("data/ruins_colliders.json"))["colliders"]
r_rooms = [
    room("approach", 0, 0, 56, 12, ["north"], wall_height=0.8),
    room("city", 0, -31, 56, 50, ["south", "north"], wall_height=0.8),
    room("vault", 0, -66, 30, 20, ["south"], wall_height=0.8),
]
r_enc = [
    {"id": "r_lizards_a", "position": [-14, -22], "monsters": [{"monster": "golden_rabbit", "count": 3}]},
    {"id": "r_goblins_a", "position": [14, -12], "monsters": [{"monster": "goblin", "count": 4}]},
    {"id": "r_scorp", "position": [12, -28], "monsters": [{"monster": "venom_scorpion", "count": 3}]},
    {"id": "r_bats", "position": [0, -42], "monsters": [{"monster": "plague_bat", "count": 4}]},
    {"id": "r_lizards_b", "position": [-18, -44], "monsters": [{"monster": "golden_rabbit", "count": 3}]},
    {"id": "r_goblins_b", "position": [-10, -62], "monsters": [{"monster": "goblin", "count": 5}]},
    {"id": "r_warden", "position": [0, -70], "monsters": [{"monster": "ruin_warden", "count": 1}]},
]
r_decor = [{"collider": c["size"], "position": [c["position"][0], round(c["position"][1] - 31, 2)]} for c in colliders]
r_decor.append({"piece": "Ruins_Layout", "position": [0, -31], "rotation": 0})
for rd in r_rooms:
    r_decor += scatter(rr, rd, ["Pl_Bush", "Pl_Hemp"], int(rd["size"][0] * rd["size"][1] / 90), margin=2.0)
r_decor += [{"piece": "Pr_BrokenPillar1", "position": [-8, -2], "solid": [1.2, 1.2]}, {"piece": "Pr_BrokenPillar2", "position": [9, -3], "solid": [1.2, 1.2]},
            {"piece": "Pr_Obelisk3", "position": [0, -72], "solid": [1.4, 1.4]}, {"piece": "Pr_Cross4", "position": [-10, -68], "solid": [1.2, 1.2]}]
# Caixotes e barris das ruínas: só soltam poções (loot.json "breakable_potion").
RUINS_BOXES = [{"id": "b%d" % (i + 1), "monster": m, "position": [x, y], "table": "breakable_potion"} for i, (x, y, m) in enumerate([
    (0, -10, "crate"), (8, -15, "barrel"), (-8, -11, "crate"), (-12, -22, "barrel"), (-22, -18, "crate"), (11, -29, "crate"),
    (-12, -33, "barrel"), (17, -40, "crate"), (-1, -42, "barrel"), (-19, -44, "crate"), (20, -52, "barrel"), (5, -55, "crate"),
    (-14, -56, "barrel"), (10, -60, "crate")])]
arenas["ruins_01_city"] = {
    "_comment": "Ruínas da cidade destruída na guerra (Destroyed Walls, LFA, CC BY 3.0): a cena de paredes inteira do pacote é o labirinto de ruas (Ruins_Layout, 1 unidade = 25 cm); a colisão vem dos recortes de cada parede (data/ruins_colliders.json). O guardião do cofre real espera no fundo. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_RUINS", "player_class": "mage", "map_id": "map_ruins", "area_level": 5, "outdoor": True,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": r_rooms, "encounters": r_enc, "hazards": [],
    "entries": {"start": [0, 3], "ruins": [0, 3]},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "forest", "expedition_end": True},
        {"id": "to_cemetery", "kind": "exit", "name_key": "PROP_TO_CEMETERY", "position": [0, -73], "to": "cemetery_01_yard", "entry": "start", "group": True},
        {"id": "ruins_spartan", "kind": "npc", "npc": "ruins_spartan", "position": [5, 0]},
        {"id": "ruins_chest_1", "kind": "chest", "position": [20, -50], "loot": "chest"},
        {"id": "ruins_chest_2", "kind": "chest", "position": [-22, -20], "loot": "chest"},
    ],
    "quest_spots": [], "breakables": RUINS_BOXES,
    "style": {"_comment": "Ruínas: sem muro de sala (a cena de paredes já fecha as ruas), chão de terra.", "walls": [""], "floor": "Ground_Dirt", "low": "",
              "ground": [0.2, 0.18, 0.14]},
    "decor": r_decor, "passive": True,
}

# --- Cemitério --------------------------------------------------------------------------------------
# Mapa de salas e corredores no desenho de calabouço da referência do autor (~/Downloads/map-cemitery.jpeg), cercado de vazio, com
# ~18 mil m2 (3x o da primeira versão) e sete áreas numeradas, uma por setor, cada uma com um só tipo de monstro:
#   1 Campo de Covas (entrada, sudeste: ratos) · 2 Terra dos Escorpiões (sala leste: escorpiões e a Praça das Pedras, com mini-chefe)
#   3 Ossuário (salão grande de pilares a noroeste: esqueletos) · 4 Cova dos Mortos (salão central em cruz e a sala do sul: zumbis)
#   5 Alameda da Estátua (sala grande a oeste: golens de pedra e a Praça da Estátua, com mini-chefe invocado)
#   6 Catacumbas (os corredores: morcegos) · 7 Covil do Troll (sala do topo: trolls e o Senhor da Cripta, no fundo, com a saída).
# Os corredores formam anéis (o corredor leste, o de cima e o salão central; o salão central, o do sul e o corredor leste), então há mais
# de um caminho. Uma trilha de pedras musgosas liga as portas; todas as salas têm grades pretas nas paredes, com abertura nas portas.
cr = rng("cemetery")

# id: (centro x, centro z, largura, altura, {lado: coordenada da porta}). Salas vizinhas no leste-oeste ficam a 1 m uma da outra e as do
# norte-sul se tocam (como no labirinto do Esgoto); cada lado tem no máximo uma porta, de 6 m.
CEM_ROOMS = {
    "gate": (0, 0, 14, 12, {"north": 0}),
    "r1": (0, -14, 26, 16, {"south": 0, "west": -14}),                                  # 1 Campo de Covas
    "e0": (-20, -11, 12, 30, {"north": -20, "east": -14, "west": 0}),                   # corredor leste, em trechos
    "e1": (-20, -38, 12, 24, {"north": -20, "south": -20, "west": -43}),
    "e2": (-20, -63, 12, 26, {"north": -20, "south": -20, "east": -57.5}),
    "e3": (-20, -89, 12, 26, {"north": -20, "south": -20, "east": -84}),
    "e4": (-20, -111, 12, 18, {"south": -20, "west": -114}),
    "r2": (5, -52, 36, 26, {"west": -57.5}),                                            # 2 Terra dos Escorpiões
    "alcove": (-2, -84, 22, 14, {"west": -84}),
    "ct": (-73, -114, 92, 12, {"east": -114, "west": -114, "north": -80, "south": -80}),  # corredor de cima
    "room3": (-163, -111, 86, 48, {"east": -114}),                                      # 3 Ossuário
    "cv": (-80, -136, 12, 32, {"south": -80, "north": -80}),
    "top": (-80, -166, 38, 28, {"south": -80}),                                         # 7 Covil do Troll
    "hn": (-80, -83.5, 12, 49, {"north": -80, "south": -80}),
    "hub": (-83, -43, 36, 32, {"north": -80, "east": -43, "west": -43, "south": -83}),  # 4 Cova dos Mortos (salão central em cruz)
    "he": (-45.5, -43, 37, 8, {"west": -43, "east": -43}),
    "hw": (-119, -43, 34, 8, {"west": -43, "east": -43}),
    "room5": (-166, -43, 58, 56, {"east": -43}),                                        # 5 Alameda da Estátua
    "hs": (-83, -16, 12, 22, {"north": -83, "south": -83}),
    "j": (-83, 0, 40, 10, {"north": -83, "south": -83, "west": 0, "east": 0}),
    "sw": (-111, 0, 14, 14, {"east": 0}),
    "se": (-55, 0, 14, 14, {"west": 0, "east": 0}),
    "je": (-37, 0, 20, 8, {"west": 0, "east": 0}),
    "bottom": (-83, 16, 40, 22, {"north": -83}),                                        # sala do sul (zumbis)
}
SECTOR_ROOMS = ("r1", "r2", "room3", "hub", "room5", "top", "bottom", "alcove", "sw", "se")     # salas com túmulos, jarros e ossos


def _door_list(cx, cz, doors):
    out = []
    for side, coord in doors.items():
        off = coord - (cx if side in ("north", "south") else cz)
        out.append(side if abs(off) < 1e-6 else "%s:%g" % (side, off))
    return out


def _rect(rid):
    cx, cz, w, h, _ = CEM_ROOMS[rid]
    return cx - w / 2, cx + w / 2, cz - h / 2, cz + h / 2


c_rooms = [room(rid, cx, cz, w, h, _door_list(cx, cz, doors), wall_height=0.8, **({"torch": True} if rid == "gate" else {}))
           for rid, (cx, cz, w, h, doors) in CEM_ROOMS.items()]
ROOM_DEF = {r["id"]: r for r in c_rooms}
# Pontos das portas no chão (x, z) e conferência: do outro lado da parede tem de haver uma sala com a porta no mesmo lugar.
DOOR_PTS = []
_OUT = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}
_FACE = {"north": "south", "south": "north", "west": "east", "east": "west"}
for _rid, (_cx, _cz, _w, _h, _doors) in CEM_ROOMS.items():
    _x0, _x1, _z0, _z1 = _rect(_rid)
    for _side, _coord in _doors.items():
        _pt = {"north": (_coord, _z0), "south": (_coord, _z1), "west": (_x0, _coord), "east": (_x1, _coord)}[_side]
        DOOR_PTS.append((_pt[0], _pt[1], _rid, _side))
        _probe = (_pt[0] + _OUT[_side][0] * 1.4, _pt[1] + _OUT[_side][1] * 1.4)
        _hits = [o for o in CEM_ROOMS if o != _rid and _rect(o)[0] <= _probe[0] <= _rect(o)[1] and _rect(o)[2] <= _probe[1] <= _rect(o)[3]]
        assert len(_hits) == 1 and CEM_ROOMS[_hits[0]][4].get(_FACE[_side]) == _coord, ("porta sem par", _rid, _side, _coord, _hits)


def in_rooms(x, z, margin=0.0, only=None):
    """O ponto está dentro de alguma sala (ou das `only`), a `margin` m das paredes."""
    for rid in (only or CEM_ROOMS):
        x0, x1, z0, z1 = _rect(rid)
        if x0 + margin <= x <= x1 - margin and z0 + margin <= z <= z1 - margin:
            return True
    return False


def near_door(x, z, r=6.0):
    return any(math.hypot(x - dx, z - dz) < r for dx, dz, _, _ in DOOR_PTS)


# --- Trilhas: pontos fixos nas portas e nos cruzamentos, com meandro suave no meio dos trechos longos ---------------
def meander(points, amp=1.6, wave=26.0, step=2.0, seed="m", taper=7.0):
    mr = random.Random(seed)
    phase = mr.uniform(0, math.tau)
    out, walked = [], 0.0
    for (x0, z0), (x1, z1) in zip(points, points[1:]):
        length = math.hypot(x1 - x0, z1 - z0)
        if length < 0.01:
            continue
        dx, dz = (x1 - x0) / length, (z1 - z0) / length
        n = max(int(length / step), 1)
        for i in range(n):
            t = i * length / n
            off = amp * min(1.0, min(t, length - t) / taper) * math.sin(math.tau * (walked + t) / wave + phase)
            out.append((round(x0 + dx * t - dz * off, 2), round(z0 + dz * t + dx * off, 2)))
        walked += length
    out.append(points[-1])
    return out


TRAIL_WAYPOINTS = {
    "spine": [(0, 2), (0, -9), (-5, -14), (-14, -14), (-20, -16), (-20, -30), (-20, -60), (-20, -90), (-20, -110), (-27, -114), (-60, -114),
              (-90, -114), (-119, -114), (-130, -113), (-163, -111), (-185, -104), (-195, -99)],     # do portão ao salão dos pilares
    "r2": [(-20, -57.5), (-14, -57.5), (-6, -57.5), (-3, -52), (5, -52), (14, -50), (19, -46)],                  # até a Praça das Pedras
    "alcove": [(-20, -84), (-14, -84), (-6, -84), (1, -84)],
    "he": [(-20, -43), (-27, -43), (-45, -43), (-64, -43), (-83, -43)],                             # corredor leste -> salão central
    "hn": [(-83, -43), (-80, -52), (-80, -70), (-80, -100), (-80, -114)],                           # salão central -> corredor de cima
    "hw": [(-83, -43), (-101, -43), (-119, -43), (-137, -43), (-150, -43), (-166, -43), (-182, -41), (-190, -38)],   # -> Praça da Estátua
    "hs": [(-83, -43), (-83, -27), (-83, -12), (-83, 0)],
    "j": [(-111, 0), (-104, 0), (-83, 0), (-62, 0), (-55, 0), (-47, 0), (-37, 0), (-27, 0), (-20, 0), (-20, -14)],  # laço do sul
    "jb": [(-83, 0), (-83, 5), (-83, 16)],
    "top": [(-80, -114), (-80, -130), (-80, -152), (-80, -160), (-80, -168)],                       # até o Covil do Troll
}
STRAIGHT = ("r2", "hw")      # perto das praças a trilha passa reta entre os arcos
trails = [meander(pts, amp=0.5 if name in STRAIGHT else 1.6, seed="trail_" + name) for name, pts in TRAIL_WAYPOINTS.items()]


def trail_dist(x, z):
    return min(seg_dist(x, z, a, b) for line in trails for a, b in zip(line, line[1:]))


# Praças de ruínas (mais abaixo): a das Pedras (sala 2) e a da Estátua (sala 5), a 170 m uma da outra, cada uma com um mini-chefe.
PLAZA_A = (5.0, -52.0)
PLAZA_B = (-166.0, -43.0)
er_enc = rng("cemetery_groups")
# Peças sólidas postas à mão mais abaixo (x, z, raio de folga): os grupos de monstros não nascem junto delas.
HALL_COLUMNS = [(x, z) for x in (-196, -174, -152, -130) for z in (-121, -101)]
KNIGHT_STATUES = [(-125, -121, 90), (-125, -107, 90), (-87, -157, 0), (-73, -157, 0)]
KNIGHT_TOMBS = [(-6.5, -17.5, 0), (6.5, -17.5, 180)]
TOP_DECOR = [(-90, -176, "Pr_Cross4"), (-70, -176, "Pr_Cross4"), (-96, -157, "Pr_BrokenPillar2"), (-64, -157, "Pr_BrokenPillar2")]
HAND_SOLIDS = ([(x, z, 3.5) for x, z in HALL_COLUMNS] + [(-185, -129, 5.5), (-141, -93, 5.5)] + [(x, z, 3.0) for x, z, _ in KNIGHT_STATUES]
               + [(x, z, 3.5) for x, z, _ in KNIGHT_TOMBS] + [(x, z, 3.0) for x, z, _ in TOP_DECOR])
c_enc = []
group_pts = []          # posições dos grupos já postos (afastar os próximos)


def put_groups(tag, kind, counts, rid, inset=4.0, min_sep=12.0, tries=300, avoid=()):
    avoid = tuple(avoid) + tuple(HAND_SOLIDS)
    """Um grupo de `kind` para cada número de `counts`, em pontos sorteados da sala: longe das paredes, das portas, das praças, da
    trilha (pelo menos 2,5 m) e dos outros grupos."""
    x0, x1, z0, z1 = _rect(rid)
    for i, count in enumerate(counts):
        for _ in range(tries):
            x, z = er_enc.uniform(x0 + inset, x1 - inset), er_enc.uniform(z0 + inset, z1 - inset)
            if (trail_dist(x, z) > 2.5 and not near_door(x, z, 7.0)
                    and all(math.hypot(x - px, z - pz) > min_sep for px, pz in group_pts)
                    and all(math.hypot(x - px, z - pz) > 14.0 for px, pz in (PLAZA_A, PLAZA_B))
                    and all(math.hypot(x - ax, z - az) > ar for ax, az, ar in avoid)):
                group_pts.append((x, z))
                c_enc.append({"id": "c_%s_%d" % (tag, len(c_enc) + 1), "position": [round(x, 1), round(z, 1)], "monsters": [{"monster": kind, "count": count}]})
                break


# Um monstro por setor (nome em pt-BR no locale): 1 ratos de esgoto, 2 escorpiões, 3 esqueletos, 4 zumbis, 5 golens de pedra, 6 morcegos, 7 trolls.
put_groups("s1", "plague_frog", (3, 3), "r1", inset=3.5, avoid=((0, 3, 14),))      # ratos de esgoto (os "ratos pestilentos" agora são sapos)
put_groups("s2", "venom_scorpion", (3, 4, 3), "r2", inset=4.0, min_sep=10.0)
put_groups("s3", "skeleton", (3, 4, 3, 4, 3, 4), "room3", inset=5.0, min_sep=15.0, avoid=((-163, -111, 8),))
put_groups("s4", "zombie", (3, 4, 3, 4), "hub", inset=5.0, min_sep=11.0)
put_groups("s4", "zombie", (3,), "bottom", inset=5.0)
put_groups("s5", "golem_stone", (2, 2, 2), "room5", inset=6.0, min_sep=16.0)
BAT_SPOTS = [(-20, -38), (-20, -63), (-20, -89), (-45, -114), (-73, -114), (-100, -114), (-80, -136), (-80, -85), (-119, -43)]   # corredores
for i, (bx, bz) in enumerate(BAT_SPOTS):
    group_pts.append((bx, bz))
    c_enc.append({"id": "c_s6_%d" % (len(c_enc) + 1), "position": [bx, bz], "monsters": [{"monster": "plague_bat", "count": 4 + i % 2}]})
put_groups("s7", "troll", (1, 1, 1), "top", inset=5.0, min_sep=9.0, avoid=((-80, -170, 9),))
c_enc.append({"id": "c_plaza_a", "position": [PLAZA_A[0], PLAZA_A[1] + 4.2], "spread": 2.6,    # Praça das Pedras: só o mini-chefe
              "monsters": [{"monster": "crypt_scorpion", "count": 1}]})
c_enc.append({"id": "c_boss", "position": [-80, -170], "monsters": [{"monster": "crypt_lord", "count": 1}]})
c_props = [
    {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "forest", "expedition_end": True},
    {"id": "to_fort", "kind": "exit", "name_key": "PROP_TO_DARK_FOREST", "position": [-80, -177], "to": "dark_forest_01_woods", "entry": "start", "group": True},
]

c_decor = []
# Cada peça colocada à mão entra aqui (x, z, raio) para as lápides sorteadas e os arbustos não ficarem em cima.
blockers = [(p["position"][0], p["position"][1], 3.0) for p in c_props] + [(e["position"][0], e["position"][1], 3.2) for e in c_enc]


def put(entry, radius):
    c_decor.append(entry)
    blockers.append((entry["position"][0], entry["position"][1], radius))


put({"piece": "Pr_LampPost", "position": [-3, 3], "solid": [0.6, 0.6]}, 1.0)
put({"piece": "Pr_LampPost", "position": [4, -3], "solid": [0.6, 0.6]}, 1.0)
# Grades pretas de ferro (Fence_Iron, original do jogo; build_iron_fence.py) em todas as paredes das salas e dos corredores, com uma
# abertura de 6 m em cada porta (a área inteira fica cercada); e, ao lado de cada porta de sala dos setores, um par de marcos de pedra
# (obelisco, cruz, pilar, e de novo).
BORDER_MARKS = (("Pr_Obelisk3", "Pr_Obelisk2"), ("Pr_Cross4", "Pr_Cross4"), ("Pr_BrokenPillar2", "Pr_BrokenPillar2"))
mark_n = 0
for rid in CEM_ROOMS:                 # todas as salas e corredores: a área toda fica cercada
    x0, x1, z0, z1 = _rect(rid)
    doors_here = [(dx, dz, side) for dx, dz, r_, side in DOOR_PTS if r_ == rid]
    walls = (("north", x0 + 1.0, x1 - 1.0, z0 + 0.9, 0, True), ("south", x0 + 1.0, x1 - 1.0, z1 - 0.9, 0, True),
             ("west", z0 + 1.0, z1 - 1.0, x0 + 0.9, 90, False), ("east", z0 + 1.0, z1 - 1.0, x1 - 0.9, 90, False))
    for side, a, b, fixed, rot, along_x in walls:
        if rid == "gate" and side == "west":      # ali fica o portal de volta a Tortuga
            continue
        door = next(((dx if along_x else dz) for dx, dz, s_ in doors_here if s_ == side), None)
        t = a + 1.0
        while t <= b:
            if door is None or abs(t - door) > 4.0:
                c_decor.append({"piece": "Fence_Iron", "position": [round(t, 1), fixed] if along_x else [fixed, round(t, 1)], "rotation": rot})
            t += 2.0
    for dx, dz, side in (doors_here if rid in SECTOR_ROOMS else []):      # os marcos só nas portas das salas dos setores
        left, right = BORDER_MARKS[mark_n % 3]
        mark_n += 1
        inward = {"north": (0, 1), "south": (0, -1), "west": (1, 0), "east": (-1, 0)}[side]
        tangent = (1, 0) if side in ("north", "south") else (0, 1)
        for sign, piece in ((-1, left), (1, right)):
            put({"piece": piece, "position": [round(dx + inward[0] * 2.4 + tangent[0] * sign * 4.8, 1), round(dz + inward[1] * 2.4 + tangent[1] * sign * 4.8, 1)],
                 "solid": [1.4, 1.4]}, 2.4)

# Duas praças de ruínas (3D Fantasy Ruins Pack, Ron Kapaun, CC0; build_ruins.sh), cada uma com um mini-chefe:
#   Praça das Pedras (sala 2): o círculo de pedras em pé (Ruin_Stones); o mini-chefe (Escorpião da Cripta) já está lá, dormindo.
#   Praça da Estátua (sala 5): o coreto em ruínas (Ruin_Temple2) com a estátua do poste de luz (Statue_Lamp, Colorado Stark, CC0) no meio;
#   falar com a estátua desperta o Guardião do Túmulo (mini-chefe), 4 s depois.
# Cada praça tem piso de lajes, colunas em volta e um arco de cada lado, no eixo da trilha (leste-oeste).
PLAZA_R = 6.5
plazas = []


def plaza(cx, cz, centerpiece):
    plazas.append((cx, cz, PLAZA_R))
    blockers.append((cx, cz, PLAZA_R + 3.0))
    pr = random.Random("plaza_%d_%d" % (cx, cz))
    for gx in range(-8, 9, 2):
        for gz in range(-8, 9, 2):
            if math.hypot(gx, gz) < PLAZA_R + 0.8:
                c_decor.append({"piece": "Floor_UnevenBrick", "position": [cx + gx, cz + gz], "rotation": pr.choice((0, 90, 180, 270)), "y": 0.03})
    for k in range(10):                                        # colunas em volta, longe da trilha e dos arcos
        a = math.tau * (k + 0.5) / 10
        x, z = cx + (PLAZA_R + 1.0) * math.cos(a), cz + (PLAZA_R + 1.0) * math.sin(a)
        if abs(math.cos(a)) > 0.85 or trail_dist(x, z) < 1.8:
            continue
        put({"piece": "Ruin_Column" if k % 3 else "Ruin_Pillar", "position": [round(x, 1), round(z, 1)],
             "rotation": pr.randrange(0, 360, 15), "solid": [0.8, 0.8]}, 1.2)
    for dx in (-(PLAZA_R + 2.4), PLAZA_R + 2.4):               # um arco de cada lado, virado para a trilha leste-oeste
        x = cx + dx
        c_decor.append({"piece": "Ruin_Arch", "position": [round(x, 1), cz], "rotation": 90})
        for lz in (-3.07, 3.07):                               # só os pés do arco bloqueiam
            put({"collider": [1.1, 1.1], "position": [round(x + 0.34, 2), round(cz + lz, 2)]}, 1.6)
    centerpiece()


def stones_center():
    c_decor.append({"piece": "Ruin_Stones", "position": list(PLAZA_A)})
    put({"collider": [8.0, 3.6], "position": [PLAZA_A[0], PLAZA_A[1] - 1.46]}, 1.0)    # o arco de pedras em pé, no fundo


def statue_center():
    cx, cz = PLAZA_B
    c_decor.append({"piece": "Ruin_Temple2", "position": [cx, cz]})
    for dx, dz in ((0, -3.77), (0, 3.79), (-3.73, 0), (3.73, 0)):          # as quatro colunas do coreto
        put({"collider": [1.1, 1.1], "position": [round(cx + dx, 2), round(cz + dz, 2)]}, 1.0)
    put({"collider": [1.3, 1.3], "position": [cx, cz]}, 1.2)                # a estátua
    c_decor.append({"light": [1.0, 0.82, 0.5], "position": [cx + 0.6, cz + 0.4], "y": 3.2, "range": 11.0, "energy": 1.4})
    c_props.append({"id": "lamp_statue", "kind": "npc", "npc": "lightpost_statue", "kit": "Statue_Lamp", "rotation": 0,
                    "position": [cx, cz],
                    "summon": {"id": "c_plaza_b", "position": [cx, cz + 7.5], "spread": 3.0,
                               "monsters": [{"monster": "tomb_guardian", "count": 1}]}})


plaza(PLAZA_A[0], PLAZA_A[1], stones_center)
plaza(PLAZA_B[0], PLAZA_B[1], statue_center)
# Salão dos pilares (sala 3): duas fileiras de quatro colunas e dois muros em ruínas, como na referência.
for x, z in HALL_COLUMNS:
    put({"piece": "Ruin_Column", "position": [x, z], "solid": [0.8, 0.8]}, 1.6)
put({"piece": "Ruin_Wall", "position": [-185, -129], "solid": [5.8, 0.6]}, 3.5)
put({"piece": "Ruin_Wall", "position": [-141, -93], "solid": [5.8, 0.6]}, 3.5)
# Estátuas do cavaleiro (Knight Statue, yd, CC0; build_knight_statue.py): um par na entrada do salão dos pilares (viradas para a porta)
# e um na entrada do Covil do Troll (viradas para o corredor); a peça olha para +Z.
for x, z, rot in KNIGHT_STATUES:
    put({"piece": "Statue_Knight", "position": [x, z], "rotation": rot, "solid": [1.1, 1.2]}, 2.0)
# Túmulos do cavaleiro deitado (Knight Lying, yd, CC0): dois na entrada, com os degraus (lado +X da peça) voltados para o meio.
for x, z, rot in KNIGHT_TOMBS:
    put({"piece": "Statue_Knight_Lying", "position": [x, z], "rotation": rot, "solid": [1.9, 1.9]}, 2.6)
# No fundo do Covil do Troll, em volta do Senhor da Cripta: cruzes e pilares quebrados.
for x, z, piece in TOP_DECOR:
    put({"piece": piece, "position": [x, z], "solid": [1.2, 1.2]}, 2.0)

# Fileiras de túmulos (cruzes e lápides) nas salas dos setores, deixando de fora portas, trilhas, praças e peças postas à mão.
for rid in SECTOR_ROOMS:
    x0, x1, z0, z1 = _rect(rid)
    gz = z0 + 3.0
    while gz < z1 - 2.5:
        gx = x0 + 3.0
        while gx < x1 - 2.5:
            x, z = gx + cr.uniform(-0.6, 0.6), gz + cr.uniform(-0.5, 0.5)
            if not (cr.random() < 0.18 or near_door(x, z, 6.0) or trail_dist(x, z) < 2.6 or any(math.hypot(x - bx, z - bz) < br for bx, bz, br in blockers)):
                c_decor.append({"piece": cr.choice(["Pr_Tombstone1", "Pr_Tombstone2", "Pr_Tombstone3", "Pr_Cross1", "Pr_Cross2", "Pr_Cross3"]),
                                "position": [round(x, 1), round(z, 1)], "rotation": cr.choice([0, 0, 10, -10, 180, 190]), "solid": [0.8, 0.5]})
            gx += 5.0
        gz += 5.0


# Trilha com o solo e as pedras do Mossy Rock Environment Pack (rubberduck, CC0; build_mossy_trail.py): um leito de manchas de terra
# e musgo e lajes de pedra musgosa achatadas por cima (as pedras das margens vêm mais abaixo). A Floresta continua com o stone_trail comum.
SLAB_SCALE = {1: (0.8, 1.1), 2: (0.65, 0.9), 3: (0.8, 1.1), 4: (0.45, 0.62), 5: (0.55, 0.75)}


def mossy_slabs(rng_, points, step=1.0, spread=0.5):
    """Lajes da trilha: as cinco pedras achatadas (Mossy_Slab_1..5) em duas fileiras tortas ao longo da linha `points`, cada
    uma girada ao acaso e a uma altura um pouco diferente (as que se sobrepõem não brigam no chão)."""
    out = []
    n = 0
    for (x0, z0), (x1, z1) in zip(points, points[1:]):
        length = math.hypot(x1 - x0, z1 - z0)
        if length < 0.01:
            continue
        dx, dz = (x1 - x0) / length, (z1 - z0) / length
        for i in range(max(int(length / step), 1)):
            t = (i + 0.5) * step
            for lane in (-1, 1):
                off = lane * spread * 0.6 + rng_.uniform(-0.15, 0.15)
                along = t + rng_.uniform(-0.2, 0.2) + (step / 2 if lane > 0 else 0)
                kind = rng_.randint(1, 5)
                out.append({"piece": "Mossy_Slab_%d" % kind, "rotation": rng_.randrange(0, 360, 15),
                            "position": [round(x0 + dx * along - dz * off, 2), round(z0 + dz * along + dx * off, 2)],
                            "scale": round(rng_.uniform(*SLAB_SCALE[kind]), 2), "y": round(-0.04 + 0.01 * (n % 6), 3)})
                n += 1
    return out


def trail_bed(rng_, points, step=1.5):
    """Leito da trilha: manchas de solo do pacote (Trail_Dirt: terra seca com pedrinhas; Trail_Moss: chão musgoso), de borda
    irregular e transparente, sobrepostas ao longo da linha, por baixo das lajes."""
    out = []
    n = 0
    for (x0, z0), (x1, z1) in zip(points, points[1:]):
        length = math.hypot(x1 - x0, z1 - z0)
        if length < 0.01:
            continue
        dx, dz = (x1 - x0) / length, (z1 - z0) / length
        for i in range(max(int(length / step), 1)):
            t = (i + 0.5) * step
            off = rng_.uniform(-0.3, 0.3)
            out.append({"piece": "Trail_Dirt" if rng_.random() < 0.65 else "Trail_Moss", "rotation": rng_.randrange(0, 360, 15),
                        "position": [round(x0 + dx * t - dz * off, 2), round(z0 + dz * t + dx * off, 2)],
                        "scale": round(rng_.uniform(0.85, 1.2), 2), "y": round(0.012 + 0.002 * (n % 5), 3)})
            n += 1
    return out


# Sorteio próprio para as lajes (não mexe nos túmulos).
tr = random.Random("cemetery_trails")
# A trilha atravessa as praças: nada de laje ou leito dentro dos colisores nem sob as plataformas das ruínas.
plaza_colliders = [(q["position"][0], q["position"][1], q["collider"][0] / 2 + 0.7, q["collider"][1] / 2 + 0.7) for q in c_decor if q.get("collider")]
plaza_platforms = [(PLAZA_A[0], PLAZA_A[1], 4.6), (PLAZA_B[0], PLAZA_B[1], 5.8)]


def trail_piece_ok(piece):
    x, z = piece["position"]
    return (all(abs(x - cx) > hw or abs(z - cz) > hd for cx, cz, hw, hd in plaza_colliders)
            and all(math.hypot(x - px, z - pz) > pr for px, pz, pr in plaza_platforms)
            and (in_rooms(x, z, 0.6) or near_door(x, z, 3.4)))      # (o vão de 1 m entre salas, na porta, também vale)


for line in trails:
    c_decor += [q for q in trail_bed(tr, line) if trail_piece_ok(q)]
for line in trails:
    c_decor += [q for q in mossy_slabs(tr, line) if trail_piece_ok(q)]

for rid in SECTOR_ROOMS:
    area = CEM_ROOMS[rid][2] * CEM_ROOMS[rid][3]
    for bush in scatter(cr, ROOM_DEF[rid], ["Pl_Hemp", "Pl_Bush"], int(area / 28), margin=2.5):
        x, z = bush["position"]
        if trail_dist(x, z) > 2.2 and not near_door(x, z, 5.0) and not any(math.hypot(x - bx, z - bz) < br for bx, bz, br in blockers):
            c_decor.append(bush)

# Jarros e garrafas brancos quebráveis, em grupos de quatro ou cinco: metade solta poção de vida e metade de mana
# (tabelas "breakable_hp" e "breakable_mana", sorteadas dentro do grupo). Cada jarro vai para um ponto livre de sólidos,
# de portas, de trilhas, de grupos de monstros, de baús e de praças, e a pelo menos 0,9 m dos outros.
jr = random.Random("cemetery_jars")
jar_solids = [(d["position"][0], d["position"][1], max(d["solid"]) / 2 + 0.9) for d in c_decor if d.get("solid")]
c_jars = []


def jar_ok(x, z):
    return (in_rooms(x, z, 1.8, SECTOR_ROOMS) and not near_door(x, z, 5.5) and trail_dist(x, z) > 1.9
            and all(math.hypot(x - sx, z - sz) > sr for sx, sz, sr in jar_solids)
            and all(math.hypot(x - e["position"][0], z - e["position"][1]) > 3.0 for e in c_enc)
            and all(math.hypot(x - q["position"][0], z - q["position"][1]) > 3.0 for q in c_props)
            and all(math.hypot(x - px, z - pz) > pr + 1.5 for px, pz, pr in plazas)
            and all(math.hypot(x - j["position"][0], z - j["position"][1]) > 0.9 for j in c_jars))


def jar_cluster(cx, cz, count, spread=1.8):
    spots = []
    for _ in range(count):
        for _try in range(80):
            a = jr.uniform(0, math.tau)
            r = spread * math.sqrt(jr.random())
            x, z = cx + r * math.cos(a), cz + r * math.sin(a)
            if jar_ok(x, z) and all(math.hypot(x - px, z - pz) > 0.9 for px, pz in spots):
                spots.append((x, z))
                break
    tables = ["breakable_hp", "breakable_mana"] * 3
    jr.shuffle(tables)
    for (x, z), table in zip(spots, tables):
        c_jars.append({"id": "j%d" % (len(c_jars) + 1), "monster": "mug", "position": [round(x, 1), round(z, 1)], "table": table})


for cx, cz, count in ((-6, -80, 4), (-109, 3, 4), (-53, -3, 4), (-75, 20, 5), (-92, 12, 4), (-5, -45, 4), (19, -60, 4),
                      (-190, -92, 5), (-140, -128, 4), (-185, -62, 5), (-150, -25, 4), (-92, -172, 4), (-95, -30, 4), (-8, -17, 4)):
    jar_cluster(cx, cz, count)

# Pedras das margens da trilha: as formações rochosas do pacote (Mossy_Formation_1..4), uma a cada 4 a 5 m, num lado ou no
# outro, fora das lajes e de qualquer coisa sólida, jarro, grupo de monstros ou baú.
er = random.Random("cemetery_edge_rocks")
edge_solids = [(d["position"][0], d["position"][1], max(d["solid"]) / 2 + 0.9) for d in c_decor if d.get("solid")]
edge_solids += [(j["position"][0], j["position"][1], 1.3) for j in c_jars]
edge_solids += [(px, pz, pr + 1.2) for px, pz, pr in plazas]
edge_solids += [(e["position"][0], e["position"][1], 2.0) for e in c_enc] + [(q["position"][0], q["position"][1], 3.0) for q in c_props]
edge_rocks = []
for line in trails:
    for (x0, z0), (x1, z1) in zip(line, line[1:]):
        length = math.hypot(x1 - x0, z1 - z0)
        if length < 0.01:
            continue
        dx, dz = (x1 - x0) / length, (z1 - z0) / length
        t = er.uniform(0.5, 2.0)
        while t < length:
            side = er.choice((-1, 1)) * er.uniform(1.9, 2.5)
            x, z = x0 + dx * t - dz * side, z0 + dz * t + dx * side
            if (in_rooms(x, z, 1.6) and trail_dist(x, z) > 1.7 and not near_door(x, z, 4.5)
                    and all(math.hypot(x - sx, z - sz) > sr for sx, sz, sr in edge_solids)
                    and all(math.hypot(x - r["position"][0], z - r["position"][1]) > 1.8 for r in edge_rocks)):
                edge_rocks.append({"piece": "Mossy_Formation_%d" % er.randint(1, 4), "position": [round(x, 2), round(z, 2)],
                                   "rotation": er.randrange(0, 360, 15), "scale": round(er.uniform(0.5, 0.9), 2), "y": -0.05})
            t += er.uniform(4.0, 5.5)
c_decor += edge_rocks

# Ossos e crânios espalhados (3D Dungeon Debris - Skull and Bones, Paul Wortmann, CC0; build_bone_debris.py): poucos e soltos na entrada,
# mais e maiores a cada setor, e muitos no covil do troll. Baixos, sem colisão, fora da trilha, de portas, de sólidos, jarros, grupos de
# monstros, praças e pedras das margens.
BONES_SMALL = ["Dungeon_Skull_1", "Dungeon_Skull_2", "Dungeon_Bone"]
BONES_MID = ["Dungeon_CrossBones", "Dungeon_BonePile_1", "Dungeon_Arm", "Dungeon_Leg", "Dungeon_Ribcage", "Dungeon_Pelvis", "Dungeon_Spine"]
BONES_BIG = ["Dungeon_SkullPile", "Dungeon_BonePile_2", "Dungeon_BonePile_3", "Dungeon_BonePile_4", "Dungeon_BonePile_5", "Dungeon_BonePile_6"]
# (sala, quantos, pesos pequeno / médio / grande)
BONE_AREAS = [("r1", 6, (0.8, 0.2, 0.0)), ("r2", 10, (0.5, 0.4, 0.1)), ("room3", 40, (0.3, 0.5, 0.2)), ("hub", 14, (0.3, 0.45, 0.25)),
              ("room5", 32, (0.2, 0.4, 0.4)), ("top", 16, (0.15, 0.35, 0.5)), ("bottom", 12, (0.3, 0.4, 0.3)), ("alcove", 5, (0.5, 0.4, 0.1)),
              ("sw", 4, (0.5, 0.4, 0.1)), ("se", 4, (0.5, 0.4, 0.1))]
bn = random.Random("cemetery_bones")
bones = []
for rid, count, weights in BONE_AREAS:
    x0, x1, z0, z1 = _rect(rid)
    placed = 0
    for _try in range(count * 60):
        if placed >= count:
            break
        x, z = bn.uniform(x0 + 2.0, x1 - 2.0), bn.uniform(z0 + 2.0, z1 - 2.0)
        group = bn.choices((BONES_SMALL, BONES_MID, BONES_BIG), weights)[0]
        if (trail_dist(x, z) > 1.5 and not near_door(x, z, 4.5)
                and all(math.hypot(x - sx, z - sz) > sr for sx, sz, sr in edge_solids)
                and all(math.hypot(x - r["position"][0], z - r["position"][1]) > 1.4 for r in edge_rocks)
                and all(math.hypot(x - b["position"][0], z - b["position"][1]) > 2.2 for b in bones)):
            bones.append({"piece": bn.choice(group), "position": [round(x, 2), round(z, 2)], "rotation": bn.randrange(0, 360, 15),
                          "scale": round(bn.uniform(0.8, 1.25), 2), "y": -0.02})
            placed += 1
c_decor += bones

# Terra por fora: o vazio em volta das salas e entre elas (sem acesso: as paredes e as grades fecham tudo) vira chão de terra, o mesmo
# Ground_Grave das salas, em peças de 6 m, até 36 m das paredes (o resto some no escuro).
DIRT_SIZE = 6.0
_all = [_rect(r_) for r_ in CEM_ROOMS]
_gx0, _gx1 = min(r_[0] for r_ in _all) - 40, max(r_[1] for r_ in _all) + 40
_gz0, _gz1 = min(r_[2] for r_ in _all) - 40, max(r_[3] for r_ in _all) + 40
dr = random.Random("cemetery_dirt")


def rect_dist(x, z):
    """Distância do ponto à sala mais próxima (0 se está dentro de alguma)."""
    return min(math.hypot(max(rx0 - x, 0.0, x - rx1), max(rz0 - z, 0.0, z - rz1)) for rx0, rx1, rz0, rz1 in _all)


outside_dirt = []
gx = math.floor(_gx0 / DIRT_SIZE) * DIRT_SIZE
while gx < _gx1:
    gz = math.floor(_gz0 / DIRT_SIZE) * DIRT_SIZE
    while gz < _gz1:
        cx_, cz_ = gx + DIRT_SIZE / 2, gz + DIRT_SIZE / 2
        if 4.0 <= rect_dist(cx_, cz_) <= 36.0:
            outside_dirt.append({"piece": "Ground_Grave", "position": [cx_, cz_], "scale": DIRT_SIZE / 2.0, "y": 0.0})      # sem girar: o ruído da textura só emenda na mesma direção
        gz += DIRT_SIZE
    gx += DIRT_SIZE
c_decor += outside_dirt

# Ratinhos de cenário (só enfeite, não são monstros: não atacam nem têm vida): o papel "rat" do crowd, o mesmo ratinho do Esgoto e do
# Forte. Cada um vai e volta entre dois pontos da mesma sala ou corredor, num trajeto reto livre de peças sólidas, um para cada ~300 m2
# das salas dos setores e ~220 m2 dos corredores, longe do ponto onde o herói começa.
rtr = random.Random("cemetery_rats")
rat_solids = [(d["position"][0], d["position"][1], max(sz_) / 2 + 0.9) for d in c_decor for sz_ in [d.get("solid") or d.get("collider")] if sz_]
c_rats = []
for rid, (rcx, rcz, rw, rh, _doors) in CEM_ROOMS.items():
    if rid == "gate":
        continue
    x0, x1, z0, z1 = _rect(rid)
    want = round(rw * rh / (300.0 if rid in SECTOR_ROOMS else 220.0))
    for _ in range(want):
        for _try in range(60):
            ax, az = rtr.uniform(x0 + 2.2, x1 - 2.2), rtr.uniform(z0 + 2.2, z1 - 2.2)
            ang, dist = rtr.uniform(0, math.tau), rtr.uniform(5.0, 12.0)
            bx, bz = ax + dist * math.cos(ang), az + dist * math.sin(ang)
            if not (x0 + 2.0 <= bx <= x1 - 2.0 and z0 + 2.0 <= bz <= z1 - 2.0) or math.hypot(ax, az - 3) < 8:
                continue
            steps = max(int(math.hypot(bx - ax, bz - az) / 0.8), 1)
            if any(math.hypot(ax + (bx - ax) * t / steps - sx, az + (bz - az) * t / steps - sz) < sr for t in range(steps + 1) for sx, sz, sr in rat_solids):
                continue
            c_rats.append({"role": "rat", "position": [round(ax, 2), round(az, 2)], "path": [round(bx, 2), round(bz, 2)],
                           "speed": round(rtr.uniform(0.6, 1.6), 1), "pose": "walk"})
            break
arenas["cemetery_01_yard"] = {
    "_comment": "Cemitério (Medieval Props Textured, Clint Bellanger, CC BY 3.0, modelos de Lamoot): mapa de salas e corredores no desenho de calabouço da referência do autor, cercado de vazio, com sete setores de um monstro cada (1 Campo de Covas, 2 Terra dos Escorpiões, 3 Ossuário, 4 Cova dos Mortos, 5 Alameda da Estátua, 6 Catacumbas, 7 Covil do Troll), duas praças de ruínas com mini-chefe a 170 m uma da outra, corredores em anéis e uma rede de trilhas de lajes musgosas, grades pretas nas salas, jarros que soltam poção, ossos e a cripta do Senhor da Cripta no fundo. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_CEMETERY", "player_class": "mage", "map_id": "map_cemetery", "area_level": 7, "outdoor": True,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": c_rooms, "encounters": c_enc, "hazards": [],
    "entries": {"start": [0, 3], "cemetery": [0, 3]},
    "props": c_props,
    "quest_spots": [], "breakables": c_jars,
    "style": {"_comment": "Cemitério: as salas têm chão de pedra (Floor_Slate, a lajota do piso do Forte em 2 x 2 m, feita por build_floor_slate.py, escurecida pelo tint); o vazio em volta é terra (Ground_Grave, de build_ground.py) em peças de decor; sem cercas de madeira.", "walls": [""], "floor": "Floor_Slate", "low": "", "tint": [0.68, 0.68, 0.72],
              "ground": [0.09, 0.085, 0.08]},
    "decor": c_decor, "crowd": c_rats, "passive": True,
}

# --- Floresta Escura (entre o Cemitério e o Forte) -----------------------------------------------------
dr = rng("dark_forest")
d_rooms = [
    room("edge", 0, 0, 22, 12, ["north"], wall_height=0.8, torch=True),
    room("thicket", 0, -22, 40, 32, ["south", "north", "west"], wall_height=0.8),
    room("hollow", -26, -22, 12, 20, ["east"], wall_height=0.8),
    room("roots", 0, -52, 30, 28, ["south", "north"], wall_height=0.8),
    room("elder", 0, -82, 36, 32, ["south"], wall_height=0.8),
]
d_enc = []  # por enquanto só o mapa: sem monstros, chefe nem baús
d_decor = []
for rd in d_rooms:
    d_decor += ring(dr, rd, ["Pl_Bamboo", "Pl_Bamboo", "Pl_Bamboo", "Pl_Swirl"], 1.8, scale=(1.1, 1.8))
    d_decor += scatter(dr, rd, ["Pl_Bush", "Pl_Swirl", "Pl_Hemp", "Pl_Bamboo"], int(rd["size"][0] * rd["size"][1] / 14), margin=2.0, avoid=[(0, 3, 3)])
# Entrada do Forte (Medieval Gatehouse, Daniel Andersson, CC0): o portão de ~20 x 12,6 m fecha o fundo do bosque (frente para +Z, a grade
# voltada para quem chega) e o portal para o Forte fica à frente dele; os obeliscos o ladeiam. Nada sorteado dentro do portão ou no portal.
D_GATE, D_PORTAL = (0, -92), (0, -82.5)
d_decor = [d for d in d_decor if not (abs(d["position"][0] - D_GATE[0]) < 11.8 and abs(d["position"][1] - D_GATE[1]) < 7.5
                                      or math.hypot(d["position"][0] - D_PORTAL[0], d["position"][1] - D_PORTAL[1]) < 3.5)]
d_decor += [{"piece": "Gatehouse", "position": list(D_GATE), "solid": [20.0, 11.5]},
            {"piece": "Pr_Obelisk2", "position": [-5, -80], "solid": [1.0, 1.0]}, {"piece": "Pr_Obelisk2", "position": [5, -80], "solid": [1.0, 1.0]},
            {"piece": "Pr_Cross3", "position": [-26, -26], "solid": [1.0, 1.0]},
            {"piece": "Pr_Cross2", "position": [-24, -18], "solid": [1.0, 1.0]}, {"piece": "Pr_BrokenPillar1", "position": [-10, -60], "solid": [1.2, 1.2]},
            {"piece": "Pr_BrokenPillar2", "position": [10, -46], "solid": [1.2, 1.2]}, {"piece": "Pr_LampPost", "position": [-4, 3], "solid": [0.6, 0.6]}]
arenas["dark_forest_01_woods"] = {
    "_comment": "Floresta Escura (entre o Cemitério e o Forte): a mesma vegetação da Floresta (Stylish Plants), mas mais densa, mais escura e com cruzes esquecidas; uma clareira lateral e o bosque do fundo, por enquanto vazios: só o mapa, sem monstros, chefe nem baús. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_DARK_FOREST", "player_class": "mage", "map_id": "map_dark_forest", "area_level": 8, "outdoor": True,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": d_rooms, "encounters": d_enc, "hazards": [],
    "entries": {"start": [0, 3], "dark_forest": [0, 3]},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "forest", "expedition_end": True},
        {"id": "to_fort", "kind": "exit", "name_key": "PROP_TO_FORT", "position": list(D_PORTAL), "to": "fort_01_gate", "entry": "start", "group": True},
    ],
    "quest_spots": [], "breakables": [],
    "style": {"_comment": "Floresta Escura: grama escura, cerca viva densa, tom azulado.", "walls": [""], "floor": "Ground_Grass", "low": "Pl_Bush",
              "ground": [0.05, 0.1, 0.06], "tint": [0.45, 0.55, 0.6]},
    "decor": d_decor, "passive": True,
}

# --- Mina de Cristais (Lowpoly Crystals Pack, iPoly3D, CC0 + todas as pedras do jogo) -------------------
mr = rng("mine")
ROCKS = ["Rock_1", "Rock_2", "Rock_3", "Rock_4", "Rock_5", "RockP_1", "RockP_2", "RockP_3", "RockP_4", "RockP_5", "RockP_6"]
BLUE, PURPLE = (0.3, 0.6, 1.0), (0.7, 0.4, 1.0)
m_rooms = [
    room("entry", 0, 0, 20, 12, ["north"], wall_height=2.0, torch=True),
    room("shaft", 0, -22, 26, 28, ["south", "north", "east"], wall_height=2.0),
    room("vein", 24, -22, 16, 16, ["west"], wall_height=2.0),
    room("hall", 0, -52, 36, 30, ["south", "north", "west"], wall_height=2.0),
    room("cart_cave", -27, -52, 16, 18, ["east"], wall_height=2.0),
    room("heart", 0, -84, 38, 34, ["south"], wall_height=2.0),
]
m_enc = [
    {"id": "m_bats_a", "position": [-6, -16], "monsters": [{"monster": "plague_bat", "count": 3}, {"monster": "stalker", "count": 1}]},
    {"id": "m_rats", "position": [7, -26], "monsters": [{"monster": "plague_frog", "count": 5}]},
    {"id": "m_gob_a", "position": [-5, -29], "monsters": [{"monster": "goblin", "count": 4}]},
    {"id": "m_vein", "position": [26, -22], "monsters": [{"monster": "venom_scorpion", "count": 3}]},
    {"id": "m_skel", "position": [-8, -46], "monsters": [{"monster": "skeleton", "count": 4}]},
    {"id": "m_gob_b", "position": [8, -50], "monsters": [{"monster": "goblin", "count": 3}, {"monster": "stalker", "count": 2}]},
    {"id": "m_troll", "position": [-27, -52], "monsters": [{"monster": "troll", "count": 1}]},
    {"id": "m_golem_stone", "position": [0, -62], "monsters": [{"monster": "golem_stone", "count": 1}]},
    {"id": "m_golem_a", "position": [-10, -78], "monsters": [{"monster": "golem_stone", "count": 1}, {"monster": "goblin", "count": 3}]},
    {"id": "m_golem_b", "position": [10, -80], "monsters": [{"monster": "golem_ice", "count": 1}, {"monster": "golem_fire", "count": 1}, {"monster": "stalker", "count": 2}]},
    {"id": "m_boss", "position": [0, -92], "monsters": [{"monster": "crystal_golem", "count": 1}]},
]
monster("stalker", "plague_bat", _comment="Espreitador da Mina (Stalker 3D, GuieA_7, CC BY-SA 4.0): olho alado que voa em bando e ataca de perto.",
        name_key="MONSTER_STALKER", max_health=110, damage=14, move_speed=3.6, attack_range=1.8, attack_windup=0.5, attack_cooldown=1.4,
        size=1.0, element="earth", look="stalker", color=[1.0, 1.0, 1.0])
monster("crystal_golem", "golem_stone", _comment="Chefe da Mina: o golem do coração de cristal (usa o modelo do Golem de Pedra até haver arte própria).",
        name_key="MONSTER_CRYSTAL_GOLEM", max_health=500, damage=24, size=2.6, color=[0.6, 0.75, 1.0])
m_decor = []
m_lights = []


def crystal_cluster(x, z, n, spread, big=(1.0, 2.0), light=True):
    """Aglomerado de cristais (azuis ou roxos) em volta de (x, z), com uma luz da mesma cor no meio."""
    tag, color = ("B", BLUE) if mr.random() < 0.6 else ("P", PURPLE)
    for _ in range(n):
        ang, dist = mr.uniform(0, 6.283), mr.uniform(0, spread)
        m_decor.append({"piece": "Crystal_%s_%d" % (tag, mr.randint(1, 28)),
                        "position": [round(x + math.cos(ang) * dist, 1), round(z + math.sin(ang) * dist, 1)],
                        "rotation": mr.randrange(0, 360, 15), "scale": round(mr.uniform(*big), 2)})
    if light:
        m_lights.append({"light": list(color), "position": [round(x, 1), round(z, 1)], "range": 9.0, "energy": 1.6, "y": 1.2})


# Paredes de pedra: fileira de pedras grandes (todas as pedras do jogo) junto às bordas, com vão nas portas.
for rd in m_rooms:
    m_decor += ring(mr, rd, ROCKS, 2.0, inset=0.4, scale=(2.2, 3.6))
    m_decor += ring(mr, rd, ROCKS, 3.2, inset=1.6, scale=(1.2, 2.2))
# Pedras menores espalhadas no chão e um ou outro bloco com colisão.
for rd in m_rooms:
    m_decor += scatter(mr, rd, ROCKS, int(rd["size"][0] * rd["size"][1] / 22), margin=2.5, scale=(0.3, 0.9), avoid=[(0, 3, 4)])
# Cristais: veios nas paredes e aglomerados nas salas.
for rd, n in zip(m_rooms, (2, 5, 6, 6, 4, 9)):
    cx, cz = rd["center"]
    w, h = rd["size"]
    for _ in range(n):
        crystal_cluster(cx + mr.uniform(-w / 2 + 3, w / 2 - 3), cz + mr.uniform(-h / 2 + 3, h / 2 - 3), mr.randint(2, 4), 1.6)
# A gruta lateral e o coração da mina: cristais gigantes.
m_decor += [{"piece": "Crystal_B_%d" % i, "position": p, "rotation": r, "scale": s, "solid": [s * 0.6, s * 0.6]} for i, p, r, s in (
    (4, [22, -26], 30, 3.2), (12, [28, -19], 100, 2.6), (16, [-6, -90], 0, 3.6), (21, [8, -92], 45, 3.0), (3, [-12, -96], 200, 3.4))]
m_lights += [{"light": list(BLUE), "position": [24, -22], "range": 12.0, "energy": 2.4, "y": 1.5},
             {"light": list(PURPLE), "position": [0, -92], "range": 16.0, "energy": 3.0, "y": 2.0}]
# Trilhos (Rails, yd, GPL 2.0; peças de 6 m): a linha principal do portão ao coração da mina e dois ramais, para a gruta dos veios e
# para a gruta das carroças. Pedras e cristais pequenos saem de cima deles.
RAIL_LINES = [(0, -1, 0, -91), (3, -22, 17, -22), (-3, -52, -19, -52)]
rails = []
for x0, z0, x1, z1 in RAIL_LINES:
    horizontal = z0 == z1
    n = max(round(abs((x1 - x0) if horizontal else (z1 - z0)) / 6.0), 1)
    for i in range(n):
        t = (i + 0.5) / n
        rails.append({"piece": "Rail_Straight", "position": [round(x0 + (x1 - x0) * t, 2), round(z0 + (z1 - z0) * t, 2)],
                      "rotation": 90 if horizontal else 0, "scale": round(abs((x1 - x0) if horizontal else (z1 - z0)) / n / 6.0, 3), "y": 0.02})


def on_rail(d):
    if "solid" in d or d.get("piece", "").startswith("Rail") or "light" in d or "position" not in d:
        return False
    x, z = d["position"]
    return any(min(a, c) - 0.8 <= x <= max(a, c) + 0.8 and min(b, e) - 0.8 <= z <= max(b, e) + 0.8
               for a, b, c, e in [(l[0], l[1], l[2], l[3]) for l in RAIL_LINES]) and d.get("scale", 1.0) < 1.6
m_decor = [d for d in m_decor if not on_rail(d)] + rails
# Equipamento dos mineiros.
m_decor += [{"piece": "Cart_Wood", "position": [-14, -52], "rotation": 90, "y": 0.05, "solid": [2.0, 1.2]}, {"piece": "Cart_Wood", "position": [0, -10], "rotation": 0, "y": 0.05, "solid": [1.2, 2.0]}, {"piece": "Cart_Wood", "position": [-29, -50], "rotation": 40, "solid": [2.0, 1.2]},
            {"piece": "Barrel", "position": [-24, -57], "scale": 1.0, "solid": [0.9, 0.9]}, {"piece": "Beer_Barrel", "position": [-30, -56], "solid": [0.9, 0.9]},
            {"piece": "Bucket_Crate", "position": [-23, -47], "solid": [0.9, 0.9]}, {"piece": "Whetstone", "position": [-4, 4], "scale": 2.0},
            {"piece": "Pr_BrokenPillar1", "position": [-8, -36], "solid": [1.2, 1.2]}, {"piece": "Pr_BrokenPillar2", "position": [9, -36], "solid": [1.2, 1.2]},
            {"piece": "Pr_BrokenPillar1", "position": [-9, -66], "solid": [1.2, 1.2]}, {"piece": "Pr_BrokenPillar2", "position": [9, -66], "solid": [1.2, 1.2]},
            {"piece": "Pr_LampPost", "position": [-3, 3], "solid": [0.6, 0.6]}, {"piece": "Pr_LampPost", "position": [3, -34], "solid": [0.6, 0.6]},
            {"piece": "Pr_LampPost", "position": [-3, -66], "solid": [0.6, 0.6]}]
m_lights += [{"light": [1.0, 0.7, 0.35], "position": [-3, 3], "range": 8.0, "energy": 1.2, "y": 2.2},
             {"light": [1.0, 0.7, 0.35], "position": [3, -34], "range": 8.0, "energy": 1.2, "y": 2.2},
             {"light": [1.0, 0.7, 0.35], "position": [-3, -66], "range": 8.0, "energy": 1.2, "y": 2.2}]
# Teias (Spider Webs, p0ss, CC BY 3.0): de pé nos cantos das salas e atravessando as bocas das grutas laterais, deitadas no chão das grutas.
wr = rng("mine_webs")
for rd in m_rooms:
    cx, cz = rd["center"]
    w, h = rd["size"]
    for sx, sz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        if wr.random() < 0.55 and rd["id"] != "entry":
            x, z = cx + sx * (w / 2 - 2.2), cz + sz * (h / 2 - 2.2)
            m_decor.append({"piece": wr.choice(["Web_Round_Up", "Web_Square_Up"]), "position": [round(x, 1), round(z, 1)],
                            "rotation": wr.choice([0, 90, 180, 270]) + wr.randrange(-15, 16, 5), "scale": round(wr.uniform(2.2, 3.6), 2), "y": round(wr.uniform(0.0, 0.6), 2)})
for x, z, rot in ((-17.8, -52, 90), (15.8, -22, 90), (0.0, -66.5, 0)):   # bocas da gruta das carroças, da gruta dos veios e do coração
    m_decor.append({"piece": "Web_Square_Up", "position": [x, z], "rotation": rot, "scale": 3.4, "y": 0.2})
for rd, n in zip(m_rooms[2:5], (3, 2, 4)):
    for d in scatter(wr, rd, ["Web_Round_Flat", "Web_Square_Flat"], n, margin=2.5, scale=(1.6, 2.8)):
        d.pop("solid", None)
        m_decor.append(d)
m_decor += m_lights
arenas["mine_01_crystal_vein"] = {
    "_comment": "Mina de Cristais (Lowpoly Crystals Pack, iPoly3D, CC0; Rocks, Nobiax, CC0; Low Poly Rocks, para, CC0): galerias entre paredes de pedra (todas as pedras do jogo) com cristais azuis e roxos que brilham no escuro, uma gruta lateral de veios, a gruta das carroças e o coração da mina, onde o golem de cristal espera. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_MINE", "player_class": "mage", "map_id": "map_mine", "area_level": 5,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": m_rooms, "encounters": m_enc, "hazards": [],
    "entries": {"start": [0, 3], "mine": [0, 3]},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "forest", "expedition_end": True},
        {"id": "mine_chest_1", "kind": "chest", "position": [29, -26], "loot": "chest"},
        {"id": "mine_chest_2", "kind": "chest", "position": [-32, -46], "loot": "chest"},
        {"id": "mine_chest_3", "kind": "chest", "position": [16, -96], "loot": "chest"},
    ],
    "quest_spots": [], "breakables": [],
    "style": {"_comment": "Mina: chão de terra escuro; as paredes são fileiras de pedras (decor), sem muro do kit.", "walls": [""], "floor": "Ground_Dirt", "low": "",
              "ground": [0.05, 0.045, 0.05], "tint": [0.55, 0.5, 0.55]},
    "decor": m_decor, "passive": True,
}
if not any(p["id"] == "mine_gate" for p in arenas["tortuga"]["props"]):
    arenas["tortuga"]["props"].append({"id": "mine_gate", "kind": "exit", "name_key": "PROP_TO_MINE", "position": [-28.5, 5.9], "to": "mine_01_crystal_vein", "entry": "start"})

# --- Forte (3D Dungeon Tileset, grade de 2,5 m) -------------------------------------------------------
import os
COLS, ROWS, CELL = 34, 34, 2.5
grid = [["#"] * COLS for _ in range(ROWS)]


def carve(c0, r0, c1, r1, ch="."):
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            grid[r][c] = ch


# Planta no desenho de ~/Downloads/fort-map.jpg: 1 = partida (sudeste), 5 = sala do chefe final (noroeste, com a saída), 3 e 4 = as duas
# áreas dos mini-chefes (leste e sudoeste), 2 = áreas de monstros (quatro salas grandes); o resto são corredores de 2 células, salas
# vazias e becos sem saída. Retângulos (c0, r0, c1, r1), inclusive.
F_ROOMS = {
    "start": (25, 24, 31, 31), "pillars": (18, 24, 23, 31), "boss": (3, 2, 8, 6), "west": (3, 8, 8, 15), "hall": (10, 2, 18, 11),
    "ne": (20, 2, 27, 8), "mid": (10, 14, 15, 17), "cross": (11, 19, 15, 25), "east_hall": (19, 16, 24, 21),
    "mb_east": (29, 10, 31, 16), "mb_west": (6, 25, 10, 30),
}
F_LINKS = [
    (24, 27, 24, 28),   # partida -> sala dos pilares
    (21, 22, 22, 23),   # pilares -> salão leste
    (16, 19, 18, 20),   # salão leste -> sala em cruz
    (25, 18, 25, 19),   # salão leste -> corredor leste
    (28, 12, 28, 13),   # corredor leste -> mini-chefe leste
    (19, 4, 19, 5),     # sala nordeste -> salão do alto
    (9, 9, 9, 10),      # salão do alto -> salão oeste
    (5, 7, 6, 7),       # salão oeste -> sala do chefe final
    (12, 12, 13, 13),   # salão do alto -> sala do meio
    (12, 18, 13, 18),   # sala do meio -> sala em cruz
    (12, 26, 13, 26),   # sala em cruz -> corredor do sul
    (5, 1, 6, 1),       # a saída, no norte da sala do chefe
]
F_CORRIDORS = [
    (26, 9, 27, 23),    # corredor leste, da sala nordeste até a partida
    (2, 16, 3, 31),     # corredor oeste, do salão oeste até o sul
    (4, 29, 5, 30),     # ... entra no mini-chefe sudoeste
    (11, 27, 17, 28),   # corredor do sul: mini-chefe sudoeste -> sala dos pilares
]
F_DEAD_ENDS = [(4, 18, 9, 19), (4, 22, 8, 23), (22, 10, 25, 11)]   # becos sem saída (um baú no fundo de cada)
for rect in list(F_ROOMS.values()) + F_LINKS + F_CORRIDORS + F_DEAD_ENDS:
    carve(*rect)

# Todo o piso é um só pedaço ligado à partida.
_flood, _stack = set(), [(28, 28)]
while _stack:
    c, r = _stack.pop()
    if (c, r) in _flood or not (0 <= c < COLS and 0 <= r < ROWS) or grid[r][c] == "#":
        continue
    _flood.add((c, r))
    _stack += [(c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)]
assert _flood == {(c, r) for r in range(ROWS) for c in range(COLS) if grid[r][c] != "#"}, "há piso do Forte sem ligação com a partida"


def is_rock(c, r):
    return c < 0 or r < 0 or c >= COLS or r >= ROWS or grid[r][c] == "#"


def cell_pos(c, r):
    return [round((c - COLS / 2 + 0.5) * CELL, 2), round((r - ROWS / 2 + 0.5) * CELL, 2)]


def room_pos(name, dc=0.0, dr=0.0):
    c0, r0, c1, r1 = F_ROOMS[name]
    return [round(((c0 + c1) / 2 + dc - COLS / 2 + 0.5) * CELL, 2), round(((r0 + r1) / 2 + dr - ROWS / 2 + 0.5) * CELL, 2)]


fort_decor = []
available = set(f[5:13] for f in os.listdir("assets/models/maps/fort") if f.startswith("Fort_") and f.endswith(".gltf") and f != "Fort_Floor.gltf")
NEIGH = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]  # N, NE, E, SE, S, SW, W, NW
for r in range(ROWS):
    for c in range(COLS):
        if grid[r][c] != "#":
            continue
        bits = [is_rock(c + dx, r + dz) for dx, dz in NEIGH]
        for i in (1, 3, 5, 7):  # canto só conta se os dois lados vizinhos também são pedra
            bits[i] = bits[i] and bits[(i - 1) % 8] and bits[(i + 1) % 8]
        mask = "".join("1" if b else "0" for b in bits)
        if mask == "11111111" and not any(not is_rock(c + dx, r + dz) for dx in range(-2, 3) for dz in range(-2, 3)):
            continue  # pedra escondida no meio do maciço
        rotation = 0
        if mask not in available:
            # O pacote só traz uma orientação de cada peça: gira a máscara de 90 em 90 graus até achar uma que exista.
            for k in (1, 2, 3):
                turned = "".join(mask[(i - 2 * k) % 8] for i in range(8))  # máscara do tile base que, girado k vezes no sentido horário, vira `mask`
                if turned in available:
                    mask, rotation = turned, -90 * k
                    break
            else:
                mask = "11111111" if mask.count("1") > 6 else "00000000"
        entry = {"piece": "Fort_" + mask, "position": cell_pos(c, r)}
        if rotation:
            entry["rotation"] = rotation
        fort_decor.append(entry)
# Colisão: uma caixa por trecho de pedra em cada linha.
for r in range(ROWS):
    c = 0
    while c < COLS:
        if grid[r][c] == "#":
            c0 = c
            while c < COLS and grid[r][c] == "#":
                c += 1
            x0, z = cell_pos(c0, r)
            x1, _ = cell_pos(c - 1, r)
            fort_decor.append({"collider": [round(x1 - x0 + CELL, 2), CELL], "position": [round((x0 + x1) / 2, 2), z]})
        else:
            c += 1

# Luzes quentes: uma em cada sala (quatro na partida, nos cantos) e uma no meio de cada beco.
fort_decor += [{"light": [1.0, 0.65, 0.3], "position": room_pos(n), "y": 2.2, "range": 9.5, "energy": 1.3} for n in F_ROOMS if n not in ("start", "mb_east", "mb_west")]
fort_decor += [{"light": [1.0, 0.65, 0.3], "position": cell_pos(c, r), "y": 2.2, "range": 8.0, "energy": 1.0} for c, r in ((26, 25), (30, 25), (26, 30), (30, 30))]
fort_decor += [{"light": [0.85, 0.3, 0.25], "position": room_pos(n), "y": 2.2, "range": 8.5, "energy": 1.1} for n in ("mb_east", "mb_west")]  # as salas dos mini-chefes, em vermelho
fort_decor += [{"light": [0.7, 0.4, 0.9], "position": room_pos("boss"), "y": 2.4, "range": 11.0, "energy": 1.4}]  # a sala do chefe, em roxo
# Peças do castelo (3D Castle Dungeon Tileset Extended, rubberduck, CC0; build_castle_kit.py), na mesma altura da pedra do Forte:
# portões em arco nas passagens; colunas e pilares são sólidos, arcos e lajotas não.
castle = [{"piece": "Castle_GateBig", "position": cell_pos(5 + k, 7)} for k in (0, 1)]                                        # sala do chefe
castle += [{"piece": "Castle_GateBig", "position": cell_pos(28, 12 + k), "rotation": 90} for k in (0, 1)]                      # mini-chefe leste
castle += [{"piece": "Castle_GateBig", "position": cell_pos(24, 27 + k), "rotation": 90} for k in (0, 1)]                      # partida
castle += [{"piece": "Castle_GateBig", "position": cell_pos(19, 4 + k), "rotation": 90} for k in (0, 1)]                      # sala nordeste
castle += [{"piece": "Castle_" + n, "position": cell_pos(c, r), "solid": [0.9, 0.9]} for n, c, r in (
    ("Column", 12, 4), ("Column", 16, 4), ("Column", 12, 9), ("Column", 16, 9),                    # salão do alto
    ("Column", 19, 25), ("Column", 22, 25), ("Column", 19, 30), ("Column", 22, 30),                # sala dos pilares
    ("Column", 20, 18), ("Column", 23, 18), ("Column", 4, 4), ("Column", 7, 4),                    # salão leste, sala do chefe
    ("EdgeColumn", 26, 31), ("EdgeColumn", 30, 31))]                                                # partida
castle += [{"piece": "Castle_Dais", "position": cell_pos(5, 2)}, {"piece": "Castle_Altar", "position": cell_pos(7, 2), "solid": [1.2, 1.2]}]
castle += [{"piece": "Castle_Tiles", "position": [round(cell_pos(11, 5)[0] + i * 1.3, 2), round(cell_pos(11, 5)[1] + j * 1.3, 2)]}
           for i in range(4) for j in range(3)]
fort_decor += castle
# Peças do Labirinto (3D Walls & Props, deadkir, CC0; build_labyrinth_kit.py): caixões no salão oeste, barris e caixotes na partida,
# o escudo com a espada caídos perto do chefe; cada sala sem monstros ganha, no canto, barris, um caixote, um caixão, ruínas, uma coluna
# ou nada (sorteio fixo).
lab = [{"piece": "Lab_" + n, "position": cell_pos(c, r), "rotation": rot, "solid": [w, d]} for n, c, r, rot, w, d in (
    ("Coffin", 4, 9, 0, 2.0, 0.9), ("Coffin", 7, 9, 0, 2.0, 0.9), ("Coffin", 4, 14, 0, 2.0, 0.9),
    ("Barrel", 25, 25, 0, 0.6, 0.6), ("Barrel", 31, 25, 0, 0.6, 0.6), ("Barrel", 25, 26, 0, 0.6, 0.6), ("Barrel", 31, 26, 0, 0.6, 0.6),
    ("Crate", 25, 30, 0, 0.6, 0.6), ("Crate", 31, 30, 0, 0.6, 0.6), ("Crate", 25, 29, 0, 0.6, 0.6), ("Crate", 31, 29, 0, 0.6, 0.6))]
lab.append({"piece": "Lab_ShieldSword", "position": cell_pos(6, 5), "rotation": 25})
md = rng("fort_room_decor")
for name in ("ne", "mid", "cross", "pillars", "hall", "mb_east", "mb_west"):
    c0, r0, c1, r1 = F_ROOMS[name]
    cx, cz = cell_pos(md.choice((c0 + 1, c1 - 1)), md.choice((r0 + 1, r1 - 1)))
    sx, sz = md.choice((-1, 1)), md.choice((-1, 1))
    bx, bz = cx, cz
    kind = md.choice(("barrels", "crate", "coffin", "ruin", "column"))
    if kind == "barrels":
        lab += [{"piece": "Lab_Barrel", "position": [bx, bz], "solid": [0.6, 0.6]}, {"piece": "Lab_Barrel", "position": [round(bx - sx * 0.7, 2), bz], "solid": [0.6, 0.6]}]
    elif kind == "crate":
        lab.append({"piece": "Lab_Crate", "position": [bx, bz], "rotation": md.randrange(0, 360, 15), "solid": [0.6, 0.6]})
    elif kind == "coffin":
        lab.append({"piece": "Lab_Coffin", "position": [bx, bz], "solid": [2.0, 0.9]})
    elif kind == "ruin":
        lab.append({"piece": md.choice(("Lab_WallBroken", "Lab_WallLong")), "position": [bx, bz], "solid": [1.3, 0.32]})
        lab.append({"piece": "Lab_ColumnBroken", "position": [round(bx - sx * 1.2, 2), round(bz + sz * 0.3, 2)], "solid": [0.32, 0.32]})
    elif kind == "column":
        lab.append({"piece": "Lab_ColumnBig", "position": [bx, bz], "solid": [0.63, 0.63]})
fort_decor += lab
# Canhões de navio (Ship Cannon, jameswhite, CC0; build_cannon.py), a boca para +Z com rotação 0: dois na partida apontados para o
# forte (norte) e dois na sala do chefe apontados para a porta (sul).
fort_decor += [{"piece": "Ship_Cannon", "position": cell_pos(c, r), "rotation": rot, "solid": [0.8, 1.5]}
               for c, r, rot in ((27, 31, 180), (29, 31, 180), (4, 6, 0), (7, 6, 0))]
# Tochas de parede (Wall mounted torch, scribe, CC BY 3.0; build_wall_torch.py): presas na face da pedra voltada para o piso, com
# pelo menos 6 m entre elas; metade tem uma luz própria de chama (as outras só enfeitam).
wt_rng = rng("fort_wall_torches")
wt_cells = []
for r in range(ROWS):
    for c in range(COLS):
        if grid[r][c] == "#":
            continue
        for dx, dz in ((0, -1), (1, 0), (-1, 0)):  # N, E, W: lado onde está a pedra (sem o S: a tocha ficaria voltada para o norte, escondida pelo topo da parede, vista da câmera)
            if is_rock(c + dx, r + dz) and 0 < c + dx < COLS - 1 and 0 < r + dz < ROWS - 1:
                wt_cells.append((c, r, dx, dz))
wt_rng.shuffle(wt_cells)
wt_placed = []
for c, r, dx, dz in wt_cells:
    x, z = cell_pos(c, r)
    if any(math.hypot(x - px, z - pz) < 6.0 for px, pz, _, _ in wt_placed):
        continue
    wt_placed.append((x, z, dx, dz))
    if len(wt_placed) == 26:
        break
for i, (x, z, dx, dz) in enumerate(wt_placed):
    face = [round(x + dx * (CELL / 2 - 0.02), 2), round(z + dz * (CELL / 2 - 0.02), 2)]
    fort_decor.append({"piece": "Wall_Torch", "position": face, "rotation": round(math.degrees(math.atan2(-dx, -dz)))})
    if i % 2 == 0:
        fort_decor.append({"light": [1.0, 0.6, 0.25], "position": [round(x - dx * 0.2, 2), round(z - dz * 0.2, 2)], "y": 1.9, "range": 5.5, "energy": 0.9})
# Ratos pequenos de cenário (papel "rat" do NpcModel): correm de um canto a outro, sempre entre duas células de piso a até 3 células
# de distância, com sorteio fixo.
fr = rng("fort_rats")
floor_cells = [(c, r) for r in range(ROWS) for c in range(COLS) if grid[r][c] != "#"]
fort_rats = []
while len(fort_rats) < 20:
    c, r = fr.choice(floor_cells)
    c2, r2 = c + fr.randint(-3, 3), r + fr.randint(-3, 3)
    if (c2, r2) == (c, r) or not (0 <= c2 < COLS and 0 <= r2 < ROWS) or grid[r2][c2] == "#":
        continue
    if any(grid[r + round((r2 - r) * t / 6)][c + round((c2 - c) * t / 6)] == "#" for t in range(7)):
        continue  # o caminho não atravessa pedra
    a, b = cell_pos(c, r), cell_pos(c2, r2)
    fort_rats.append({"role": "rat", "position": [round(a[0] + fr.uniform(-0.8, 0.8), 2), round(a[1] + fr.uniform(-0.8, 0.8), 2)],
                      "path": b, "speed": round(fr.uniform(1.2, 2.2), 1), "pose": "walk"})
# Baús: no fundo de cada beco, na sala nordeste e no fim do corredor oeste.
fort_chests = [{"id": i, "kind": "chest", "position": cell_pos(c, r), **extra} for i, (c, r), extra in zip(
    ("fort_chest_1", "fort_chest_2", "fort_potions_1", "fort_potions_2", "fort_potions_3"),
    ((9, 18), (8, 22), (25, 10), (26, 3), (3, 30)),
    ({"loot": "chest"}, {"loot": "chest"}, {"loot": "potion_chest", "model": "Chest_Potion"}, {"loot": "potion_chest", "model": "Chest_Potion"},
     {"loot": "potion_chest", "model": "Chest_Potion"}))]
# As quatro áreas de monstros (salão do alto, salão oeste, sala do meio, salão leste) e a sala do chefe final. Os dois mini-chefes não
# estão aqui: um NPC de cada área os desperta (propriedade "summon", como a Floresta).
fort_encounters = [
    {"id": "fo_area_hall", "position": room_pos("hall"), "monsters": [{"monster": "dark_elf", "count": 3}, {"monster": "plague_bat", "count": 2}]},
    {"id": "fo_area_west", "position": room_pos("west"), "monsters": [{"monster": "succubus", "count": 2}, {"monster": "dark_elf", "count": 1}]},
    {"id": "fo_area_mid", "position": room_pos("mid"), "monsters": [{"monster": "venom_scorpion", "count": 3}, {"monster": "mutant_frog", "count": 2}]},
    {"id": "fo_area_east", "position": room_pos("east_hall"), "monsters": [{"monster": "dark_elf", "count": 2}, {"monster": "succubus", "count": 2}]},
    {"id": "fo_commander", "position": room_pos("boss", 0, 0.5), "monsters": [{"monster": "fort_commander", "count": 1}, {"monster": "dark_elf", "count": 2}]},
]
fo_summons = {
    "east": {"id": "fo_succubus_queen", "position": room_pos("mb_east"), "spread": 3.0, "toast": "TOAST_PENITENT_AWAKENS",
             "monsters": [{"monster": "succubus_queen", "count": 1, "rank": "miniboss"}]},
    "west": {"id": "fo_dark_elf_lord", "position": room_pos("mb_west"), "spread": 3.0, "toast": "TOAST_EXILE_AWAKENS",
             "monsters": [{"monster": "dark_elf_lord", "count": 1, "rank": "miniboss"}]},
}
arenas["fort_01_gate"] = {
    "_comment": "Forte (3D Dungeon Tileset, Skorpio, CC BY-SA 3.0): uma grade de 34 x 34 células de 2,5 m com pedra e piso do pacote (Fort_<máscara>, a máscara é o 8-vizinhança de pedra); a colisão é uma caixa por trecho de pedra. Planta no desenho de ~/Downloads/fort-map.jpg: partida no sudeste, quatro áreas de monstros (salões do alto, oeste, do meio e leste), dois mini-chefes (Rainha das Súcubos no leste, Senhor Elfo Sombrio no sudoeste, cada um despertado por um NPC), becos sem saída com baús e, no noroeste, a sala do chefe final com a saída para a Capital. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_FORT", "player_class": "mage", "map_id": "map_fort", "area_level": 10,
    "wake_radius": 10.0, "alert_radius": 5.0,
    "rooms": [room("fort", 0, 0, COLS * CELL, ROWS * CELL, [], wall_height=0.8, torch=False)],
    "encounters": fort_encounters,
    "hazards": [], "entries": {"start": cell_pos(28, 28)},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": cell_pos(30, 30), "to": "tortuga", "entry": "forest", "expedition_end": True},
        {"id": "to_capital", "kind": "exit", "name_key": "PROP_TO_CAPITAL", "position": [cell_pos(5, 1)[0] + CELL / 2, cell_pos(5, 1)[1] - 0.6], "to": "capital_01_aurenhold", "entry": "start", "after_victory": True, "group": True},
        {"id": "fort_penitent", "kind": "npc", "npc": "fort_penitent", "position": cell_pos(27, 15), "rotation": 90, "summon": fo_summons["east"]},
        {"id": "fort_exile", "kind": "npc", "npc": "fort_exile", "position": cell_pos(12, 28), "rotation": 270, "summon": fo_summons["west"]},
        *fort_chests,
    ],
    "quest_spots": [], "breakables": [],
    "style": {"_comment": "Forte: piso de pedra do pacote; a pedra vem das peças Fort_* em decor.", "walls": [""], "floor": "Fort_Floor", "low": "", "ground": [0.07, 0.07, 0.08]},
    "decor": fort_decor, "crowd": fort_rats, "passive": True,
}

# --- Capital Real, Aurenhold (cidade-base; depois do Forte) ---------------------------------------------
kr = rng("capital")
cap_rooms = [
    room("gate_plaza", 0, 0, 44, 14, ["north"], torch=True, roofs=False),
    room("avenue", 0, -15, 56, 16, ["south", "north"], torch=True, roofs=True),
    room("castle_court", 0, -31, 34, 16, ["south"], torch=True, wall_height=2.0),
]
cap_decor = [{"piece": "Pr_CoveredWell", "position": [0, -15], "solid": [1.8, 1.8]}]
for x in (-18, -9, 9, 18):
    cap_decor.append({"piece": "Pr_LampPost", "position": [x, -9.5], "solid": [0.6, 0.6]})
    cap_decor.append({"piece": "Pr_LampPost", "position": [x, -20.5], "solid": [0.6, 0.6]})
# Suportes de armas (Medieval Weapon Rack, CC BY 3.0) junto aos guardas: uma de cada lado da avenida e uma no portão, cada uma com as espadas por rank.
for rx, rz, rot in ((-14, -9.2, 0), (14, -9.2, 0), (-17, 5.2, 0)):
    cap_decor.append({"piece": "Weapon_Rack", "position": [rx, rz], "rotation": rot, "solid": [2.2, 0.9]})
    for k, rank in enumerate("DCBAS"):
        cap_decor.append({"piece": "Sword_" + rank, "position": [round(rx - 0.8 + 0.4 * k, 2), rz], "y": 0.85, "rotation": 90})
cap_decor += [{"piece": "Pr_Obelisk3", "position": [-8, -36], "solid": [1.4, 1.4]}, {"piece": "Pr_Obelisk3", "position": [8, -36], "solid": [1.4, 1.4]},
              {"piece": "Pr_RoadSign", "position": [5, 2], "rotation": 200}]
# Os guardas que treinavam em Tortuga agora fazem a segurança daqui (data/capital_royal_guards.json): portão, avenida e pátio do castelo.
guards = json.load(open("data/capital_royal_guards.json"))["guards"]
spots = [(-6, 1, 0), (6, 1, 0), (-20, -2, 90), (20, -2, 270), (-12, -15, 90), (12, -15, 270), (-5, -20, 0), (5, -20, 0), (-24, -12, 90), (24, -12, 270)]
cap_crowd = []
for g, (x, z, rot) in zip(guards, spots):
    # Guarda animado (Defender): os do portão ficam parados; os da avenida e do castelo fazem ronda de ida e volta.
    c = {"role": "defender", "position": [x, z], "rotation": rot, "pose": "idle"}
    if z < -10:
        c["path"] = [x + (10 if x < 0 else -10), z]
        c["speed"] = 0.9
    cap_crowd.append(c)
if "capital_01_aurenhold" not in arenas:  # depois de criada, a Capital (lojas, pátio de treino) é editada direto em arenas.json: não regenerar
    arenas["capital_01_aurenhold"] = {
        "_comment": "Capital Real, Aurenhold (04-1-capital-real.md): a cidade do reino vencedor, rica e cheia de guardas; segunda cidade-base, depois do Forte. Primeira passada: praça do portão, avenida e pátio do castelo, com a segurança feita pelos 10 guardas que treinavam em Tortuga. Ainda sem lojas, Bobo da Corte nem missões. Gerado por tools/assets/build_maps.py.",
        "name_key": "ARENA_CAPITAL", "town": True, "outdoor": True, "player_class": "mage", "area_level": 10,
        "wake_radius": 10.0, "alert_radius": 5.0, "rooms": cap_rooms, "encounters": [],
        "entries": {"start": [0, 3], "capital": [0, 3]},
        "props": [
            {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "forest"},
        ],
        "style": {"_comment": "Capital: casas de reboco e tijolo como Tortuga, mas piso de tijolo limpo e cerca baixa branca.",
                  "walls": ["Wall_Plaster_Straight", "Wall_Plaster_Window_Wide_Round", "Wall_Plaster_WoodGrid", "Wall_UnevenBrick_Straight", "Wall_Plaster_Door_Round", "Wall_Plaster_Window_Thin_Round"],
                  "floor": "Floor_Brick", "low": "Prop_WoodenFence_Single", "ground": [0.16, 0.15, 0.13], "roof": "Roof_RoundTiles_4x4", "tint": [1.1, 1.08, 1.0]},
        "decor": cap_decor, "crowd": cap_crowd,
    }

# --- Fazenda (cidade-base campestre; só o mapa por enquanto, ligada a Tortuga por um portal) -----------------
fr = rng("farm")
farm_rooms = [
    room("gate", 0, 0, 56, 14, ["north"], torch=True, wall_height=0.8),  # da largura dos campos: sem chão liso nas pontas
    room("fields", 0, -26, 56, 38, ["south", "east"], wall_height=0.8),
    room("mill", 38, -26, 20, 38, ["west"], wall_height=0.8),
]
CREEK_X, CREEK_W, BRIDGE_Z = 36.9, 3.6, -36.0
farm_decor = [
    # Serraria movida a água (CC0) no fundo da clareira lateral; barricadas de toras (CC-BY) fechando o portão.
    {"piece": "Pr_Sawmill", "position": [CREEK_X + 2.1, -22], "rotation": 270, "solid": [8.0, 6.5]},
    # Casa da Fazenda (Old Medieval Shack House, Spiral, CC0): 7 x 4,9 m, porta para o portão (+Z), ao lado da horta.
    {"piece": "Pr_Farmhouse", "position": [-14, -12], "solid": [7.0, 4.9]},
    # Entrada do Bunker (peças Bk_*, CC0): batente de pedra com duas paredes laterais, no canto nordeste dos campos.
    {"piece": "Bk_Pillar", "position": [15.9, -10.0], "solid": [0.9, 0.9]}, {"piece": "Bk_Pillar", "position": [18.1, -10.0], "solid": [0.9, 0.9]},
    {"piece": "Bk_Lintel", "position": [17.0, -10.0], "rotation": 90},
    {"piece": "Bk_Wall", "position": [14.7, -10.0], "rotation": 90, "solid": [2.0, 0.5]}, {"piece": "Bk_Wall", "position": [19.3, -10.0], "rotation": 90, "solid": [2.0, 0.5]},
    {"piece": "Pr_Barricade", "position": [-8.5, -5.0], "rotation": 15, "solid": [2.0, 1.2]},
    {"piece": "Pr_Barricade", "position": [8.5, -5.0], "rotation": 345, "solid": [2.0, 1.2]},
    {"piece": "Well_Covered", "position": [-12, -20], "solid": [1.6, 1.6]},
    # Carroças (Carts, cemkalyoncu, CC-BY 3.0): a grande no campo, as pequenas (de mão) perto do portão e do pasto dos cavalos.
    {"piece": "Pr_CartLarge", "position": [-22, -29], "rotation": 20, "solid": [3.2, 2.6]},
    {"piece": "Pr_CartSmall", "position": [5, -12], "rotation": 100, "solid": [1.2, 2.4]},
    {"piece": "Pr_CartSmall", "position": [10, -40], "rotation": 300, "solid": [2.0, 1.8]},
    {"piece": "Bucket_Wooden_1", "position": [-10.4, -19.2]},
    # Ponte de tábuas sobre o riacho (Pr_Bridge, feita para o jogo): os corrimãos bloqueiam, a travessia fica livre.
    {"piece": "Pr_Bridge", "position": [CREEK_X, BRIDGE_Z]},
    {"collider": [5.0, 0.2], "position": [CREEK_X, BRIDGE_Z - 0.92]}, {"collider": [5.0, 0.2], "position": [CREEK_X, BRIDGE_Z + 0.92]},
]
# Riacho que passa debaixo da roda d'água da serraria (a roda fica no lado oeste do prédio, com o eixo de leste a oeste:
# a água corre de norte a sul), de ponta a ponta da clareira, com pedras e capim nas margens (menos na ponte).
for z in range(-44, -7, 4):
    if abs(z - BRIDGE_Z) < 3.0:
        continue
    for side in (-1, 1):
        farm_decor.append({"piece": fr.choice(["RockP_1", "RockP_2", "RockP_3", "RockP_6"]),
                           "position": [round(CREEK_X + side * (CREEK_W / 2 + fr.uniform(0.1, 0.6)), 1), z + round(fr.uniform(-1.2, 1.2), 1)],
                           "rotation": fr.randrange(0, 360, 15), "scale": round(fr.uniform(0.6, 1.1), 2)})
        farm_decor.append({"piece": fr.choice(["Pl_Grass1", "Pl_Grass2", "Pl_Grass3"]),
                           "position": [round(CREEK_X + side * (CREEK_W / 2 + fr.uniform(0.7, 1.5)), 1), z + round(fr.uniform(-1.5, 1.5), 1)],
                           "rotation": fr.randrange(0, 360, 15), "scale": round(fr.uniform(1.0, 1.8), 2)})


def fence_rect(x0, z0, x1, z1, gaps=(), piece="Prop_WoodenFence_Single", step=2.0):
    """Cerca retangular de peças da cerca de madeira do kit (2,06 m, ao longo de x), com vãos de portão: `gaps` = (lado, posição
    ao longo do lado, largura), lados "n"/"s" (z mínimo/máximo) e "w"/"e"."""
    out = []
    sides = {"n": ((x0, z0), (x1, z0)), "s": ((x0, z1), (x1, z1)), "w": ((x0, z0), (x0, z1)), "e": ((x1, z0), (x1, z1))}
    for side, ((ax, az), (bx, bz)) in sides.items():
        length = math.hypot(bx - ax, bz - az)
        dx, dz = (bx - ax) / length, (bz - az) / length
        n = max(1, round(length / step))
        for i in range(n):
            t = (i + 0.5) * length / n
            px, pz = ax + dx * t, az + dz * t
            along = px if side in "ns" else pz
            if any(g[0] == side and abs(along - g[1]) < g[2] / 2 + 0.6 for g in gaps):
                continue
            horizontal = side in "ns"
            out.append({"piece": piece, "position": [round(px, 1), round(pz, 1)], "rotation": 0 if horizontal else 90,
                        "scale": round(length / n / 2.06 * 1.02, 2), "solid": [length / n, 0.3] if horizontal else [0.3, length / n]})
    return out


# Cercados (portão virado para o portão da fazenda, lado "s"): pasto das ovelhas, curral dos porcos, pasto dos cavalos; horta dos fazendeiros.
PASTURE = (-2, -35, 12, -27)
PIGPEN = (-26, -44, -14, -34)
PADDOCK = (14, -44, 28, -33)
GARDEN = (-10, -17, 2, -10)
farm_decor += fence_rect(*PASTURE, gaps=[("s", 5, 3.0)])
farm_decor += fence_rect(*PIGPEN, gaps=[("s", -20, 2.6)])
farm_decor += fence_rect(*PADDOCK, gaps=[("s", 21, 3.4)])
farm_decor += fence_rect(*GARDEN, gaps=[("s", -4, 2.6)])
for row_z in (-15.9, -12.2, -10.9):
    for gx in range(-9, 2, 1):
        farm_decor.append({"piece": "Pl_Hemp", "position": [gx + fr.uniform(-0.15, 0.15), round(row_z + fr.uniform(-0.1, 0.1), 1)],
                           "rotation": fr.randrange(0, 360, 15), "scale": round(fr.uniform(0.8, 1.0), 2)})
# Terra batida e lama (Ground_FarmDirt / Ground_FarmMud, da biblioteca de texturas assets/textures/maps; build_farm_ground.py): caminhos entre
# os pontos da fazenda, horta, pátio da serraria, curral dos porcos (lama) e manchas de terra no pasto dos cavalos. Cada ladrilho de 2 x 2 m
# gira em múltiplos de 90 graus e fica numa altura levemente diferente da dos vizinhos (sem brigar na tela).
dirt_spots = []
dirt_n = [0]


def dirt_tile(piece, x, z, scale=1.0, free=False):
    dirt_n[0] += 1
    farm_decor.append({"piece": piece, "position": [round(x, 2), round(z, 2)], "y": round(0.02 + (dirt_n[0] % 6) * 0.003, 3),
                       "rotation": fr.randrange(0, 360, 5) if free else fr.choice([0, 90, 180, 270]), "scale": round(scale, 2)})
    dirt_spots.append((x, z, 1.5))


def dirt_path(points, step=1.6, piece="Ground_FarmDirt"):
    for (ax, az), (bx, bz) in zip(points, points[1:]):
        length = math.hypot(bx - ax, bz - az)
        for i in range(max(1, int(length / step) + 1)):
            t = min(i * step / length, 1.0)
            cx, cz = ax + (bx - ax) * t, az + (bz - az) * t
            dirt_tile(piece, cx + fr.uniform(-0.25, 0.25), cz + fr.uniform(-0.25, 0.25), fr.uniform(0.95, 1.15), free=True)  # giro livre: borda irregular
            if fr.random() < 0.8:  # ladrilho pequeno ao lado: desmancha a quina da borda
                side = fr.choice([-1, 1]) * fr.uniform(1.0, 1.5)
                dirt_tile(piece, cx - (bz - az) / length * side, cz + (bx - ax) / length * side, fr.uniform(0.4, 0.65), free=True)


def dirt_fill(rect, piece="Ground_FarmDirt", chance=1.0):
    x0, z0, x1, z1 = rect
    for ix in range(int((x1 - x0) // 2)):
        for iz in range(int((z1 - z0) // 2)):
            if fr.random() < chance:
                dirt_tile(piece, x0 + 1 + ix * 2, z0 + 1 + iz * 2, 1.0)


for line in (
        [(0, 3), (0, -9), (0, -20), (5, -25), (5, -28)],                 # do portão ao pasto das ovelhas
        [(0, -8), (-8, -8), (-14, -8.6)],                                # até a porta da casa
        [(-8, -8), (-4, -8), (-4, -11)],                                 # portão da horta
        [(0, -9), (9, -8.5), (17, -8.5)],                                # entrada do bunker
        [(0, -20), (-10, -27), (-20, -33.5)],                            # curral dos porcos
        [(5, -25), (14, -30), (21, -32.5)],                              # pasto dos cavalos
        [(5, -24), (16, -26), (28, -26), (33, -30), (34, -36)],          # serraria e ponte (margem oeste)
        [(39.8, -36), (45, -36)]):                                       # depois da ponte
    dirt_path(line)
dirt_fill(GARDEN)                                                         # horta: terra lavrada
dirt_fill((PIGPEN[0] + 0.4, PIGPEN[1] + 0.4, PIGPEN[2] - 0.4, PIGPEN[3] - 0.4), "Ground_FarmMud")
dirt_fill((PADDOCK[0] + 0.4, PADDOCK[1] + 0.4, PADDOCK[2] - 0.4, PADDOCK[3] - 0.4), chance=0.4)
dirt_fill((39.0, -31.0, 47.0, -13.0), chance=0.8)                         # pátio da serraria, no lado leste do riacho
# Capim com mais detalhe: três tufos em quantidade, ervas e flores (Tiny Weeds, Stylish Plants) espalhadas, e bordas mais cheias; fora da
# casa, da horta, da serraria, do riacho, da ponte e da entrada do bunker.
grass_avoid = ([(0, 3, 3), (-14, -12, 5), (-4, -13.5, 6.5), (CREEK_X + 2.1, -22, 6), (17, -10, 3), (CREEK_X, BRIDGE_Z, 4)]
               + [(CREEK_X, z, 3.0) for z in range(-45, -6, 3)] + dirt_spots)
for rd in farm_rooms:
    area_m2 = rd["size"][0] * rd["size"][1]
    farm_decor += scatter(fr, rd, ["Pl_Grass1", "Pl_Grass2", "Pl_Grass3"], int(area_m2 / 5), margin=1.5, scale=(0.7, 2.0), avoid=grass_avoid)
    farm_decor += scatter(fr, rd, ["Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Weed4", "Pl_Weed5"], int(area_m2 / 22), margin=1.5, scale=(0.8, 1.5), avoid=grass_avoid)
    farm_decor += scatter(fr, rd, ["Pl_Flower"], int(area_m2 / 45), margin=1.5, scale=(0.35, 0.6), avoid=grass_avoid)
    farm_decor += ring(fr, rd, ["Pl_Grass1", "Pl_Grass2", "Pl_Grass3", "Pl_Bush", "Pl_Weed2"], 1.8, scale=(1.0, 2.0))
# Fazendeiros (data/crowd.json, papel "farmer"): só caminham pelos campos, de ida e volta, com as ferramentas do pacote Gnarly Tools na mão.
farm_crowd = []
for (x, z), (tx, tz), tool, speed in (
        ((-8, -8.0), (4, -8.0), "Tool_Hoe", 0.9), ((-18, -16), (-18, -26), "Tool_Shovel", 0.8), ((15, -14), (15, -26), "Tool_Pitchfork", 0.9),
        (( -6, -22), (8, -22), "Tool_Scythe", 1.0), ((18, -20), (26, -20), "Tool_Sickle", 0.8), ((18, -28), (26, -28), "Tool_Pitchfork", 0.8),
        ((-24, -10), (-24, -18), "Tool_Hoe", 0.8), ((33, -12), (33, -40), "Tool_Scythe", 1.0)):
    farm_crowd.append({"role": "farmer", "position": [x, z], "rotation": 0, "pose": "idle", "weapon": tool, "path": [tx, tz], "speed": speed})
for i in range(9):  # ovelhas dentro do pasto cercado
    x, z = fr.uniform(PASTURE[0] + 1.5, PASTURE[2] - 1.5), fr.uniform(PASTURE[1] + 1.5, PASTURE[3] - 1.5)
    tx = min(max(x + fr.uniform(-2.5, 2.5), PASTURE[0] + 1.2), PASTURE[2] - 1.2)
    tz = min(max(z + fr.uniform(-2.0, 2.0), PASTURE[1] + 1.2), PASTURE[3] - 1.2)
    farm_crowd.append({"role": "sheep", "position": [round(x, 1), round(z, 1)], "rotation": fr.randrange(0, 360, 15), "pose": "idle",
                       "path": [round(tx, 1), round(tz, 1)], "speed": 0.5})
for role, box, count, speed in (("pig", PIGPEN, 5, 0.5), ("farm_horse", PADDOCK, 3, 0.7)):  # porcos no curral, cavalos no pasto
    for i in range(count):
        x, z = fr.uniform(box[0] + 2.0, box[2] - 2.0), fr.uniform(box[1] + 2.0, box[3] - 2.0)
        tx = min(max(x + fr.uniform(-3, 3), box[0] + 1.6), box[2] - 1.6)
        tz = min(max(z + fr.uniform(-3, 3), box[1] + 1.6), box[3] - 1.6)
        farm_crowd.append({"role": role, "position": [round(x, 1), round(z, 1)], "rotation": fr.randrange(0, 360, 15), "pose": "idle",
                           "path": [round(tx, 1), round(tz, 1)], "speed": speed})
for i, (x, z) in enumerate(((-16, -8), (-6, -7), (-12, -23), (-20, -20), (4, -20), (12, -19), (20, -16), (-4, -25), (8, -8), (24, -24))):  # galinhas soltas
    farm_crowd.append({"role": "chicken", "position": [x, z], "rotation": fr.randrange(0, 360, 15), "pose": "idle",
                       "path": [round(x + fr.uniform(-3.5, 3.5), 1), round(z + fr.uniform(-3.0, 3.0), 1)], "speed": 0.6})
# Galos (Rooster (animated), CDmir, CC0): caminham de ponta a ponta pela fazenda, em trechos mais longos que os das galinhas.
for x, z in ((-2, -4), (22, -24), (-20, -14), (34, -8)):
    farm_crowd.append({"role": "rooster", "position": [x, z], "rotation": fr.randrange(0, 360, 15), "pose": "idle",
                       "path": [round(x + fr.uniform(-6.0, 6.0), 1), round(z + fr.uniform(-5.0, 5.0), 1)], "speed": 0.8})
# Coelhos (Rabbit, cdmir, CC0; o mesmo de Tortuga): pulam pela grama fora dos cercados; o pulo de 1 s fica no lugar enquanto o Wanderer anda.
for x, z in ((-24, -24), (10, -20), (4, -4), (-6, -42), (30, -10), (31, -40), (42, -14), (-22, -6)):
    farm_crowd.append({"role": "rabbit", "position": [x, z], "rotation": fr.randrange(0, 360, 15), "pose": "idle",
                       "path": [round(x + fr.uniform(-4.0, 4.0), 1), round(z + fr.uniform(-3.5, 3.5), 1)], "speed": 0.9})
# Cestos de vime (Willow Basket with Handle, ulf, CC-BY-SA 3.0; Pr_Basket): quebráveis que sempre soltam poção (tabela breakable_potion).
monster("basket", "pot", _comment="Cesto de vime da Fazenda (Willow Basket with Handle, ulf, CC BY-SA 3.0): quebra com qualquer golpe e sempre solta poção (data/loot.json 'breakable_potion'). Não dá XP.",
        name_key="PROP_BASKET", max_health=8, size=0.8, look="basket", pieces=["Pr_Basket"], shards=False, color=[0.75, 0.6, 0.3])
farm_baskets = [{"id": "bk%d" % (i + 1), "monster": "basket", "position": pos, "table": "breakable_potion"} for i, pos in enumerate(
    ([-16.6, -8.3], [-11.6, -8.3], [-6.4, -7.2], [-10.0, -21.5], [7.6, -25.6], [-20.0, -31.8], [33.8, -13.6], [41.4, -30.0], [-12.4, -33.2], [22.4, -31.8]))]
arenas["farm_01_fields"] = {
    "_comment": "Fazenda: campos abertos com capim (Grass Pack 01, Yughues / Nobiax, CC0), casa de fazenda (CC0), serraria movida a água (CC0) com a roda sobre um riacho, barricadas de toras (Sullivan, CC-BY), fazendeiros com ferramentas (Retextured Gnarly Tools, Mev Lyshkin, CC-BY) e ovelhas (p0ss, CC-BY-SA). Só o mapa por enquanto: sem monstros, lojas, baús nem missões (só cestos quebráveis que soltam poção); portal em Tortuga ao lado do da Floresta e entrada do Bunker no canto nordeste dos campos. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_FARM", "town": True, "outdoor": True, "player_class": "mage", "map_id": "map_farm", "area_level": 1,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": farm_rooms, "encounters": [], "hazards": [],
    "entries": {"start": [0, 3], "farm": [0, 3], "bunker": [17.0, -7.6]},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "forest"},
        {"id": "to_bunker", "kind": "exit", "name_key": "PROP_TO_BUNKER", "position": [17.0, -9.0], "to": "bunker_01_entrance", "entry": "start", "group": True},
        {"id": "creek", "kind": "water", "position": [CREEK_X, -26], "size": [CREEK_W, 38], "color": [0.18, 0.36, 0.45]},
        {"id": "mine_gate", "kind": "exit", "name_key": "PROP_TO_MINE", "position": [26, -12], "to": "mine_01_crystal_vein", "entry": "start"},
    ],
    "quest_spots": [], "breakables": farm_baskets,
    "style": {"_comment": "Fazenda: chão de capim (Ground_FarmGrass, texturas contínuas de Lattice, CC0), cerca baixa de madeira nas bordas.", "walls": [""], "floor": "Ground_FarmGrass",
              "low": "Prop_WoodenFence_Single", "ground": [0.2, 0.28, 0.12]},
    "decor": farm_decor, "crowd": farm_crowd, "passive": True,
}
# Portal de Tortuga para a Fazenda (ao lado do da Floresta; sem duplicar se o script rodar de novo).
tortuga_props = arenas["tortuga"]["props"]
if not any(p["id"] == "farm_gate" for p in tortuga_props):
    tortuga_props.append({"id": "farm_gate", "kind": "exit", "name_key": "PROP_TO_FARM", "position": [-27.5, 3.2], "to": "farm_01_fields", "entry": "start"})

# --- Docas (ligadas ao porto de Tortuga; Modular Wooden Docks, loafbrr, CC0) ---------------------------------
dr2 = rng("docks")
dk_rooms = [
    room("landing", 0, 0, 20, 10, ["north"], torch=True, wall_height=0.8),
    room("pier_main", 0, -12, 8, 14, ["south", "north"], wall_height=0.8),
    room("crossing", 0, -25, 40, 8, ["south", "west", "east", "north"], wall_height=0.8),
    room("west_pier", -26, -25, 12, 8, ["east"], wall_height=0.8),
    room("east_pier", 26, -25, 12, 8, ["west"], wall_height=0.8),
    room("end_pier", 0, -37, 10, 16, ["south"], wall_height=0.8),
]
dk_enc = [
    {"id": "dk_rats_a", "position": [0, -12], "monsters": [{"monster": "plague_frog", "count": 4}]},
    {"id": "dk_toads", "position": [-24, -23], "monsters": [{"monster": "acid_toad", "count": 3}]},
    {"id": "dk_bats", "position": [26, -25], "monsters": [{"monster": "plague_bat", "count": 4}]},
    {"id": "dk_rats_b", "position": [0, -40], "monsters": [{"monster": "mutant_frog", "count": 3}, {"monster": "angler", "count": 2}]},
    {"id": "dk_anglers", "position": [-26, -25], "monsters": [{"monster": "angler", "count": 2}]},
]
dk_decor = []
for bx, bz, rot, piece in ((-12, -14, 20, "Dock_Boat_A_1"), (12, -15, -15, "Dock_Boat_B_1"), (-14, -33, 80, "Dock_Boat_A_2"), (14, -34, 100, "Dock_Boat_A_1"), (-8, 6, 0, "Dock_Boat_B_1")):
    dk_decor.append({"piece": piece, "position": [bx, bz], "y": -0.2, "rotation": rot})
dk_decor.append({"piece": "Dock_Boat_Stand", "position": [10, 8], "rotation": 90})
for x in (-9, 9):
    for z in (3, -4):
        dk_decor.append({"piece": "Dock_Dock_Bollard_1", "position": [x, z], "y": 0.12, "solid": [0.4, 0.4]})
for z in (-8, -16):
    for x in (-3, 3):
        dk_decor.append({"piece": "Dock_Dock_Bollard_1", "position": [x, z], "y": 0.12, "solid": [0.4, 0.4]})
crates = ["Dock_Props_Barrel", "Dock_Props_Crate", "Dock_Props_Box"]
for cx, cz in ((-7, 2), (7, 1), (-18, -26), (-30, -23), (22, -27), (30, -23), (-3, -33), (3, -42), (-3, -29), (7, -24)):
    for k in range(dr2.randint(2, 3)):
        dk_decor.append({"piece": dr2.choice(crates), "position": [round(cx + dr2.uniform(-0.8, 0.8), 1), round(cz + dr2.uniform(-0.8, 0.8), 1)],
                         "y": 0.12, "rotation": dr2.randrange(0, 360, 15)})
dk_decor += [{"piece": "Dock_Props_Rack_Fish", "position": [-24, -28], "y": 0.12, "solid": [2.4, 1.1]}, {"piece": "Dock_Props_Rack", "position": [24, -28], "y": 0.12, "solid": [2.4, 1.1]},
             {"piece": "Dock_Props_Table_1", "position": [-8, -29.5], "y": 0.12, "solid": [1.8, 1.1]}, {"piece": "Dock_Props_Bench", "position": [-8, -27.8], "y": 0.12},
             {"piece": "Pr_LampPost", "position": [-5, -3], "y": 0.12, "solid": [0.6, 0.6]}, {"piece": "Pr_LampPost", "position": [5, -22], "y": 0.12, "solid": [0.6, 0.6]},
             {"piece": "Pr_LampPost", "position": [0, -43], "y": 0.12, "solid": [0.6, 0.6]}]
arenas["docks_01_pier"] = {
    "_comment": "Docas, ligadas ao porto de Tortuga (Modular Wooden Docks, loafbrr, CC0): píeres de madeira sobre o mar, com barcos, defensas, barris e caixotes; saída para o porto no sul. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_DOCKS", "player_class": "mage", "map_id": "map_docks", "area_level": 2, "outdoor": True,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": dk_rooms, "encounters": dk_enc, "hazards": [],
    "entries": {"start": [0, 3], "docks": [0, 3]},
    "props": [
        {"id": "sea", "kind": "water", "position": [0, -22], "size": [110, 90]},
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_TO_PORT", "position": [-4, 3], "to": "tortuga", "entry": "docks"},
        {"id": "dock_chest_1", "kind": "chest", "position": [-30, -27], "loot": "chest"},
        {"id": "dock_chest_2", "kind": "chest", "position": [0, -44], "loot": "chest"},
    ],
    "quest_spots": [], "breakables": [],
    "style": {"_comment": "Docas: tábuas de píer do pacote, cerca de madeira nas bordas; o mar é o objeto 'sea'.", "walls": [""], "floor": "Dock_Floor_Dock_Half",
              "low": "Dock_Fence_Plane_Half", "ground": [0.03, 0.1, 0.16]},
    "decor": dk_decor, "passive": True,
}
arenas["tortuga"]["entries"]["docks"] = [0, -26]
arenas["tortuga"]["props"] = [p for p in arenas["tortuga"]["props"] if p["id"] != "docks_gate"] + [
    {"id": "docks_gate", "kind": "exit", "name_key": "PROP_TO_DOCKS", "position": [3, -26.8], "to": "docks_01_pier", "entry": "start"}]

# --- Bolsa de moedas: uma por mapa de expedição; ao bater nela, cai ouro (data/loot.json "coin_bag") --------
for key in ("docks_01_pier", "sewers_01_drains", "sewers_02_canals", "sewers_03_war_passage", "sewers_04_nest", "forest_01_path", "ruins_01_city",
            "cemetery_01_yard", "dark_forest_01_woods", "fort_01_gate", "mine_01_crystal_vein"):
    area = arenas[key]
    start = area["entries"]["start"]
    boxes = [b for b in area.get("breakables", []) if b.get("id") != "coin_bag"]
    boxes.append({"id": "coin_bag", "monster": "coin_bag", "position": [round(start[0] + 4.0, 1), round(start[1] - 1.5, 1)], "table": "coin_bag"})
    area["breakables"] = boxes
monster("coin_bag", "pot", _comment="Bolsa de moedas (Bag of Coins, yd, CC0): uma por mapa; quebra com qualquer golpe e solta ouro (data/loot.json 'coin_bag'). Não dá XP.",
        name_key="PROP_COIN_BAG", max_health=6, size=0.8, look="coin_bag", pieces=["Coin_Bag"], shards=False, color=[0.8, 0.6, 0.2])

# --- Bunker (3D Dungeon Modular Wall Set 2, Paul Wortmann, CC0; entrada pela Fazenda) --------------------
# Grade de células de 2 m (o módulo das peças Bk_*): salão de entrada, corredor, sala principal com dois nichos e uma câmara ao
# fundo. Uma parede em cada divisa entre célula aberta e pedra, e um pilar onde as paredes viram, terminam ou se cruzam.
BK_COLS, BK_ROWS, BK_CELL = 16, 20, 2.0
bk_grid = [["#"] * BK_COLS for _ in range(BK_ROWS)]


def bk_carve(c0, r0, c1, r1):
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            bk_grid[r][c] = "."


bk_carve(6, 15, 9, 17)    # salão de entrada
bk_carve(7, 10, 8, 14)    # corredor
bk_carve(3, 3, 12, 9)     # sala principal
bk_carve(1, 5, 2, 6)      # nicho oeste
bk_carve(13, 5, 14, 6)    # nicho leste
bk_carve(7, 1, 8, 2)      # câmara do fundo


def bk_open(c, r):
    return 0 <= c < BK_COLS and 0 <= r < BK_ROWS and bk_grid[r][c] == "."


def bk_pos(c, r):
    return [round((c - BK_COLS / 2 + 0.5) * BK_CELL, 2), round((r - BK_ROWS / 2 + 0.5) * BK_CELL, 2)]


bk_h, bk_v = set(), set()  # h[(i, j)]: parede do vértice (i, j) ao (i+1, j); v[(i, j)]: do vértice (i, j) ao (i, j+1)
for r in range(BK_ROWS):
    for c in range(BK_COLS):
        if bk_open(c, r):
            if not bk_open(c, r - 1):
                bk_h.add((c, r))
            if not bk_open(c, r + 1):
                bk_h.add((c, r + 1))
            if not bk_open(c - 1, r):
                bk_v.add((c, r))
            if not bk_open(c + 1, r):
                bk_v.add((c + 1, r))
bk_decor = []
for r in range(BK_ROWS):
    for c in range(BK_COLS):
        if not bk_open(c, r):  # o piso do estilo cobre a sala toda: blocos de rocha tapam o que fica fora das paredes
            bk_decor.append({"piece": "Bk_Rock", "position": bk_pos(c, r)})
half_w, half_h = BK_COLS * BK_CELL / 2, BK_ROWS * BK_CELL / 2
for i, j in sorted(bk_h):
    x, z = (i + 0.5) * BK_CELL - half_w, j * BK_CELL - half_h
    bk_decor.append({"piece": "Bk_Wall", "position": [round(x, 2), round(z, 2)], "rotation": 90})
    bk_decor.append({"collider": [BK_CELL, 0.5], "position": [round(x, 2), round(z, 2)]})
for i, j in sorted(bk_v):
    x, z = i * BK_CELL - half_w, (j + 0.5) * BK_CELL - half_h
    bk_decor.append({"piece": "Bk_Wall", "position": [round(x, 2), round(z, 2)]})
    bk_decor.append({"collider": [0.5, BK_CELL], "position": [round(x, 2), round(z, 2)]})
for i in range(BK_COLS + 1):
    for j in range(BK_ROWS + 1):
        edges = ((i - 1, j) in bk_h, (i, j) in bk_h, (i, j - 1) in bk_v, (i, j) in bk_v)  # oeste, leste, norte, sul
        if not any(edges) or edges in ((True, True, False, False), (False, False, True, True)):
            continue  # sem parede, ou parede reta passando
        x, z = i * BK_CELL - half_w, j * BK_CELL - half_h
        bk_decor.append({"piece": "Bk_Pillar", "position": [round(x, 2), round(z, 2)]})
        bk_decor.append({"collider": [0.9, 0.9], "position": [round(x, 2), round(z, 2)]})
# Lampiões de parede (Lamp, Mev Lyshkin, CC-BY 3.0; Pr_WallLamp), cada um com a sua luz: (coluna, linha, lado da parede), na célula aberta.
BK_SIDES = {"W": (-1, 0, 90), "E": (1, 0, 270), "N": (0, -1, 0), "S": (0, 1, 180)}  # direção da parede e giro do braço (para dentro da sala)
for lc, lr, side in ((6, 16, "W"), (9, 16, "E"), (7, 12, "W"), (8, 12, "E"), (5, 3, "N"), (10, 3, "N"), (3, 8, "W"), (12, 8, "E"),
                     (1, 5, "W"), (14, 5, "E"), (7, 1, "N")):
    cx, cz = bk_pos(lc, lr)
    dx, dz, turn = BK_SIDES[side]
    bk_decor.append({"piece": "Pr_WallLamp", "position": [round(cx + dx * 0.75, 2), round(cz + dz * 0.75, 2)], "y": 2.3, "rotation": turn})
    bk_decor.append({"light": [1.0, 0.65, 0.3], "position": [round(cx + dx * 0.2, 2), round(cz + dz * 0.2, 2)], "y": 1.9, "range": 7.0, "energy": 1.2})
arenas["bunker_01_entrance"] = {
    "_comment": "Bunker (3D Dungeon Modular Wall Set 2, Paul Wortmann, CC0): grade de células de 2 m com paredes e pilares do pacote (Bk_*) e lampiões de parede (Lamp, Mev Lyshkin, CC-BY), uma parede em cada divisa entre piso e pedra, colisão por parede e pilar. Salão de entrada, corredor, sala principal com dois nichos e câmara ao fundo; por enquanto só o mapa (sem monstros, baús nem missões). Entrada pela Fazenda. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_BUNKER", "player_class": "mage", "map_id": "map_bunker", "area_level": 2,
    "wake_radius": 10.0, "alert_radius": 5.0,
    "rooms": [room("bunker", 0, 0, BK_COLS * BK_CELL, BK_ROWS * BK_CELL, [], wall_height=0.8, torch=False)],
    "encounters": [], "hazards": [], "entries": {"start": bk_pos(8, 16)},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_FARM", "position": bk_pos(6, 16), "to": "farm_01_fields", "entry": "bunker"},
    ],
    "quest_spots": [], "breakables": [],
    "style": {"_comment": "Bunker: piso de lajotas do kit; paredes, pilares e blocos de rocha do pacote em decor.", "walls": [""], "floor": "Floor_Brick", "low": "", "ground": [0.05, 0.05, 0.06]},
    "decor": bk_decor, "passive": True,
}

json.dump(arenas, open(ARENAS, "w"), indent=2, ensure_ascii=False); open(ARENAS, "a").write("\n")
json.dump(monsters, open(MONSTERS, "w"), indent=2, ensure_ascii=False); open(MONSTERS, "a").write("\n")
import subprocess, sys
subprocess.run([sys.executable, "tools/assets/add_minibosses.py"], check=True)  # 2 mini-chefes por mapa + drops das relíquias
subprocess.run([sys.executable, "tools/assets/add_fish.py"], check=True)  # peixes no riacho da Fazenda e no mar das Docas
subprocess.run([sys.executable, "tools/assets/build_desert.py"], check=True)  # mapa do Deserto ligado à Fazenda
print("OK", [k for k in arenas if k.split("_")[0] in ("forest", "ruins", "cemetery", "fort", "farm", "mine")])
