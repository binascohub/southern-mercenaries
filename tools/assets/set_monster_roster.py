"""Cada mapa tem os seus próprios monstros (só o Mímico e os guardiões dos portões se repetem), todos macabros e ligados ao cenário. Os mapas da Floresta e do Esgoto NÃO são tocados:
os modelos deles (frog, toad, chitin_beast, fungus, forest, forest_troll, golem_fire, golem_stone, golem_king, troll_mauler, mutant, barbarian_monster, champ_warrior, shadow_spirit,
demon_twelve, necromancer, demon_boss) ficam fora dos outros mapas.
Para cada mapa: troca cada tipo de monstro dos encontros e das invocações por um monstro novo do mapa (clone dos números do antigo, com nome, visual e cor próprios) ou muda o visual dos
mini-chefes e chefes. Quem não achou um modelo diferente fica com o visual "placeholder" (uma cápsula com a cor do tema; o campo "visual_pending" marca os que esperam arte).
Os modelos novos vêm do OpenGameArt (CC0), convertidos por tools/assets/build_oga_monsters.py; textos pt/en/es acrescentados aos .po.
Chamado no fim de tools/assets/build_maps.py (depois dos geradores dos mapas, antes de set_map_order.py); idempotente.
uso: python3 tools/assets/set_monster_roster.py   (a partir da raiz do projeto)"""
import json, re, copy
ARENAS, MONSTERS = "data/arenas.json", "data/monsters.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
monsters = json.load(open(MONSTERS, encoding="utf-8"))
FLYERS = {"bat", "stalker", "raven", "ghost_wing", "tentacleye"}
NAMES = {}                  # name_key -> (pt, en, es)
PENDING = []


def make(arena, old, new, names, look, color=(1.0, 1.0, 1.0), size=1.0, sound="beast", **extra):
    """Cria o monstro `new` (clone de `old`) e troca `old` por `new` nos encontros e invocações de `arena`."""
    if old in monsters and new != old:
        m = copy.deepcopy(monsters[old])
    elif new in monsters:
        m = copy.deepcopy(monsters[new])
    else:
        raise KeyError(old)
    m.pop("_comment", None)
    if new != old:
        m.pop("quest_drop", None)          # só o monstro original solta a relíquia da missão
    m["name_key"] = "MONSTER_" + new.upper()
    NAMES[m["name_key"]] = names
    m["look"] = look
    m["color"] = list(color)
    m["size"] = round(float(monsters.get(old, m).get("size", 1.0)) * size, 2)
    if look not in FLYERS:
        m.pop("flyer", None)
    if look == "placeholder":
        m["sound"] = sound
        m["visual_pending"] = True
        PENDING.append(new)
    else:
        m.pop("sound", None)
        m.pop("visual_pending", None)
    m.update(extra)
    m["_comment"] = "Monstro de %s (%s): %s." % (arena.split("_")[0], names[0], "visual pendente (sem modelo ainda)" if look == "placeholder" else "modelo %s" % look)
    monsters[new] = m
    if new != old:
        swap(arena, old, new)


def swap(arena, old, new):
    a = arenas[arena]
    for e in a.get("encounters", []):
        for x in e["monsters"]:
            if x["monster"] == old:
                x["monster"] = new
    for p in a.get("props", []):
        for s in ([p["summon"]] if p.get("summon") else []) + [x["summon"] for x in p.get("extra_summons", [])]:
            for x in s["monsters"]:
                if x["monster"] == old:
                    x["monster"] = new


def restyle(monster, names, look, color=(1.0, 1.0, 1.0), sound="giant", **extra):
    """Muda só o visual de um monstro que continua com o mesmo id (mini-chefes e chefes)."""
    m = monsters[monster]
    m["look"] = look
    m["color"] = list(color)
    if names:
        NAMES[m["name_key"]] = names
    if look == "placeholder":
        m["sound"] = sound
        m["visual_pending"] = True
        PENDING.append(monster)
    else:
        m.pop("sound", None)
        m.pop("visual_pending", None)
    m.update(extra)


P = "placeholder"
# ------------------------------------------------------------------ Docas: o porto afogado
A = "docks_01_pier"
make(A, "plague_frog", "dk_drowned", ("Marujo Afogado", "Drowned Sailor", "Marinero Ahogado"), P, (0.4, 0.62, 0.55), sound="shade")
make(A, "acid_toad", "dk_gator", ("Jacaré do Cais", "Dock Alligator", "Caimán del Muelle"), "gator", (0.55, 0.7, 0.5))
make(A, "plague_bat", "dk_crab", ("Caranguejo Carniceiro", "Carrion Crab", "Cangrejo Carroñero"), "crab", size=1.1, sound="beetle")
make(A, "mutant_frog", "dk_deckhand", ("Pirata Morto", "Dead Pirate", "Pirata Muerto"), P, (0.55, 0.5, 0.35), sound="shade")
restyle("angler", None, "angler")
restyle("drowned_captain", None, "octaminator", (0.75, 1.0, 0.9))
restyle("hull_beast", None, "plank_monster", (0.55, 0.75, 0.7))
# ------------------------------------------------------------------ Ruínas: a cidade destruída na guerra
A = "ruins_01_city"
make(A, "venom_scorpion", "ru_ghost", ("Soldado Fantasma", "Ghost Soldier", "Soldado Fantasma"), "ghost_wing", (0.8, 0.85, 1.0), size=1.2)
make(A, "plague_bat", "ru_hound", ("Cão de Guerra Morto", "Dead War Hound", "Perro de Guerra Muerto"), P, (0.35, 0.3, 0.28), sound="beast")
restyle("ruin_alpha", None, P, (0.3, 0.28, 0.3), sound="wolfman")
restyle("ruin_warden", None, "golem_block", (0.9, 0.9, 1.0))
restyle("war_champion", None, P, (0.7, 0.3, 0.25), sound="ogre")
restyle("fallen_king", None, P, (0.7, 0.6, 0.85), sound="giant")
# ------------------------------------------------------------------ Cemitério
A = "cemetery_01_yard"
make(A, "plague_frog", "ce_digger", ("Coveiro Louco", "Mad Gravedigger", "Sepulturero Loco"), P, (0.45, 0.4, 0.3), sound="beast")
make(A, "venom_scorpion", "ce_maggot", ("Verme de Cova", "Grave Maggot", "Gusano de Tumba"), P, (0.85, 0.8, 0.6), sound="slime")
make(A, "golem_stone", "ce_gargoyle", ("Gárgula de Lápide", "Tombstone Gargoyle", "Gárgola de Lápida"), P, (0.5, 0.5, 0.55), sound="giant")
make(A, "plague_bat", "ce_ghoul", ("Carniçal Inchado", "Bloated Ghoul", "Necrófago Hinchado"), "fatty", (0.8, 0.85, 0.7), size=1.0, sound="ogre")
make(A, "troll", "ce_brute", ("Ogro Coveiro", "Gravedigger Ogre", "Ogro Sepulturero"), P, (0.45, 0.5, 0.4), sound="ogre")
make(A, "tomb_guardian", "ce_warden", ("Sentinela do Túmulo", "Tomb Sentinel", "Centinela de la Tumba"), P, (0.55, 0.58, 0.62), sound="giant")
restyle("skeleton", None, "skeleton")
restyle("zombie", None, "zombie")
restyle("crypt_scorpion", None, P, (0.45, 0.55, 0.4), sound="ogre")
restyle("crypt_lord", None, "undead")
# ------------------------------------------------------------------ Forte
A = "fort_01_gate"
make(A, "plague_bat", "fo_imp", ("Diabrete Aranha", "Spider Imp", "Diablillo Araña"), "exp_demon", size=1.1, sound="shade")
make(A, "venom_scorpion", "fo_hound", ("Cão do Inferno", "Hellhound", "Perro Infernal"), P, (0.5, 0.15, 0.1), sound="wolfman")
swap(A, "mutant_frog", "night_demon")
restyle("night_demon", None, "night_demon")
restyle("dark_elf", None, "dark_elf")
restyle("succubus", None, "succubus")
restyle("fort_commander", None, "demon")
restyle("fort_baron", None, "glutton", (1.0, 0.8, 0.78))
# ------------------------------------------------------------------ Catacumbas
A = "catacombs_01_depths"
make(A, "skeleton", "ct_prisoner_dead", ("Preso Esquelético", "Skeletal Prisoner", "Preso Esquelético"), P, (0.8, 0.78, 0.7), sound="shade")
make(A, "zombie", "ct_crawler", ("Rastejante das Celas", "Cell Crawler", "Reptante de las Celdas"), "crawlmaster", size=1.0, sound="shade")
make(A, "plague_bat", "ct_eye", ("Olho de Tentáculos", "Tentacle Eye", "Ojo de Tentáculos"), "tentacleye", size=1.0, sound="slime")
make(A, "shadow_spirit", "ct_wretch", ("Miserável Acorrentado", "Chained Wretch", "Miserable Encadenado"), "sonask", size=1.0, sound="shade")
make(A, "night_demon", "ct_ghoul", ("Carniçal da Cela", "Cell Ghoul", "Necrófago de Celda"), P, (0.45, 0.5, 0.45), sound="shade")
make(A, "champ_warrior", "ct_guard", ("Guarda Acorrentado", "Chained Guard", "Guardia Encadenado"), P, (0.55, 0.55, 0.65), sound="ogre")
make(A, "barbarian_monster", "ct_torturer", ("Torturador Encapuzado", "Hooded Torturer", "Torturador Encapuchado"), P, (0.5, 0.25, 0.25), sound="ogre")
make(A, "stalker", "ct_bonebat", ("Morcego de Ossos", "Bone Bat", "Murciélago de Huesos"), P, (0.85, 0.85, 0.75), sound="beast")
make(A, "demon_twelve", "ct_tormentor", ("Atormentador", "Tormentor", "Atormentador"), P, (0.5, 0.2, 0.35), sound="giant")
make(A, "troll_mauler", "ct_deadjailer", ("Carcereiro Morto", "Dead Jailer", "Carcelero Muerto"), P, (0.4, 0.4, 0.5), sound="ogre")
restyle("ct_headsman", None, "ogre", (0.8, 0.6, 0.6))
restyle("ct_soul", None, P, (0.55, 0.75, 1.0), sound="shade")
restyle("ct_king", None, "darsh", (0.8, 0.85, 1.0))
# ------------------------------------------------------------------ Deserto
A = "desert_01_canyon"
restyle("venom_scorpion", None, "scorpion")
make(A, "chitin_beast", "de_scarab", ("Escaravelho Devorador", "Devouring Scarab", "Escarabajo Devorador"), "alien_bug", size=1.3, sound="beetle")
make(A, "stalker", "de_vulture", ("Abutre Carniceiro", "Carrion Vulture", "Buitre Carroñero"), P, (0.3, 0.25, 0.22), sound="beast")
make(A, "goblin", "de_cobra", ("Naja das Dunas", "Dune Cobra", "Cobra de las Dunas"), "cobra", size=1.1, sound="beast")
make(A, "troll", "de_cactus", ("Cacto Carnívoro", "Carnivorous Cactus", "Cactus Carnívoro"), "cactus", size=1.0, sound="ogre")
restyle("queen_scorpion", None, "scorpion", (1.0, 0.7, 0.55))
restyle("sand_lamassu", None, "earth_dragon")
restyle("sphinx", None, P, (1.0, 0.85, 0.5), sound="giant")
# ------------------------------------------------------------------ Mina
A = "mine_01_crystal_vein"
restyle("stalker", None, "stalker")
make(A, "plague_bat", "mn_spider", ("Aranha das Cavernas", "Cave Spider", "Araña de las Cavernas"), "spider_big", size=1.2, sound="beetle")
make(A, "goblin", "mn_digger", ("Mineiro Morto", "Dead Miner", "Minero Muerto"), P, (0.5, 0.42, 0.3), sound="beast")
make(A, "venom_scorpion", "mn_worm", ("Verme de Rocha", "Rock Worm", "Gusano de Roca"), P, (0.55, 0.5, 0.45), sound="slime")
make(A, "mutant", "mn_gnome", ("Gnomo das Sombras", "Shadow Gnome", "Gnomo de las Sombras"), P, (0.3, 0.3, 0.45), sound="beast")
make(A, "skeleton", "mn_bones", ("Esqueleto de Mineiro", "Miner's Skeleton", "Esqueleto de Minero"), P, (0.8, 0.75, 0.65), sound="shade")
make(A, "golem_fire", "mn_magma", ("Golem de Magma", "Magma Golem", "Gólem de Magma"), "lava_golem", size=1.0, sound="giant")
make(A, "golem_stone", "mn_rock", ("Golem de Rocha", "Rock Golem", "Gólem de Roca"), P, (0.5, 0.48, 0.45), sound="giant")
make(A, "troll_mauler", "mn_cave_troll", ("Troll das Cavernas", "Cave Troll", "Troll de las Cavernas"), "troll", (0.8, 0.85, 0.9), sound="ogre")
restyle("golem_ice", None, "golem_ice")
restyle("crystal_golem", None, "golem_ice", (0.7, 0.8, 1.0))
restyle("troll_chief", None, "troll")
restyle("tomb_guardian", None, P, (0.55, 0.58, 0.62), sound="giant")
restyle("mn_quartz_beast", None, P, (0.5, 0.75, 1.0), sound="beetle")
# ------------------------------------------------------------------ Bunker
A = "bunker_01_entrance"
make(A, "skeleton", "bk_dead", ("Soldado Morto", "Dead Soldier", "Soldado Muerto"), P, (0.55, 0.55, 0.45), sound="shade")
make(A, "goblin", "bk_scavenger", ("Saqueador do Bunker", "Bunker Scavenger", "Saqueador del Búnker"), P, (0.45, 0.4, 0.3), sound="beast")
make(A, "plague_bat", "bk_rat", ("Ratazana de Paiol", "Magazine Rat", "Rata de Polvorín"), "rat", (0.7, 0.6, 0.55), size=1.3, sound="beast")
make(A, "plague_frog", "bk_gas", ("Soldado Infectado", "Infected Soldier", "Soldado Infectado"), "hazmat", sound="shade")
make(A, "champ_warrior", "bk_plate", ("Armadura Vazia", "Empty Armor", "Armadura Vacía"), P, (0.6, 0.62, 0.7), sound="ogre")
make(A, "venom_scorpion", "bk_beetle", ("Besouro de Guerra", "War Beetle", "Escarabajo de Guerra"), P, (0.3, 0.35, 0.25), sound="beetle")
make(A, "zombie", "bk_infected", ("Recruta Infectado", "Infected Recruit", "Recluta Infectado"), P, (0.55, 0.7, 0.45), sound="shade")
make(A, "barbarian_monster", "bk_brute", ("Brutamontes de Trincheira", "Trench Brute", "Bruto de Trinchera"), P, (0.5, 0.4, 0.35), sound="ogre")
make(A, "shadow_spirit", "bk_specter", ("Espectro do Rádio", "Radio Specter", "Espectro de la Radio"), P, (0.5, 0.6, 0.55), sound="shade")
restyle("bk_armor", None, P, (0.85, 0.85, 0.95), sound="ogre")
restyle("bk_commander", None, P, (0.65, 0.85, 0.55), sound="shade")
restyle("bk_general", None, "mutant_grunt", (1.0, 0.8, 0.7))
# ------------------------------------------------------------------ Floresta Escura
A = "dark_forest_01_woods"
make(A, "stalker", "fd_raven", ("Corvo Negro", "Black Raven", "Cuervo Negro"), "raven", size=1.2, sound="beast")
make(A, "goblin", "fd_wolf", ("Lobisomem", "Werewolf", "Hombre Lobo"), "werewolf", sound="wolfman")
make(A, "venom_scorpion", "fd_widow", ("Viúva da Mata", "Forest Widow", "Viuda del Bosque"), P, (0.15, 0.1, 0.18), sound="beetle")
make(A, "fungus_uncle", "fd_mushroom", ("Cogumelo Carniceiro", "Carrion Mushroom", "Hongo Carroñero"), "mushroom_cap", size=1.6, sound="ogre")
make(A, "zombie", "fd_hanged", ("Enforcado", "Hanged Man", "Ahorcado"), P, (0.5, 0.45, 0.35), sound="shade")
make(A, "skeleton", "fd_hunter", ("Caçador Esquelético", "Skeletal Hunter", "Cazador Esquelético"), P, (0.75, 0.72, 0.6), sound="shade")
make(A, "night_demon", "fd_stag", ("Cervo Espectral", "Spectral Stag", "Ciervo Espectral"), P, (0.5, 0.6, 0.7), sound="beast")
make(A, "shadow_spirit", "fd_wisp", ("Fogo-Fátuo", "Will-o'-the-Wisp", "Fuego Fatuo"), P, (0.5, 0.9, 0.6), sound="shade")
restyle("plague_bat", None, "bat")
restyle("forest_reptile", None, "reptile")
restyle("fd_viper", None, "reptile")
restyle("fd_spore_king", None, P, (0.85, 0.65, 1.0), sound="ogre")
restyle("fd_elder", None, "horror")

# ------------------------------------------------------------------ confere: nenhum visual repetido entre os mapas (fora a Floresta, o Esgoto e o Mímico)
from collections import defaultdict
FIXED = {"sewers_01_drains", "forest_01_path"}
used = defaultdict(set)
for k, v in arenas.items():
    for e in v.get("encounters", []):
        for x in e["monsters"]:
            used[monsters[x["monster"]]["look"]].add(k)
    for p in v.get("props", []):
        for s in ([p["summon"]] if p.get("summon") else []) + [x["summon"] for x in p.get("extra_summons", [])]:
            for x in s["monsters"]:
                used[monsters[x["monster"]]["look"]].add(k)
dupes = {look: sorted(maps) for look, maps in used.items() if look not in (P, "chest_mimic") and len(maps) > 1}
if dupes:
    print("AVISO visuais repetidos entre mapas:", dupes)

json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
json.dump(monsters, open(MONSTERS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(MONSTERS, "a").write("\n")
for lang_i, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po", "locale/messages.pot")):
    t = open(path, encoding="utf-8").read()
    add = ""
    for key, trio in NAMES.items():
        val = "" if path.endswith(".pot") else trio[lang_i].replace('"', '\\"')
        if re.search(r'msgid "%s"\n' % re.escape(key), t):
            if val:
                t = re.sub(r'(msgid "%s"\nmsgstr )"[^\n]*"' % re.escape(key), lambda m: m.group(1) + '"' + val.replace("\\", "\\\\") + '"', t)
        else:
            add += '\nmsgid "%s"\nmsgstr "%s"\n' % (key, val)
    open(path, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + add)
print("OK monstros: %d com visual pendente: %s" % (len(PENDING), ", ".join(sorted(set(PENDING)))))
