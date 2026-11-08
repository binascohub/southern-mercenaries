"""Mapa novo: Colinas dos Cogumelos (mushroom_01_hills), ligado à Capital. Mundo colorido e alegre de colinas, cogumelos gigantes, plataformas de pedra e moedas pelo chão,
com a estrutura da Floresta e das Docas (partida, duas áreas de mini-chefe, guardião do portão e chefe final), no mesmo traçado de salas das Docas:
  Prado de partida -> Trilha -> Vila dos Cogumelos; laço oeste (Ponte Oeste -> Bosque dos Chapéus Gigantes, com o Toco Antigo onde desperta o Bruto Esporento) e laço leste
  (Ponte Leste -> Degraus de Pedra, onde a Moedeira desperta o Jacaré-Musgo), fechando no Bosque dos Esporos e na Gruta de Cristal; Estrada das Flores -> Campo das Moedas
  -> Alameda do Castelo (Guarda da Ponte, duas chaves) -> Pátio do Vulcão do Rei-Lagarto Vulcânico (chefe final, com a saída).
Monstros próprios, com modelos que nenhum outro mapa usa: Coelho-Espora (rabbit), Dragãozinho de Brasa (baby_dragon), Lince das Colinas (lynx), Fantasma de Esporos (ghost_wing);
mini-chefes Jacaré-Musgo (gator) e Bruto Esporento (pork_shark); chefe Rei-Lagarto Vulcânico (lizard).
Missão da cidade: a Botânica Real, na igreja da Capital, abre o mapa depois do Deserto (build_map_mechanics.py a troca pelo item do chefe, a Coroa do Vulcão).
O livro, o altar, as chaves e o item do chefe vêm de build_map_mechanics.py (entrada "mushroom"); força, nível e XP de balance_monsters.py (depois do Deserto).
Sorteio com semente fixa; idempotente; chamado em tools/assets/build_maps.py depois dos geradores dos mapas (antes de build_city_quests.py e build_map_mechanics.py).
uso: python3 tools/assets/build_mushroom_hills.py   (a partir da raiz do projeto)"""
import json, math, random, re

AREA = "mushroom_01_hills"
ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES = ("data/arenas.json", "data/monsters.json", "data/npcs.json", "data/quests.json", "data/valuables.json")
arenas, monsters, npcs, quests, valuables = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES))
rng = random.Random("mushroom-hills-v1")
DOOR = 4.5

# ---------------------------------------------------------------- salas (o traçado das Docas, já conferido: portas e sem sobreposição)
ROOMS = [("meadow", 0, 0, 36, 16), ("clover_patch", -32, 0, 28, 12), ("berry_patch", 32, 0, 28, 12), ("trail", 0, -18, 7, 20), ("village", 0, -46, 64, 36),
         ("west_bridge", -46, -46, 28, 8), ("east_bridge", 46, -46, 28, 8), ("giant_caps", -52, -70, 36, 40), ("stone_steps", 52, -70, 36, 40), ("flower_road", 0, -80, 7, 32),
         ("coin_field", 0, -107, 80, 22), ("spore_grove", -55, -105, 30, 30), ("crystal_hollow", 55, -105, 30, 30), ("castle_lane", 0, -130, 7, 24), ("volcano_court", 0, -170, 70, 56)]
LINKS = [("meadow", "clover_patch", "west"), ("meadow", "berry_patch", "east"), ("meadow", "trail", "north"), ("trail", "village", "north"), ("village", "west_bridge", "west"),
         ("village", "east_bridge", "east"), ("west_bridge", "giant_caps", "north"), ("east_bridge", "stone_steps", "north"), ("village", "flower_road", "north"),
         ("flower_road", "coin_field", "north"), ("giant_caps", "spore_grove", "north"), ("stone_steps", "crystal_hollow", "north"), ("spore_grove", "coin_field", "east"),
         ("crystal_hollow", "coin_field", "west"), ("coin_field", "castle_lane", "north"), ("castle_lane", "volcano_court", "north")]
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}
by_id = {r[0]: r for r in ROOMS}
doors = {r[0]: [] for r in ROOMS}
door_points = []
for a, b, side in LINKS:
    _, ax, az, aw, ah = by_id[a]
    _, bx, bz, bw, bh = by_id[b]
    if side in ("north", "south"):
        lo, hi = max(ax - aw / 2, bx - bw / 2), min(ax + aw / 2, bx + bw / 2)
        edge = az - ah / 2 if side == "north" else az + ah / 2
        assert abs(edge - (bz + bh / 2 if side == "north" else bz - bh / 2)) < 1e-6, (a, b)
        mid = round((lo + hi) / 2 * 2) / 2
        offs = (mid - ax, mid - bx)
        door_points.append((mid, edge))
    else:
        lo, hi = max(az - ah / 2, bz - bh / 2), min(az + ah / 2, bz + bh / 2)
        edge = ax - aw / 2 if side == "west" else ax + aw / 2
        assert abs(edge - (bx + bw / 2 if side == "west" else bx - bw / 2)) < 1e-6, (a, b)
        mid = round((lo + hi) / 2 * 2) / 2
        offs = (mid - az, mid - bz)
        door_points.append((edge, mid))
    assert hi - lo >= DOOR + 2, (a, b)
    for rid, s, off in ((a, side, offs[0]), (b, OPP[side], offs[1])):
        doors[rid].append(s if abs(off) < 1e-6 else "%s:%g" % (s, off))
rooms = []
for rid, cx, cz, w, h in ROOMS:
    r = {"id": rid, "center": [cx, cz], "size": [w, h], "doors": doors[rid], "wall_height": 0.8}
    if rid in ("meadow", "village", "coin_field", "volcano_court"):
        r["torch"] = True
    rooms.append(r)
for i, (_, ax, az, aw, ah) in enumerate(ROOMS):
    for _, bx, bz, bw, bh in ROOMS[i + 1:]:
        assert abs(ax - bx) >= (aw + bw) / 2 - 1e-6 or abs(az - bz) >= (ah + bh) / 2 - 1e-6, "salas sobrepostas"


def room_at(x, z, pad=0.0):
    for r in rooms:
        if abs(x - r["center"][0]) < r["size"][0] / 2 + pad and abs(z - r["center"][1]) < r["size"][1] / 2 + pad:
            return r
    return None


# ---------------------------------------------------------------- monstros (os números de vida/dano/nível vêm de balance_monsters.py, pelo "role")
def base(name_key, look, size, element, ai, role, color, **extra):
    m = {"name_key": name_key, "max_health": 210, "move_speed": 3.2, "damage": 16, "attack_range": 2.0, "attack_windup": 0.7, "attack_cooldown": 1.6, "aggro_range": 40.0,
         "size": size, "category": "common", "element": element, "ai": ai, "look": look, "color": color, "role": role}
    m.update(extra)
    return m


MONS = {
    "mh_bunny": base("MONSTER_MH_BUNNY", "rabbit", 1.1, "earth", "melee", "swarm", [0.95, 0.7, 0.85], move_speed=4.8, attack_range=1.4, attack_windup=0.4, attack_cooldown=1.1, sound="beast",
                     _comment="Coelho-Espora: coelho rosado das colinas que anda em bando e morde rápido."),
    "mh_dragonling": base("MONSTER_MH_DRAGONLING", "baby_dragon", 1.0, "fire", "melee", "light", [1.0, 0.55, 0.35], move_speed=3.8, sound="beast",
                          fireball={"_comment": "Bafo de brasa: cospe uma bolinha de fogo onde o herói está; o chão fica em brasa um instante.", "min": 3.5, "max": 10.0, "windup": 0.8,
                                    "cooldown": 5.5, "radius": 1.5, "damage_mult": 0.8, "element": "fire", "puddle_time": 2.5, "puddle_dps": 4.0, "glob": [1.0, 0.45, 0.1], "glob_size": 0.7},
                          _comment="Dragãozinho de Brasa: filhote de dragão que pula pelas colinas e cospe brasa."),
    "mh_lynx": base("MONSTER_MH_LYNX", "lynx", 1.2, "earth", "charger", "normal", [1.0, 0.85, 0.6], move_speed=4.2, sound="beast",
                    charge={"min": 4.0, "max": 10.0, "windup": 0.8, "speed": 13.0, "time": 0.5, "damage_mult": 1.2, "cooldown": 5.0},
                    _comment="Lince das Colinas: caçador malhado que dá o bote de longe."),
    "mh_ghost": base("MONSTER_MH_GHOST", "ghost_wing", 1.3, "air", "ranged", "light", [0.75, 1.0, 0.8], move_speed=3.0, attack_range=9.0, attack_windup=1.0, attack_cooldown=2.6,
                     keep_distance=6.0, sound="shade",
                     spit={"_comment": "Nuvem de esporos: deixa uma poça de esporos venenosos no chão.", "radius": 2.0, "damage_mult": 0.6, "puddle_time": 4.0, "puddle_dps": 5.0,
                           "glob": [0.55, 0.95, 0.5]},
                     _comment="Fantasma de Esporos: alma alada dos cogumelos velhos; solta nuvens de esporos de longe."),
}
MONS["mh_moss_gator"] = base("MONSTER_MH_MOSS_GATOR", "gator", 2.8, "water", "melee", "normal", [0.6, 0.95, 0.55], move_speed=2.8, attack_range=2.8, attack_windup=0.8,
                             attack_cooldown=1.8, sound="beast", category="miniboss", quest_drop="star_brick",
                             slam={"_comment": "Bote que arrasta: bate o rabo no chão e puxa para a boca quem está em volta.", "interval": 7.5, "radius": 5.5, "windup": 1.0, "damage_mult": 1.1,
                                   "pull": 4.5},
                             waves={"first": 8.0, "interval": 22.0, "radius": 6.0, "toast": "TOAST_MH_GATOR_WAVE",
                                    "list": [[{"monster": "mh_bunny", "count": 4}], [{"monster": "mh_lynx", "count": 2}], [{"monster": "mh_ghost", "count": 1}, {"monster": "mh_bunny", "count": 3}]]},
                             _comment="Mini-chefe das Colinas (Degraus de Pedra): o Jacaré-Musgo, jacaré gigante coberto de musgo que sobe do lago e engoliu o Tijolo-Estrela; bote que arrasta e ondas.")
MONS["mh_spore_brute"] = base("MONSTER_MH_SPORE_BRUTE", "pork_shark", 2.4, "earth", "melee", "normal", [0.8, 0.65, 1.0], move_speed=3.0, attack_range=2.6, sound="ogre",
                              category="miniboss", quest_drop="golden_spore",
                              slam={"_comment": "Sopro de esporos: solta uma nuvem em volta de si que deixa lento quem está perto.", "interval": 7.0, "radius": 5.0, "windup": 1.0,
                                    "damage_mult": 0.9, "slow": [0.45, 2.5]},
                              waves={"first": 8.0, "interval": 22.0, "radius": 6.0, "toast": "TOAST_MH_BRUTE_WAVE",
                                     "list": [[{"monster": "mh_ghost", "count": 2}], [{"monster": "mh_bunny", "count": 4}], [{"monster": "mh_ghost", "count": 1}, {"monster": "mh_lynx", "count": 1}]]},
                              _comment="Mini-chefe das Colinas (Bosque dos Chapéus Gigantes): o Bruto Esporento, gigante lilás coberto de esporos que engoliu o Esporo Dourado.")
MONS["mh_lizard_king"] = base("MONSTER_MH_LIZARD_KING", "lizard", 3.0, "fire", "melee", "normal", [1.0, 0.45, 0.3], move_speed=2.8, attack_range=2.8, attack_windup=0.8,
                              attack_cooldown=1.8, sound="giant", category="boss", aggressive=False, chest_loot="chest",
                              sweep={"_comment": "Rabo de lava: o rabo em brasa varre o chão em volta dele; pule-o ou fique longe.", "interval": 13.0, "windup": 1.3, "duration": 4.5,
                                     "speed": 95.0, "length": 9.0, "width": 1.0, "damage_mult": 0.9},
                              barrage={"_comment": "Chuva do vulcão: pedras em brasa caem uma atrás da outra em volta de cada herói (a primeira em cima dele).", "interval": 11.0, "count": 5,
                                       "radius": 2.2, "spread": 6.0, "delay": 1.4, "step": 0.35, "damage_mult": 0.8, "max": 22.0, "boom": [1.0, 0.45, 0.15]},
                              waves={"first": 10.0, "interval": 20.0, "radius": 7.0, "toast": "TOAST_MH_KING_WAVE",
                                     "list": [[{"monster": "mh_dragonling", "count": 3}], [{"monster": "mh_lynx", "count": 2}, {"monster": "mh_bunny", "count": 2}],
                                              [{"monster": "mh_dragonling", "count": 2}, {"monster": "mh_ghost", "count": 2}], [{"monster": "mh_bunny", "count": 3}, {"monster": "mh_dragonling", "count": 2}]]},
                              _comment="Chefe final das Colinas: o Rei-Lagarto Vulcânico, lagarto gigante em brasa que guarda o Pátio do Vulcão atrás do portão; rabo de lava, chuva do vulcão e ondas.")
for mid, m in MONS.items():
    old = monsters.get(mid, {})
    for keep in ("role", "max_health", "damage", "boss_factor"):  # o balanceamento já ajustado fica (idempotente)
        if keep in old and keep != "role":
            m[keep] = old[keep]
    monsters[mid] = m

# ---------------------------------------------------------------- itens das missões
valuables.update({
    "star_brick": {"name_key": "VALUABLE_STAR_BRICK", "value": 0, "maps": [], "quest_item": True, "model": "Crate_Small"},
    "golden_spore": {"name_key": "VALUABLE_GOLDEN_SPORE", "value": 0, "maps": [], "quest_item": True, "model": "Mushroom_Cluster"},
    "key_sun": {"name_key": "VALUABLE_KEY_SUN", "value": 0, "maps": [], "quest_item": True, "model": "Key_Gold"},
    "key_moon": {"name_key": "VALUABLE_KEY_MOON", "value": 0, "maps": [], "quest_item": True, "model": "Key_Hearts"}})

# ---------------------------------------------------------------- objetos do mapa
SUMMON_BRUTE = {"id": "mh_brute", "position": [-52.0, -62.0], "spread": 3.0, "toast": "TOAST_MH_BRUTE_AWAKENS", "monsters": [{"monster": "mh_spore_brute", "count": 1, "rank": "miniboss"}]}
SUMMON_GATOR = {"id": "mh_gator", "position": [62.0, -80.0], "spread": 3.0, "toast": "TOAST_MH_GATOR_AWAKENS", "monsters": [{"monster": "mh_moss_gator", "count": 1, "rank": "miniboss"}]}
props = [
    {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-4, 3], "to": "capital_01_aurenhold", "entry": "mushroom", "expedition_end": False},
    {"id": "victory_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [0, -195.5], "to": "capital_01_aurenhold", "entry": "mushroom", "after_victory": True, "group": True},
    {"id": "mh_gardener", "kind": "npc", "npc": "mh_gardener", "position": [-6, -46], "rotation": 160},
    {"id": "mh_old_stump", "kind": "npc", "npc": "mh_old_stump", "kit": "Mushroom_Cluster", "solid": [1.4, 1.4], "rotation": 0, "position": [-52.0, -70.0], "summon": SUMMON_BRUTE,
     "needs_quest": "mh_spore"},
    {"id": "mh_coin_keeper", "kind": "npc", "npc": "mh_coin_keeper", "position": [42.0, -60.0], "rotation": 0, "summon": SUMMON_GATOR, "needs_quest": "mh_brick"},
    {"id": "boss_gate", "kind": "gate", "name_key": "PROP_BOSS_GATE", "position": [0.0, -124.0], "rotation": 0, "scale": 1.8, "block": 8.0, "count": 2, "opened_by": "mh_gate"},
    {"id": "mh_bridge_guard", "kind": "npc", "npc": "mh_bridge_guard", "position": [0.0, -120.0], "rotation": 0},
    {"id": "mh_chest_1", "kind": "chest", "position": [-40, -2], "loot": "chest"}, {"id": "mh_chest_2", "kind": "chest", "position": [40, 3], "loot": "chest"},
    {"id": "mh_chest_3", "kind": "chest", "position": [-62, -112], "loot": "chest"}, {"id": "mh_chest_4", "kind": "chest", "position": [62, -112], "loot": "chest"},
    {"id": "mh_chest_5", "kind": "chest", "position": [-28, -58], "loot": "chest"}, {"id": "mh_chest_6", "kind": "chest", "position": [-30, -190], "loot": "chest"},
    {"id": "mh_chest_7", "kind": "chest", "position": [30, -190], "loot": "chest"}]
E = lambda eid, pos, *mons: {"id": eid, "position": pos, "monsters": [{"monster": m, "count": c} for m, c in mons]}
encounters = [
    E("mh_trail", [0, -18], ("mh_bunny", 4)), E("mh_clover", [-32, 0], ("mh_ghost", 2)), E("mh_berries", [32, 0], ("mh_bunny", 4)),
    E("mh_village_a", [-18, -42], ("mh_bunny", 3)), E("mh_village_b", [18, -52], ("mh_lynx", 2)), E("mh_village_c", [-4, -36], ("mh_lynx", 1), ("mh_bunny", 3)),
    E("mh_west_bridge", [-46, -46], ("mh_ghost", 2)), E("mh_east_bridge", [46, -46], ("mh_bunny", 3)),
    E("mh_caps_a", [-62, -80], ("mh_ghost", 3)), E("mh_caps_b", [-42, -58], ("mh_lynx", 2), ("mh_bunny", 2)),
    E("mh_steps_a", [44, -84], ("mh_ghost", 2)), E("mh_steps_b", [62, -58], ("mh_lynx", 2)),
    E("mh_road", [0, -80], ("mh_dragonling", 2), ("mh_bunny", 2)),
    E("mh_spores_a", [-55, -112], ("mh_ghost", 3)), E("mh_spores_b", [-62, -98], ("mh_bunny", 4)), E("mh_crystal_a", [55, -112], ("mh_dragonling", 3)), E("mh_crystal_b", [62, -98], ("mh_lynx", 2)),
    E("mh_coins_a", [-20, -107], ("mh_dragonling", 2), ("mh_bunny", 3)), E("mh_coins_b", [20, -107], ("mh_lynx", 2), ("mh_ghost", 1)),
    E("mh_berry_mimic", [38, 3], ("chest_mimic", 1)), E("mh_caps_mimic", [-60, -60], ("chest_mimic", 1)), E("mh_spore_mimic", [-66, -112], ("chest_mimic", 1)),
    E("mh_crystal_mimic", [66, -112], ("chest_mimic", 1)),
    E("mh_court_a", [-18, -158], ("mh_dragonling", 3)), E("mh_court_b", [18, -158], ("mh_dragonling", 2), ("mh_lynx", 1)),
    E("mh_king", [0, -188], ("mh_lizard_king", 1))]
interest = [p["position"] for p in props] + [e["position"] for e in encounters] + [SUMMON_BRUTE["position"], SUMMON_GATOR["position"], [0, 3]] + [list(d) for d in door_points]


def near_interest(x, z, rad=3.5):
    return any(math.hypot(x - ix, z - iz) < rad for ix, iz in interest)


# ---------------------------------------------------------------- decoração
decor = []
taken = []


def near_taken(x, z, rad=0.0):
    return any(math.hypot(x - tx, z - tz) < tr + rad for tx, tz, tr in taken)


def put(piece, x, z, rot=None, scale=1.0, solid=None, y=0.0, r=0.8, free=2.0, force=False, pad=-0.9):
    if room_at(x, z, pad) is None:
        return False
    if not force and (near_interest(x, z, free) or near_taken(x, z, r)):
        return False
    d = {"piece": piece, "position": [round(x, 1), round(z, 1)], "rotation": int(rot if rot is not None else rng.randrange(0, 360, 15)), "y": y}
    if scale != 1.0:
        d["scale"] = round(scale, 2)
    if solid:
        d["solid"] = [round(solid[0], 1), round(solid[1], 1)]
    decor.append(d)
    taken.append((x, z, r))
    return True


def scatter(rid, pieces, n, scale=(1.0, 1.0), solid=None, margin=2.5, r=0.9, tries=40, **kw):
    cx, cz, w, h = by_id[rid][1:]
    done = 0
    for _ in range(n):
        for _t in range(tries):
            x, z = cx + rng.uniform(-w / 2 + margin, w / 2 - margin), cz + rng.uniform(-h / 2 + margin, h / 2 - margin)
            s = rng.uniform(*scale)
            if put(rng.choice(pieces) if isinstance(pieces, list) else pieces, x, z, scale=s, solid=[solid[0] * s, solid[1] * s] if solid else None, r=r * s, **kw):
                done += 1
                break
    return done


def light(x, z, energy=1.3, rng_=9.0, y=1.6, color=(1.0, 0.6, 0.25), flicker=True):
    decor.append({"light": list(color), "position": [round(x, 1), round(z, 1)], "y": y, "range": rng_, "energy": energy, "flicker": flicker})


def lamp(x, z):
    if put("Lamp_Street_2", x, z, rot=0, solid=[0.6, 0.6], r=0.8, free=1.2):
        light(x, z, 0.9, 8.0, 3.0, (1.0, 0.85, 0.55), False)


def brazier(x, z, scale=1.8):
    if put("Tv_Fire", x, z, rot=0, scale=scale, solid=[0.9 * scale, 0.7 * scale], r=1.3, free=1.2):
        decor.append({"piece": "Fire_Flame", "position": [round(x, 1), round(z, 1)], "y": 0.2, "scale": round(scale * 0.9, 2), "flicker": True})
        light(x, z, 1.6, 11.0, 1.2)


# Cogumelos gigantes (as peças do kit são pequenas: Mushroom_Tall 0,65 m de altura, Mushroom_Flat 0,52 m de largura, Mushroom_Cluster 0,8 m): (escala mínima, máxima, colisão e raio por escala)
GIANT = {"Mushroom_Tall": (8.0, 12.0, 0.12, 0.16), "Mushroom_Flat": (7.0, 10.0, 0.4, 0.3), "Mushroom_Cluster": (4.5, 7.0, 0.55, 0.5)}


def giant_mushroom(x, z, grow=1.0, kind=None, force=False):
    kind = kind or rng.choice(list(GIANT))
    lo, hi, solid, rad = GIANT[kind]
    s = rng.uniform(lo, hi) * grow
    return put(kind, x, z, scale=s, solid=[solid * s, solid * s], r=rad * s, free=2.5, force=force)


def giant_grove(rid, n, grow=1.0, tries=400):
    cx, cz, w, h = by_id[rid][1:]
    done = 0
    for _ in range(tries):
        if done >= n:
            break
        if giant_mushroom(cx + rng.uniform(-w / 2 + 3, w / 2 - 3), cz + rng.uniform(-h / 2 + 3, h / 2 - 3), grow):
            done += 1
    return done


def coin_row(x0, z0, x1, z1, n, y=1.1):
    """Moedas de ouro paradas no ar, em fila (enfeite das colinas)."""
    for i in range(n):
        t = i / max(1, n - 1)
        x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
        if room_at(x, z, -1.0) is not None:
            decor.append({"piece": "Coin_Gold", "position": [round(x, 1), round(z, 1)], "rotation": 90, "y": y, "scale": 3.0})


FLOWERS = ["Pl_Flower", "Pl_Swirl", "Pl_Grass1", "Pl_Grass2", "Pl_Grass3", "Pl_Shrub1", "Pl_Shrub3"]
SMALL_MUSH = ["Mushroom_Cluster", "Mushroom_Tall", "Mushroom_Flat"]
CARGO = ["Barrel_Oga_1", "Barrel_Oga_2", "Crate_Small", "Crate_Big", "Tv_Sack", "Pr_Basket", "Bucket_Wooden_1"]
TREES = ["Tree_Medium_A", "Tree_Medium_B", "Tree_Medium_C", "Tree_Large_A", "Tree_Large_B"]
ROCKS = ["Rock_1", "Rock_2", "Rock_3", "Rock_4", "Rock_5", "Rock_Mossy"]
CRYSTALS = ["Crystal_P_%d" % i for i in (1, 4, 7, 10, 13, 16, 19, 22)] + ["Crystal_B_%d" % i for i in (2, 5, 8, 11, 14, 17)]

# --- Prado de partida: placa, lampiões, cogumelos de enfeite, flores
lamp(-8, -3), lamp(8, 5)
put("Signpost_Fantasy", 6, -4, rot=200, scale=1.2, r=0.8)
for x in (-14, 14):
    giant_mushroom(x, -5, kind="Mushroom_Tall")
scatter("meadow", FLOWERS, 22, scale=(0.8, 1.4), margin=1.5, r=0.5, free=1.5)
scatter("meadow", SMALL_MUSH, 8, scale=(2.0, 3.5), margin=2.0, r=0.9)
coin_row(-10, 6, 10, 6, 9)
# --- Canteiro de Trevos e Moitas de Frutas
scatter("clover_patch", FLOWERS, 18, scale=(0.8, 1.4), margin=1.5, r=0.5, free=1.5)
scatter("clover_patch", SMALL_MUSH, 6, scale=(2.0, 3.5), margin=2.0, r=0.9)
scatter("berry_patch", ["Pl_Bush", "Pl_Shrub2", "Pl_Shrub4", "Pl_Shrub5"], 12, scale=(0.9, 1.4), margin=2.0, r=0.8)
scatter("berry_patch", CARGO, 5, scale=(0.9, 1.2), margin=2.0)
# --- Trilha e Estrada das Flores: lampiões e flores nas beiras
for z in (-12, -24):
    lamp(-2.6, z), lamp(2.6, z)
for z in (-68, -78, -88):
    lamp(-2.8, z), lamp(2.8, z)
scatter("trail", FLOWERS, 6, scale=(0.7, 1.1), margin=0.8, r=0.4, free=1.0)
scatter("flower_road", FLOWERS, 12, scale=(0.7, 1.1), margin=0.8, r=0.4, free=1.0)
coin_row(0, -66, 0, -94, 8)
# --- Vila dos Cogumelos: casas de cogumelo gigante, bancas, poço, carroças, lampiões e flores
for x, z in ((-26, -34), (-26, -58), (26, -34), (26, -58), (-14, -60), (14, -32)):  # as casas da vila: tufos de cogumelo de ~6 m
    giant_mushroom(x, z, 1.15, kind="Mushroom_Cluster", force=True)
for x, z, rot in ((-12, -58, 0), (12, -34, 180), (-20, -46, 90), (20, -46, 270)):
    put("Stall_Empty", x, z, rot=rot, scale=1.4, solid=[2.6, 1.3], r=1.8)
put("Pr_CoveredWell", 0, -46, rot=0, scale=1.3, solid=[2.3, 2.3], r=2.0, free=0.5)
for x, z in ((-28, -40), (28, -52), (-10, -32), (10, -60), (-8, -48), (8, -44)):
    lamp(x, z)
scatter("village", ["Cart_Wood", "Pr_CartSmall"], 3, scale=(1.1, 1.3), solid=(2.2, 1.2), margin=5.0, r=1.8)
scatter("village", CARGO, 16, scale=(0.9, 1.2), margin=3.0)
scatter("village", FLOWERS, 40, scale=(0.8, 1.4), margin=2.0, r=0.5, free=1.5)
scatter("village", SMALL_MUSH, 12, scale=(2.0, 3.5), margin=2.5, r=0.9)
for x in (-30, 30):
    put("Banner_1", x, -34, rot=0, scale=1.2, r=0.8)
# --- pontes: cerca baixa e flores
for rid, x0 in (("west_bridge", -46), ("east_bridge", 46)):
    for dx in (-9, -3, 3, 9):
        put("Pr_Fence1", x0 + dx, -49.5, rot=0, r=0.6, free=1.0)
        put("Pr_Fence1", x0 + dx, -42.5, rot=0, r=0.6, free=1.0)
    scatter(rid, FLOWERS, 6, scale=(0.7, 1.1), margin=1.0, r=0.4, free=1.0)
# --- Bosque dos Chapéus Gigantes: floresta de cogumelos enormes e árvores
giant_grove("giant_caps", 22, 1.1)
scatter("giant_caps", TREES, 6, scale=(0.9, 1.2), solid=(1.2, 1.2), margin=3.0, r=2.0)
scatter("giant_caps", SMALL_MUSH + FLOWERS, 24, scale=(1.5, 3.0), margin=2.0, r=0.6)
# --- Degraus de Pedra: pedras e plataformas, moedas no ar entre elas
scatter("stone_steps", ["Rock_Mossy", "Rock_MossyStone"], 9, scale=(1.0, 1.7), solid=(2.6, 2.3), margin=4.0, r=2.2)
scatter("stone_steps", ROCKS, 14, scale=(0.9, 1.8), solid=(1.2, 1.2), margin=2.5, r=1.2)
scatter("stone_steps", FLOWERS, 14, scale=(0.8, 1.2), margin=2.0, r=0.5)
coin_row(40, -64, 64, -64, 8, 1.6), coin_row(40, -76, 64, -76, 8, 1.6)
# --- Bosque dos Esporos: cogumelos com brilho verde, redemoinhos
scatter("spore_grove", SMALL_MUSH, 20, scale=(2.5, 4.5), margin=2.5, r=1.0)
for _ in range(60):
    cx, cz, w, h = by_id["spore_grove"][1:]
    x, z = cx + rng.uniform(-w / 2 + 3, w / 2 - 3), cz + rng.uniform(-h / 2 + 3, h / 2 - 3)
    if sum(1 for d in decor if d.get("light") == [0.5, 1.0, 0.55]) >= 8:
        break
    if giant_mushroom(x, z, 0.8):
        light(x, z, 0.9, 7.0, 1.5, (0.5, 1.0, 0.55))
scatter("spore_grove", ["Pl_Swirl", "Pl_Grass2"], 14, scale=(0.9, 1.4), margin=2.0, r=0.5)
# --- Gruta de Cristal: cristais com luz roxa e azul
for _ in range(16):
    cx, cz, w, h = by_id["crystal_hollow"][1:]
    x, z = cx + rng.uniform(-w / 2 + 2.5, w / 2 - 2.5), cz + rng.uniform(-h / 2 + 2.5, h / 2 - 2.5)
    s = rng.uniform(1.2, 2.4)
    if put(rng.choice(CRYSTALS), x, z, scale=s, solid=[0.8 * s, 0.8 * s], r=0.9 * s):
        if rng.random() < 0.5:
            light(x, z, 0.8, 6.0, 1.2, rng.choice(((0.75, 0.45, 1.0), (0.45, 0.7, 1.0))), False)
scatter("crystal_hollow", ROCKS, 8, scale=(0.8, 1.4), solid=(1.2, 1.2), margin=2.5, r=1.2)
# --- Campo das Moedas: pilhas de moedas, fileiras de moedas no ar, arbustos e lampiões
scatter("coin_field", ["Coin_Pile"], 10, scale=(1.3, 2.0), margin=3.0, r=1.2)
for z in (-101, -113):
    coin_row(-34, z, -8, z, 10), coin_row(8, z, 34, z, 10)
for x in (-34, -20, -8, 8, 20, 34):
    lamp(x, -99)
scatter("coin_field", FLOWERS + ["Pl_Bush"], 26, scale=(0.8, 1.3), margin=2.0, r=0.5)
scatter("coin_field", SMALL_MUSH, 10, scale=(2.0, 3.5), margin=2.5, r=0.9)
giant_grove("coin_field", 6, 0.9)
# --- Alameda do Castelo: lampiões e estandartes
for z in (-122, -136):
    lamp(-2.6, z), lamp(2.6, z)
# --- Pátio do Vulcão: braseiros, pedras escuras, colunas, estandartes do dragão e estátuas
for x in (-26, -12, 12, 26):
    for z in (-150, -164, -178):
        if abs(x) > 20 or z != -164:
            brazier(x, z, 2.2)
for x in (-14, 14):
    for z in (-152, -170):
        put("Banner_Dragon", x, z, rot=0, scale=2.6, r=1.2)
for x, z, rot in ((-30, -146, 90), (30, -146, -90)):
    put("Statue_Knight", x, z, rot=rot, scale=1.6, solid=[1.6, 1.7], r=1.7)
scatter("volcano_court", ["Ruin_Column", "Ruin_PillarStub", "Pr_BrokenPillar1", "Pr_BrokenPillar2"], 10, scale=(1.0, 1.4), solid=(1.2, 1.2), margin=4.0, r=1.4)
scatter("volcano_court", ["Canyon_Rock_Boulders_%d" % i for i in (1, 2, 3, 4, 5, 6)], 16, scale=(1.0, 1.8), solid=(2.2, 2.2), margin=4.0, r=2.2)
scatter("volcano_court", ["Coin_Pile"], 8, scale=(1.3, 1.8), margin=4.0, r=1.4)
for x, z in ((-30, -190), (30, -190)):
    lamp(x, z)
for _ in range(16):  # brasas no chão: luzes vermelhas baixas
    light(rng.uniform(-30, 30), rng.uniform(-195, -146), 1.0, 7.0, 0.5, (1.0, 0.35, 0.1))

# ---------------------------------------------------------------- animais e moradores
crowd = []
for rid in ("meadow", "clover_patch", "village", "coin_field"):
    cx, cz, w, h = by_id[rid][1:]
    for _ in range(2):
        x, z = cx + rng.uniform(-w / 2 + 3, w / 2 - 3), cz + rng.uniform(-h / 2 + 3, h / 2 - 3)
        crowd.append({"role": "rabbit", "position": [round(x, 1), round(z, 1)], "rotation": rng.randrange(0, 360), "pose": "walk",
                      "path": [round(x + rng.uniform(-2, 2), 1), round(z + rng.uniform(-1.5, 1.5), 1)], "speed": 0.6})
for rid, n in (("village", 4), ("meadow", 2)):
    cx, cz, w, h = by_id[rid][1:]
    for i in range(n):
        along, across, reach = rng.uniform(-0.3, 0.3) * w, rng.uniform(-0.3, 0.3) * h, w / 2 - 5.0
        a, b = [cx - reach, cz + across], [cx + reach, cz + across]
        if i % 2:
            a, b = b, a
        crowd.append({"role": rng.choice(["civilian_1", "civilian_2", "civilian_3", "civilian_5"]), "position": [round(a[0], 1), round(a[1], 1)], "pose": "walk",
                      "path": [round(b[0], 1), round(b[1], 1)], "speed": round(rng.uniform(0.8, 1.2), 2)})

arenas[AREA] = {
    "_comment": "Colinas dos Cogumelos (mapa novo, ligado à Capital): colinas coloridas, cogumelos gigantes, plataformas de pedra e moedas, com a estrutura da Floresta e das Docas. Prado -> Trilha -> "
                "Vila dos Cogumelos; laço oeste (Bosque dos Chapéus Gigantes: o Toco Antigo desperta o Bruto Esporento) e laço leste (Degraus de Pedra: a Moedeira desperta o Jacaré-Musgo), "
                "fechando no Bosque dos Esporos e na Gruta de Cristal; Estrada das Flores -> Campo das Moedas -> Alameda do Castelo (Guarda da Ponte, duas chaves) -> Pátio do Vulcão do "
                "Rei-Lagarto Vulcânico (chefe final, com a saída). Gerado por tools/assets/build_mushroom_hills.py.",
    "name_key": "ARENA_MUSHROOM", "player_class": "mage", "map_id": "map_mushroom", "area_level": 16, "outdoor": True, "final": True, "victory_groups": ["mh_king"],
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": rooms, "encounters": encounters, "hazards": [], "entries": {"start": [0, 3], "mushroom": [0, 3]}, "props": props,
    "quest_spots": [[-32, 0], [0, -46], [-52, -70], [52, -70], [0, -107]],
    "breakables": [{"id": "coin_bag", "monster": "coin_bag", "position": [4.0, 1.5], "table": "coin_bag"}],
    "style": {"_comment": "Colinas: grama clara, cerca viva de arbustos nas bordas; o vazio entre as salas vira grama.", "walls": [""], "floor": "Ground_Grass", "low": "Pl_Bush",
              "fill_grass": True, "hedge_edges": True, "ground": [0.06, 0.1, 0.03]},
    "decor": decor, "crowd": crowd, "passive": True}

# ---------------------------------------------------------------- Capital: portão novo (a fileira dos portões ao sul da praça) e a Botânica Real na igreja
cap = arenas["capital_01_aurenhold"]
cap["props"] = [p for p in cap["props"] if p["id"] not in ("mushroom_gate", "royal_botanist")]
cap["props"].append({"id": "mushroom_gate", "kind": "exit", "name_key": "PROP_TO_MUSHROOM", "position": [-0.5, 4.5], "to": AREA, "entry": "start"})
cap["props"].append({"id": "royal_botanist", "kind": "npc", "npc": "royal_botanist", "position": [-21.0, -33.6], "rotation": 180})
cap["entries"]["mushroom"] = [-0.5, 2.0]


# ---------------------------------------------------------------- NPCs e missões (mesma forma das Docas)
def body(sex, hair, color, outfit=None):
    return {"sex": sex, "hair": [hair] if isinstance(hair, str) else hair, "hair_color": color, "pose": "idle", "outfit": outfit or {"body": "cloth"}}


npcs["royal_botanist"] = {"name_key": "NPC_ROYAL_BOTANIST", "color": [0.45, 0.65, 0.35], "dialogues": [
    {"when": {"quest_new": "map_mushroom", "after": "map_desert"}, "lines": ["DLG_BOTANIST_1", "DLG_BOTANIST_2", "DLG_BOTANIST_3"], "offer": "map_mushroom"},
    {"when": {"quest_active": "map_mushroom"}, "lines": ["DLG_BOTANIST_ACTIVE"]}, {"when": {}, "lines": ["DLG_BOTANIST_DONE"]}], "body": body("female", "Hair_Buns", [0.55, 0.3, 0.15])}
quests["map_mushroom"] = {"name_key": "QUEST_MAP_MUSHROOM", "desc_key": "QUEST_MAP_MUSHROOM_DESC", "type": "main", "giver": "royal_botanist", "area": AREA, "clear": ["mh_king"],
                          "target_element": "water", "reward": {"gold": 950, "xp": 1900}}
npcs["mh_gardener"] = {"name_key": "NPC_MH_GARDENER", "color": [0.4, 0.55, 0.3], "dialogues": [
    {"when": {"quest_new": "mh_spore"}, "lines": ["DLG_MH_GARDENER_1", "DLG_MH_GARDENER_2", "DLG_MH_GARDENER_3"], "offer": "mh_spore"},
    {"when": {"quest_active": "mh_spore"}, "lines": ["DLG_MH_GARDENER_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_MH_GARDENER_DONE"]}], "body": body("male", "Hair_Beard", [0.6, 0.58, 0.55])}
npcs["mh_old_stump"] = {"name_key": "NPC_MH_OLD_STUMP", "color": [0.5, 0.4, 0.3], "dialogues": [
    {"when": {"quest_active": "mh_spore"}, "lines": ["DLG_MH_STUMP_1", "DLG_MH_STUMP_2"]}, {"when": {}, "lines": ["DLG_MH_STUMP_LOCKED"]}]}
npcs["mh_coin_keeper"] = {"name_key": "NPC_MH_COIN_KEEPER", "color": [0.85, 0.7, 0.3], "dialogues": [
    {"when": {"quest_new": "mh_brick"}, "lines": ["DLG_MH_COINS_1", "DLG_MH_COINS_2", "DLG_MH_COINS_3"], "offer": "mh_brick"},
    {"when": {"quest_active": "mh_brick"}, "lines": ["DLG_MH_COINS_ACTIVE"], "service": "turn_in"},
    {"when": {"quest_done": "mh_brick"}, "lines": ["DLG_MH_COINS_DONE"]}, {"when": {}, "lines": ["DLG_MH_COINS_WAIT"]}], "body": body("female", "Hair_Long", [0.85, 0.6, 0.2])}
npcs["mh_bridge_guard"] = {"name_key": "NPC_MH_BRIDGE_GUARD", "color": [0.5, 0.45, 0.4], "dialogues": [
    {"when": {"quest_new": "mh_gate"}, "lines": ["DLG_MH_GUARD_1", "DLG_MH_GUARD_2", "DLG_MH_GUARD_3"], "offer": "mh_gate"},
    {"when": {"quest_active": "mh_gate"}, "lines": ["DLG_MH_GUARD_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_MH_GUARD_DONE"]}], "body": body("male", "Hair_SimpleParted", [0.2, 0.15, 0.1])}
quests["mh_spore"] = {"name_key": "QUEST_MH_SPORE", "desc_key": "QUEST_MH_SPORE_DESC", "type": "village", "giver": "mh_gardener", "area": AREA, "target_element": "fire",
                      "reward": {"gold": 120, "xp": 240}, "item": "golden_spore", "gives": "key_sun"}
quests["mh_brick"] = {"name_key": "QUEST_MH_BRICK", "desc_key": "QUEST_MH_BRICK_DESC", "type": "village", "giver": "mh_coin_keeper", "area": AREA, "target_element": "air",
                      "reward": {"gold": 120, "xp": 240}, "item": "star_brick", "gives": "key_moon"}
quests["mh_gate"] = {"name_key": "QUEST_MH_GATE", "desc_key": "QUEST_MH_GATE_DESC", "type": "village", "giver": "mh_bridge_guard", "area": AREA, "items": ["key_sun", "key_moon"],
                     "opens_gate": "boss_gate", "target_element": "water", "reward": {"gold": 160, "xp": 320}}

T = {
    "ARENA_MUSHROOM": ("Colinas dos Cogumelos", "Mushroom Hills", "Colinas de los Hongos"),
    "PROP_TO_MUSHROOM": ("Caminho para as Colinas dos Cogumelos", "Road to the Mushroom Hills", "Camino a las Colinas de los Hongos"),
    "MONSTER_MH_BUNNY": ("Coelho-Espora", "Spur Bunny", "Conejo Espolón"),
    "MONSTER_MH_DRAGONLING": ("Dragãozinho de Brasa", "Ember Dragonling", "Dragoncito de Brasa"),
    "MONSTER_MH_LYNX": ("Lince das Colinas", "Hill Lynx", "Lince de las Colinas"),
    "MONSTER_MH_GHOST": ("Fantasma de Esporos", "Spore Wraith", "Espectro de Esporas"),
    "MONSTER_MH_MOSS_GATOR": ("Jacaré-Musgo", "Moss Gator", "Caimán Musgoso"),
    "MONSTER_MH_SPORE_BRUTE": ("Bruto Esporento", "Spore Brute", "Bruto Esporoso"),
    "MONSTER_MH_LIZARD_KING": ("Rei-Lagarto Vulcânico", "Volcanic Lizard King", "Rey Lagarto Volcánico"),
    "TOAST_MH_GATOR_WAVE": ("O Jacaré-Musgo bate o rabo no lago: onda {n} de bichos!", "The Moss Gator slaps the pond: creature wave {n}!", "El Caimán Musgoso golpea el estanque: ¡oleada {n} de bichos!"),
    "TOAST_MH_BRUTE_WAVE": ("O Bruto Esporento solta esporos: onda {n}!", "The Spore Brute bursts spores: wave {n}!", "El Bruto Esporoso suelta esporas: ¡oleada {n}!"),
    "TOAST_MH_KING_WAVE": ("O Rei-Lagarto ruge e o vulcão responde: onda {n}!", "The Lizard King roars and the volcano answers: wave {n}!", "El Rey Lagarto ruge y el volcán responde: ¡oleada {n}!"),
    "TOAST_MH_BRUTE_AWAKENS": ("O toco se abre numa nuvem lilás: o Bruto Esporento acorda!", "The stump bursts in a lilac cloud: the Spore Brute awakens!", "El tocón se abre en una nube lila: ¡el Bruto Esporoso despierta!"),
    "TOAST_MH_GATOR_AWAKENS": ("O lago borbulha: o Jacaré-Musgo sobe aos Degraus!", "The pond bubbles: the Moss Gator climbs onto the Steps!", "El estanque burbujea: ¡el Caimán Musgoso sube a los Escalones!"),
    "NPC_ROYAL_BOTANIST": ("Botânica Real", "Royal Botanist", "Botánica Real"),
    "NPC_MH_GARDENER": ("Velho Jardineiro", "Old Gardener", "Viejo Jardinero"),
    "NPC_MH_OLD_STUMP": ("Toco Antigo", "Ancient Stump", "Tocón Antiguo"),
    "NPC_MH_COIN_KEEPER": ("Moedeira", "Coin Keeper", "Guardamonedas"),
    "NPC_MH_BRIDGE_GUARD": ("Guarda da Ponte", "Bridge Guard", "Guardia del Puente"),
    "VALUABLE_STAR_BRICK": ("Tijolo-Estrela", "Star Brick", "Ladrillo Estrella"),
    "VALUABLE_GOLDEN_SPORE": ("Esporo Dourado", "Golden Spore", "Espora Dorada"),
    "VALUABLE_KEY_SUN": ("Chave do Sol", "Sun Key", "Llave del Sol"),
    "VALUABLE_KEY_MOON": ("Chave da Lua", "Moon Key", "Llave de la Luna"),
    "QUEST_MAP_MUSHROOM": ("As Colinas em Brasa", "The Smoldering Hills", "Las Colinas en Brasas"),
    "QUEST_MAP_MUSHROOM_DESC": ("A Botânica Real quer que vocês vão às Colinas dos Cogumelos, depois do portão da Capital, e derrubem o Rei-Lagarto Vulcânico, que está queimando as colinas.",
                                "The Royal Botanist wants you to go to the Mushroom Hills, past the Capital's gate, and bring down the Volcanic Lizard King, who is burning the hills.",
                                "La Botánica Real quiere que vayan a las Colinas de los Hongos, tras el portón de la Capital, y derriben al Rey Lagarto Volcánico, que está quemando las colinas."),
    "QUEST_MH_SPORE": ("O Esporo Dourado", "The Golden Spore", "La espora dorada"),
    "QUEST_MH_SPORE_DESC": ("O Velho Jardineiro guardava o Esporo Dourado, a semente de todos os cogumelos das colinas, e o Bruto Esporento o engoliu. Desperte-o, derrote-o e traga o esporo: em troca vem a Chave do Sol, uma das duas do portão do Rei-Lagarto.",
                            "The Old Gardener kept the Golden Spore, the seed of every mushroom in the hills, and the Spore Brute swallowed it. Wake it, defeat it and bring the spore: in return you get the Sun Key, one of the two for the Lizard King's gate.",
                            "El Viejo Jardinero guardaba la Espora Dorada, la semilla de todos los hongos de las colinas, y el Bruto Esporoso se la tragó. Despiértalo, derrótalo y trae la espora: a cambio recibes la Llave del Sol, una de las dos del portón del Rey Lagarto."),
    "QUEST_MH_BRICK": ("O Tijolo-Estrela", "The Star Brick", "El ladrillo estrella"),
    "QUEST_MH_BRICK_DESC": ("A Moedeira contava as moedas das colinas sobre o Tijolo-Estrela, até o Jacaré-Musgo engoli-lo. Desperte o jacaré, derrote-o e traga o tijolo para receber a Chave da Lua, a outra do portão do Rei-Lagarto.",
                            "The Coin Keeper counted the hills' coins on the Star Brick, until the Moss Gator swallowed it. Wake the gator, defeat it and bring the brick to receive the Moon Key, the other one for the Lizard King's gate.",
                            "La Guardamonedas contaba las monedas de las colinas sobre el Ladrillo Estrella, hasta que el Caimán Musgoso se lo tragó. Despierta al caimán, derrótalo y trae el ladrillo para recibir la Llave de la Luna, la otra del portón del Rey Lagarto."),
    "QUEST_MH_GATE": ("O Portão do Vulcão", "The Volcano Gate", "El portón del volcán"),
    "QUEST_MH_GATE_DESC": ("O Guarda da Ponte só abre o portão para quem trouxer as duas chaves: a do Sol (Velho Jardineiro) e a da Lua (Moedeira). Atrás dele fica o Pátio do Vulcão do Rei-Lagarto.",
                           "The Bridge Guard only opens the gate for those with both keys: the Sun (Old Gardener) and the Moon (Coin Keeper). Beyond lies the Lizard King's Volcano Court.",
                           "El Guardia del Puente solo abre el portón a quien traiga las dos llaves: la del Sol (Viejo Jardinero) y la de la Luna (Guardamonedas). Tras él está el Patio del Volcán del Rey Lagarto."),
    "DLG_BOTANIST_1": ("Ah, vocês voltaram do Deserto! Então aguentam calor. Ótimo, porque eu preciso de gente que aguente calor.",
                       "Ah, you came back from the Desert! Then you can take the heat. Good, because I need people who can take the heat.",
                       "¡Ah, volvieron del Desierto! Entonces aguantan el calor. Bien, porque necesito gente que aguante el calor."),
    "DLG_BOTANIST_2": ("Além do portão da praça ficam as Colinas dos Cogumelos, de onde vêm todos os cogumelos do jardim real. Um lagarto enorme saiu do vulcão e está queimando tudo.",
                       "Past the plaza gate lie the Mushroom Hills, where every mushroom of the royal garden comes from. A huge lizard came out of the volcano and is burning everything.",
                       "Tras el portón de la plaza están las Colinas de los Hongos, de donde vienen todos los hongos del jardín real. Un lagarto enorme salió del volcán y lo está quemando todo."),
    "DLG_BOTANIST_3": ("Falem com os moradores da vila: eles sabem como chegar ao vulcão. E derrubem o Rei-Lagarto Vulcânico antes que não sobre um chapéu de cogumelo de pé.",
                       "Talk to the village folk: they know how to reach the volcano. And bring down the Volcanic Lizard King before not a single mushroom cap is left standing.",
                       "Hablen con los aldeanos: saben cómo llegar al volcán. Y derriben al Rey Lagarto Volcánico antes de que no quede un sombrero de hongo en pie."),
    "DLG_BOTANIST_ACTIVE": ("O portão das Colinas fica na praça, na fileira dos portões ao sul. Sigam a trilha até a vila dos cogumelos.",
                            "The Hills gate is in the plaza, in the row of gates to the south. Follow the trail to the mushroom village.",
                            "El portón de las Colinas está en la plaza, en la fila de portones al sur. Sigan el sendero hasta la aldea de los hongos."),
    "DLG_BOTANIST_DONE": ("As colinas voltaram a dar cogumelo! O jardim real agradece, e eu também.", "The hills grow mushrooms again! The royal garden thanks you, and so do I.",
                          "¡Las colinas vuelven a dar hongos! El jardín real lo agradece, y yo también."),
    "DLG_MH_GARDENER_1": ("Cuidado onde pisam, forasteiros: cada cogumelo destas colinas foi plantado por estas mãos velhas.",
                          "Watch your step, strangers: every mushroom in these hills was planted by these old hands.",
                          "Cuidado dónde pisan, forasteros: cada hongo de estas colinas lo plantaron estas manos viejas."),
    "DLG_MH_GARDENER_2": ("Eu guardava o Esporo Dourado, a semente de todos eles. Um bruto lilás saiu do Toco Antigo, no Bosque dos Chapéus Gigantes, e o engoliu inteiro.",
                          "I kept the Golden Spore, the seed of them all. A lilac brute came out of the Ancient Stump, in the Giant Caps Grove, and swallowed it whole.",
                          "Yo guardaba la Espora Dorada, la semilla de todos. Un bruto lila salió del Tocón Antiguo, en el Bosque de los Sombreros Gigantes, y se la tragó entera."),
    "DLG_MH_GARDENER_3": ("Derrubem o Bruto Esporento e tragam o esporo de volta. Em troca eu dou a Chave do Sol, uma das duas que abrem o portão do vulcão.",
                          "Bring down the Spore Brute and bring the spore back. In return I give the Sun Key, one of the two that open the volcano gate.",
                          "Derriben al Bruto Esporoso y traigan la espora. A cambio doy la Llave del Sol, una de las dos que abren el portón del volcán."),
    "DLG_MH_GARDENER_ACTIVE": ("O Bosque dos Chapéus Gigantes fica a oeste da vila, depois da ponte. O esporo brilha como ouro: não tem como errar.",
                               "The Giant Caps Grove is west of the village, past the bridge. The spore shines like gold: you cannot miss it.",
                               "El Bosque de los Sombreros Gigantes está al oeste de la aldea, tras el puente. La espora brilla como oro: no tiene pérdida."),
    "DLG_MH_GARDENER_DONE": ("O Esporo Dourado! Já sinto o chão mais macio. A Chave do Sol é de vocês: levem-na ao Guarda da Ponte, junto com a da Lua.",
                             "The Golden Spore! I already feel the soil softer. The Sun Key is yours: take it to the Bridge Guard, together with the Moon one.",
                             "¡La Espora Dorada! Ya siento la tierra más blanda. La Llave del Sol es suya: llévenla al Guardia del Puente, junto con la de la Luna."),
    "DLG_MH_STUMP_1": ("O toco é macio e quente, coberto de pó lilás. Algo grande respira lá dentro.", "The stump is soft and warm, covered in lilac dust. Something large breathes inside.",
                       "El tocón es blando y tibio, cubierto de polvo lila. Algo grande respira adentro."),
    "DLG_MH_STUMP_2": ("O Bruto Esporento acorda!", "The Spore Brute awakens!", "¡El Bruto Esporoso despierta!"),
    "DLG_MH_STUMP_LOCKED": ("Um toco velho cheio de cogumelos. Nada responde às suas mãos.", "An old stump full of mushrooms. Nothing answers your hands.",
                            "Un tocón viejo lleno de hongos. Nada responde a sus manos."),
    "DLG_MH_COINS_1": ("Cento e doze, cento e treze... ah, visitas! Eu conto as moedas que brotam destas colinas. Todo dia nascem mais.",
                       "One hundred twelve, one hundred thirteen... oh, visitors! I count the coins that sprout from these hills. More grow every day.",
                       "Ciento doce, ciento trece... ¡ah, visitas! Cuento las monedas que brotan de estas colinas. Cada día nacen más."),
    "DLG_MH_COINS_2": ("Eu contava em cima do Tijolo-Estrela, que nunca erra a conta. Um jacaré coberto de musgo subiu do lago para os Degraus de Pedra e engoliu o tijolo inteiro.",
                       "I counted on top of the Star Brick, which never miscounts. A moss-covered gator climbed from the pond onto the Stone Steps and swallowed the brick whole.",
                       "Contaba encima del Ladrillo Estrella, que nunca se equivoca. Un caimán cubierto de musgo subió del estanque a los Escalones de Piedra y se tragó el ladrillo entero."),
    "DLG_MH_COINS_3": ("Eu chamo o jacaré para vocês, aqui nos Degraus. Derrubem-no e tragam o tijolo: eu dou a Chave da Lua, a outra do portão do vulcão.",
                       "I will call the gator for you, here on the Steps. Bring it down and bring the brick: I give the Moon Key, the other for the volcano gate.",
                       "Llamaré al caimán para ustedes, aquí en los Escalones. Derríbenlo y traigan el ladrillo: doy la Llave de la Luna, la otra del portón del volcán."),
    "DLG_MH_COINS_ACTIVE": ("O tijolo tem uma estrela dourada no meio. Está na barriga do jacaré. Derrubem-no e tragam-no para mim.",
                            "The brick has a golden star in the middle. It is in the gator's belly. Bring it down and bring the brick to me.",
                            "El ladrillo tiene una estrella dorada en el medio. Está en la panza del caimán. Derríbenlo y tráiganmelo."),
    "DLG_MH_COINS_DONE": ("O meu tijolo! A Chave da Lua é de vocês. Levem-na ao Guarda da Ponte, na alameda ao norte do Campo das Moedas.",
                          "My brick! The Moon Key is yours. Take it to the Bridge Guard, in the lane north of the Coin Field.",
                          "¡Mi ladrillo! La Llave de la Luna es suya. Llévenla al Guardia del Puente, en la alameda al norte del Campo de las Monedas."),
    "DLG_MH_COINS_WAIT": ("Cento e catorze... perdi a conta de novo. Voltem depois, sim?", "One hundred fourteen... I lost count again. Come back later, yes?",
                          "Ciento catorce... perdí la cuenta otra vez. Vuelvan luego, ¿sí?"),
    "DLG_MH_GUARD_1": ("Alto! Atrás deste portão fica o Pátio do Vulcão, e lá manda o Rei-Lagarto. Ele sai da lava quando quer e queima o que vê pela frente.",
                       "Halt! Behind this gate lies the Volcano Court, and the Lizard King rules there. He comes out of the lava whenever he likes and burns whatever he sees.",
                       "¡Alto! Tras este portón está el Patio del Volcán, y allí manda el Rey Lagarto. Sale de la lava cuando quiere y quema lo que ve."),
    "DLG_MH_GUARD_2": ("O portão só abre com DUAS chaves: a do Sol e a da Lua. A primeira está com o Velho Jardineiro, na vila; a segunda, com a Moedeira, nos Degraus de Pedra.",
                       "The gate only opens with TWO keys: the Sun and the Moon. The first is with the Old Gardener, in the village; the second, with the Coin Keeper, on the Stone Steps.",
                       "El portón solo abre con DOS llaves: la del Sol y la de la Luna. La primera la tiene el Viejo Jardinero, en la aldea; la segunda, la Guardamonedas, en los Escalones de Piedra."),
    "DLG_MH_GUARD_3": ("Tragam as duas chaves a mim e eu abro a passagem. Depois disso, é com vocês.", "Bring both keys to me and I will open the way. After that, it is up to you.",
                       "Tráiganme las dos llaves y abro el paso. Después de eso, es cosa suya."),
    "DLG_MH_GUARD_ACTIVE": ("Só abro com as duas chaves, Sol e Lua, na mesma bolsa. O Jardineiro fica na vila; a Moedeira, nos Degraus de Pedra, a leste.",
                            "I only open with both keys, Sun and Moon, in the same bag. The Gardener is in the village; the Coin Keeper, on the Stone Steps to the east.",
                            "Solo abro con las dos llaves, Sol y Luna, en la misma bolsa. El Jardinero está en la aldea; la Guardamonedas, en los Escalones de Piedra, al este."),
    "DLG_MH_GUARD_DONE": ("As duas chaves! O portão está aberto. Levem água, se tiverem: lá dentro o chão ferve.", "Both keys! The gate is open. Bring water if you have any: inside, the ground boils.",
                          "¡Las dos llaves! El portón está abierto. Lleven agua si tienen: adentro el suelo hierve."),
}
for lang_i, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po", "locale/messages.pot")):
    t = open(path, encoding="utf-8").read()
    add = ""
    for key, trio in T.items():
        val = "" if path.endswith(".pot") else trio[lang_i].replace('"', '\\"')
        if re.search(r'msgid "%s"\n' % re.escape(key), t):
            if val:
                t = re.sub(r'(msgid "%s"\nmsgstr )"[^\n]*"' % re.escape(key), lambda m: m.group(1) + '"' + val.replace("\\", "\\\\") + '"', t)
        else:
            add += '\nmsgid "%s"\nmsgstr "%s"\n' % (key, val)
    open(path, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + add)

# ---------------------------------------------------------------- ícones dos itens (tingidos dos existentes)
try:
    from PIL import Image
    ICONS = "assets/ui/icons/"
    for dst, src, mul in (("key_sun", "key_spades", (1.4, 1.15, 0.45)), ("key_moon", "key_hearts", (0.75, 0.8, 1.4)), ("star_brick", "bone_dagger", (1.3, 0.75, 0.45)),
                          ("golden_spore", "royal_seal_ring", (1.15, 1.05, 0.5))):
        im = Image.open(ICONS + src + ".png").convert("RGBA")
        r_, g_, b_, a_ = im.split()
        Image.merge("RGBA", (r_.point(lambda v: min(255, int(v * mul[0]))), g_.point(lambda v: min(255, int(v * mul[1]))), b_.point(lambda v: min(255, int(v * mul[2]))), a_)).save(ICONS + dst + ".png")
except Exception as exc:
    print("aviso: ícones não gerados:", exc)

for path, data in ((ARENAS, arenas), (MONSTERS, monsters), (NPCS, npcs), (QUESTS, quests), (VALUABLES, valuables)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
print("OK colinas dos cogumelos", len(rooms), "salas,", len(decor), "peças de cenário,", len(encounters), "encontros")
