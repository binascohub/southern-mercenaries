"""Mapa do Bunker (bunker_01_entrance), ampliado e feito LABIRINTO como o Esgoto, com outro caminho: o bunker de um exército antigo, cheio de armamentos, ferramentas e suprimentos.
Paredes e pilares do 3D Dungeon Modular Wall Set 2 (Paul Wortmann, CC0; peças Bk_*) numa grade de células de 2 m (a mesma do mapa antigo): salas de 5 x 5 células (10 m) separadas por paredes de 1 célula,
ligadas por vãos de 3 células (árvore crescente com muitos becos e alguns laços; setores de monstros). Salas especiais nas laterais, ligadas ao labirinto por vãos: Depósito de Suprimentos e Alojamento (leste),
Cofre (leste, no alto), Arsenal e Enfermaria (oeste). A Guarnição (partida) fica ao sul; o túnel do portão e a Sala de Comando (chefe final), ao norte.
  Intendente Vorn (Depósito) pede o Selo do Arsenal: tocar o rack de armas do Arsenal (missão ativa) desperta a Armadura Viva; entrega a Chave de Latão.
  Médica de Campo Lena (Enfermaria) pede a Medalha de Guerra: tocar o catre do Alojamento desperta o Comandante Podre; entrega a Chave de Aço.
  A Sentinela só abre o portão com as duas chaves; atrás dele, a Sala de Comando do General Ferrugem (chefe final, com a saída).
Sorteio com semente fixa; idempotente; chamado no fim de tools/assets/build_maps.py (antes de set_map_order.py).
uso: python3 tools/assets/build_bunker.py   (a partir da raiz do projeto)"""
import json, math, random, re
from collections import deque
ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES = ("data/arenas.json", "data/monsters.json", "data/npcs.json", "data/quests.json", "data/valuables.json")
arenas, monsters, npcs, quests, valuables = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES))
rng = random.Random("bunker-v2")
NC, NR, P = 7, 9, 6                   # salas do labirinto (colunas x linhas), passo em células finas (5 de sala + 1 de parede)
CELL = 2.0
MX, MY = 13, 19                       # célula da parede de cima, à esquerda do labirinto
MAZE_W, MAZE_H = NC * P + 1, NR * P + 1
COLS, ROWS = MX + MAZE_W + 13, MY + MAZE_H + 8      # margens para as salas especiais, o túnel e a sala de comando (norte), a guarnição (sul)
CC = MX + 3 + P * (NC // 2)           # coluna central do labirinto
grid = [["#"] * COLS for _ in range(ROWS)]


def carve(c0, r0, c1, r1):
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            grid[r][c] = "."


def colc(c): return MX + 3 + P * c
def rowc(r): return MY + 3 + P * r


START, END = (NC // 2, NR - 1), (NC // 2, 0)


def neighbors(c):
    x, z = c
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (x + dx, z + dz)
        if 0 <= n[0] < NC and 0 <= n[1] < NR:
            yield n


passages = set()
seen = {START}
active = [START]
while active:
    cur = active[-1] if rng.random() < 0.7 else rng.choice(active)
    free = [n for n in neighbors(cur) if n not in seen]
    if not free:
        active.remove(cur)
        continue
    n = rng.choice(free)
    passages.add(frozenset((cur, n)))
    seen.add(n)
    active.append(n)
for c in list(seen):
    for n in neighbors(c):
        if frozenset((c, n)) not in passages and rng.random() < 0.07:
            passages.add(frozenset((c, n)))
adj = {c: [n for n in neighbors(c) if frozenset((c, n)) in passages] for c in seen}


def bfs_path(src, goals):
    prev = {src: None}
    q = deque([src])
    while q:
        c = q.popleft()
        if c in goals:
            path = []
            while c is not None:
                path.append(c)
                c = prev[c]
            return path[::-1]
        for n in adj[c]:
            if n not in prev:
                prev[n] = c
                q.append(n)
    raise RuntimeError("sem caminho")


main_path = bfs_path(START, {END})
leaves = [c for c in adj if len(adj[c]) == 1 and c not in (START, END)]
for r in range(NR):
    for c in range(NC):
        carve(MX + 1 + P * c, MY + 1 + P * r, MX + 5 + P * c, MY + 5 + P * r)
door_cells = []                       # (coluna, linha) do centro de cada vão
for p in passages:
    a, b = sorted(p)
    if a[0] == b[0]:                  # mesma coluna: vão na parede horizontal entre as duas salas
        wr = MY + P * max(a[1], b[1])
        carve(colc(a[0]) - 1, wr, colc(a[0]) + 1, wr)
        door_cells.append((colc(a[0]), wr))
    else:
        wc = MX + P * max(a[0], b[0])
        carve(wc, rowc(a[1]) - 1, wc, rowc(a[1]) + 1)
        door_cells.append((wc, rowc(a[1])))
# salas especiais: (id, lado, linha da sala do labirinto, interior c0..c1, r0..r1)
SPECIALS = {"depot": ("east", 7), "barracks": ("east", 4), "vault": ("east", 1), "arsenal": ("west", 5), "infirmary": ("west", 2)}
spec_rect = {}
for k, (side, r) in SPECIALS.items():
    r0, r1 = rowc(r) - 4, rowc(r) + 4
    if side == "west":
        c0, c1, wc, cell = 2, MX - 1, MX, 0
    else:
        c0, c1, wc, cell = MX + MAZE_W, COLS - 3, MX + MAZE_W - 1, NC - 1
    carve(c0, r0, c1, r1)
    carve(wc, rowc(r) - 1, wc, rowc(r) + 1)
    door_cells.append((wc, rowc(r)))
    spec_rect[k] = (c0, r0, c1, r1, (cell, r))
HALL = (CC - 7, MY + MAZE_H, CC + 7, ROWS - 3)                  # guarnição (partida), ao sul
carve(*HALL)
carve(CC - 1, MY + MAZE_H - 1, CC + 1, MY + MAZE_H - 1)         # vão da parede de baixo do labirinto
door_cells.append((CC, MY + MAZE_H - 1))
carve(CC - 1, MY - 6, CC + 1, MY - 1)                           # túnel do portão
carve(CC - 1, MY, CC + 1, MY)                                   # vão da parede de cima do labirinto
carve(CC - 10, 1, CC + 10, MY - 8)                              # sala de comando
carve(CC - 1, MY - 7, CC + 1, MY - 7)
door_cells += [(CC, MY), (CC, MY - 7)]
_flood, _stack = set(), [(CC, ROWS - 4)]
while _stack:
    c, r = _stack.pop()
    if (c, r) in _flood or not (0 <= c < COLS and 0 <= r < ROWS) or grid[r][c] == "#":
        continue
    _flood.add((c, r))
    _stack += [(c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)]
assert _flood == {(c, r) for r in range(ROWS) for c in range(COLS) if grid[r][c] != "#"}, "há piso do Bunker sem ligação com a partida"
FLOOR_CELLS = len(_flood)


def is_open(c, r): return 0 <= c < COLS and 0 <= r < ROWS and grid[r][c] == "."
def pos(c, r): return [round((c - COLS / 2 + 0.5) * CELL, 2), round((r - ROWS / 2 + 0.5) * CELL, 2)]
def to_cell(x, z): return int(math.floor(x / CELL + COLS / 2)), int(math.floor(z / CELL + ROWS / 2))


def floor_clear(x, z, margin=1):
    c, r = to_cell(x, z)
    return all(is_open(c + i, r + j) for i in range(-margin, margin + 1) for j in range(-margin, margin + 1))


# ---------------------------------------------------------------- paredes, pilares, rochas e colisões (como o mapa antigo)
decor = []
bk_h, bk_v = set(), set()
for r in range(ROWS):
    for c in range(COLS):
        if is_open(c, r):
            if not is_open(c, r - 1): bk_h.add((c, r))
            if not is_open(c, r + 1): bk_h.add((c, r + 1))
            if not is_open(c - 1, r): bk_v.add((c, r))
            if not is_open(c + 1, r): bk_v.add((c + 1, r))
for r in range(ROWS):
    for c in range(COLS):
        if not is_open(c, r) and any(is_open(c + i, r + j) for i in range(-2, 3) for j in range(-2, 3)):
            decor.append({"piece": "Bk_Rock", "position": pos(c, r)})          # blocos de rocha só em volta do piso (o resto é maciço escondido)
half_w, half_h = COLS * CELL / 2, ROWS * CELL / 2
for i, j in sorted(bk_h):
    x, z = (i + 0.5) * CELL - half_w, j * CELL - half_h
    decor.append({"piece": "Bk_Wall", "position": [round(x, 2), round(z, 2)], "rotation": 90})
    decor.append({"collider": [CELL, 0.5], "position": [round(x, 2), round(z, 2)]})
for i, j in sorted(bk_v):
    x, z = i * CELL - half_w, (j + 0.5) * CELL - half_h
    decor.append({"piece": "Bk_Wall", "position": [round(x, 2), round(z, 2)]})
    decor.append({"collider": [0.5, CELL], "position": [round(x, 2), round(z, 2)]})
for i in range(COLS + 1):
    for j in range(ROWS + 1):
        edges = ((i - 1, j) in bk_h, (i, j) in bk_h, (i, j - 1) in bk_v, (i, j) in bk_v)
        if not any(edges) or edges in ((True, True, False, False), (False, False, True, True)):
            continue
        x, z = i * CELL - half_w, j * CELL - half_h
        decor.append({"piece": "Bk_Pillar", "position": [round(x, 2), round(z, 2)]})
        decor.append({"collider": [0.9, 0.9], "position": [round(x, 2), round(z, 2)]})

# ---------------------------------------------------------------- monstros novos e itens
def clone(name, base, **changes):
    m = json.loads(json.dumps(monsters[base]))
    m.pop("_comment", None)
    m.pop("quest_drop", None)
    m.update(changes)
    monsters[name] = m


clone("bk_armor", "ruin_warden", _comment="Mini-chefe do Bunker (Arsenal): a Armadura Viva, armadura de guerra que se levanta quando o rack de armas é tocado; investidas.",
      name_key="MONSTER_BK_ARMOR", max_health=300, damage=22, size=2.6, element="earth", look="champ_warrior", color=[0.85, 0.85, 0.95], quest_drop="armory_seal")
clone("bk_commander", "ruin_warden", _comment="Mini-chefe do Bunker (Alojamento): o Comandante Podre, oficial morto que acorda do catre; investidas.",
      name_key="MONSTER_BK_COMMANDER", max_health=320, damage=24, size=2.6, element="water", look="zombie", color=[0.65, 0.85, 0.55], quest_drop="commander_medal")
clone("bk_general", "sphinx", _comment="Chefe final do Bunker: o General Ferrugem, comandante enferrujado que guarda a Sala de Comando atrás do portão; investidas e pisões.",
      name_key="MONSTER_BK_GENERAL", max_health=900, damage=30, size=3.6, element="fire", look="barbarian_monster", color=[0.8, 0.6, 0.5], chest_loot="chest")
valuables.update({
    "armory_seal": {"name_key": "VALUABLE_ARMORY_SEAL", "value": 0, "maps": [], "quest_item": True, "model": "Shield_C"},
    "commander_medal": {"name_key": "VALUABLE_COMMANDER_MEDAL", "value": 0, "maps": [], "quest_item": True, "model": "Coin_Gold"},
    "key_brass": {"name_key": "VALUABLE_KEY_BRASS", "value": 0, "maps": [], "quest_item": True, "model": "Key_Gold"},
    "key_steel": {"name_key": "VALUABLE_KEY_STEEL", "value": 0, "maps": [], "quest_item": True, "model": "Key_Spades"}})


# ---------------------------------------------------------------- encontros
def sector(c, r):
    return 1 if r >= 6 else 2 if r >= 3 else 3


SETS = {1: [[("goblin", 3), ("plague_bat", 2)], [("goblin", 4)], [("skeleton", 3)], [("plague_frog", 4)]],
        2: [[("skeleton", 3), ("goblin", 2)], [("zombie", 3)], [("venom_scorpion", 3)], [("champ_warrior", 1)]],
        3: [[("zombie", 3), ("skeleton", 2)], [("champ_warrior", 2)], [("barbarian_monster", 1)], [("shadow_spirit", 2)]]}
E = lambda eid, p, *mons: {"id": eid, "position": [round(p[0], 1), round(p[1], 1)], "monsters": [{"monster": m, "count": n} for m, n in mons]}


def room_world(c, r): return pos(colc(c), rowc(r))


encounters, counters = [], {}
for c in sorted(seen, key=lambda c: (-c[1], c[0])):
    if c[1] == NR - 1 and c[0] in (NC // 2 - 1, NC // 2, NC // 2 + 1):
        continue
    if rng.random() > (0.5 if c in main_path else 0.62):
        continue
    s = sector(*c)
    counters[s] = counters.get(s, 0) + 1
    x, z = room_world(*c)
    encounters.append(E("bk_s%d_%d" % (s, counters[s]), (x + rng.choice((-3.0, 3.0)), z + rng.choice((-3.0, 3.0))), *rng.choice(SETS[s])))
for c in leaves:
    if rng.random() < 0.15:
        x, z = room_world(*c)
        encounters.append(E("bk_mimic_%d_%d" % c, (x - 3.0, z + 3.0), ("chest_mimic", 1)))
clear_ids = [e["id"] for e in encounters if e["id"].startswith("bk_s1_")][:2]
encounters.append(E("bk_vault", pos((spec_rect["vault"][0] + spec_rect["vault"][2]) // 2, spec_rect["vault"][1] + 3), ("champ_warrior", 2)))
encounters.append(E("bk_boss", pos(CC, 5), ("bk_general", 1)))
encounters.append(E("bk_guard_a", pos(CC - 6, 8), ("skeleton", 3)))
encounters.append(E("bk_guard_b", pos(CC + 6, 8), ("skeleton", 3)))


def spec_center(k):
    c0, r0, c1, r1, _ = spec_rect[k]
    return pos((c0 + c1) // 2, (r0 + r1) // 2)


SUMMON_ARMOR = {"id": "bk_armor", "position": [spec_center("arsenal")[0], spec_center("arsenal")[1] + 6], "spread": 3.0, "toast": "TOAST_ARMORY_AWAKENS", "monsters": [{"monster": "bk_armor", "count": 1, "rank": "miniboss"}]}
SUMMON_COMMANDER = {"id": "bk_commander", "position": [spec_center("barracks")[0], spec_center("barracks")[1] + 6], "spread": 3.0, "toast": "TOAST_COT_AWAKENS",
                    "monsters": [{"monster": "bk_commander", "count": 1, "rank": "miniboss"}]}
props = [
    {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_FARM", "position": pos(CC - 4, ROWS - 4), "to": "farm_01_fields", "entry": "bunker", "expedition_end": True},
    {"id": "victory_portal", "kind": "exit", "name_key": "PROP_RETURN_FARM", "position": pos(CC, 2), "to": "farm_01_fields", "entry": "bunker", "after_victory": True, "group": True},
    {"id": "bk_sergeant", "kind": "npc", "npc": "bk_sergeant", "position": [28.0, 74.0], "rotation": 200},
    {"id": "bk_quartermaster", "kind": "npc", "npc": "bk_quartermaster", "position": pos((spec_rect["depot"][0] + spec_rect["depot"][2]) // 2 - 2, spec_rect["depot"][3] - 1), "rotation": 180},
    {"id": "bk_rack", "kind": "npc", "npc": "bk_rack", "kit": "Weapon_Rack", "rotation": 0, "position": spec_center("arsenal"), "solid": [2.4, 1.0], "summon": SUMMON_ARMOR, "needs_quest": "bk_seal"},
    {"id": "bk_medic", "kind": "npc", "npc": "bk_medic", "position": pos((spec_rect["infirmary"][0] + spec_rect["infirmary"][2]) // 2 + 2, spec_rect["infirmary"][3] - 1), "rotation": 180},
    {"id": "bk_cot", "kind": "npc", "npc": "bk_cot", "kit": "Bed_2", "rotation": 90, "position": spec_center("barracks"), "solid": [1.8, 2.4], "summon": SUMMON_COMMANDER, "needs_quest": "bk_medal"},
    {"id": "boss_gate", "kind": "gate", "name_key": "PROP_BOSS_GATE", "position": pos(CC, MY - 3), "rotation": 0, "scale": 1.5, "block": 6.0, "count": 2, "opened_by": "bk_gate"},
    {"id": "bk_gatekeeper", "kind": "npc", "npc": "bk_gatekeeper", "position": pos(CC, MY - 1), "rotation": 0}]
for i, c in enumerate(rng.sample(leaves, min(len(leaves), 10)), start=1):
    x, z = room_world(*c)
    props.append({"id": "bk_chest_%d" % i, "kind": "chest", "position": [round(x + 3.0, 1), round(z - 3.0, 1)], "loot": "chest"})
for i, (k, dx, dz) in enumerate((("depot", 6, -6), ("arsenal", -6, -6), ("infirmary", 6, -6), ("barracks", -6, -6), ("vault", 0, -6), ("vault", -6, 4)), start=1):
    c = spec_center(k)
    props.append({"id": "bk_potions_%d" % i, "kind": "chest", "position": [round(c[0] + dx, 1), round(c[1] + dz, 1)], "loot": "potion_chest" if i < 5 else "chest", **({"model": "Chest_Mini"} if i < 5 else {})})
interest = [p["position"] for p in props] + [e["position"] for e in encounters] + [SUMMON_ARMOR["position"], SUMMON_COMMANDER["position"]] + [pos(c, r) for c, r in door_cells]
taken = []


def near_interest(x, z, rad):
    return any(math.hypot(x - ix, z - iz) < rad for ix, iz in interest)


def near_taken(x, z, rad):
    return any(math.hypot(x - tx, z - tz) < tr + rad for tx, tz, tr in taken)


def put(piece, x, z, rot=None, scale=1.0, solid=None, y=None, r=0.8, free=2.2, force=False, margin=1):
    if not floor_clear(x, z, margin):
        return False
    if not force and (near_interest(x, z, free) or near_taken(x, z, r)):
        return False
    d = {"piece": piece, "position": [round(x, 2), round(z, 2)], "rotation": int(rot if rot is not None else rng.randrange(0, 360, 15))}
    if y is not None:
        d["y"] = y
    if scale != 1.0:
        d["scale"] = round(scale, 2)
    if solid:
        d["solid"] = [round(solid[0], 2), round(solid[1], 2)]
    decor.append(d)
    taken.append((x, z, r))
    return True


def scatter_rect(c0, r0, c1, r1, pieces, n, scale=(1.0, 1.0), solid=None, r=0.9, tries=40, inset=1, **kw):
    done = 0
    for _ in range(n):
        for _t in range(tries):
            x, z = pos(rng.uniform(c0 + inset, c1 - inset), rng.uniform(r0 + inset, r1 - inset))
            s = rng.uniform(*scale)
            if put(rng.choice(pieces) if isinstance(pieces, list) else pieces, x, z, scale=s, solid=[solid[0] * s, solid[1] * s] if solid else None, r=r * s, **kw):
                done += 1
                break
    return done


def light(x, z, color=(1.0, 0.65, 0.3), rng_=8.0, energy=1.2, y=1.9):
    decor.append({"light": list(color), "position": [round(x, 2), round(z, 2)], "y": y, "range": rng_, "energy": energy})


SUPPLY = ["Crate_Big", "Crate_Long", "Crate_Metal", "Crate_Open", "Crate_Small", "Crate_Wooden", "Barrel", "Barrel_Apples", "Barrel_Oga_1", "Barrel_Oga_2", "Barrel_Oga_Damaged", "Tv_Sack", "Tv_Sack_2", "Bag",
          "Pr_Basket", "Lab_Barrel", "Lab_Crate"]
SHELVES = ["Shelf_Simple", "Shelf_Small_Bottles"]
BOTTLES = ["Bottle_set_1", "Bottle_set_2", "Bottle_set_3", "Bottle_set_4", "Bottle_1", "Bottle_2", "Bottle_3", "Bottle_4"]
FOOD = ["Food_Bread", "Food_Cheese_Wheel", "Food_Meat", "Food_Sausage", "Food_Apple", "Food_Bread_Half", "Food_Cheese"]
ARMS = ["Weapon_Rack", "WeaponStand", "Shield_A", "Shield_B", "Shield_C", "Shield_D", "Shield_Viking", "Shield_Wooden", "Sword_A", "Sword_B", "Sword_C", "Sword_D", "Weapon_Crossbow", "Weapon_Axe", "Weapon_Hammer",
        "Weapon_FM_Great_Axe", "Weapon_FM_Great_Sword", "Weapon_FM_Mace", "Weapon_FM_Spear", "Weapon_FM_War_Axe", "Weapon_MS_Bow", "Weapon_Polearm", "Weapon_Longsword", "Weapon_Shortsword", "Lab_ShieldSword"]
RACKS = ["Weapon_Rack", "WeaponStand"]
TOOLS = ["Tool_Shovel", "Tool_Hoe", "Tool_Pitchfork", "Tool_Scythe", "Tool_Sickle", "Anvil", "Workbench", "Whetstone", "Cauldron", "Vl_ChoppingBlock", "Axe_Bronze", "Vl_Logs"]
BEDS = ["Bed_1", "Bed_2", "Bed_3", "Bed_4"]
FURN = ["Bench_Wood", "Tv_Bench", "Table_Large", "Table_Plate", "Chair_1", "Tv_Table", "Furn_Chair_1", "Furn_Chair_2"]
GEAR = ["Pr_Barricade", "Barricade_Stakes", "Ship_Cannon", "Pr_CartSmall", "Cart_Wood", "War_Banner", "Banner_1"]


def room_decor(c, r):
    """Cada sala do labirinto ganha um tema: depósito (suprimentos), arsenal (armas e escudos), oficina (ferramentas), alojamento (camas e mesas) ou refeitório (mesa e comida)."""
    kind = rng.choice(("supply", "supply", "arms", "tools", "barracks", "mess") if sector(c, r) != 3 else ("arms", "arms", "tools", "supply", "barracks", "mess"))
    c0, r0 = MX + 1 + P * c, MY + 1 + P * r
    c1, r1 = c0 + 4, r0 + 4
    if kind == "supply":
        scatter_rect(c0, r0, c1, r1, SUPPLY, rng.randint(6, 9), scale=(0.95, 1.2), r=0.9)
        scatter_rect(c0, r0, c1, r1, SHELVES, 2, solid=(1.3, 0.5), r=1.2)
    elif kind == "arms":
        scatter_rect(c0, r0, c1, r1, RACKS, 2, scale=(1.0, 1.2), solid=(2.0, 0.8), r=1.4)
        scatter_rect(c0, r0, c1, r1, [p for p in ARMS if p not in RACKS], rng.randint(6, 9), scale=(1.6, 2.4), r=0.6)
        scatter_rect(c0, r0, c1, r1, ["Crate_Metal", "Crate_Long", "Lab_Crate"], 2, r=0.9)
    elif kind == "tools":
        scatter_rect(c0, r0, c1, r1, TOOLS, rng.randint(6, 9), scale=(1.0, 1.4), solid=(0.9, 0.9), r=1.0)
        scatter_rect(c0, r0, c1, r1, SUPPLY, 3, r=0.9)
    elif kind == "barracks":
        scatter_rect(c0, r0, c1, r1, BEDS, rng.randint(3, 4), solid=(1.0, 2.0), r=1.5)
        scatter_rect(c0, r0, c1, r1, ["Bench_Wood", "Tv_Bench", "Chair_1"], 2, solid=(1.2, 0.6), r=1.0)
        scatter_rect(c0, r0, c1, r1, ["Shield_A", "Shield_B", "Weapon_Shortsword", "Bag"], 3, scale=(1.0, 1.3), r=0.6)
    else:
        scatter_rect(c0, r0, c1, r1, ["Table_Large", "Table_Plate", "Tv_Table"], 1, scale=(1.0, 1.2), solid=(2.2, 1.2), r=1.8)
        scatter_rect(c0, r0, c1, r1, FURN[:3] + ["Chair_1"], 3, solid=(1.0, 0.6), r=1.0)
        scatter_rect(c0, r0, c1, r1, FOOD + BOTTLES, 6, scale=(1.0, 1.4), r=0.5)
    if rng.random() < 0.35:
        scatter_rect(c0, r0, c1, r1, GEAR, 1, scale=(1.0, 1.2), solid=(1.2, 1.2), r=1.4)
    if rng.random() < 0.3:
        scatter_rect(c0, r0, c1, r1, ["Web_Round_Up", "Web_Square_Up", "Web_Round_Flat"], 1, scale=(1.5, 2.2), r=1.0)
    if rng.random() < 0.25:
        scatter_rect(c0, r0, c1, r1, ["Dungeon_BonePile_%d" % i for i in range(1, 7)] + ["Dungeon_Skull_1", "Dungeon_CrossBones"], 2, scale=(2.2, 3.0), r=0.7)


for r in range(NR):
    for c in range(NC):
        room_decor(c, r)
# lampiões de parede (Lamp, Mev Lyshkin, CC-BY 3.0): em células abertas junto a uma parede N, W ou E, a pelo menos 9 m uns dos outros; metade com luz
BK_SIDES = {"W": (-1, 0, 90), "E": (1, 0, 270), "N": (0, -1, 0)}
cands = []
for r in range(ROWS):
    for c in range(COLS):
        if not is_open(c, r):
            continue
        for side, (dx, dz, turn) in BK_SIDES.items():
            if not is_open(c + dx, r + dz) and 0 < c + dx < COLS - 1 and 0 < r + dz < ROWS - 1:
                cands.append((c, r, side))
rng.shuffle(cands)
lamps = []
for c, r, side in cands:
    x, z = pos(c, r)
    if any(math.hypot(x - lx, z - lz) < 9.0 for lx, lz in lamps):
        continue
    lamps.append((x, z))
    dx, dz, turn = BK_SIDES[side]
    decor.append({"piece": "Pr_WallLamp", "position": [round(x + dx * 0.75, 2), round(z + dz * 0.75, 2)], "y": 2.3, "rotation": turn})
    if len(lamps) % 2 == 0:
        light(x + dx * 0.2, z + dz * 0.2)
    if len(lamps) >= 70:
        break
# ---- Guarnição (partida): barricadas, canhões, estoque e o braseiro de campanha
c0, r0, c1, r1 = HALL
for c, r, rot in ((c0 + 1, r0 + 1, 0), (c1 - 1, r0 + 1, 0)):
    x, z = pos(c, r)
    put("Ship_Cannon", x, z, rot=180, solid=[0.8, 1.5], r=1.2, free=0.5)
scatter_rect(c0, r0, c1, r1, SUPPLY, 10, scale=(0.95, 1.2), r=0.9)
scatter_rect(c0, r0, c1, r1, ["Pr_Barricade", "Barricade_Stakes", "War_Banner", "Weapon_Rack"], 5, solid=(1.6, 0.8), r=1.4)
x, z = pos(CC, r1 - 1)
put("Tv_Fire", x + 6, z, rot=0, scale=1.4, solid=[1.2, 0.9], r=1.4, free=0.5)
decor.append({"piece": "Fire_Flame", "position": [round(x + 6, 2), round(z, 2)], "y": 0.2, "scale": 1.3, "flicker": True})
light(x + 6, z, (1.0, 0.6, 0.25), 10.0, 1.6, 1.2)
# ---- Salas especiais
for k, (c0, r0, c1, r1, cell) in spec_rect.items():
    cx_, cz_ = spec_center(k)
    if k == "depot":                                    # Depósito de Suprimentos: pilhas de caixotes e barris, prateleiras com garrafas e comida
        scatter_rect(c0, r0, c1, r1, SUPPLY, 22, scale=(0.95, 1.3), r=1.0)
        scatter_rect(c0, r0, c1, r1, SHELVES, 6, solid=(1.3, 0.5), r=1.2)
        scatter_rect(c0, r0, c1, r1, FOOD + BOTTLES, 10, scale=(1.0, 1.4), r=0.5)
        scatter_rect(c0, r0, c1, r1, ["Cart_Wood", "Pr_CartSmall"], 2, solid=(2.0, 1.2), r=1.6, y=0.05)
    elif k == "arsenal":                                # Arsenal: racks, escudos, espadas, bestas, machados, martelos, canhão
        scatter_rect(c0, r0, c1, r1, RACKS, 6, scale=(1.0, 1.3), solid=(2.0, 0.8), r=1.4)
        scatter_rect(c0, r0, c1, r1, [p for p in ARMS if p not in RACKS], 26, scale=(1.7, 2.5), r=0.6)
        scatter_rect(c0, r0, c1, r1, ["Ship_Cannon", "Anvil", "Workbench", "Crate_Metal", "Crate_Long"], 6, solid=(1.4, 1.4), r=1.4)
    elif k == "barracks":                               # Alojamento: fileiras de catres, baús e bancos
        for i, c in enumerate(range(c0 + 1, c1, 2)):
            for r in (r0 + 1, r1 - 1):
                x, z = pos(c, r)
                put(BEDS[(i + r) % 4], x, z, rot=90 if r == r0 + 1 else 270, solid=[1.0, 2.0], r=1.5, free=1.5)
        scatter_rect(c0, r0, c1, r1, ["Bench_Wood", "Tv_Bench", "Table_Large"], 4, solid=(1.6, 0.8), r=1.2)
        scatter_rect(c0, r0, c1, r1, ["Shield_A", "Shield_B", "Weapon_Shortsword", "Bag", "Crate_Small"], 10, scale=(1.0, 1.4), r=0.6)
    elif k == "infirmary":                              # Enfermaria: camas, garrafas, prateleiras
        scatter_rect(c0, r0, c1, r1, BEDS, 7, solid=(1.0, 2.0), r=1.5)
        scatter_rect(c0, r0, c1, r1, SHELVES, 4, solid=(1.3, 0.5), r=1.2)
        scatter_rect(c0, r0, c1, r1, BOTTLES + ["Cauldron", "Bag", "Crate_Small"], 14, scale=(1.0, 1.4), r=0.6)
    else:                                               # Cofre: tesouro do exército
        scatter_rect(c0, r0, c1, r1, ["Gold_Pile_1", "Gold_Pile_2", "Gold_Pile_3", "Coin_Pile", "Chest_Large", "Crate_Metal", "Cage_Small"], 16, scale=(1.2, 1.7), r=1.0)
        scatter_rect(c0, r0, c1, r1, ARMS[2:12], 8, scale=(1.2, 1.6), r=0.6)
    for dc, dr in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        x, z = pos((c0 + c1) // 2 + dc, (r0 + r1) // 2 + dr)
        if floor_clear(x, z, 1):
            light(x, z, (1.0, 0.7, 0.35) if k != "vault" else (1.0, 0.85, 0.4), 8.0, 1.0, 2.0)
# ---- Túnel e Sala de Comando: mesa de guerra, mapas, bandeiras, armas, canhões
for r in (MY - 5, MY - 2):
    light(*pos(CC, r), (1.0, 0.65, 0.3), 6.0, 1.0, 2.0)
put("Table_Large", *pos(CC, 8), rot=0, scale=1.3, solid=[2.6, 1.4], r=2.2, free=0.5)
for dc in (-8, 8):
    for dr in (3, 8):
        put("War_Banner", *pos(CC + dc, dr), rot=0, scale=1.3, r=1.0, free=0.8)
for dc in (-9, 9):
    put("Ship_Cannon", *pos(CC + dc, 10), rot=0, solid=[0.8, 1.5], r=1.4, free=0.5)
scatter_rect(CC - 10, 1, CC + 10, MY - 8, RACKS + ["Shield_A", "Shield_D", "Shield_Viking", "Sword_B", "Weapon_FM_Great_Sword"], 16, scale=(1.0, 1.5), r=0.8)
scatter_rect(CC - 10, 1, CC + 10, MY - 8, SUPPLY, 8, r=0.9)
scatter_rect(CC - 10, 1, CC + 10, MY - 8, ["Dungeon_BonePile_%d" % i for i in range(1, 7)] + ["Dungeon_SkullPile", "Dungeon_Skull_1"], 8, scale=(2.5, 3.5), r=0.8)
for c, r in ((CC - 5, 3), (CC + 5, 3), (CC - 5, 8), (CC + 5, 8)):
    light(*pos(c, r), (1.0, 0.45, 0.3), 9.0, 1.3, 2.0)
light(*pos(CC, 5), (0.9, 0.6, 0.5), 14.0, 1.6, 2.4)

breakables = []
cells = list(seen)
rng.shuffle(cells)
for c in cells:
    if len(breakables) >= 40:
        break
    x, z = room_world(*c)
    px, pz = round(x + rng.choice((-3.4, 3.4)), 1), round(z + rng.choice((-3.4, 3.4)), 1)
    if floor_clear(px, pz, 0) and not near_interest(px, pz, 2.5) and not near_taken(px, pz, 1.0):
        breakables.append({"id": "b%d" % (len(breakables) + 1), "monster": "crate" if len(breakables) % 2 == 0 else "barrel", "position": [px, pz], "table": "breakable_potion"})
        taken.append((px, pz, 1.0))
breakables.append({"id": "coin_bag", "monster": "coin_bag", "position": [round(pos(CC, ROWS - 4)[0] + 4.0, 1), round(pos(CC, ROWS - 4)[1] - 1.5, 1)], "table": "coin_bag"})
for i, p in enumerate((room_world(*main_path[2]), room_world(*main_path[len(main_path) // 2]), room_world(*main_path[-3]), spec_center("depot"), spec_center("arsenal"), spec_center("infirmary")), start=2):
    breakables.append({"id": "coin_bag_%d" % i, "monster": "coin_bag", "position": [round(p[0] + 3.0, 1), round(p[1] - 3.0, 1)], "table": "coin_bag"})
# ratos de cenário
fr = random.Random("bunker2_rats")
floor_cells = [(c, r) for r in range(ROWS) for c in range(COLS) if grid[r][c] != "#"]
rats = []
while len(rats) < 40:
    c, r = fr.choice(floor_cells)
    c2, r2 = c + fr.randint(-3, 3), r + fr.randint(-3, 3)
    if (c2, r2) == (c, r) or not is_open(c2, r2) or any(not is_open(c + round((c2 - c) * t / 6), r + round((r2 - r) * t / 6)) for t in range(7)):
        continue
    a, b = pos(c, r), pos(c2, r2)
    rats.append({"role": "rat", "position": [round(a[0] + fr.uniform(-0.6, 0.6), 2), round(a[1] + fr.uniform(-0.6, 0.6), 2)], "path": b, "speed": round(fr.uniform(1.2, 2.2), 1), "pose": "walk"})

arenas["bunker_01_entrance"] = {
    "_comment": "Bunker, ampliado e feito labirinto (3D Dungeon Modular Wall Set 2, Paul Wortmann, CC0; Lamp, Mev Lyshkin, CC-BY): grade de células de 2 m (Bk_*), salas de 10 m ligadas por vãos de 6 m como o Esgoto, "
                "setores de monstros e salas especiais nas laterais (Depósito, Alojamento, Cofre, Arsenal, Enfermaria). Guarnição (partida) -> labirinto -> túnel do portão (Sentinela, duas chaves) -> Sala de Comando "
                "(General Ferrugem, chefe final, com a saída). Armamentos, ferramentas e suprimentos fazem a decoração. Gerado por tools/assets/build_bunker.py.",
    "name_key": "ARENA_BUNKER", "player_class": "mage", "map_id": "map_bunker", "area_level": 2, "final": True, "victory_groups": ["bk_boss"], "wake_radius": 10.0, "alert_radius": 5.0,
    "rooms": [{"id": "bunker", "center": [0, 0], "size": [COLS * CELL, ROWS * CELL], "doors": [], "wall_height": 0.8, "torch": False}],
    "encounters": encounters, "hazards": [], "entries": {"start": pos(CC, ROWS - 4), "bunker": pos(CC, ROWS - 4)}, "props": props, "quest_spots": [], "breakables": breakables,
    "style": {"_comment": "Bunker: piso de lajotas do kit; paredes, pilares e blocos de rocha do pacote em decor.", "walls": [""], "floor": "Floor_Brick", "low": "", "ground": [0.05, 0.05, 0.06]},
    "decor": decor, "crowd": rats, "passive": True}


# ---------------------------------------------------------------- NPCs e missões
def body(sex, hair, color):
    return {"sex": sex, "hair": [hair], "hair_color": color, "pose": "idle", "outfit": {"body": "cloth"}}


npcs["bk_sergeant"] = {"name_key": "NPC_BK_SERGEANT", "color": [0.45, 0.4, 0.3], "dialogues": [
    {"when": {"quest_new": "bk_clear"}, "lines": ["DLG_BKSGT_1", "DLG_BKSGT_2", "DLG_BKSGT_3"], "offer": "bk_clear"},
    {"when": {"quest_active": "bk_clear"}, "lines": ["DLG_BKSGT_ACTIVE"]}, {"when": {}, "lines": ["DLG_BKSGT_DONE"]}], "body": body("male", "Hair_Buzzed", [0.2, 0.15, 0.1])}
npcs["bk_quartermaster"] = {"name_key": "NPC_BK_QUARTERMASTER", "color": [0.5, 0.4, 0.25], "dialogues": [
    {"when": {"quest_new": "bk_seal"}, "lines": ["DLG_BKQM_1", "DLG_BKQM_2", "DLG_BKQM_3"], "offer": "bk_seal"},
    {"when": {"quest_active": "bk_seal"}, "lines": ["DLG_BKQM_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_BKQM_DONE"]}], "body": body("male", "Hair_Beard", [0.35, 0.28, 0.2])}
npcs["bk_rack"] = {"name_key": "NPC_BK_RACK", "color": [0.5, 0.5, 0.55], "dialogues": [
    {"when": {"quest_active": "bk_seal"}, "lines": ["DLG_BKRACK_1", "DLG_BKRACK_2"]}, {"when": {}, "lines": ["DLG_BKRACK_LOCKED"]}]}
npcs["bk_medic"] = {"name_key": "NPC_BK_MEDIC", "color": [0.75, 0.6, 0.6], "dialogues": [
    {"when": {"quest_new": "bk_medal"}, "lines": ["DLG_BKMED_1", "DLG_BKMED_2", "DLG_BKMED_3"], "offer": "bk_medal"},
    {"when": {"quest_active": "bk_medal"}, "lines": ["DLG_BKMED_ACTIVE"], "service": "turn_in"},
    {"when": {"quest_done": "bk_medal"}, "lines": ["DLG_BKMED_DONE"]}, {"when": {}, "lines": ["DLG_BKMED_WAIT"]}], "body": body("female", "Hair_Buns", [0.4, 0.25, 0.15])}
npcs["bk_cot"] = {"name_key": "NPC_BK_COT", "color": [0.5, 0.45, 0.4], "dialogues": [
    {"when": {"quest_active": "bk_medal"}, "lines": ["DLG_BKCOT_1", "DLG_BKCOT_2"]}, {"when": {}, "lines": ["DLG_BKCOT_LOCKED"]}]}
npcs["bk_gatekeeper"] = {"name_key": "NPC_BK_GATEKEEPER", "color": [0.35, 0.35, 0.4], "dialogues": [
    {"when": {"quest_new": "bk_gate"}, "lines": ["DLG_BKGUARD_1", "DLG_BKGUARD_2", "DLG_BKGUARD_3"], "offer": "bk_gate"},
    {"when": {"quest_active": "bk_gate"}, "lines": ["DLG_BKGUARD_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_BKGUARD_DONE"]}], "body": body("male", "Hair_Beard", [0.12, 0.12, 0.14])}
quests["bk_clear"] = {"name_key": "QUEST_BK_CLEAR", "desc_key": "QUEST_BK_CLEAR_DESC", "type": "village", "giver": "bk_sergeant", "area": "bunker_01_entrance", "clear": clear_ids,
                      "target_element": "earth", "reward": {"gold": 200, "xp": 400}}
quests["bk_seal"] = {"name_key": "QUEST_BK_SEAL", "desc_key": "QUEST_BK_SEAL_DESC", "type": "village", "giver": "bk_quartermaster", "area": "bunker_01_entrance", "target_element": "earth",
                     "reward": {"gold": 220, "xp": 440}, "item": "armory_seal", "gives": "key_brass"}
quests["bk_medal"] = {"name_key": "QUEST_BK_MEDAL", "desc_key": "QUEST_BK_MEDAL_DESC", "type": "village", "giver": "bk_medic", "area": "bunker_01_entrance", "target_element": "water",
                      "reward": {"gold": 220, "xp": 440}, "item": "commander_medal", "gives": "key_steel"}
quests["bk_gate"] = {"name_key": "QUEST_BK_GATE", "desc_key": "QUEST_BK_GATE_DESC", "type": "village", "giver": "bk_gatekeeper", "area": "bunker_01_entrance",
                     "items": ["key_brass", "key_steel"], "opens_gate": "boss_gate", "target_element": "fire", "reward": {"gold": 280, "xp": 560}}
T = {
    "MONSTER_BK_ARMOR": ("Armadura Viva", "Living Armor", "Armadura Viva"),
    "MONSTER_BK_COMMANDER": ("Comandante Podre", "Rotting Commander", "Comandante Podrido"),
    "MONSTER_BK_GENERAL": ("General Ferrugem", "General Rust", "General Óxido"),
    "NPC_BK_SERGEANT": ("Sargento da Guarnição", "Garrison Sergeant", "Sargento de la Guarnición"),
    "NPC_BK_QUARTERMASTER": ("Intendente Vorn", "Quartermaster Vorn", "Intendente Vorn"),
    "NPC_BK_RACK": ("Rack de Armas", "Weapon Rack", "Armero"),
    "NPC_BK_MEDIC": ("Médica de Campo Lena", "Field Medic Lena", "Médica de Campaña Lena"),
    "NPC_BK_COT": ("Catre do Comandante", "Commander's Cot", "Catre del Comandante"),
    "NPC_BK_GATEKEEPER": ("Sentinela do Portão", "Gate Sentinel", "Centinela del Portón"),
    "VALUABLE_ARMORY_SEAL": ("Selo do Arsenal", "Armory Seal", "Sello del Arsenal"),
    "VALUABLE_COMMANDER_MEDAL": ("Medalha do Comandante", "Commander's Medal", "Medalla del Comandante"),
    "VALUABLE_KEY_BRASS": ("Chave de Latão", "Brass Key", "Llave de Latón"),
    "VALUABLE_KEY_STEEL": ("Chave de Aço", "Steel Key", "Llave de Acero"),
    "TOAST_ARMORY_AWAKENS": ("As armas tilintam nos racks: a Armadura Viva se levanta!", "The weapons clatter on their racks: the Living Armor rises!", "Las armas tintinean en los armeros: ¡la Armadura Viva se levanta!"),
    "TOAST_COT_AWAKENS": ("O catre range: o Comandante Podre se levanta!", "The cot creaks: the Rotting Commander rises!", "El catre cruje: ¡el Comandante Podrido se levanta!"),
    "QUEST_BK_CLEAR": ("Limpar a Entrada", "Clear the Entrance", "Limpiar la entrada"),
    "QUEST_BK_CLEAR_DESC": ("O Sargento da Guarnição pede que os dois primeiros bandos que rondam as salas perto da entrada sejam derrubados, antes que o exército de sombras se organize.",
                            "The Garrison Sergeant asks that the first two packs roaming the rooms near the entrance be brought down before the army of shadows organizes.",
                            "El Sargento de la Guarnición pide que se derriben las dos primeras bandas que rondan las salas cerca de la entrada antes de que el ejército de sombras se organice."),
    "QUEST_BK_SEAL": ("O Selo do Arsenal", "The Armory Seal", "El sello del Arsenal"),
    "QUEST_BK_SEAL_DESC": ("O Intendente Vorn, no Depósito de Suprimentos (leste, perto da entrada), perdeu o selo que lacrava o Arsenal: uma armadura de guerra o carrega. Toque o rack de armas do Arsenal (oeste) com a missão ativa, derrote a Armadura Viva e traga o selo: em troca vem a Chave de Latão, uma das duas do portão do General Ferrugem.",
                           "Quartermaster Vorn, in the Supply Depot (east, near the entrance), lost the seal that locked the Armory: a suit of war armor carries it. Touch the weapon rack in the Armory (west) with the quest active, defeat the Living Armor and bring the seal: in return you get the Brass Key, one of the two for General Rust's gate.",
                           "El Intendente Vorn, en el Depósito de Suministros (este, cerca de la entrada), perdió el sello que cerraba el Arsenal: una armadura de guerra lo lleva. Toca el armero del Arsenal (oeste) con la misión activa, derrota a la Armadura Viva y trae el sello: a cambio recibes la Llave de Latón, una de las dos del portón del General Óxido."),
    "QUEST_BK_MEDAL": ("A Medalha de Guerra", "The War Medal", "La medalla de guerra"),
    "QUEST_BK_MEDAL_DESC": ("A Médica de Campo Lena, na Enfermaria (oeste, no alto), quer a medalha de guerra do comandante que morreu no Alojamento (leste). Toque o catre dele com a missão ativa, derrote o Comandante Podre e traga a medalha para receber a Chave de Aço, a outra do portão do General Ferrugem.",
                           "Field Medic Lena, in the Infirmary (west, high up), wants the war medal of the commander who died in the Barracks (east). Touch his cot with the quest active, defeat the Rotting Commander and bring the medal to receive the Steel Key, the other one for General Rust's gate.",
                           "La Médica de Campaña Lena, en la Enfermería (oeste, en lo alto), quiere la medalla de guerra del comandante que murió en el Alojamiento (este). Toca su catre con la misión activa, derrota al Comandante Podrido y trae la medalla para recibir la Llave de Acero, la otra del portón del General Óxido."),
    "QUEST_BK_GATE": ("O Portão da Sala de Comando", "The Command Room Gate", "El portón de la Sala de Mando"),
    "QUEST_BK_GATE_DESC": ("A Sentinela do Portão, no túnel ao norte do labirinto, só abre o portão para quem trouxer as duas chaves: a de Latão (Intendente) e a de Aço (Médica). Atrás dele fica a Sala de Comando do General Ferrugem.",
                           "The Gate Sentinel, in the tunnel north of the maze, only opens the gate for those with both keys: the Brass (Quartermaster) and the Steel (Medic). Beyond lies General Rust's Command Room.",
                           "El Centinela del Portón, en el túnel al norte del laberinto, solo abre el portón a quien traiga las dos llaves: la de Latón (Intendente) y la de Acero (Médica). Tras él está la Sala de Mando del General Óxido."),
    "DLG_BKSGT_1": ("Alto lá, civis. Este bunker foi a última trincheira do exército do rei, e ainda está cheio de armas, ferramentas e comida. Só que também está cheio dos soldados que nunca saíram.",
                    "Halt, civilians. This bunker was the king's army's last trench, and it is still full of weapons, tools and food. It is also full of the soldiers who never left.",
                    "Alto ahí, civiles. Este búnker fue la última trinchera del ejército del rey, y aún está lleno de armas, herramientas y comida. Pero también está lleno de los soldados que nunca salieron."),
    "DLG_BKSGT_2": ("As salas perto da entrada já estão se enchendo de novo. Dois bandos, os mais próximos, antes que o resto acorde.",
                    "The rooms near the entrance are filling up again. Two packs, the closest ones, before the rest wake.",
                    "Las salas cerca de la entrada se están llenando otra vez. Dos bandas, las más cercanas, antes de que despierte el resto."),
    "DLG_BKSGT_3": ("Derrubem os dois e eu pago. Depois, procurem o Intendente Vorn, no depósito a leste: ele e a Médica Lena guardam as chaves do portão do General.",
                    "Bring both down and I will pay. Then look for Quartermaster Vorn, at the depot to the east: he and Medic Lena keep the keys to the General's gate.",
                    "Derriben las dos y pago. Luego busquen al Intendente Vorn, en el depósito al este: él y la Médica Lena guardan las llaves del portón del General."),
    "DLG_BKSGT_ACTIVE": ("As salas ficam logo depois da guarnição, atrás dos vãos largos. Ouçam os passos antes de entrar.", "The rooms lie just past the garrison, behind the wide gaps. Listen for footsteps before entering.", "Las salas quedan justo después de la guarnición, tras los vanos anchos. Escuchen los pasos antes de entrar."),
    "DLG_BKSGT_DONE": ("Bom trabalho. Agora o caminho é seu: o bunker é um labirinto, então sigam as paredes e anotem o que passarem.", "Good work. The way is yours now: the bunker is a maze, so follow the walls and note what you pass.", "Buen trabajo. Ahora el camino es suyo: el búnker es un laberinto, así que sigan las paredes y anoten lo que pasen."),
    "DLG_BKQM_1": ("Vorn, intendente, trinta anos contando cada caixote deste depósito. Falta um selo: o do Arsenal, o selo de lacre que prova que as armas são do rei.",
                   "Vorn, quartermaster, thirty years counting every crate in this depot. One seal is missing: the Armory's, the wax seal that proves the weapons are the king's.",
                   "Vorn, intendente, treinta años contando cada caja de este depósito. Falta un sello: el del Arsenal, el sello de lacre que prueba que las armas son del rey."),
    "DLG_BKQM_2": ("Uma armadura de guerra o levou: está no Arsenal, a oeste, parada entre os racks, e acorda se alguém toca as armas. Foi o último a sair armado.",
                   "A suit of war armor took it: it stands in the Armory, to the west, among the racks, and wakes if anyone touches the weapons. It was the last to leave armed.",
                   "Una armadura de guerra se lo llevó: está en el Arsenal, al oeste, entre los armeros, y despierta si alguien toca las armas. Fue el último en salir armado."),
    "DLG_BKQM_3": ("Toquem o rack, derrubem a Armadura Viva e tragam o selo. Eu dou a Chave de Latão, uma das duas que abrem o portão do General, no túnel ao norte.",
                   "Touch the rack, bring down the Living Armor and bring me the seal. I give the Brass Key, one of the two that open the General's gate, in the tunnel to the north.",
                   "Toquen el armero, derriben a la Armadura Viva y tráiganme el sello. Doy la Llave de Latón, una de las dos que abren el portón del General, en el túnel al norte."),
    "DLG_BKQM_ACTIVE": ("O Arsenal fica a oeste: atravessem o labirinto até a sala dos racks. O selo é de cera vermelha, preso ao peitoral. Tragam-no.",
                        "The Armory is to the west: cross the maze to the room of racks. The seal is red wax, stuck to the breastplate. Bring it.",
                        "El Arsenal está al oeste: crucen el laberinto hasta la sala de los armeros. El sello es de cera roja, pegado al peto. Tráiganlo."),
    "DLG_BKQM_DONE": ("O selo do Arsenal! Agora as contas fecham. A Chave de Latão é de vocês: levem-na à Sentinela, junto com a de Aço.", "The Armory seal! Now the books balance. The Brass Key is yours: take it to the Sentinel, together with the Steel one.", "¡El sello del Arsenal! Ahora las cuentas cuadran. La Llave de Latón es suya: llévenla al Centinela, junto con la de Acero."),
    "DLG_BKRACK_1": ("As armas vibram nos racks, escudos batem uns nos outros, e uma sombra de ferro se mexe entre as lanças.", "The weapons hum on the racks, shields knock against each other, and an iron shadow moves among the spears.", "Las armas vibran en los armeros, los escudos chocan entre sí, y una sombra de hierro se mueve entre las lanzas."),
    "DLG_BKRACK_2": ("A Armadura Viva se levanta!", "The Living Armor rises!", "¡La Armadura Viva se levanta!"),
    "DLG_BKRACK_LOCKED": ("Um rack de armas antigo, com lanças e escudos. Nada responde ao seu toque.", "An old weapon rack with spears and shields. Nothing answers your touch.", "Un viejo armero con lanzas y escudos. Nada responde a tu toque."),
    "DLG_BKMED_1": ("Cuidei de feridos aqui até o último dia. O comandante morreu no Alojamento, a leste, com a medalha de guerra no peito, e nunca me deixou enterrá-lo.",
                    "I tended the wounded here until the last day. The commander died in the Barracks, to the east, with his war medal on his chest, and never let me bury him.",
                    "Cuidé a los heridos aquí hasta el último día. El comandante murió en el Alojamiento, al este, con la medalla de guerra en el pecho, y nunca me dejó enterrarlo."),
    "DLG_BKMED_2": ("Ele não descansa: levanta do catre e vaga pelo alojamento, procurando alguém para dar ordens. Só uma luta o convence a deitar de novo.",
                    "He does not rest: he rises from the cot and wanders the barracks, looking for someone to give orders to. Only a fight convinces him to lie down again.",
                    "No descansa: se levanta del catre y vaga por el alojamiento, buscando a quién dar órdenes. Solo una pelea lo convence de acostarse de nuevo."),
    "DLG_BKMED_3": ("Toquem o catre dele, derrubem o Comandante Podre e tragam a medalha. Eu dou a Chave de Aço, a outra do portão do General Ferrugem.",
                    "Touch his cot, bring down the Rotting Commander and bring the medal. I give the Steel Key, the other for General Rust's gate.",
                    "Toquen su catre, derriben al Comandante Podrido y traigan la medalla. Doy la Llave de Acero, la otra del portón del General Óxido."),
    "DLG_BKMED_ACTIVE": ("O Alojamento fica a leste, com fileiras de catres. A medalha é de bronze, com uma águia. Tragam-na para mim.", "The Barracks lie to the east, with rows of cots. The medal is bronze, with an eagle. Bring it to me.", "El Alojamiento está al este, con filas de catres. La medalla es de bronce, con un águila. Tráiganmela."),
    "DLG_BKMED_DONE": ("A medalha dele! Agora posso enterrá-lo com honra. A Chave de Aço é de vocês: levem-na à Sentinela, junto com a de Latão.", "His medal! Now I can bury him with honor. The Steel Key is yours: take it to the Sentinel, together with the Brass one.", "¡Su medalla! Ahora puedo enterrarlo con honor. La Llave de Acero es suya: llévenla al Centinela, junto con la de Latón."),
    "DLG_BKMED_WAIT": ("As camas estão limpas e as ataduras, secas. Voltem se precisarem de cura.", "The beds are clean and the bandages dry. Come back if you need healing.", "Las camas están limpias y las vendas secas. Vuelvan si necesitan curación."),
    "DLG_BKCOT_1": ("O colchão ainda está quente, e a medalha brilha sobre o travesseiro, onde um peito já não respira.", "The mattress is still warm, and the medal gleams on the pillow where a chest no longer breathes.", "El colchón aún está tibio, y la medalla brilla sobre la almohada, donde un pecho ya no respira."),
    "DLG_BKCOT_2": ("O Comandante Podre se levanta!", "The Rotting Commander rises!", "¡El Comandante Podrido se levanta!"),
    "DLG_BKCOT_LOCKED": ("Um catre militar, vazio e frio. Nada responde ao seu toque.", "A military cot, empty and cold. Nothing answers your touch.", "Un catre militar, vacío y frío. Nada responde a tu toque."),
    "DLG_BKGUARD_1": ("Alto. Este portão fecha a Sala de Comando, e na Sala manda o General Ferrugem, que nunca aceitou a rendição e mandou lacrar o bunker com todos dentro.",
                      "Halt. This gate closes the Command Room, and in the Room General Rust rules, who never accepted surrender and had the bunker sealed with everyone inside.",
                      "Alto. Este portón cierra la Sala de Mando, y en la Sala manda el General Óxido, que nunca aceptó la rendición y mandó sellar el búnker con todos dentro."),
    "DLG_BKGUARD_2": ("O portão só abre com DUAS chaves: a de Latão e a de Aço. A primeira está com o Intendente Vorn, no depósito a leste; a segunda, com a Médica Lena, na enfermaria a oeste.",
                      "The gate only opens with TWO keys: the Brass and the Steel. The first is with Quartermaster Vorn, in the depot to the east; the second, with Medic Lena, in the infirmary to the west.",
                      "El portón solo abre con DOS llaves: la de Latón y la de Acero. La primera la tiene el Intendente Vorn, en el depósito al este; la segunda, la Médica Lena, en la enfermería al oeste."),
    "DLG_BKGUARD_3": ("Cada um cobra um preço: um selo, uma medalha. Tragam as duas chaves a mim e eu abro a passagem.", "Each charges a price: a seal, a medal. Bring both keys to me and I will open the way.", "Cada uno cobra un precio: un sello, una medalla. Tráiganme las dos llaves y abro el paso."),
    "DLG_BKGUARD_ACTIVE": ("Só abro com as duas chaves, Latão e Aço, na mesma bolsa. O Intendente fica a leste; a Médica, a oeste.", "I only open with both keys, Brass and Steel, in the same bag. The Quartermaster is to the east; the Medic, to the west.", "Solo abro con las dos llaves, Latón y Acero, en la misma bolsa. El Intendente está al este; la Médica, al oeste."),
    "DLG_BKGUARD_DONE": ("As duas chaves! O portão está aberto. Cuidado: o General Ferrugem não aceita visitas, e a ferrugem dele corrói até o aço.", "Both keys! The gate is open. Beware: General Rust accepts no visitors, and his rust eats even steel.", "¡Las dos llaves! El portón está abierto. Cuidado: el General Óxido no acepta visitas, y su óxido corroe hasta el acero."),
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

try:
    from PIL import Image
    ICONS = "assets/ui/icons/"
    for dst, src, mul in (("key_brass", "key_hearts", (1.4, 1.2, 0.5)), ("key_steel", "key_spades", (0.8, 0.9, 1.2)), ("armory_seal", "royal_seal_ring", (1.4, 0.6, 0.5)),
                          ("commander_medal", "crown_jewel", (1.4, 1.1, 0.5))):
        im = Image.open(ICONS + src + ".png").convert("RGBA")
        r_, g_, b_, a_ = im.split()
        Image.merge("RGBA", (r_.point(lambda v: min(255, int(v * mul[0]))), g_.point(lambda v: min(255, int(v * mul[1]))), b_.point(lambda v: min(255, int(v * mul[2]))), a_)).save(ICONS + dst + ".png")
except Exception as exc:
    print("aviso: ícones não gerados:", exc)

for path, data in ((ARENAS, arenas), (MONSTERS, monsters), (NPCS, npcs), (QUESTS, quests), (VALUABLES, valuables)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
print("OK bunker: grade %dx%d, %d células de piso (%d m2 de piso), %d m2 da sala, %d peças, %d encontros, caminho principal %d salas" % (COLS, ROWS, FLOOR_CELLS, FLOOR_CELLS * 4, COLS * ROWS * 4, len(decor), len(encounters), len(main_path)))
