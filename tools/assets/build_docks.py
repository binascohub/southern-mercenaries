"""Mapa das Docas (docks_01_pier), ampliado: mesma estrutura da Floresta (partida, duas áreas de mini-chefe, guardião do portão e chefe final) com outro caminho.
Píeres de madeira sobre o mar (Modular Wooden Docks, loafbrr, CC0): o Cais de partida sobe pelo Píer Principal até o Mercado de Peixe; dali um laço a oeste
(Estaleiro, onde o NPC do porto manda tocar o casco encalhado e acordar o Casco Vivo), um laço a leste (Peixaria, onde a Peixeira desperta o Tubarão-Porco), os dois
fechando no Farol e no Armazém; a Calçada ao norte leva ao Atracadouro e ao corredor do portão, onde o Vigia pede as duas chaves; atrás dele fica o Convés do Capitão Afogado
(chefe final, com a saída). Mantém os encontros dk_* da missão dos contrabandistas. Sorteio com semente fixa; idempotente; chamado no fim de tools/assets/build_maps.py
(antes de set_map_order.py). Também põe NPCs, missões, itens, textos pt/en/es e ícones.
uso: python3 tools/assets/build_docks.py   (a partir da raiz do projeto)"""
import json, math, random, re
ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES = ("data/arenas.json", "data/monsters.json", "data/npcs.json", "data/quests.json", "data/valuables.json")
arenas, monsters, npcs, quests, valuables = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES))
rng = random.Random("docks-v2")
DOOR = 6.0

ROOMS = [("landing", 0, 0, 36, 16), ("fish_pier", -32, 0, 28, 12), ("boathouse", 32, 0, 28, 12), ("main_pier", 0, -18, 10, 20), ("market", 0, -46, 64, 36),
         ("west_pier", -46, -46, 28, 8), ("east_pier", 46, -46, 28, 8), ("shipyard", -52, -70, 36, 40), ("fishery", 52, -70, 36, 40), ("causeway", 0, -80, 12, 32),
         ("wharf", 0, -107, 80, 22), ("lighthouse", -55, -105, 30, 30), ("warehouse", 55, -105, 30, 30), ("gate_lane", 0, -130, 10, 24), ("deck", 0, -170, 70, 56)]
LINKS = [("landing", "fish_pier", "west"), ("landing", "boathouse", "east"), ("landing", "main_pier", "north"), ("main_pier", "market", "north"), ("market", "west_pier", "west"),
         ("market", "east_pier", "east"), ("west_pier", "shipyard", "north"), ("east_pier", "fishery", "north"), ("market", "causeway", "north"), ("causeway", "wharf", "north"),
         ("shipyard", "lighthouse", "north"), ("fishery", "warehouse", "north"), ("lighthouse", "wharf", "east"), ("warehouse", "wharf", "west"), ("wharf", "gate_lane", "north"),
         ("gate_lane", "deck", "north")]
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
    if rid in ("landing", "market", "wharf", "deck"):
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


# ---------------------------------------------------------------- monstros novos (mini-chefes e chefe final) e itens
def clone(name, base, **changes):
    m = json.loads(json.dumps(monsters[base]))
    m.pop("_comment", None)
    m.pop("quest_drop", None)
    m.update(changes)
    monsters[name] = m


clone("hull_beast", "frog_king", _comment="Mini-chefe das Docas (Estaleiro): o Casco Vivo, monstro de tábuas e pregos que acorda do casco encalhado; investidas.",
      name_key="MONSTER_HULL_BEAST", max_health=190, damage=13, size=3.0, element="water", look="plank_monster", color=[0.55, 0.75, 0.7], quest_drop="ship_helm")
clone("pork_shark", "frog_king", _comment="Mini-chefe das Docas (Peixaria): o Tubarão-Porco, tubarão de dentes de ouro que a Peixeira desperta; investidas.",
      name_key="MONSTER_PORK_SHARK", max_health=210, damage=14, size=2.4, element="water", look="pork_shark", color=[1.0, 1.0, 1.0], quest_drop="golden_shark_tooth")
clone("drowned_captain", "frog_king", _comment="Chefe final das Docas: o Capitão Afogado, esqueleto verde do mar que guarda o Convés atrás do portão; investidas e pisões.",
      name_key="MONSTER_DROWNED_CAPTAIN", category="boss", aggressive=False, max_health=420, damage=18, size=2.8, element="water", look="skeleton", color=[0.4, 0.85, 0.75],
      chest_loot="chest")
valuables.update({
    "ship_helm": {"name_key": "VALUABLE_SHIP_HELM", "value": 0, "maps": [], "quest_item": True, "model": "Bucket_Wooden_1"},
    "golden_shark_tooth": {"name_key": "VALUABLE_GOLDEN_SHARK_TOOTH", "value": 0, "maps": [], "quest_item": True, "model": "Coin_Gold"},
    "key_anchor": {"name_key": "VALUABLE_KEY_ANCHOR", "value": 0, "maps": [], "quest_item": True, "model": "Key_Gold"},
    "key_compass": {"name_key": "VALUABLE_KEY_COMPASS", "value": 0, "maps": [], "quest_item": True, "model": "Key_Hearts"}})

# ---------------------------------------------------------------- objetos do mapa
SUMMON_HULL = {"id": "dk_hull", "position": [-52.0, -62.0], "spread": 3.0, "toast": "TOAST_HULL_AWAKENS", "monsters": [{"monster": "hull_beast", "count": 1, "rank": "miniboss"}]}
SUMMON_SHARK = {"id": "dk_shark", "position": [62.0, -80.0], "spread": 3.0, "toast": "TOAST_SHARK_AWAKENS", "monsters": [{"monster": "pork_shark", "count": 1, "rank": "miniboss"}]}
props = [
    {"id": "sea", "kind": "water", "position": [0, -95], "size": [240, 260]},
    {"id": "return_portal", "kind": "exit", "name_key": "PROP_TO_PORT", "position": [-4, 3], "to": "tortuga", "entry": "docks"},
    {"id": "victory_portal", "kind": "exit", "name_key": "PROP_TO_PORT", "position": [0, -195.5], "to": "tortuga", "entry": "docks", "after_victory": True, "group": True},
    {"id": "dock_master", "kind": "npc", "npc": "dock_master", "position": [8, -2], "rotation": 200},
    {"id": "wrecked_hull", "kind": "npc", "npc": "wrecked_hull", "kit": "Dock_Boat_Stand", "rotation": 0, "position": [-52.0, -70.0], "summon": SUMMON_HULL, "needs_quest": "dock_helm"},
    {"id": "dock_fishwife", "kind": "npc", "npc": "dock_fishwife", "position": [42.0, -60.0], "rotation": 0, "summon": SUMMON_SHARK, "needs_quest": "dock_tooth"},
    {"id": "boss_gate", "kind": "gate", "name_key": "PROP_BOSS_GATE", "position": [0.0, -124.0], "rotation": 0, "scale": 3.0, "block": 10.0, "count": 2, "opened_by": "dock_gate"},
    {"id": "dock_sentinel", "kind": "npc", "npc": "dock_sentinel", "position": [0.0, -120.0], "rotation": 0},
    {"id": "dock_chest_1", "kind": "chest", "position": [-40, -2], "loot": "chest"}, {"id": "dock_chest_2", "kind": "chest", "position": [40, 3], "loot": "chest"},
    {"id": "dock_chest_3", "kind": "chest", "position": [-62, -112], "loot": "chest"}, {"id": "dock_chest_4", "kind": "chest", "position": [62, -112], "loot": "chest"},
    {"id": "dock_chest_5", "kind": "chest", "position": [-28, -58], "loot": "chest"}, {"id": "dock_chest_6", "kind": "chest", "position": [-30, -190], "loot": "chest"},
    {"id": "dock_chest_7", "kind": "chest", "position": [30, -190], "loot": "chest"}]
E = lambda eid, pos, *mons: {"id": eid, "position": pos, "monsters": [{"monster": m, "count": c} for m, c in mons]}
encounters = [
    E("dk_rats_a", [0, -18], ("plague_frog", 4)), E("dk_toads", [-32, 0], ("acid_toad", 3)), E("dk_bats", [32, 0], ("plague_bat", 4)),
    E("dk_rats_b", [0, -80], ("mutant_frog", 3), ("angler", 2)), E("dk_anglers", [-46, -46], ("angler", 2)),
    E("dk_market_a", [-18, -42], ("plague_frog", 3)), E("dk_market_b", [18, -52], ("mutant_frog", 3)), E("dk_market_c", [-4, -36], ("plague_bat", 3)),
    E("dk_east_pier", [46, -46], ("acid_toad", 2)), E("dk_yard_a", [-62, -80], ("angler", 3)), E("dk_yard_b", [-42, -58], ("acid_toad", 3)),
    E("dk_fishery_a", [44, -84], ("plague_bat", 4)), E("dk_fishery_b", [62, -58], ("mutant_frog", 3)),
    E("dk_light_a", [-55, -112], ("angler", 3)), E("dk_light_b", [-62, -98], ("plague_bat", 3)), E("dk_ware_a", [55, -112], ("mutant_frog", 3)), E("dk_ware_b", [62, -98], ("angler", 3)),
    E("dk_wharf_a", [-20, -107], ("plague_frog", 4)), E("dk_wharf_b", [20, -107], ("plague_bat", 4)),
    E("dk_boathouse_mimic", [38, 3], ("chest_mimic", 1)), E("dk_yard_mimic", [-60, -60], ("chest_mimic", 1)), E("dk_light_mimic", [-66, -112], ("chest_mimic", 1)),
    E("dk_ware_mimic", [66, -112], ("chest_mimic", 1)), E("dk_deck_a", [-18, -158], ("angler", 2)), E("dk_deck_b", [18, -158], ("angler", 2)),
    E("dk_captain", [0, -188], ("drowned_captain", 1))]
interest = [p["position"] for p in props if p["kind"] != "water"] + [e["position"] for e in encounters] + [SUMMON_HULL["position"], SUMMON_SHARK["position"], [0, 3]]
interest += [list(d) for d in door_points]


def near_interest(x, z, rad=3.5):
    return any(math.hypot(x - ix, z - iz) < rad for ix, iz in interest)


# ---------------------------------------------------------------- decoração
decor = []
taken = []


def near_taken(x, z, rad=0.0):
    return any(math.hypot(x - tx, z - tz) < tr + rad for tx, tz, tr in taken)


def put(piece, x, z, rot=None, scale=1.0, solid=None, y=0.12, r=0.8, free=2.0, force=False):
    if room_at(x, z, -0.9) is None:
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


def light(x, z, energy=1.3, rng_=9.0, y=1.6, color=(1.0, 0.6, 0.25)):
    decor.append({"light": list(color), "position": [round(x, 1), round(z, 1)], "y": y, "range": rng_, "energy": energy, "flicker": True})


def torch(x, z, scale=1.5):
    if put("Tv_Torch", x, z, scale=scale, r=0.5, free=1.2):
        light(x, z, 0.8, 6.5, 1.8)


def lamp(x, z):
    if put("Pr_LampPost", x, z, rot=0, solid=[0.6, 0.6], r=0.8, free=1.2):
        light(x, z, 0.9, 8.0, 3.2, (1.0, 0.8, 0.5))


def brazier(x, z, scale=1.8):
    if put("Tv_Fire", x, z, rot=0, scale=scale, solid=[0.9 * scale, 0.7 * scale], r=1.3, free=1.2):
        decor.append({"piece": "Fire_Flame", "position": [round(x, 1), round(z, 1)], "y": 0.2, "scale": round(scale * 0.9, 2), "flicker": True})
        light(x, z, 1.6, 11.0, 1.2)


CARGO = ["Dock_Props_Barrel", "Dock_Props_Crate", "Dock_Props_Box", "Barrel_Oga_1", "Barrel_Oga_2", "Crate_Big", "Crate_Small", "Tv_Sack", "Tv_Sack_2", "Pr_Basket", "Tv_Basket", "Bucket_Wooden_1"]
BONES = ["Dungeon_BonePile_%d" % i for i in range(1, 7)] + ["Dungeon_CrossBones", "Dungeon_Pelvis", "Dungeon_Arm", "Dungeon_Leg", "Dungeon_Skull_1", "Dungeon_Skull_2"]
BOATS = ["Dock_Boat_A_1", "Dock_Boat_A_2", "Dock_Boat_B_1"]

# --- bitolas (cabeços) ao longo das bordas de todos os píeres e postes de apoio
for r in rooms:
    cx, cz = r["center"]
    w, h = r["size"]
    n = max(3, round((w + h) / 14))
    for _ in range(n):
        side = rng.choice("nsew")
        t = rng.uniform(-0.45, 0.45)
        x, z = (cx + t * w, cz - h / 2 + 0.9) if side == "n" else (cx + t * w, cz + h / 2 - 0.9) if side == "s" else (cx - w / 2 + 0.9, cz + t * h) if side == "w" else (cx + w / 2 - 0.9, cz + t * h)
        put("Dock_Dock_Bollard_1", x, z, rot=rng.randrange(0, 360, 15), solid=[0.4, 0.4], r=0.6, free=2.6)
# --- cais de partida: poste de luz, estandartes, carga e o barco no cavalete
lamp(-8, -3), lamp(8, 5)
put("Dock_Boat_Stand", 12, 4, rot=90, solid=[3.0, 1.5], r=2.5)
for x in (-13, 13):
    put("War_Banner", x, -6, rot=0, scale=1.0, r=0.8)
for x, z in ((-14, 6), (14, -6), (-2, -6), (4, 6)):
    torch(x, z)
scatter("landing", CARGO, 14, scale=(0.9, 1.2), margin=3.0)
scatter("fish_pier", CARGO, 10, scale=(0.9, 1.2), margin=2.0)
put("Dock_Props_Rack_Fish", -34, -3, rot=0, solid=[2.4, 1.1], r=1.5)
put("Dock_Props_Rack", -28, 3, rot=180, solid=[2.4, 1.1], r=1.5)
put("Dock_Props_Table_1", -38, 2, rot=0, solid=[1.8, 1.1], r=1.2)
put("Dock_Props_Bench", -38, 3.8, rot=0, r=0.8)
scatter("boathouse", CARGO, 12, scale=(0.9, 1.2), margin=2.0)
put("Dock_Boat_Stand", 30, -2, rot=0, solid=[3.0, 1.5], r=2.5)
put("Cart_Wood", 40, 2, rot=40, scale=1.3, solid=[2.6, 1.3], r=1.6)
# --- píer principal e calçada: postes de luz e tochas
for z in (-12, -24):
    lamp(-4.2, z), lamp(4.2, z)
for z in (-66, -74, -82, -90):
    torch(-5.2, z)
    torch(5.2, z)
scatter("main_pier", CARGO, 4, scale=(0.9, 1.1), margin=1.5)
# --- Mercado de Peixe: bancas, balcões de peixe, carrinhos, carga, cestos e bandeiras
for x in (-24, -12, 12, 24):
    for z, rot in ((-58, 0), (-34, 180)):
        put("Stall_Empty", x, z, rot=rot, scale=1.5, solid=[2.7, 1.4], r=2.0)
put("Stall_Cart_Empty", -26, -46, rot=90, scale=1.3, solid=[1.5, 4.0], r=2.2)
put("Stall_Cart_Empty", 26, -46, rot=270, scale=1.3, solid=[1.5, 4.0], r=2.2)
for x, z, rot in ((-18, -46, 90), (18, -46, 90), (-6, -52, 0), (6, -40, 180)):
    put("Dock_Props_Rack_Fish", x, z, rot=rot, solid=[2.4, 1.1], r=1.6)
    put("Vl_FishRack", x + rng.choice((-3, 3)), z + 3, rot=rot, scale=1.1, solid=[2.0, 1.0], r=1.4)
for x, z in ((-28, -40), (28, -52), (-10, -32), (10, -60)):
    lamp(x, z)
for x, z in ((-30, -34), (30, -34), (-30, -58), (30, -58)):
    put("Banner_1", x, z, rot=0, scale=1.2, r=0.8)
scatter("market", CARGO, 34, scale=(0.9, 1.3), margin=3.0)
scatter("market", ["Cart_Wood", "Dock_Props_Table_1"], 3, scale=(1.2, 1.4), solid=(2.2, 1.2), margin=5.0, r=1.8)
put("Pr_CoveredWell", 0, -46, rot=0, scale=1.3, solid=[2.3, 2.3], r=2.0, free=0.5)
# --- Estaleiro: cavaletes com barcos em reparo, toras, bigorna, cepos e ferramentas
for x, z, rot in ((-64, -76, 90), (-64, -62, 90), (-40, -80, 90), (-44, -58, 0)):
    put("Dock_Boat_Stand", x, z, rot=rot, solid=[3.0, 1.6], r=2.6)
    put(rng.choice(BOATS), x, z, rot=rot, y=0.9, r=0.1, force=True)
scatter("shipyard", ["Vl_Logs", "Vl_ChoppingBlock"], 8, scale=(1.0, 1.4), solid=(1.5, 0.8), margin=3.0, r=1.2)
scatter("shipyard", ["Anvil", "Cauldron", "Bucket_Wooden_1", "Axe_Bronze"], 5, scale=(1.0, 1.4), margin=3.0, r=1.0)
scatter("shipyard", CARGO, 30, scale=(0.9, 1.3), margin=3.0)
for x, z in ((-70, -86), (-34, -86), (-70, -52), (-36, -52)):
    torch(x, z)
# --- Peixaria: secadores de peixe, mesas, caixas de gelo e redes
for x, z in ((38, -52), (66, -52), (38, -88), (66, -88)):
    put("Dock_Props_Rack_Fish", x, z, rot=0, solid=[2.4, 1.1], r=1.6)
scatter("fishery", ["Dock_Props_Rack_Fish", "Dock_Props_Rack", "Vl_FishRack"], 6, scale=(1.0, 1.2), solid=(2.2, 1.0), margin=3.0, r=1.6)
scatter("fishery", ["Dock_Props_Table_1", "Dock_Props_Bench"], 4, scale=(1.0, 1.2), solid=(1.5, 1.0), margin=3.0, r=1.2)
scatter("fishery", CARGO, 20, scale=(0.9, 1.3), margin=3.0)
for x, z in ((36, -54), (68, -54), (36, -86), (68, -86)):
    torch(x, z)
put("Stall_Empty", 38, -62, rot=180, scale=1.5, solid=[2.7, 1.4], r=2.0)
# --- Farol (oeste): braseiro enorme no centro, estátuas-lâmpada e tochas
brazier(-55, -105, 3.0)
for dx, dz in ((-9, -9), (9, -9), (-9, 9), (9, 9)):
    if put("Statue_Lamp", -55 + dx, -105 + dz, rot=0, scale=1.3, solid=[2.4, 1.4], r=2.0):
        light(-55 + dx, -105 + dz, 1.0, 8.0, 2.8, (1.0, 0.85, 0.5))
scatter("lighthouse", CARGO, 10, scale=(0.9, 1.2), margin=3.0)
scatter("lighthouse", BONES, 6, scale=(2.5, 3.5), margin=3.0, r=0.8)
# --- Armazém (leste): pilhas de carga, jaulas, moedas e baús
scatter("warehouse", CARGO, 30, scale=(1.0, 1.5), margin=2.5, r=1.0)
scatter("warehouse", ["Cage_Small", "Coin_Pile", "Chest_Large"], 6, scale=(1.2, 1.6), margin=3.0, r=1.2)
scatter("warehouse", ["Cart_Wood"], 2, scale=(1.3, 1.5), solid=(2.6, 1.3), margin=4.0, r=1.8)
for x, z in ((43, -118), (67, -118), (43, -92), (67, -92)):
    torch(x, z)
# --- Atracadouro: bandeiras piratas, carga e postes de luz
for x in (-28, -14, 14, 28):
    put("War_Banner", x, -113, rot=0, scale=1.2, r=0.9)
for x in (-34, -20, -8, 8, 20, 34):
    lamp(x, -101)
scatter("wharf", CARGO, 18, scale=(0.9, 1.3), margin=2.5)
scatter("wharf", BONES, 6, scale=(2.5, 3.5), margin=2.5, r=0.8)
# --- corredor do portão: lanternas e bandeiras
for z in (-122, -128, -136):
    lamp(-3.8, z), lamp(3.8, z)
for z in (-126, -134):
    put("War_Banner", -3.8, z, rot=90, scale=1.1, r=0.8, free=1.0)
    put("War_Banner", 3.8, z, rot=270, scale=1.1, r=0.8, free=1.0)
# --- Convés do Capitão Afogado: braseiros, bandeiras, carga, tesouro e os ossos da tripulação
for x in (-26, 26):
    for z in (-150, -164, -178):
        brazier(x, z, 2.0)
for x in (-14, 14):
    for z in (-152, -170):
        put("War_Banner", x, z, rot=0, scale=1.3, r=1.0)
scatter("deck", CARGO, 44, scale=(1.0, 1.4), margin=3.0)
scatter("deck", BONES, 34, scale=(2.5, 3.5), margin=4.0, r=0.8)
scatter("deck", ["Dungeon_SkullPile", "Dungeon_Ribcage"], 8, scale=(3.0, 4.5), margin=4.0, r=1.2)
scatter("deck", ["Coin_Pile", "Chest_Large", "Cage_Small"], 8, scale=(1.3, 1.8), margin=4.0, r=1.4)
for x, z in ((-30, -190), (30, -190), (-30, -146), (30, -146)):
    lamp(x, z)

# --- mar: barcos de verdade e galeões piratas ancorados em volta do porto; peixes e caranguejos
def in_sea(x, z, pad):
    return room_at(x, z, pad) is None


for x, z, rot in ((-86, -107, 90), (86, -107, 90), (-50, -194, 70), (50, -194, 110), (-86, -40, 80), (86, -40, 100)):
    decor.append({"piece": "pirate_ship", "position": [x, z], "y": 0.0, "scale": 0.95, "rotation": rot})
placed = []
for _ in range(400):
    if len(placed) >= 34:
        break
    x, z = rng.uniform(-96, 96), rng.uniform(-205, 14)
    if not in_sea(x, z, 5.0) or any(math.hypot(x - px, z - pz) < 9 for px, pz in placed) or any(math.hypot(x - sx, z - sz) < 14 for sx, sz in ((-86, -107), (86, -107), (-50, -194), (50, -194), (-86, -40), (86, -40))):
        continue
    placed.append((x, z))
    decor.append({"piece": rng.choice(BOATS), "position": [round(x, 1), round(z, 1)], "y": -0.2, "rotation": rng.randrange(0, 360, 15)})
fish = []
for _ in range(2000):
    if len(fish) >= 40:
        break
    x, z, radius = rng.uniform(-100, 100), rng.uniform(-205, 14), rng.uniform(1.0, 2.2)
    if not in_sea(x, z, radius + 1.0) or any((x - f["position"][0]) ** 2 + (z - f["position"][1]) ** 2 < 36 for f in fish) or any(math.hypot(x - px, z - pz) < 5 for px, pz in placed):
        continue
    fish.append({"piece": "Fish_Catfish", "position": [round(x, 2), round(z, 2)], "y": -0.03, "scale": 2.2, "swim": {"radius": round(radius, 2), "speed": round(rng.uniform(0.5, 1.0), 2), "phase": round(rng.uniform(0, 6.28), 2)}})
decor += fish
crowd = []
for rid in ("landing", "market", "fishery", "shipyard", "wharf", "deck", "boathouse", "fish_pier"):
    cx, cz, w, h = by_id[rid][1:]
    for _ in range(2):
        x, z = cx + rng.uniform(-w / 2 + 3, w / 2 - 3), cz + rng.uniform(-h / 2 + 3, h / 2 - 3)
        crowd.append({"role": "crab", "position": [round(x, 1), round(z, 1)], "rotation": rng.randrange(0, 360), "pose": "walk", "path": [round(x + rng.uniform(-1.5, 1.5), 1), round(z + rng.uniform(-1.2, 1.2), 1)], "speed": 0.5})

arenas["docks_01_pier"] = {
    "_comment": "Docas, ampliadas (Modular Wooden Docks, loafbrr, CC0): píeres sobre o mar com a estrutura da Floresta e outro caminho. Cais de partida -> Píer Principal -> Mercado de Peixe; laço oeste (Estaleiro: casco encalhado "
                "desperta o Casco Vivo) e laço leste (Peixaria: a Peixeira desperta o Tubarão-Porco), fechando no Farol e no Armazém; Calçada -> Atracadouro -> corredor do portão (Vigia, duas chaves) -> Convés do "
                "Capitão Afogado (chefe final, com a saída). Mantém os encontros dk_* da missão dos contrabandistas. Gerado por tools/assets/build_docks.py.",
    "name_key": "ARENA_DOCKS", "player_class": "mage", "map_id": "map_docks", "area_level": 2, "outdoor": True, "final": True, "victory_groups": ["dk_captain"], "wake_radius": 10.0, "alert_radius": 5.0,
    "rooms": rooms, "encounters": encounters, "hazards": [], "entries": {"start": [0, 3], "docks": [0, 3]}, "props": props, "quest_spots": [],
    "breakables": [{"id": "coin_bag", "monster": "coin_bag", "position": [4.0, 1.5], "table": "coin_bag"}] + [
        {"id": "coin_bag_%d" % i, "monster": "coin_bag", "position": p, "table": "coin_bag"} for i, p in enumerate(([-24, -40], [24, -52], [-52, -90], [52, -90], [0, -100], [-20, -176], [20, -176]), start=2)],
    "style": {"_comment": "Docas: tábuas de píer do pacote, cerca de madeira nas bordas; o mar é o objeto 'sea'.", "walls": [""], "floor": "Dock_Floor_Dock_Half",
              "low": "Dock_Fence_Plane_Half", "ground": [0.03, 0.1, 0.16]},
    "decor": decor, "crowd": crowd, "passive": True}

# ---------------------------------------------------------------- NPCs e missões (mesma forma da Floresta e do Deserto)
def body(sex, hair, color):
    return {"sex": sex, "hair": [hair], "hair_color": color, "pose": "idle", "outfit": {"body": "cloth"}}


npcs["dock_master"] = {"name_key": "NPC_DOCK_MASTER", "color": [0.3, 0.45, 0.6], "dialogues": [
    {"when": {"quest_new": "dock_helm"}, "lines": ["DLG_DOCKMASTER_1", "DLG_DOCKMASTER_2", "DLG_DOCKMASTER_3"], "offer": "dock_helm"},
    {"when": {"quest_active": "dock_helm"}, "lines": ["DLG_DOCKMASTER_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_DOCKMASTER_DONE"]}], "body": body("male", "Hair_SimpleParted", [0.35, 0.3, 0.25])}
npcs["wrecked_hull"] = {"name_key": "NPC_WRECKED_HULL", "color": [0.45, 0.35, 0.25], "dialogues": [
    {"when": {"quest_active": "dock_helm"}, "lines": ["DLG_HULL_1", "DLG_HULL_2"]}, {"when": {}, "lines": ["DLG_HULL_LOCKED"]}]}
npcs["dock_fishwife"] = {"name_key": "NPC_DOCK_FISHWIFE", "color": [0.7, 0.4, 0.35], "dialogues": [
    {"when": {"quest_new": "dock_tooth"}, "lines": ["DLG_FISHWIFE_1", "DLG_FISHWIFE_2", "DLG_FISHWIFE_3"], "offer": "dock_tooth"},
    {"when": {"quest_active": "dock_tooth"}, "lines": ["DLG_FISHWIFE_ACTIVE"], "service": "turn_in"},
    {"when": {"quest_done": "dock_tooth"}, "lines": ["DLG_FISHWIFE_DONE"]}, {"when": {}, "lines": ["DLG_FISHWIFE_WAIT"]}], "body": body("female", "Hair_Long", [0.45, 0.2, 0.1])}
npcs["dock_sentinel"] = {"name_key": "NPC_DOCK_SENTINEL", "color": [0.4, 0.45, 0.5], "dialogues": [
    {"when": {"quest_new": "dock_gate"}, "lines": ["DLG_DOCKGUARD_1", "DLG_DOCKGUARD_2", "DLG_DOCKGUARD_3"], "offer": "dock_gate"},
    {"when": {"quest_active": "dock_gate"}, "lines": ["DLG_DOCKGUARD_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_DOCKGUARD_DONE"]}], "body": body("male", "Hair_SimpleParted", [0.12, 0.1, 0.1])}
quests["dock_helm"] = {"name_key": "QUEST_DOCK_HELM", "desc_key": "QUEST_DOCK_HELM_DESC", "type": "village", "giver": "dock_master", "area": "docks_01_pier", "target_element": "air",
                       "reward": {"gold": 120, "xp": 240}, "item": "ship_helm", "gives": "key_anchor"}
quests["dock_tooth"] = {"name_key": "QUEST_DOCK_TOOTH", "desc_key": "QUEST_DOCK_TOOTH_DESC", "type": "village", "giver": "dock_fishwife", "area": "docks_01_pier", "target_element": "earth",
                        "reward": {"gold": 120, "xp": 240}, "item": "golden_shark_tooth", "gives": "key_compass"}
quests["dock_gate"] = {"name_key": "QUEST_DOCK_GATE", "desc_key": "QUEST_DOCK_GATE_DESC", "type": "village", "giver": "dock_sentinel", "area": "docks_01_pier",
                       "items": ["key_anchor", "key_compass"], "opens_gate": "boss_gate", "target_element": "earth", "reward": {"gold": 160, "xp": 320}}
T = {
    "MONSTER_HULL_BEAST": ("Casco Vivo", "Living Hull", "Casco Viviente"),
    "MONSTER_PORK_SHARK": ("Tubarão-Porco", "Pork Shark", "Tiburón-Cerdo"),
    "MONSTER_DROWNED_CAPTAIN": ("Capitão Afogado", "Drowned Captain", "Capitán Ahogado"),
    "NPC_DOCK_MASTER": ("Mestre do Porto", "Harbor Master", "Maestro del Puerto"),
    "NPC_WRECKED_HULL": ("Casco Encalhado", "Beached Hull", "Casco Varado"),
    "NPC_DOCK_FISHWIFE": ("Peixeira", "Fishwife", "Pescadera"),
    "NPC_DOCK_SENTINEL": ("Vigia do Cais", "Dock Watchman", "Vigía del Muelle"),
    "VALUABLE_SHIP_HELM": ("Leme do Casco Vivo", "Living Hull's Helm", "Timón del Casco Viviente"),
    "VALUABLE_GOLDEN_SHARK_TOOTH": ("Dente de Ouro do Tubarão", "Shark's Golden Tooth", "Diente de Oro del Tiburón"),
    "VALUABLE_KEY_ANCHOR": ("Chave da Âncora", "Anchor Key", "Llave del Ancla"),
    "VALUABLE_KEY_COMPASS": ("Chave da Bússola", "Compass Key", "Llave de la Brújula"),
    "TOAST_HULL_AWAKENS": ("O casco range e se levanta: o Casco Vivo acorda!", "The hull creaks and rises: the Living Hull awakens!", "El casco cruje y se levanta: ¡el Casco Viviente despierta!"),
    "TOAST_SHARK_AWAKENS": ("A água ferve: o Tubarão-Porco salta para o cais!", "The water boils: the Pork Shark leaps onto the pier!", "El agua hierve: ¡el Tiburón-Cerdo salta al muelle!"),
    "QUEST_DOCK_HELM": ("O Leme Perdido", "The Lost Helm", "El timón perdido"),
    "QUEST_DOCK_HELM_DESC": ("O Mestre do Porto quer o leme de volta: um casco encalhado no Estaleiro (a oeste do mercado) acorda como o Casco Vivo, que o carrega. Toque o casco, derrote-o e traga o leme: em troca vem a Chave da Âncora, uma das duas do portão do Capitão Afogado.",
                             "The Harbor Master wants his helm back: a beached hull in the Shipyard (west of the market) wakes as the Living Hull, which carries it. Touch the hull, defeat it and bring the helm: in return you get the Anchor Key, one of the two for the Drowned Captain's gate.",
                             "El Maestro del Puerto quiere su timón: un casco varado en el Astillero (al oeste del mercado) despierta como el Casco Viviente, que lo lleva. Toca el casco, derrótalo y trae el timón: a cambio recibes la Llave del Ancla, una de las dos del portón del Capitán Ahogado."),
    "QUEST_DOCK_TOOTH": ("O Dente de Ouro", "The Golden Tooth", "El diente de oro"),
    "QUEST_DOCK_TOOTH_DESC": ("A Peixeira perdeu o dente de ouro do marido para o Tubarão-Porco, na Peixaria a leste do mercado. A fala dela o desperta; derrote-o e traga o dente para receber a Chave da Bússola, a outra do portão do Capitão Afogado.",
                              "The Fishwife lost her husband's golden tooth to the Pork Shark, at the Fishery east of the market. Her words wake it; defeat it and bring the tooth to receive the Compass Key, the other one for the Drowned Captain's gate.",
                              "La Pescadera perdió el diente de oro de su marido ante el Tiburón-Cerdo, en la Pescadería al este del mercado. Sus palabras lo despiertan; derrótalo y trae el diente para recibir la Llave de la Brújula, la otra del portón del Capitán Ahogado."),
    "QUEST_DOCK_GATE": ("O Portão do Capitão", "The Captain's Gate", "El portón del Capitán"),
    "QUEST_DOCK_GATE_DESC": ("O Vigia do Cais só abre o portão para quem trouxer as duas chaves: a da Âncora (Mestre do Porto) e a da Bússola (Peixeira). Atrás dele fica o Convés do Capitão Afogado.",
                             "The Dock Watchman only opens the gate for those with both keys: the Anchor (Harbor Master) and the Compass (Fishwife). Beyond lies the Drowned Captain's Deck.",
                             "El Vigía del Muelle solo abre el portón a quien traiga las dos llaves: la del Ancla (Maestro del Puerto) y la de la Brújula (Pescadera). Tras él está la Cubierta del Capitán Ahogado."),
    "DLG_DOCKMASTER_1": ("Maré baixa, forasteiros, e ainda assim o porto não dorme. Eu cuido deste cais há trinta anos e nunca vi o mar tão inquieto.",
                         "Low tide, strangers, and still the port does not sleep. I have run this dock for thirty years and never seen the sea so restless.",
                         "Marea baja, forasteros, y aun así el puerto no duerme. Cuido este muelle hace treinta años y nunca vi el mar tan inquieto."),
    "DLG_DOCKMASTER_2": ("Um casco encalhado no Estaleiro, a oeste do mercado, anda se mexendo à noite. Ele engoliu o leme do meu último navio, e sem o leme eu não largo nada daqui.",
                         "A beached hull in the Shipyard, west of the market, moves at night. It swallowed the helm of my last ship, and without it I cannot cast off anything here.",
                         "Un casco varado en el Astillero, al oeste del mercado, se mueve de noche. Se tragó el timón de mi último barco, y sin él no puedo soltar nada de aquí."),
    "DLG_DOCKMASTER_3": ("Toquem o casco, derrubem o que sair dele e tragam o leme. Em troca eu dou a Chave da Âncora, uma das duas que abrem o portão do Capitão Afogado, no fim do cais.",
                         "Touch the hull, bring down what comes out and bring me the helm. In return I give the Anchor Key, one of the two that open the Drowned Captain's gate at the end of the dock.",
                         "Toquen el casco, derriben lo que salga y tráiganme el timón. A cambio doy la Llave del Ancla, una de las dos que abren el portón del Capitán Ahogado, al final del muelle."),
    "DLG_DOCKMASTER_ACTIVE": ("O Estaleiro fica a oeste do mercado de peixe: sigam o píer principal e virem à esquerda. O leme é de bronze e cheira a sal. Tragam-no e a chave é de vocês.",
                              "The Shipyard is west of the fish market: follow the main pier and turn left. The helm is bronze and smells of salt. Bring it and the key is yours.",
                              "El Astillero está al oeste del mercado de pescado: sigan el muelle principal y giren a la izquierda. El timón es de bronce y huele a sal. Tráiganlo y la llave es suya."),
    "DLG_DOCKMASTER_DONE": ("O meu leme! Agora este velho porto volta a ter um futuro. A Chave da Âncora é de vocês; levem-na ao Vigia, junto com a da Bússola.",
                            "My helm! Now this old port has a future again. The Anchor Key is yours; take it to the Watchman, together with the Compass one.",
                            "¡Mi timón! Ahora este viejo puerto vuelve a tener futuro. La Llave del Ancla es suya; llévenla al Vigía, junto con la de la Brújula."),
    "DLG_HULL_1": ("As tábuas estão quentes e úmidas, e pregos novos brotam da madeira. Algo grande respira dentro do casco.",
                   "The planks are warm and damp, and new nails sprout from the wood. Something large breathes inside the hull.",
                   "Las tablas están calientes y húmedas, y brotan clavos nuevos de la madera. Algo grande respira dentro del casco."),
    "DLG_HULL_2": ("O Casco Vivo acorda!", "The Living Hull awakens!", "¡El Casco Viviente despierta!"),
    "DLG_HULL_LOCKED": ("Um casco velho no cavalete. Nada responde às suas mãos.", "An old hull on its cradle. Nothing answers your hands.", "Un casco viejo en su caballete. Nada responde a sus manos."),
    "DLG_FISHWIFE_1": ("Peixe fresquinho, só hoje! ...Ah, desculpem, hábito. Hoje nem tenho o que vender: o Tubarão-Porco anda comendo as redes todas.",
                       "Fresh fish, today only! ...Oh, sorry, habit. Today I have nothing to sell: the Pork Shark has been eating all the nets.",
                       "¡Pescado fresquito, solo hoy! ...Ah, perdón, costumbre. Hoy no tengo nada que vender: el Tiburón-Cerdo se come todas las redes."),
    "DLG_FISHWIFE_2": ("Ele levou também o dente de ouro do meu marido, que caiu na água quando ele brigou com a fera. Era tudo o que a gente tinha de valor.",
                       "It also took my husband's golden tooth, which fell in the water when he fought the beast. It was all we had of value.",
                       "También se llevó el diente de oro de mi marido, que cayó al agua cuando peleó con la bestia. Era todo lo que teníamos de valor."),
    "DLG_FISHWIFE_3": ("Vou chamar a fera para vocês, aqui na Peixaria. Derrubem o Tubarão-Porco e tragam o dente: eu dou a Chave da Bússola, a outra do portão do Capitão Afogado.",
                       "I will call the beast for you, here at the Fishery. Bring down the Pork Shark and bring the tooth: I give the Compass Key, the other for the Drowned Captain's gate.",
                       "Llamaré a la bestia para ustedes, aquí en la Pescadería. Derriben al Tiburón-Cerdo y traigan el diente: doy la Llave de la Brújula, la otra del portón del Capitán Ahogado."),
    "DLG_FISHWIFE_ACTIVE": ("O dente brilha mais que escama nova. Está na boca da fera. Derrubem-na e tragam-no para mim.",
                            "The tooth shines brighter than a fresh scale. It is in the beast's mouth. Bring it down and bring the tooth to me.",
                            "El diente brilla más que una escama nueva. Está en la boca de la bestia. Derríbenla y tráiganmelo."),
    "DLG_FISHWIFE_DONE": ("O dente do meu velho! A Chave da Bússola é de vocês. Levem-na ao Vigia, no corredor ao norte do atracadouro.",
                          "My old man's tooth! The Compass Key is yours. Take it to the Watchman, in the lane north of the wharf.",
                          "¡El diente de mi viejo! La Llave de la Brújula es suya. Llévenla al Vigía, en el pasillo al norte del atracadero."),
    "DLG_FISHWIFE_WAIT": ("As redes estão rasgadas, mas a maré volta. Levem um peixe, está fresquinho.", "The nets are torn, but the tide returns. Take a fish, it is fresh.", "Las redes están rotas, pero la marea vuelve. Lleven un pescado, está fresquito."),
    "DLG_DOCKGUARD_1": ("Parem aí. Este portão fecha o Convés, e no Convés manda o Capitão Afogado. Ele navegou até o fundo do mar e voltou com a tripulação inteira.",
                        "Stop there. This gate closes the Deck, and on the Deck the Drowned Captain rules. He sailed to the bottom of the sea and came back with his whole crew.",
                        "Alto ahí. Este portón cierra la Cubierta, y en la Cubierta manda el Capitán Ahogado. Navegó hasta el fondo del mar y volvió con toda la tripulación."),
    "DLG_DOCKGUARD_2": ("O portão só abre com DUAS chaves: a da Âncora e a da Bússola. A primeira está com o Mestre do Porto, no cais de chegada; a segunda, com a Peixeira, na Peixaria.",
                        "The gate only opens with TWO keys: the Anchor and the Compass. The first is with the Harbor Master at the landing; the second, with the Fishwife at the Fishery.",
                        "El portón solo abre con DOS llaves: la del Ancla y la de la Brújula. La primera la tiene el Maestro del Puerto, en el muelle de llegada; la segunda, la Pescadera, en la Pescadería."),
    "DLG_DOCKGUARD_3": ("Cada um cobra um preço: um leme, um dente de ouro. Tragam as duas chaves a mim e eu abro a passagem.",
                        "Each charges a price: a helm, a golden tooth. Bring both keys to me and I will open the way.",
                        "Cada uno cobra un precio: un timón, un diente de oro. Tráiganme las dos llaves y abro el paso."),
    "DLG_DOCKGUARD_ACTIVE": ("Só abro com as duas chaves, Âncora e Bússola, na mesma bolsa. O Mestre do Porto fica no cais de chegada; a Peixeira, na Peixaria a leste do mercado.",
                             "I only open with both keys, Anchor and Compass, in the same bag. The Harbor Master is at the landing; the Fishwife, at the Fishery east of the market.",
                             "Solo abro con las dos llaves, Ancla y Brújula, en la misma bolsa. El Maestro del Puerto está en el muelle de llegada; la Pescadera, en la Pescadería al este del mercado."),
    "DLG_DOCKGUARD_DONE": ("As duas chaves! O portão está aberto. Cuidado: o Capitão Afogado nunca perdeu um navio, e não vai perder este.",
                           "Both keys! The gate is open. Beware: the Drowned Captain never lost a ship, and he will not lose this one.",
                           "¡Las dos llaves! El portón está abierto. Cuidado: el Capitán Ahogado nunca perdió un barco, y no perderá este."),
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
    for dst, src, mul in (("key_anchor", "key_spades", (1.3, 1.1, 0.5)), ("key_compass", "key_hearts", (0.5, 1.2, 1.2)), ("ship_helm", "bone_dagger", (0.8, 0.6, 0.4)),
                          ("golden_shark_tooth", "royal_seal_ring", (1.0, 0.95, 0.5))):
        im = Image.open(ICONS + src + ".png").convert("RGBA")
        r_, g_, b_, a_ = im.split()
        Image.merge("RGBA", (r_.point(lambda v: min(255, int(v * mul[0]))), g_.point(lambda v: min(255, int(v * mul[1]))), b_.point(lambda v: min(255, int(v * mul[2]))), a_)).save(ICONS + dst + ".png")
except Exception as exc:
    print("aviso: ícones não gerados:", exc)

for path, data in ((ARENAS, arenas), (MONSTERS, monsters), (NPCS, npcs), (QUESTS, quests), (VALUABLES, valuables)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
print("OK docks", len(rooms), "salas,", len(decor), "peças de cenário,", len(encounters), "encontros")
