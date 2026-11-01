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
fr = rng("forest")
f_rooms = [
    room("gate", 0, 0, 24, 14, ["north"], torch=True, wall_height=0.8),
    room("glade", 0, -17.5, 34, 21, ["south", "north", "east"], wall_height=0.8),
    room("side", 23, -17.5, 12, 21, ["west"], wall_height=0.8),
    room("path", 0, -34, 10, 12, ["south", "north"], wall_height=0.8),
    room("grove", 0, -62, 36, 44, ["south"], wall_height=0.8),
]
f_enc = [
    {"id": "f_toads", "position": [-8, -17], "monsters": [{"monster": "acid_toad", "count": 2}]},
    {"id": "f_rats", "position": [8, -22], "monsters": [{"monster": "mutant_rat", "count": 3}]},
    {"id": "f_side", "position": [23, -18], "monsters": [{"monster": "golden_lizard", "count": 2}]},
    {"id": "f_path", "position": [0, -34], "monsters": [{"monster": "plague_bat", "count": 3}]},
    {"id": "f_grove_a", "position": [-9, -52], "monsters": [{"monster": "acid_toad", "count": 3}]},
    {"id": "f_grove_b", "position": [9, -54], "monsters": [{"monster": "mutant_rat", "count": 4}]},
    {"id": "f_leshy", "position": [0, -76], "monsters": [{"monster": "leshy", "count": 1}]},
]
# Um golem de cada: Pedra na clareira, Gelo na sala lateral, Fogo no bosque; e o bando de répteis no bosque. Entram depois de f_keep para não mudar o sorteio das plantas.
f_extra = [{"id": "f_golem_stone", "position": [-2, -23], "monsters": [{"monster": "golem_stone", "count": 1}]},
            {"id": "f_golem_ice", "position": [22, -12], "monsters": [{"monster": "golem_ice", "count": 1}]},
            {"id": "f_golem_fire", "position": [0, -62], "monsters": [{"monster": "golem_fire", "count": 1}]},
            {"id": "f_reptiles", "position": [-13, -58], "monsters": [{"monster": "forest_reptile", "count": 3}]},
            {"id": "f_beasts", "position": [9, -14.5], "monsters": [{"monster": "chitin_beast", "count": 2}]}]
# --- Trilhas e setores da Floresta (a mesma lógica do Cemitério) ----------------------------------------------------
# Uma pista central de lajes serpenteia do portão ao Leshy (reta nas portas) e se ramifica: a oeste leva à aldeia, a leste a um beco
# sem saída com baú; no bosque duas pistas laterais (oeste, com baú no fim; leste) se separam e se reencontram perto do Leshy, ligadas
# ao centro por travessias. Os monstros ficam em setores, separados por pares de marcos de pedra em cada pista:
#   portão (seguro) -> A Clareira (sapos, ratos, bestas, o golem de pedra; ramais: aldeia e beco do leste com o golem de gelo)
#   -> B Passagem (morcegos) -> C Bosque (sapos, ratos, répteis, o golem de fogo) -> D Covil do Leshy (o Leshy, o baú do fundo).
F_BORDERS = (-26, -38, -64)    # z dos marcos entre os setores A|B, B|C e C|D


def f_m(z):
    """Pista do centro: reta no portão e na passagem, serpenteia na clareira (meio período) e no bosque (um período), e volta ao centro nas portas."""
    if -28 < z < -7:
        return 3.0 * math.sin(math.pi * (z + 7) / 21.0)
    if -76 < z < -40:
        return 5.0 * math.sin(math.pi * (z + 40) / 18.0)
    return 0.0


def f_pts(f, za, zb, step=3):
    zs = list(range(za, zb, -step)) + [zb]
    return [(round(f(z), 2), z) for z in zs]


def f_at(line, z):
    """x da pista `line` (pontos com z decrescente) em z."""
    for (x0, z0), (x1, z1) in zip(line, line[1:]):
        if z1 <= z <= z0 and z0 != z1:
            return x0 + (x1 - x0) * (z - z0) / (z1 - z0)
    return line[-1][0]


F_M = f_pts(f_m, 1, -79) + [(0.0, -82)]
F_W_VILLAGE = [(round(f_m(-12), 2), -12), (-8, -14.5), (-14, -16.6), (-17, -17.5), (-23, -18.4), (-29.5, -18.8), (-34.5, -19.8)]   # ramal até a aldeia
F_E_ALLEY = [(round(f_m(-14), 2), -14), (7, -15.2), (13, -17), (17, -17.5), (21, -18.2), (24.5, -20.5)]                           # beco do leste (baú)
F_W_LANE = [(round(f_m(-42), 2), -42), (-6, -46.5), (-12, -52), (-14.5, -58), (-13, -65), (-14, -70), (-14, -73.5)]               # oeste: acaba num beco (baú)
F_E_LANE = [(round(f_m(-42), 2), -42), (5, -46), (11, -52.5), (14, -60), (13, -67), (9, -73), (4, -77.5), (0.0, -79)]            # leste: volta ao centro
f_trails = [F_M, F_W_VILLAGE, F_E_ALLEY, F_W_LANE, F_E_LANE,
            [(-6, 3), (-2.5, 2.4), (0.0, 1.0)],                                                                                    # do portal de volta à pista
            [(-14.5, -58), (-7, -58.5), (0.0, -58)], [(13, -67), (9, -66.6), (round(f_m(-67), 2), -67)]]                          # travessias do bosque


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
for rd in f_rooms:
    f_decor += ring(fr, rd, ["Pl_Bamboo", "Pl_Bamboo", "Pl_Bush"], 2.4, scale=(0.9, 1.5))
    f_decor += scatter(fr, rd, plants, int(rd["size"][0] * rd["size"][1] / 22), margin=2.0, avoid=[(0, 3, 3)])
# Pedras (Rocks, Nobiax, CC0 + Low Poly Rocks, para, CC0): semente própria para não mexer no sorteio das plantas. As grandes bloqueiam, as pequenas são só enfeite.
ROCK_FOOTPRINT = {"Rock_1": 0.9, "Rock_2": 0.75, "Rock_3": 1.2, "Rock_4": 1.0, "Rock_5": 0.75,
                  "RockP_1": 0.9, "RockP_2": 1.1, "RockP_3": 1.0, "RockP_4": 1.0, "RockP_5": 1.0, "RockP_6": 0.95}
rkr = rng("forest_rocks")
f_keep = [(0, 3, 4), (-6, 3, 3), (0, -82, 4), (24, -22, 3), (-14, -74, 3)] + [(e["position"][0], e["position"][1], 3) for e in f_enc]
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
# Nenhuma pedra (sólida) onde um golem nasce.
f_decor = [d for d in f_decor if not (d["piece"].startswith("Rock_") and any(math.hypot(d["position"][0] - g["position"][0], d["position"][1] - g["position"][1]) < 3.5 for g in f_extra))]
# Árvores mortas (Dead Tree, piacenti, CC BY 3.0): troncos secos com raízes à mostra, semente própria; o tronco bloqueia (colisor pequeno).
dtr = rng("forest_dead_trees")
for rd in f_rooms:
    for tree in scatter(dtr, rd, ["Dead_Tree"], int(rd["size"][0] * rd["size"][1] / 110), margin=4.0, scale=(0.6, 1.1), avoid=f_keep):
        side = round(0.9 * tree["scale"], 1)
        tree["solid"] = [side, side]
        f_decor.append(tree)
f_decor += [{"piece": "Pr_RoadSign", "position": [4, 2], "rotation": 200}, {"piece": "Pr_LampPost", "position": [-6, 3], "rotation": 0, "solid": [0.6, 0.6]},
            {"piece": "Pr_Obelisk3", "position": [0, -80], "solid": [1.4, 1.4]}, {"piece": "Pr_Obelisk2", "position": [-6, -78], "solid": [1.0, 1.0]},
            {"piece": "Pr_Obelisk2", "position": [6, -78], "solid": [1.0, 1.0]}, {"piece": "Pr_BrokenPillar2", "position": [-12, -70], "solid": [1.2, 1.2]},
            {"piece": "Pr_BrokenPillar1", "position": [12, -68], "solid": [1.2, 1.2]}, {"piece": "Pr_CoveredWell", "position": [-8, -4], "solid": [1.8, 1.8]}]
# Poucos cervos: semente própria, longe das portas, do portal, dos baús, da saída, dos grupos de monstros, dos adereços fixos e uns dos outros.
f_deer = []
dr_ = rng("forest_deer")
f_fixed = [(4, 2, 3), (-8, -4, 4), (0, -80, 5), (-6, -78, 3), (6, -78, 3), (-12, -70, 3), (12, -68, 3)]
for rd, count in ((f_rooms[1], 2), (f_rooms[2], 1), (f_rooms[4], 2), (f_rooms[0], 1)):  # clareira, lateral, bosque, portão
    for spot in scatter(dr_, rd, ["deer"], count, margin=4.0, avoid=f_keep + f_fixed + [(g["position"][0], g["position"][1], 5) for g in f_extra] + f_samples() + [(d["position"][0], d["position"][1], 10) for d in f_deer]):
        f_deer.append({"id": "d%d" % (len(f_deer) + 1), "monster": "deer_buck" if len(f_deer) % 2 == 0 else "deer_doe",
                       "position": spot["position"], "table": "breakable_potion"})
# --- Aldeia de Ferncroft (Medieval Props Pack 3, Daniel Andersson, CC0; casas do kit de Tortuga) ---------------------------------------------
# Sala nova a oeste da clareira (porta no meio da parede). Os encontros e o sorteio das outras salas ficam como estavam: a porta nova da
# clareira só entra na lista final de salas, e o que o sorteio pôs na passagem é tirado depois.
village_room = room("village", -29, -17.5, 24, 21, ["east"], wall_height=0.8)
f_rooms_out = [dict(r, doors=r["doors"] + ["west"]) if r["id"] == "glade" else r for r in f_rooms] + [village_room]
f_decor = [d for d in f_decor if not (-20.5 < d["position"][0] < -13.5 and abs(d["position"][1] + 17.5) < 3.6)]


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
    {"piece": "Vl_TanningStand", "position": [-30.2, -24.4], "solid": [2.2, 0.5]},
    {"piece": "Vl_FishRack", "position": [-21.0, -22.0], "solid": [2.1, 0.4]},
    {"piece": "Vl_Ladder", "position": [-33.2, -25.2], "rotation": 0, "y": 0.0},
    {"piece": "Well_Covered", "position": [-27.5, -15.5], "solid": [1.8, 1.8]},
    {"piece": "Cart_Wood", "position": [-30.0, -9.6], "rotation": 15, "solid": [2.4, 1.3]},
    {"piece": "Wheelbarrow", "position": [-34.5, -12.3], "rotation": 340, "solid": [1.0, 0.8]},
    {"piece": "Barrel", "position": [-32.0, -26.3], "solid": [0.9, 0.9]},
    {"piece": "Barrel", "position": [-22.0, -26.2], "solid": [0.9, 0.9]},
    {"piece": "Crate_Wooden", "position": [-31.0, -26.4], "rotation": 20, "solid": [0.9, 0.9]},
    {"piece": "Bucket_Wooden_1", "position": [-26.2, -16.9]},
    {"piece": "Stool_Wood", "position": [-35.9, -17.2]},
    {"piece": "Bench_Wood", "position": [-22.6, -19.4], "rotation": 0},
    {"piece": "Mushroom_Cluster", "position": [-40.0, -25.2]}, {"piece": "Mushroom_Tall", "position": [-39.4, -25.8]},
    {"piece": "Mushroom_Flat", "position": [-39.0, -7.9]},
]
vr = rng("forest_village")
v_keep = [(-35, -23, 4.6), (-26, -23.5, 4.6), (-36.5, -10.6, 2.2), (-38.3, -14.6, 1.6), (-27.5, -15.5, 2.0), (-30, -9.6, 2.2),
          (-19, -17.5, 4.0), (-34.5, -19, 2.0), (-30.2, -21.2, 2.0), (-30.2, -24.4, 2.0), (-21, -22, 2.0), (-38.5, -19.9, 2.0), (-37.0, -17.4, 1.5)]
v_decor += ring(vr, village_room, ["Pl_Bamboo", "Pl_Bamboo", "Pl_Bush"], 2.4, scale=(0.9, 1.5))
v_decor += scatter(vr, village_room, ["Pl_Bush", "Pl_Flower", "Pl_Swirl", "Pl_Shrub1", "Pl_Shrub3"], 10, margin=2.5, scale=(0.8, 1.4), avoid=v_keep)
v_decor += scatter(vr, village_room, ["Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Weed4", "Pl_Weed5"], 60, margin=1.5, scale=(1.0, 2.0), avoid=v_keep)
f_decor += v_decor

# Marcos de pedra nas divisas dos setores: um par de cada lado de cada pista, de um tipo por divisa (como no Cemitério).
f_markers = []
for z, (left, right), lanes in zip(F_BORDERS, (("Pr_Obelisk3", "Pr_Obelisk2"), ("Pr_Cross4", "Pr_Cross4"), ("Pr_BrokenPillar2", "Pr_BrokenPillar2")),
                                   ((("M", F_M, 3.6),), (("M", F_M, 3.4),), (("W", F_W_LANE, 3.6), ("M", F_M, 4.5), ("E", F_E_LANE, 3.6)))):
    for _, line, half in lanes:
        x = f_at(line, z)
        f_markers += [{"piece": left, "position": [round(x - half, 1), z], "solid": [1.4, 1.4]},
                      {"piece": right, "position": [round(x + half, 1), z], "solid": [1.4, 1.4]}]
# Nada sorteado (plantas, pedras) em cima das trilhas ou dos marcos.
f_decor = [d for d in f_decor if not (d["piece"].startswith(("Pl_", "Rock_", "Dead_")) and (
    f_trail_dist(*d["position"]) < (2.6 if d["piece"].startswith(("Rock_", "Dead_")) else 1.9)
    or any(math.hypot(d["position"][0] - m["position"][0], d["position"][1] - m["position"][1]) < 2.2 for m in f_markers)))]
f_decor += f_markers
ft = random.Random("forest_trails")
for line in f_trails:
    f_decor += stone_trail(ft, line)
v_props = [
    {"id": "village_hunter", "kind": "npc", "npc": "village_hunter", "position": [-34.5, -19.0]},
    {"id": "village_wife", "kind": "npc", "npc": "village_wife", "position": [-30.2, -21.2]},
    {"id": "elf_archer", "kind": "npc", "npc": "elf_archer", "position": [-32.0, -16.6], "rotation": 200},
    {"id": "village_sign", "kind": "sign", "name_key": "PROP_VILLAGE_SIGN", "position": [-19.5, -14.6], "text_key": "PROP_VILLAGE_SIGN_TEXT"},
]
arenas["forest_01_path"] = {
    "_comment": "Floresta (04-tortuga-e-missoes.md, missão 3 na ordem do mapa: Tortuga -> Floresta -> Ruínas -> Cemitério -> Forte). Uma pista central de lajes do portão ao Leshy, com ramais (aldeia a oeste, beco do baú a leste) e duas pistas laterais no bosque, e quatro setores de monstros (A Clareira, B Passagem, C Bosque, D Covil do Leshy) separados por pares de marcos de pedra, como no Cemitério. Clareiras abertas com cerca viva de bambu e arbustos (Stylish Plants, Nobiax, CC0), obeliscos e pilares quebrados (Medieval Props Textured). O Leshy guarda o bosque do fundo. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_FOREST", "player_class": "mage", "map_id": "map_forest", "area_level": 3, "outdoor": True,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": f_rooms_out, "encounters": f_enc + f_extra, "hazards": [],
    "entries": {"start": [0, 3], "forest": [0, 3]},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "forest", "expedition_end": True},
        {"id": "to_ruins", "kind": "exit", "name_key": "PROP_TO_RUINS", "position": [0, -82], "to": "ruins_01_city", "entry": "start", "group": True},
        {"id": "forest_chest_1", "kind": "chest", "position": [24, -22], "loot": "chest"},
        {"id": "forest_chest_2", "kind": "chest", "position": [-14, -74], "loot": "chest"},
    ] + v_props,
    "quest_spots": [], "breakables": f_deer,
    "style": {"_comment": "Floresta: sem piso do kit (chão de grama), cerca viva de arbustos nas bordas.", "walls": [""], "floor": "Ground_Grass", "low": "Pl_Bush",
              "ground": [0.12, 0.2, 0.09]},
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
    {"id": "r_lizards_a", "position": [-14, -22], "monsters": [{"monster": "golden_lizard", "count": 3}]},
    {"id": "r_goblins_a", "position": [14, -12], "monsters": [{"monster": "goblin", "count": 4}]},
    {"id": "r_scorp", "position": [12, -28], "monsters": [{"monster": "venom_scorpion", "count": 3}]},
    {"id": "r_bats", "position": [0, -42], "monsters": [{"monster": "plague_bat", "count": 4}]},
    {"id": "r_lizards_b", "position": [-18, -44], "monsters": [{"monster": "golden_lizard", "count": 3}]},
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
# Mapa grande (64 x 324 m de pátio + cripta: o comprimento é 3x o da primeira versão, a largura é a mesma, então a área é 3x) cortado por uma rede de trilhas de pedra, para confundir os heróis:
# três pistas (oeste, centro, leste) saem do portão, se separam e se ligam por travessias; as laterais passam por mais
# grupos de monstros, a do oeste e um ramal do leste terminam em becos sem saída com baú, e só o centro e o leste
# chegam à cripta. Os monstros ficam em setores, separados por pares de marcos de pedra em cada pista:
#   portão (seguro) -> A Campo de Covas (ratos e morcegos) -> B Ossuário (esqueletos e escorpiões)
#   -> C Cova dos Mortos (zumbis) -> D Covil do Troll (o troll, esqueletos) -> cripta (o Senhor da Cripta).
cr = rng("cemetery")
ZS = 3                                  # o pátio é ZS vezes mais comprido que o da primeira versão (104 m -> 312 m)
YARD_W, YARD_TOP, YARD_BOTTOM = 64, -6, -6 - 104 * ZS
c_rooms = [
    room("gate", 0, 0, 22, 12, ["north"], wall_height=0.8, torch=True),
    room("yard", 0, (YARD_TOP + YARD_BOTTOM) / 2, YARD_W, YARD_TOP - YARD_BOTTOM, ["south", "north"], wall_height=0.8),
    room("crypt", 0, YARD_BOTTOM - 10, 24, 20, ["south"], wall_height=0.8),
]
SECTOR_BORDERS = tuple(b * ZS for b in (-38, -66, -92))     # z dos marcos entre os setores A|B, B|C e C|D


def lane_m(z):
    """Pista do centro: serpenteia pelo pátio (meio período a cada 34 m), nasce reta no portão e volta ao centro
    antes da cripta."""
    start = min(1.0, max(0.0, (2 - z) / 12.0))
    end = min(1.0, max(0.0, (z - (YARD_BOTTOM - 2)) / 14.0))
    return 6.0 * math.sin(z * math.pi / 34.0) * start * end


def lane_w(z):
    return -17 + 4.0 * math.sin(z * math.pi / 22.0 + 0.5)


def lane_e(z):
    return 17 + 4.0 * math.sin(z * math.pi / 22.0 + 2.2)


LANES = {"W": lane_w, "M": lane_m, "E": lane_e}


def on(lane, z, off=0.0):
    """Ponto da pista `lane` em z, `off` metros ao lado."""
    return [round(LANES[lane](z) + off, 1), z]


def curve(f, za, zb, step=3):
    zs = list(range(za, zb, -step)) + [zb]
    return [(round(f(z), 2), z) for z in zs]


def connect(a, b, wobble=1.2):
    """Travessia de a até b (pontos x, z), com uma curva leve no meio."""
    return [a, ((a[0] + b[0]) / 2 + wobble, (a[1] + b[1]) / 2), b]


# As trilhas (linhas de pontos): pistas, saídas do portão, travessias e becos.
def P(lane, z):
    return (round(LANES[lane](z), 2), z)


trails = [
    curve(lane_m, 2, YARD_BOTTOM - 2) + [(0.0, YARD_BOTTOM - 12)],        # centro: do portão à porta da cripta
    curve(lane_w, -26, -102 * ZS),                                         # oeste: acaba num beco (baú)
    curve(lane_e, -26, -100 * ZS),                                         # leste: segue até a cripta
    connect(P("M", -14), P("W", -26)),                                     # o centro se abre para o oeste...
    connect(P("M", -14), P("E", -26), -1.2),                               # ...e para o leste
    [P("E", -56 * ZS), (27.0, -56 * ZS)],                                  # beco do leste (baú)
    [P("M", -7), (-16.0, -7)], [P("M", -7), (16.0, -7)],                   # ramais até os túmulos do cavaleiro
    [(0.0, YARD_BOTTOM - 3.5), (-8.5, YARD_BOTTOM - 3.5)], [(0.0, YARD_BOTTOM - 3.5), (8.5, YARD_BOTTOM - 3.5)],   # ramais até as estátuas da cripta
    connect(P("E", -100 * ZS), P("M", YARD_BOTTOM + 2), -1.2),             # o leste volta ao centro antes da cripta
]
# Travessias entre as pistas, uma a cada 24 m, em quatro desenhos que se repetem (oeste-centro, centro-leste, centro-oeste,
# leste-centro); nenhuma cruza as grades das divisas (1,6 m depois de cada marco) e nenhuma nasce em cima de uma praça.
RUNG_PATTERN = (("W", "M", 1), ("M", "E", -1), ("M", "W", 1), ("E", "M", -1))
for i, rung_z in enumerate(range(-44, -98 * ZS, -24)):
    if any(border - 1.6 - 1.5 < rung_z - 4 and rung_z + 1.5 > border - 1.6 for border in SECTOR_BORDERS):
        continue
    if rung_z - 8 < -100 * ZS:
        continue
    lane_a, lane_b, wob = RUNG_PATTERN[i % 4]
    trails.append(connect(P(lane_a, rung_z), P(lane_b, rung_z - 8), 1.2 * wob))


def trail_dist(x, z):
    return min(seg_dist(x, z, a, b) for line in trails for a, b in zip(line, line[1:]))


# Praças de ruínas (mais abaixo): a das Pedras (setor B) e a da Estátua (setor C), cada uma com um mini-chefe.
PLAZA_A = (round(lane_m(-52 * ZS), 1), -52 * ZS)
PLAZA_B = (round(lane_m(-80 * ZS) + 2.6, 1), -80 * ZS)
# Grupos de monstros por setor, ao longo das pistas: em cada setor, posições z igualmente espaçadas, uma pista por vez (oeste,
# centro, leste); no centro o grupo fica ao lado da trilha (os elites, em cima dela). O desenho dos grupos é o da primeira versão,
# com o dobro de grupos para o mapa 3x mais comprido.
er_enc = rng("cemetery_groups")


def sector_groups(tag, z_top, z_bottom, palette):
    out = []
    step = (z_top - z_bottom) / len(palette)
    for i, (monster, count) in enumerate(palette):
        lane = "WME"[i % 3]
        z = round(z_top - step * (i + 0.5))
        off = 0.0 if lane != "M" or monster == "troll" else er_enc.choice((-1, 1)) * 6.0
        out.append({"id": "c_%s_%d" % (tag, i + 1), "position": on(lane, z, off), "monsters": [{"monster": monster, "count": count}]})
    return out


c_enc = []
# A - Campo de Covas: a vermina, para aquecer.
c_enc += sector_groups("a", -28, -38 * ZS + 2, [("plague_rat", 5), ("plague_bat", 4), ("plague_rat", 5), ("plague_rat", 5), ("plague_bat", 4), ("plague_rat", 5)])
# B - Ossuário: esqueletos em bando e escorpiões atirando de longe.
c_enc += sector_groups("b", -38 * ZS - 4, -66 * ZS + 2, [("skeleton", 3), ("venom_scorpion", 3), ("skeleton", 4), ("skeleton", 3), ("venom_scorpion", 3),
                                                      ("skeleton", 3), ("skeleton", 4), ("venom_scorpion", 3), ("skeleton", 3), ("skeleton", 3)])
c_enc.append({"id": "c_plaza_a", "position": [PLAZA_A[0], PLAZA_A[1] + 4.2], "spread": 2.6,    # Praça das Pedras: o mini-chefe e dois esqueletos de guarda
              "monsters": [{"monster": "crypt_scorpion", "count": 1}, {"monster": "skeleton", "count": 2}]})
# C - Cova dos Mortos: zumbis lentos e resistentes.
c_enc += sector_groups("c", -66 * ZS - 4, -92 * ZS + 2, [("zombie", 3), ("zombie", 3), ("zombie", 4), ("zombie", 3), ("zombie", 3), ("zombie", 4), ("zombie", 3), ("zombie", 3)])
# D - Covil do Troll: os elites no centro, esqueletos guardando o beco do oeste e a pista do leste.
c_enc += sector_groups("d", -92 * ZS - 4, YARD_BOTTOM - 4, [("skeleton", 3), ("troll", 1), ("skeleton", 3), ("skeleton", 3), ("troll", 1), ("skeleton", 3)])
c_enc.append({"id": "c_boss", "position": [0, YARD_BOTTOM - 8], "monsters": [{"monster": "crypt_lord", "count": 1}]})
c_props = [
    {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "forest", "expedition_end": True},
    {"id": "to_fort", "kind": "exit", "name_key": "PROP_TO_DARK_FOREST", "position": [0, YARD_BOTTOM - 14], "to": "dark_forest_01_woods", "entry": "start", "group": True},
    {"id": "cemetery_chest_1", "kind": "chest", "position": [28.8, -56 * ZS], "loot": "chest"},     # fim do beco do leste
    {"id": "cemetery_chest_2", "kind": "chest", "position": [round(lane_w(-102 * ZS) - 1.0, 1), -102 * ZS - 2], "loot": "chest"},   # fim da pista do oeste
]

c_decor = []
# Cada peça colocada à mão entra aqui (x, z, raio) para as lápides sorteadas e os arbustos não ficarem em cima.
blockers = [(p["position"][0], p["position"][1], 3.0) for p in c_props] + [(e["position"][0], e["position"][1], 3.2) for e in c_enc]


def put(entry, radius):
    c_decor.append(entry)
    blockers.append((entry["position"][0], entry["position"][1], radius))




def free_spot(x0, z0, clear=4.0, avoid=None):
    """Ponto livre das trilhas (e a 4,5 m de `avoid`, se dado) mais perto de (x0, z0); procura em espiral de 1 m."""
    for r in range(0, 30):
        for k in range(max(8 * r, 1)):
            x, z = x0 + r * math.cos(k * math.tau / max(8 * r, 1)), z0 + r * math.sin(k * math.tau / max(8 * r, 1))
            if trail_dist(x, z) > clear and abs(x) < 26 and (avoid is None or math.hypot(x - avoid[0], z - avoid[1]) > 4.5):
                return [round(x, 1), round(z, 1)]
    return [x0, z0]


well_at = free_spot(-9, -30)
put({"piece": "Pr_CoveredWell", "position": well_at, "solid": [1.8, 1.8]}, 2.2)
put({"piece": "Pr_Trough", "position": free_spot(well_at[0] - 4, well_at[1] + 1, 4.5, avoid=well_at), "rotation": 90, "solid": [3.0, 1.2]}, 2.4)
put({"piece": "Pr_LampPost", "position": [-3, 3], "solid": [0.6, 0.6]}, 1.0)
put({"piece": "Pr_LampPost", "position": [4, -3], "solid": [0.6, 0.6]}, 1.0)
# Marcos de pedra nas divisas dos setores: um par de cada lado de cada pista, de um tipo por divisa.
for z, (left, right) in zip(SECTOR_BORDERS, (("Pr_Obelisk3", "Pr_Obelisk2"), ("Pr_Cross4", "Pr_Cross4"),
                                           ("Pr_BrokenPillar2", "Pr_BrokenPillar2"))):
    for lane, half in (("W", 3.6), ("M", 4.5), ("E", 3.6)):
        put({"piece": left, "position": on(lane, z, -half), "solid": [1.4, 1.4]}, 2.4)
        put({"piece": right, "position": on(lane, z, half), "solid": [1.4, 1.4]}, 2.4)
# Grades pretas de ferro (Fence_Iron, original do jogo; build_iron_fence.py) dividindo os setores: uma linha de ponta a ponta
# do pátio 1,6 m depois de cada divisa (já dentro do setor seguinte), com uma abertura onde cada pista a atravessa. São sólidas:
# só se passa pelas aberturas, e os monstros ficam no setor deles.
FENCE_HALF_GAP = 1.6
for border in SECTOR_BORDERS:
    zf = border - 1.6
    openings = [LANES[l](zf) for l in "WME"]
    for fx in range(-31, 32, 2):
        if any(abs(fx - g) < FENCE_HALF_GAP + 1.0 for g in openings):
            continue
        put({"piece": "Fence_Iron", "position": [fx, zf], "solid": [2.0, 0.3]}, 1.4)
# Duas praças de ruínas (3D Fantasy Ruins Pack, Ron Kapaun, CC0; build_ruins.sh) no meio do pátio, cada uma com um mini-chefe:
#   Praça das Pedras (setor B): o círculo de pedras em pé (Ruin_Stones); o mini-chefe (Escorpião da Cripta) e dois esqueletos já
#   estão lá, dormindo, como qualquer grupo.
#   Praça da Estátua (setor C): o coreto em ruínas (Ruin_Temple2) com a estátua do poste de luz (Statue_Lamp, Colorado Stark,
#   CC0) no meio; falar com a estátua desperta o Guardião do Túmulo (mini-chefe) e dois esqueletos, 4 s depois.
# Cada praça tem piso de lajes, colunas em volta e um arco sobre a trilha do centro, na entrada e na saída.
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
        if abs(math.sin(a)) > 0.85 or trail_dist(x, z) < 1.8:
            continue
        put({"piece": "Ruin_Column" if k % 3 else "Ruin_Pillar", "position": [round(x, 1), round(z, 1)],
             "rotation": pr.randrange(0, 360, 15), "solid": [0.8, 0.8]}, 1.2)
    for dz in (-(PLAZA_R + 2.4), PLAZA_R + 2.4):               # arco sobre a trilha do centro, na entrada e na saída
        z = cz + dz
        x = round(lane_m(z), 1)
        c_decor.append({"piece": "Ruin_Arch", "position": [x, z], "rotation": 0})
        for lx in (-3.07, 3.07):                               # só os pés do arco bloqueiam
            put({"collider": [1.1, 1.1], "position": [round(x + lx, 2), round(z + 0.34, 2)]}, 1.6)
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
                               "monsters": [{"monster": "tomb_guardian", "count": 1}, {"monster": "skeleton", "count": 2}]}})


plaza(PLAZA_A[0], PLAZA_A[1], stones_center)
plaza(PLAZA_B[0], PLAZA_B[1], statue_center)
# Na entrada da cripta.
put({"piece": "Pr_Cross4", "position": [-6, YARD_BOTTOM + 1], "solid": [1.2, 1.2]}, 2.0)
put({"piece": "Pr_Cross4", "position": [6, YARD_BOTTOM + 1], "solid": [1.2, 1.2]}, 2.0)
put({"piece": "Pr_BrokenPillar2", "position": [-9, YARD_BOTTOM - 17], "solid": [1.2, 1.2]}, 2.0)
put({"piece": "Pr_BrokenPillar2", "position": [9, YARD_BOTTOM - 17], "solid": [1.2, 1.2]}, 2.0)
# Estátuas do cavaleiro (Knight Statue, yd, CC0; build_knight_statue.py): um par na entrada do pátio e outro na
# entrada da cripta, viradas um pouco para a trilha (a peça olha para +Z, para quem chega do portão).
for x, z, rot in ((on("M", -10, -4.5)[0], -10, 20), (on("M", -10, 4.5)[0], -10, -20), (-11, YARD_BOTTOM - 4, 25), (11, YARD_BOTTOM - 4, -25)):
    put({"piece": "Statue_Knight", "position": [x, z], "rotation": rot, "solid": [1.1, 1.2]}, 2.0)
# Túmulos do cavaleiro deitado (Knight Lying, yd, CC0): um de cada lado do pátio, perto do portão, com os degraus
# (lado +X da peça) voltados para a trilha.
for x, z, rot in ((-19, -7, 0), (19, -7, 180)):
    put({"piece": "Statue_Knight_Lying", "position": [x, z], "rotation": rot, "solid": [1.9, 1.9]}, 2.6)

# Fileiras de túmulos (cruzes e lápides) por todo o pátio, deixando as trilhas livres.
for zz in range(-16, YARD_BOTTOM + 3, -5):
    for xx in range(-28, 29, 5):
        x = xx + cr.uniform(-0.6, 0.6)
        z = zz + cr.uniform(-0.5, 0.5)
        if cr.random() < 0.18 or trail_dist(x, z) < 2.6 or any(math.hypot(x - bx, z - bz) < br for bx, bz, br in blockers):
            continue
        piece = cr.choice(["Pr_Tombstone1", "Pr_Tombstone2", "Pr_Tombstone3", "Pr_Cross1", "Pr_Cross2", "Pr_Cross3"])
        c_decor.append({"piece": piece, "position": [round(x, 1), round(z, 1)],
                        "rotation": cr.choice([0, 0, 10, -10, 180, 190]), "solid": [0.8, 0.5]})


# Trilha do Cemitério com o solo e as pedras do Mossy Rock Environment Pack (rubberduck, CC0; build_mossy_trail.py): um leito de
# manchas de terra e musgo, lajes de pedra musgosa achatadas por cima e pedras de formação rochosa nas margens (as margens vêm
# mais abaixo, depois dos jarros). A Floresta continua com o stone_trail comum.
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
            and all(math.hypot(x - px, z - pz) > pr for px, pz, pr in plaza_platforms))


for line in trails:
    c_decor += [q for q in trail_bed(tr, line) if trail_piece_ok(q)]
for line in trails:
    c_decor += [q for q in mossy_slabs(tr, line) if trail_piece_ok(q)]

for bush in scatter(cr, c_rooms[1], ["Pl_Hemp", "Pl_Bush"], 90 * ZS, margin=2.0):
    x, z = bush["position"]
    if trail_dist(x, z) > 2.2 and not any(math.hypot(x - bx, z - bz) < br for bx, bz, br in blockers):
        c_decor.append(bush)
# Jarros e garrafas brancos quebráveis, em grupos de quatro ou cinco: metade solta poção de vida e metade de mana
# (tabelas "breakable_hp" e "breakable_mana", sorteadas dentro do grupo). Cada jarro vai para um ponto livre de sólidos,
# de trilhas, de grupos de monstros e de baús, e a pelo menos 0,9 m dos outros.
jr = random.Random("cemetery_jars")
jar_solids = [(d["position"][0], d["position"][1], max(d["solid"]) / 2 + 0.9) for d in c_decor if d.get("solid")]
c_jars = []


def jar_ok(x, z):
    return (abs(x) < 29 and YARD_BOTTOM + 2 < z < 4 and trail_dist(x, z) > 1.9
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


chest_e, chest_w = c_props[2]["position"], c_props[3]["position"]
JAR_CLUSTERS = [(("W", "M"), -30, 4), (("M", "E"), -60, 5), (("W", "M"), -96, 4),                     # setor A
                (("M", "E"), -38 * ZS - 14, 5), (("W", "M"), -38 * ZS - 44, 4), (("M", "E"), -66 * ZS + 24, 5),   # setor B
                (("W", "M"), -66 * ZS - 16, 4), (("M", "E"), -66 * ZS - 46, 5), (("W", "M"), -92 * ZS + 22, 4),   # setor C
                (("M", "E"), -92 * ZS - 14, 5)]                                                         # setor D
for (lane_a, lane_b), cz, count in JAR_CLUSTERS:
    jar_cluster((LANES[lane_a](cz) + LANES[lane_b](cz)) / 2, cz, count)
for cx, cz, count in ((chest_e[0] - 2.5, chest_e[1] + 3.5, 4), (chest_w[0] + 2.5, chest_w[1] + 3.5, 4)):
    jar_cluster(cx, cz, count)
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
            if (abs(x) < 30 and YARD_BOTTOM < z < 5 and trail_dist(x, z) > 1.7
                    and all(math.hypot(x - sx, z - sz) > sr for sx, sz, sr in edge_solids)
                    and all(math.hypot(x - r["position"][0], z - r["position"][1]) > 1.8 for r in edge_rocks)):
                edge_rocks.append({"piece": "Mossy_Formation_%d" % er.randint(1, 4), "position": [round(x, 2), round(z, 2)],
                                   "rotation": er.randrange(0, 360, 15), "scale": round(er.uniform(0.5, 0.9), 2), "y": -0.05})
            t += er.uniform(4.0, 5.5)
c_decor += edge_rocks

# Ossos e crânios espalhados (3D Dungeon Debris - Skull and Bones, Paul Wortmann, CC0; build_bone_debris.py): poucos e soltos no
# setor A, mais e maiores a cada setor, e muitos na cripta. Baixos, sem colisão, fora da trilha, de sólidos, jarros, grupos de
# monstros, praças e pedras das margens.
BONES_SMALL = ["Dungeon_Skull_1", "Dungeon_Skull_2", "Dungeon_Bone"]
BONES_MID = ["Dungeon_CrossBones", "Dungeon_BonePile_1", "Dungeon_Arm", "Dungeon_Leg", "Dungeon_Ribcage", "Dungeon_Pelvis", "Dungeon_Spine"]
BONES_BIG = ["Dungeon_SkullPile", "Dungeon_BonePile_2", "Dungeon_BonePile_3", "Dungeon_BonePile_4", "Dungeon_BonePile_5", "Dungeon_BonePile_6"]
# (nome, quantos, xmax, z de cima, z de baixo, pesos pequeno / médio / grande)
BONE_AREAS = [("A", 8 * ZS, 28, -12, -38 * ZS + 2, (0.8, 0.2, 0.0)), ("B", 14 * ZS, 28, -38 * ZS - 3, -66 * ZS + 2, (0.4, 0.5, 0.1)),
              ("C", 16 * ZS, 28, -66 * ZS - 3, -92 * ZS + 2, (0.25, 0.45, 0.3)), ("D", 14 * ZS, 28, -92 * ZS - 3, YARD_BOTTOM + 2, (0.15, 0.35, 0.5)),
              ("crypt", 10, 10, YARD_BOTTOM - 2, YARD_BOTTOM - 19, (0.2, 0.3, 0.5))]
bn = random.Random("cemetery_bones")
bones = []
for _name, count, xmax, z_top, z_bottom, weights in BONE_AREAS:
    placed = 0
    for _try in range(count * 60):
        if placed >= count:
            break
        x, z = bn.uniform(-xmax, xmax), bn.uniform(z_bottom, z_top)
        group = bn.choices((BONES_SMALL, BONES_MID, BONES_BIG), weights)[0]
        if (trail_dist(x, z) > 1.5
                and all(math.hypot(x - sx, z - sz) > sr for sx, sz, sr in edge_solids)
                and all(math.hypot(x - r["position"][0], z - r["position"][1]) > 1.4 for r in edge_rocks)
                and all(math.hypot(x - b["position"][0], z - b["position"][1]) > 2.2 for b in bones)):
            bones.append({"piece": bn.choice(group), "position": [round(x, 2), round(z, 2)], "rotation": bn.randrange(0, 360, 15),
                          "scale": round(bn.uniform(0.8, 1.25), 2), "y": -0.02})
            placed += 1
c_decor += bones
arenas["cemetery_01_yard"] = {
    "_comment": "Cemitério (Medieval Props Textured, Clint Bellanger, CC BY 3.0, modelos de Lamoot): mapa grande de terra escura cortado por uma rede de trilhas de lajes (três pistas que se separam, se cruzam e se reencontram; becos sem saída com baú) do portão à cripta, com quatro setores de monstros, cada um 3x mais comprido que na primeira versão (A Campo de Covas, B Ossuário, C Cova dos Mortos, D Covil do Troll), marcos de pedra nas divisas, fileiras de lápides e cruzes, poço coberto, estátuas e túmulos de cavaleiro, e a cripta do Senhor da Cripta no fundo. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_CEMETERY", "player_class": "mage", "map_id": "map_cemetery", "area_level": 7, "outdoor": True,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": c_rooms, "encounters": c_enc, "hazards": [],
    "entries": {"start": [0, 3], "cemetery": [0, 3]},
    "props": c_props,
    "quest_spots": [], "breakables": c_jars,
    "style": {"_comment": "Cemitério: chão de terra acinzentada e escura (Ground_Grave, feito por build_ground.py; mais escura e mais cinza que a Ground_Dirt das Ruínas e da Mina), sem piso do kit e sem cercas.", "walls": [""], "floor": "Ground_Grave", "low": "",
              "ground": [0.09, 0.085, 0.08]},
    "decor": c_decor, "passive": True,
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
d_decor += [{"piece": "Pr_Obelisk3", "position": [0, -92], "solid": [1.4, 1.4]}, {"piece": "Pr_Obelisk2", "position": [-7, -90], "solid": [1.0, 1.0]},
            {"piece": "Pr_Obelisk2", "position": [7, -90], "solid": [1.0, 1.0]}, {"piece": "Pr_Cross3", "position": [-26, -26], "solid": [1.0, 1.0]},
            {"piece": "Pr_Cross2", "position": [-24, -18], "solid": [1.0, 1.0]}, {"piece": "Pr_BrokenPillar1", "position": [-10, -60], "solid": [1.2, 1.2]},
            {"piece": "Pr_BrokenPillar2", "position": [10, -46], "solid": [1.2, 1.2]}, {"piece": "Pr_LampPost", "position": [-4, 3], "solid": [0.6, 0.6]}]
arenas["dark_forest_01_woods"] = {
    "_comment": "Floresta Escura (entre o Cemitério e o Forte): a mesma vegetação da Floresta (Stylish Plants), mas mais densa, mais escura e com cruzes esquecidas; uma clareira lateral e o bosque do fundo, por enquanto vazios: só o mapa, sem monstros, chefe nem baús. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_DARK_FOREST", "player_class": "mage", "map_id": "map_dark_forest", "area_level": 8, "outdoor": True,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": d_rooms, "encounters": d_enc, "hazards": [],
    "entries": {"start": [0, 3], "dark_forest": [0, 3]},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "forest", "expedition_end": True},
        {"id": "to_fort", "kind": "exit", "name_key": "PROP_TO_FORT", "position": [0, -95], "to": "fort_01_gate", "entry": "start", "group": True},
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
    {"id": "m_rats", "position": [7, -26], "monsters": [{"monster": "plague_rat", "count": 5}]},
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
COLS, ROWS, CELL = 20, 26, 2.5
grid = [["#"] * COLS for _ in range(ROWS)]


def carve(c0, r0, c1, r1, ch="."):
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            grid[r][c] = ch


carve(2, 1, 17, 6)      # salão do comandante: a saída do labirinto dá para ele
carve(3, 20, 16, 24)    # pátio de entrada
for r, c in ((3, 6), (3, 13), (4, 6), (4, 13), (23, 9), (23, 10)):
    grid[r][c] = "#"

# Labirinto entre o pátio e o salão do comandante: 6 x 4 salas de 2 x 2 células (corredores de 5 m) em uma grade de passo 3 (a
# célula entre duas salas é a parede). Um labirinto perfeito (busca em profundidade a partir da sala de entrada, sorteio fixo): há um
# único caminho da entrada até a saída, mais dois atalhos em laço, e o resto são becos sem saída. A saída é a sala da fileira de
# cima mais longe da entrada; ela se abre para o salão do comandante.
MZ_W, MZ_H = 6, 4
def mz_cell(i, j):
    return 1 + 3 * i, 8 + 3 * j


def mz_nbrs(i, j):
    return [(i + di, j + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= i + di < MZ_W and 0 <= j + dj < MZ_H]


entry_node = (2, MZ_H - 1)


def make_maze(seed):
    mz = rng(seed)
    links, seen, stack = set(), {entry_node}, [entry_node]
    while stack:
        cur = stack[-1]
        opts = [n for n in mz_nbrs(*cur) if n not in seen]
        if opts and mz.random() < 0.8:  # às vezes volta antes de acabar: mais bifurcações e becos curtos
            nxt = mz.choice(opts)
            links.add(frozenset((cur, nxt)))
            seen.add(nxt)
            stack.append(nxt)
        elif opts and len(stack) == 1:
            continue
        else:
            stack.pop()
    for _ in range(1):  # um atalho em laço: o labirinto deixa de ser perfeito, mas os becos continuam
        a = mz.choice(sorted(seen))
        links.add(frozenset((a, mz.choice([m for m in mz_nbrs(*a) if m in seen]))))
    adj = {n: [m for m in mz_nbrs(*n) if frozenset((n, m)) in links] for n in seen}
    dist, parent, queue = {entry_node: 0}, {}, [entry_node]
    for cur in queue:
        for m in adj[cur]:
            if m not in dist:
                dist[m], parent[m] = dist[cur] + 1, cur
                queue.append(m)
    exit_node = max((n for n in dist if n[1] == 0), key=lambda n: dist[n])
    solution = [exit_node]
    while solution[-1] != entry_node:
        solution.append(parent[solution[-1]])
    solution.reverse()  # da sala de entrada até a sala de saída
    deg = {n: len(adj[n]) + (n in (entry_node, exit_node)) for n in adj}
    return links, seen, adj, dist, exit_node, solution, deg


# Primeira semente com todas as salas ligadas, 7 ou mais becos sem saída e um caminho certo de 9 a 13 salas.
for attempt in range(500):
    links, seen, adj, dist, exit_node, solution, deg = make_maze("fort_maze_%d" % attempt)
    if len(seen) == MZ_W * MZ_H and 9 <= len(solution) <= 13 and sum(1 for n in adj if deg[n] == 1) >= 7:
        break
else:
    raise RuntimeError("nenhum labirinto do Forte serve")
for i in range(MZ_W):
    for j in range(MZ_H):
        c, r = mz_cell(i, j)
        carve(c, r, c + 1, r + 1)
for link in links:
    (i, j), (k, m) = sorted(link)
    c, r = mz_cell(i, j)
    if k > i:
        carve(c + 2, r, c + 2, r + 1)
    else:
        carve(c, r + 2, c + 1, r + 2)
carve(mz_cell(*entry_node)[0], mz_cell(*entry_node)[1] + 2, mz_cell(*entry_node)[0] + 1, mz_cell(*entry_node)[1] + 2)  # do pátio para o labirinto
carve(mz_cell(*exit_node)[0], mz_cell(*exit_node)[1] - 1, mz_cell(*exit_node)[0] + 1, mz_cell(*exit_node)[1] - 1)      # do labirinto para o salão
assert len(dist) == MZ_W * MZ_H  # todas as salas ligadas


def is_rock(c, r):
    return c < 0 or r < 0 or c >= COLS or r >= ROWS or grid[r][c] == "#"


def cell_pos(c, r):
    return [round((c - COLS / 2 + 0.5) * CELL, 2), round((r - ROWS / 2 + 0.5) * CELL, 2)]


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
def node_pos(n):
    (c, r), (c2, r2) = cell_pos(*mz_cell(*n)), cell_pos(mz_cell(*n)[0] + 1, mz_cell(*n)[1] + 1)
    return [round((c + c2) / 2, 2), round((r + r2) / 2, 2)]


# Luzes: o salão do comandante e o pátio, e uma a cada duas salas do caminho certo (a luz quente leva até a saída; os becos ficam escuros).
fort_decor += [{"light": [1.0, 0.65, 0.3], "position": cell_pos(c, r), "y": 2.2, "range": 9.0, "energy": 1.4} for c, r in ((4, 3), (15, 3), (9, 23))]
fort_decor += [{"light": [1.0, 0.65, 0.3], "position": node_pos(n), "y": 2.2, "range": 8.0, "energy": 1.1} for n in solution[1::2]]
fort_decor += [{"piece": "Pr_Cross4", "position": cell_pos(9, 2), "solid": [1.2, 1.2]}]
# Peças do castelo (3D Castle Dungeon Tileset Extended, rubberduck, CC0; build_castle_kit.py), na mesma altura da pedra do Forte.
# Arcos nas duas passagens norte-sul (entrada e saída do labirinto); colunas e pilares são sólidos, arcos e lajotas não.
(ec, er), (xc, xr) = mz_cell(*entry_node), mz_cell(*exit_node)
castle = [{"piece": "Castle_GateBig", "position": cell_pos(ec + k, er + 2)} for k in (0, 1)]
castle += [{"piece": "Castle_GateBig", "position": cell_pos(xc + k, xr - 1)} for k in (0, 1)]
castle += [{"piece": "Castle_" + n, "position": cell_pos(c, r), "solid": [0.9, 0.9]} for n, c, r in (
    ("Column", 4, 2), ("Column", 4, 5), ("Column", 15, 2), ("Column", 15, 5), ("EdgeColumn", 5, 22), ("EdgeColumn", 14, 22))]
castle += [{"piece": "Castle_Dais", "position": cell_pos(9, 1)}, {"piece": "Castle_Altar", "position": cell_pos(12, 2), "solid": [1.2, 1.2]}]
castle += [{"piece": "Castle_Tiles", "position": [round(cell_pos(8, 4)[0] + i * 1.3, 2), round(cell_pos(8, 4)[1] + j * 1.3 + 1.5, 2)]}
           for i in range(4) for j in range(3)]
fort_decor += castle
# Peças do Labirinto (3D Walls & Props, deadkir, CC0; build_labyrinth_kit.py): caixões no salão do comandante, barris e caixotes no pátio
# e o escudo com a espada caídos perto do comandante; cada sala do labirinto ganha, no canto, barris, um caixote, um caixão, ruínas,
# uma coluna ou nada (sorteio fixo).
lab = [{"piece": "Lab_" + n, "position": cell_pos(c, r), "rotation": rot, "solid": [w, d]} for n, c, r, rot, w, d in (
    ("Coffin", 6, 6, 0, 2.0, 0.9), ("Coffin", 13, 6, 0, 2.0, 0.9),
    ("Barrel", 4, 23, 0, 0.6, 0.6), ("Barrel", 15, 23, 0, 0.6, 0.6), ("Barrel", 3, 21, 0, 0.6, 0.6), ("Barrel", 16, 21, 0, 0.6, 0.6),
    ("Crate", 3, 24, 0, 0.6, 0.6), ("Crate", 16, 24, 0, 0.6, 0.6), ("Crate", 3, 22, 0, 0.6, 0.6), ("Crate", 16, 22, 0, 0.6, 0.6))]
lab.append({"piece": "Lab_ShieldSword", "position": cell_pos(8, 5), "rotation": 25})
md = rng("fort_maze_decor")
for n in sorted(seen):
    if n == entry_node:
        continue
    cx, cz = node_pos(n)
    sx, sz = md.choice((-1, 1)), md.choice((-1, 1))
    bx, bz = round(cx + sx * 1.0, 2), round(cz + sz * 1.0, 2)
    kind = md.choice(("barrels", "crate", "coffin", "ruin", "column", "none", "none"))
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
# Canhões de navio (Ship Cannon, jameswhite, CC0; build_cannon.py), a boca para +Z com rotação 0: dois no pátio apontados para o forte e dois
# no salão do comandante apontados para a entrada.
fort_decor += [{"piece": "Ship_Cannon", "position": cell_pos(c, r), "rotation": rot, "solid": [0.8, 1.5]}
               for c, r, rot in ((4, 24, 180), (15, 24, 180), (3, 1, 0), (16, 1, 0))]
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
    if len(wt_placed) == 16:
        break
for i, (x, z, dx, dz) in enumerate(wt_placed):
    face = [round(x + dx * (CELL / 2 - 0.02), 2), round(z + dz * (CELL / 2 - 0.02), 2)]
    fort_decor.append({"piece": "Wall_Torch", "position": face, "rotation": round(math.degrees(math.atan2(-dx, -dz)))})
    if i % 2 == 0:
        fort_decor.append({"light": [1.0, 0.6, 0.25], "position": [round(x - dx * 0.2, 2), round(z - dz * 0.2, 2)], "y": 1.9, "range": 5.5, "energy": 0.9})
# Ratos pequenos de cenário (papel "rat" do NpcModel): correm de um canto a outro pelas celas, pelo salão do meio e pelo pátio,
# sempre entre duas células de piso a até 3 células de distância, com sorteio fixo.
fr = rng("fort_rats")
floor_cells = [(c, r) for r in range(ROWS) for c in range(COLS) if grid[r][c] != "#"]
fort_rats = []
while len(fort_rats) < 14:
    c, r = fr.choice(floor_cells)
    c2, r2 = c + fr.randint(-3, 3), r + fr.randint(-3, 3)
    if (c2, r2) == (c, r) or not (0 <= c2 < COLS and 0 <= r2 < ROWS) or grid[r2][c2] == "#":
        continue
    if any(grid[r + round((r2 - r) * t / 6)][c + round((c2 - c) * t / 6)] == "#" for t in range(7)):
        continue  # o caminho não atravessa pedra
    a, b = cell_pos(c, r), cell_pos(c2, r2)
    fort_rats.append({"role": "rat", "position": [round(a[0] + fr.uniform(-0.8, 0.8), 2), round(a[1] + fr.uniform(-0.8, 0.8), 2)],
                      "path": b, "speed": round(fr.uniform(1.2, 2.2), 1), "pose": "walk"})
# Encontros e baús nas salas do labirinto: os baús nos becos mais fundos, quatro encontros espalhados pelo caminho certo, o resto nos
# outros becos e salas (os mais longe da entrada primeiro). O comandante e as súcubos do salão ficam no salão do comandante.
used = {entry_node}
deg = {n: len(adj[n]) + (n in (entry_node, exit_node)) for n in adj}
leaves = sorted((n for n in adj if deg[n] == 1), key=lambda n: -dist[n])
far = sorted(adj, key=lambda n: -dist[n])
path_mid = [n for n in solution if n != entry_node]
spaced = []
for k in range(4):
    n = path_mid[int((k + 0.5) * len(path_mid) / 4)]
    if n not in spaced:
        spaced.append(n)


def take(cands):
    for n in cands + far:
        if n not in used:
            used.add(n)
            return n


chest_spots = [take(leaves) for _ in range(5)]
fort_chests = [{"id": i, "kind": "chest", "position": node_pos(n), **extra} for i, n, extra in zip(
    ("fort_chest_1", "fort_chest_2", "fort_potions_1", "fort_potions_2", "fort_potions_3"), chest_spots,
    ({"loot": "chest"}, {"loot": "chest"}, {"loot": "potion_chest", "model": "Chest_Potion"}, {"loot": "potion_chest", "model": "Chest_Potion"},
     {"loot": "potion_chest", "model": "Chest_Potion"}))]
fort_encounters = []
for eid, cands, kind_id, count in (
        ("fo_elves_gate", spaced, "dark_elf", 2), ("fo_succubi_hall", spaced, "succubus", 2), ("fo_elves_hall_w", spaced, "dark_elf", 2),
        ("fo_elves_hall_e", spaced, "dark_elf", 2), ("fo_cell_w", leaves, "golden_lizard", 3), ("fo_cell_e", leaves, "venom_scorpion", 3),
        ("fo_hall_a", far, "plague_bat", 4), ("fo_hall_b", far, "mutant_rat", 4)):
    fort_encounters.append({"id": eid, "position": node_pos(take(cands)), "monsters": [{"monster": kind_id, "count": count}]})
fort_encounters += [{"id": "fo_succubi_court", "position": cell_pos(9, 5), "monsters": [{"monster": "succubus", "count": 2}]},
                    {"id": "fo_commander", "position": cell_pos(9, 3), "monsters": [{"monster": "fort_commander", "count": 1}]}]
arenas["fort_01_gate"] = {
    "_comment": "Forte (3D Dungeon Tileset, Skorpio, CC BY-SA 3.0): uma grade de 20 x 26 células de 2,5 m com pedra e piso do pacote (Fort_<máscara>, a máscara é o 8-vizinhança de pedra); a colisão é uma caixa por trecho de pedra. Do pátio de entrada, um labirinto de salas de 2 x 2 células com becos sem saída (um único caminho certo, mais dois atalhos) leva ao salão do comandante no fundo. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_FORT", "player_class": "mage", "map_id": "map_fort", "area_level": 10,
    "wake_radius": 10.0, "alert_radius": 5.0,
    "rooms": [room("fort", 0, 0, COLS * CELL, ROWS * CELL, [], wall_height=0.8, torch=False)],
    "encounters": fort_encounters,
    "hazards": [], "entries": {"start": cell_pos(8, 24)},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [cell_pos(5, 24)[0], cell_pos(5, 24)[1]], "to": "tortuga", "entry": "forest", "expedition_end": True},
        {"id": "to_capital", "kind": "exit", "name_key": "PROP_TO_CAPITAL", "position": [cell_pos(9, 1)[0], cell_pos(9, 1)[1] - 1.0], "to": "capital_01_aurenhold", "entry": "start", "after_victory": True, "group": True},
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
    room("gate", 0, 0, 24, 14, ["north"], torch=True, wall_height=0.8),
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
# Capim com mais detalhe: três tufos em quantidade, ervas e flores (Tiny Weeds, Stylish Plants) espalhadas, e bordas mais cheias; fora da
# casa, da horta, da serraria, do riacho, da ponte e da entrada do bunker.
grass_avoid = ([(0, 3, 3), (-14, -12, 5), (-4, -13.5, 6.5), (CREEK_X + 2.1, -22, 6), (17, -10, 3), (CREEK_X, BRIDGE_Z, 4)]
               + [(CREEK_X, z, 3.0) for z in range(-45, -6, 3)])
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
    "style": {"_comment": "Fazenda: chão de grama, cerca baixa de madeira nas bordas.", "walls": [""], "floor": "Ground_Grass",
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
    {"id": "dk_rats_a", "position": [0, -12], "monsters": [{"monster": "plague_rat", "count": 4}]},
    {"id": "dk_toads", "position": [-24, -23], "monsters": [{"monster": "acid_toad", "count": 3}]},
    {"id": "dk_bats", "position": [26, -25], "monsters": [{"monster": "plague_bat", "count": 4}]},
    {"id": "dk_rats_b", "position": [0, -40], "monsters": [{"monster": "mutant_rat", "count": 3}, {"monster": "angler", "count": 2}]},
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
print("OK", [k for k in arenas if k.split("_")[0] in ("forest", "ruins", "cemetery", "fort", "farm", "mine")])
