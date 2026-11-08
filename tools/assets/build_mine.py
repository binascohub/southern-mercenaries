"""Mapa da Mina (mine_01_crystal_vein), ampliado e feito LABIRINTO como o Esgoto (grade de salas de 12 m ligadas por portas, em setores de monstros), com outro caminho:
os TRILHOS do trem são o caminho. Uma linha principal sai da entrada (sul), serpenteia pelo labirinto até o túnel do portão e o Coração da Mina (norte); ramais levam ao Acampamento dos
Anões (leste, perto da partida), à Gruta das Carroças (oeste), ao Salão dos Cristais (leste), à Casa do Joalheiro (oeste, no alto) e à Câmara Secreta; becos sem saída têm trilhos que
acabam numa carroça virada, baús, ouro e pedras preciosas. Estrutura da Floresta: NPCs com missão, dois mini-chefes invocados, guardião do portão (duas chaves) e chefe final.
  Capataz Brokk (acampamento) pede a Presa do Troll: tocar a carroça abandonada da Gruta (missão ativa) desperta o Chefe Troll; entrega a Chave da Picareta.
  Joalheiro Dolgrim (casa) pede o Núcleo de Quartzo: o Cristal Pulsante do Salão dos Cristais desperta a Besta de Quartzo; entrega a Chave da Lanterna.
  O Guarda-Chaves só abre o portão com as duas chaves; atrás dele, o Coração da Mina, onde o Golem de Cristal espera. O Guardião do Túmulo (relíquia do Padre) anda solto no labirinto.
Anões mineiros (o corpo do Arqueiro masculino, "class": "archer", com pá na mão) são NPCs e gente de cenário pelos trilhos. Cristais, ouro e pedras preciosas, pedras de todos os tipos fazem as paredes.
Sorteio com semente fixa; idempotente; chamado no fim de tools/assets/build_maps.py (antes de set_map_order.py).
uso: python3 tools/assets/build_mine.py   (a partir da raiz do projeto)"""
import json, math, random, re
from collections import deque
ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES = ("data/arenas.json", "data/monsters.json", "data/npcs.json", "data/quests.json", "data/valuables.json")
arenas, monsters, npcs, quests, valuables = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES))
rng = random.Random("mine-v2")
NC, NR, RS, DOOR = 13, 15, 12.0, 6.0  # dobro da área (antes 9 x 11)
START, END = (NC // 2, 0), (NC // 2, NR - 1)


def cx(c): return (c - NC // 2) * RS
def cz(r): return -RS - RS * r


# ---------------------------------------------------------------- labirinto: árvore crescente (muitos becos) + alguns laços
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
assert len(seen) == NC * NR


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

# ---------------------------------------------------------------- salas
SPECIAL = {  # id: (cx, cz, w, h, célula da borda, lado da célula)
    "camp": (cx(NC - 1) + RS / 2 + 9, cz(2), 18, 16, (NC - 1, 2), "east"),
    "troll_cave": (cx(0) - RS / 2 - 12, cz(7), 24, 20, (0, 7), "west"),
    "crystal_hall": (cx(NC - 1) + RS / 2 + 12, cz(10), 24, 20, (NC - 1, 10), "east"),
    "gem_house": (cx(0) - RS / 2 - 8, cz(12), 16, 14, (0, 12), "west"),
    "secret": (cx(NC - 1) + RS / 2 + 7, cz(12), 14, 14, (NC - 1, 12), "east")}
TOP = cz(NR - 1) - RS / 2
ROOMS = [("entry", 0, 0, 20, 12)] + [("m_%d_%d" % (c, r), cx(c), cz(r), RS, RS) for r in range(NR) for c in range(NC)] + \
        [(k, v[0], v[1], v[2], v[3]) for k, v in SPECIAL.items()] + [("tunnel", 0, TOP - 7, 8, 14), ("nest", 0, TOP - 14 - 17, 40, 34)]
by_id = {r[0]: r for r in ROOMS}
LINKS = [("entry", "m_%d_0" % START[0], "north")]
for p in passages:
    a, b = sorted(p)
    if a[0] == b[0]:                       # mesma coluna: o de linha maior fica ao norte
        s, n = (a, b) if a[1] < b[1] else (b, a)
        LINKS.append(("m_%d_%d" % s, "m_%d_%d" % n, "north"))
    else:
        w, e = (a, b) if a[0] < b[0] else (b, a)
        LINKS.append(("m_%d_%d" % w, "m_%d_%d" % e, "east"))
for k, v in SPECIAL.items():
    c = v[4]
    LINKS.append(("m_%d_%d" % c, k, v[5]))
LINKS += [("m_%d_%d" % END, "tunnel", "north"), ("tunnel", "nest", "north")]
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}
doors = {r[0]: [] for r in ROOMS}
door_points = []
door_of = {}
for a, b, side in LINKS:
    _, ax, az, aw, ah = by_id[a]
    _, bx, bz, bw, bh = by_id[b]
    if side in ("north", "south"):
        lo, hi = max(ax - aw / 2, bx - bw / 2), min(ax + aw / 2, bx + bw / 2)
        edge = az - ah / 2 if side == "north" else az + ah / 2
        assert abs(edge - (bz + bh / 2 if side == "north" else bz - bh / 2)) < 1e-6, (a, b)
        mid = round((lo + hi) / 2 * 2) / 2
        offs = (mid - ax, mid - bx)
        pt = (mid, edge)
    else:
        lo, hi = max(az - ah / 2, bz - bh / 2), min(az + ah / 2, bz + bh / 2)
        edge = ax - aw / 2 if side == "west" else ax + aw / 2
        assert abs(edge - (bx + bw / 2 if side == "west" else bx - bw / 2)) < 1e-6, (a, b)
        mid = round((lo + hi) / 2 * 2) / 2
        offs = (mid - az, mid - bz)
        pt = (edge, mid)
    assert hi - lo >= DOOR + 2 - 1e-6, (a, b, hi - lo)
    door_points.append(pt)
    door_of[(a, b)] = (side, pt)
    for rid, s, off in ((a, side, offs[0]), (b, OPP[side], offs[1])):
        doors[rid].append(s if abs(off) < 1e-6 else "%s:%g" % (s, off))
rooms = []
for rid, x, z, w, h in ROOMS:
    r = {"id": rid, "center": [x, z], "size": [w, h], "doors": doors[rid], "wall_height": 2.0, "narrow": True}
    if rid in ("entry", "camp", "gem_house", "nest"):
        r["torch"] = True
    rooms.append(r)
for i, (_, ax, az, aw, ah) in enumerate(ROOMS):
    for _, bx, bz, bw, bh in ROOMS[i + 1:]:
        assert abs(ax - bx) >= (aw + bw) / 2 - 1e-6 or abs(az - bz) >= (ah + bh) / 2 - 1e-6, ("salas sobrepostas", _)
AREA_M2 = sum(r[3] * r[4] for r in ROOMS)


def room_at(x, z, pad=0.0):
    for r in rooms:
        if abs(x - r["center"][0]) < r["size"][0] / 2 + pad and abs(z - r["center"][1]) < r["size"][1] / 2 + pad:
            return r
    return None


def cell_center(c): return (cx(c[0]), cz(c[1]))
def sp(rid): return (by_id[rid][1], by_id[rid][2])


# ---------------------------------------------------------------- monstros novos e itens
def clone(name, base, **changes):
    m = json.loads(json.dumps(monsters[base]))
    m.pop("_comment", None)
    m.pop("quest_drop", None)
    m.update(changes)
    monsters[name] = m


monsters["troll_chief"].update({"quest_drop": "troll_tusk"})
clone("mn_quartz_beast", "troll_chief", _comment="Mini-chefe da Mina (Salão dos Cristais): a Besta de Quartzo, fera de cristal que o Cristal Pulsante desperta; investidas.",
      name_key="MONSTER_MN_QUARTZ_BEAST", max_health=360, damage=28, size=2.6, element="earth", look="chitin_beast", color=[0.5, 0.75, 1.0], quest_drop="quartz_core")
valuables.update({
    "troll_tusk": {"name_key": "VALUABLE_TROLL_TUSK", "value": 0, "maps": [], "quest_item": True, "model": "Bone_Sickle"},
    "quartz_core": {"name_key": "VALUABLE_QUARTZ_CORE", "value": 0, "maps": [], "quest_item": True, "model": "Crystal_Gem"},
    "key_pickaxe": {"name_key": "VALUABLE_KEY_PICKAXE", "value": 0, "maps": [], "quest_item": True, "model": "Key_Spades"},
    "key_lantern": {"name_key": "VALUABLE_KEY_LANTERN", "value": 0, "maps": [], "quest_item": True, "model": "Key_Clubs"}})

# ---------------------------------------------------------------- setores e encontros
def sector(c, r):
    if r < 4:
        return 1
    if r < 8:
        return 2 if c <= NC // 2 else 3
    if r < 12:
        return 5 if c <= NC // 2 else 4
    return 6


SETS = {1: [[("goblin", 3), ("plague_bat", 3)], [("goblin", 4)], [("stalker", 2), ("plague_bat", 2)]],
        2: [[("venom_scorpion", 3)], [("skeleton", 3)], [("skeleton", 2), ("goblin", 2)]],
        3: [[("mutant", 1)], [("goblin", 3), ("stalker", 1)], [("venom_scorpion", 3)]],
        4: [[("golem_stone", 1), ("goblin", 2)], [("troll_mauler", 1)], [("golem_ice", 1)]],
        5: [[("golem_fire", 1)], [("troll_mauler", 1), ("goblin", 2)], [("skeleton", 4)]],
        6: [[("golem_stone", 1), ("stalker", 2)], [("golem_fire", 1), ("golem_ice", 1)], [("troll_mauler", 2)]]}
E = lambda eid, pos, *mons: {"id": eid, "position": [round(pos[0], 1), round(pos[1], 1)], "monsters": [{"monster": m, "count": n} for m, n in mons]}
encounters, counters = [], {}
tomb_cell = rng.choice([c for c in seen if sector(*c) == 4 and c not in main_path[:4]])
for c in sorted(seen, key=lambda c: (c[1], c[0])):
    if c == START and False:
        continue
    if c[1] == 0 and c[0] in (3, 4, 5):
        continue                                           # as três salas logo na entrada ficam tranquilas
    x, z = cell_center(c)
    s = sector(*c)
    if c == tomb_cell:
        encounters.append(E("mn_tomb", (x + 3.5, z + 3.5), ("tomb_guardian", 1)))
        continue
    if rng.random() > (0.5 if c in main_path else 0.62):
        continue
    counters[s] = counters.get(s, 0) + 1
    encounters.append(E("mn_s%d_%d" % (s, counters[s]), (x + rng.choice((-3.5, 3.5)), z + rng.choice((-3.5, 3.5))), *rng.choice(SETS[s])))
for c in leaves:
    if rng.random() < 0.14:
        x, z = cell_center(c)
        encounters.append(E("mn_mimic_%d_%d" % c, (x - 3.5, z + 3.5), ("chest_mimic", 1)))
clear_ids = [e["id"] for e in encounters if e["id"].startswith("mn_s1_")][:2]
SUMMON_TROLL = {"id": "mn_troll", "position": [sp("troll_cave")[0], sp("troll_cave")[1] + 6], "spread": 3.0, "toast": "TOAST_ORE_CART_AWAKENS", "monsters": [{"monster": "troll_chief", "count": 1, "rank": "miniboss"}]}
SUMMON_QUARTZ = {"id": "mn_quartz", "position": [sp("crystal_hall")[0] - 2, sp("crystal_hall")[1] + 6], "spread": 3.0, "toast": "TOAST_CRYSTAL_AWAKENS",
                 "monsters": [{"monster": "mn_quartz_beast", "count": 1, "rank": "miniboss"}]}
encounters.append(E("mn_boss", (0, TOP - 14 - 20), ("crystal_golem", 1)))
for rid in ("secret",):
    x, z = sp(rid)
    encounters.append(E("mn_secret", (x, z + 2), ("troll_mauler", 1)))
    encounters.append(E("mn_mimic_secret", (x - 3, z - 3), ("chest_mimic", 1)))

props = [
    {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_FARM", "position": [-6, 3], "to": "farm_01_fields", "entry": "mine", "expedition_end": True},
    {"id": "victory_portal", "kind": "exit", "name_key": "PROP_RETURN_FARM", "position": [0, TOP - 14 - 31], "to": "farm_01_fields", "entry": "mine", "after_victory": True, "group": True},
    {"id": "mn_apprentice", "kind": "npc", "npc": "mn_apprentice", "position": [0, -12], "rotation": 180},
    {"id": "mn_foreman", "kind": "npc", "npc": "mn_foreman", "position": [sp("camp")[0] - 3, sp("camp")[1] + 2], "rotation": 180},
    {"id": "mn_ore_cart", "kind": "npc", "npc": "mn_ore_cart", "kit": "Cart_Wood", "rotation": 90, "position": list(sp("troll_cave")), "solid": [2.4, 1.3], "summon": SUMMON_TROLL, "needs_quest": "mn_tusk"},
    {"id": "mn_jeweler", "kind": "npc", "npc": "mn_jeweler", "position": [sp("gem_house")[0] + 2, sp("gem_house")[1] + 1], "rotation": 180},
    {"id": "mn_crystal", "kind": "npc", "npc": "mn_crystal", "kit": "Crystal_P_20", "rotation": 0, "position": list(sp("crystal_hall")), "solid": [1.4, 1.4], "summon": SUMMON_QUARTZ, "needs_quest": "mn_quartz"},
    {"id": "boss_gate", "kind": "gate", "name_key": "PROP_BOSS_GATE", "position": [0.0, TOP - 7], "rotation": 0, "scale": 2.0, "block": 8.0, "count": 2, "opened_by": "mn_gate"},
    {"id": "mn_gatekeeper", "kind": "npc", "npc": "mn_gatekeeper", "position": [0.0, TOP - 3], "rotation": 0}]
chest_cells = rng.sample([c for c in leaves if c not in [(x[0], x[1]) for x in []]], min(len(leaves), 12))
for i, c in enumerate(chest_cells, start=1):
    x, z = cell_center(c)
    props.append({"id": "mn_chest_%d" % i, "kind": "chest", "position": [round(x + 3.5, 1), round(z - 3.5, 1)], "loot": "chest"})
for i, (rid, dx, dz) in enumerate((("camp", 5, -4), ("gem_house", -4, -3), ("secret", 0, -4), ("crystal_hall", -9, 8), ("troll_cave", -8, -7)), start=1):
    props.append({"id": "mn_potions_%d" % i, "kind": "chest", "position": [round(sp(rid)[0] + dx, 1), round(sp(rid)[1] + dz, 1)], "loot": "potion_chest", "model": "Chest_Mini"})
interest_things = [p["position"] for p in props] + [e["position"] for e in encounters]
interest = [p["position"] for p in props] + [e["position"] for e in encounters] + [SUMMON_TROLL["position"], SUMMON_QUARTZ["position"], [0, 3]] + [list(d) for d in door_points]

# ---------------------------------------------------------------- trilhos: linha principal e ramais (os trilhos são o caminho)
rail_edges = {}                       # chave -> (x0, z0, x1, z1)
rail_cells = set()


def add_leg(key, a, b):
    if key not in rail_edges:
        rail_edges[key] = (a[0], a[1], b[0], b[1])


pts = [(0.0, 0.0)] + [cell_center(c) for c in main_path]
for i in range(len(pts) - 1):
    add_leg(("main", i), pts[i], pts[i + 1])
add_leg(("main", "end"), pts[-1], (0.0, TOP - 4))
rail_cells.update(main_path)
for k, v in SPECIAL.items():
    border = v[4]
    path = bfs_path(border, set(main_path) | rail_cells)
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        add_leg(("cell", frozenset((a, b))), cell_center(a), cell_center(b))
    add_leg(("special", k), cell_center(border), (v[0], v[1]))
    rail_cells.update(path)
# ramais de enfeite: becos sem saída com trilhos que terminam numa carroça virada
decoys = [c for c in leaves if c in leaves and rng.random() < 0.35 and c not in rail_cells][:8]
for c in decoys:
    path = bfs_path(c, rail_cells)
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        add_leg(("cell", frozenset((a, b))), cell_center(a), cell_center(b))
    rail_cells.update(path)
rail_segments = list(rail_edges.values())


def rail_dist(x, z):
    d = 1e9
    for x0, z0, x1, z1 in rail_segments:
        px, pz = min(max(x, min(x0, x1)), max(x0, x1)), min(max(z, min(z0, z1)), max(z0, z1))
        d = min(d, math.hypot(x - px, z - pz))
    return d


decor, crowd, taken = [], [], []


def near_interest(x, z, rad):
    return any(math.hypot(x - ix, z - iz) < rad for ix, iz in interest)


def near_taken(x, z, rad):
    return any(math.hypot(x - tx, z - tz) < tr + rad for tx, tz, tr in taken)


for x0, z0, x1, z1 in rail_segments:
    horiz = abs(z1 - z0) < 1e-6
    length = abs(x1 - x0) if horiz else abs(z1 - z0)
    n = max(round(length / 6.0), 1)
    for i in range(n):
        t = (i + 0.5) / n
        decor.append({"piece": "Rail_Straight", "position": [round(x0 + (x1 - x0) * t, 2), round(z0 + (z1 - z0) * t, 2)], "rotation": 90 if horiz else 0,
                      "scale": round(length / n / 6.0, 3), "y": 0.02})

# ---------------------------------------------------------------- decoração
ROCKS = ["Rock_1", "Rock_2", "Rock_3", "Rock_4", "Rock_5", "RockP_1", "RockP_2", "RockP_3", "RockP_4", "RockP_5", "RockP_6"]
BLUE, PURPLE = (0.3, 0.6, 1.0), (0.7, 0.4, 1.0)
GOLD = ["Gold_Pile_1", "Gold_Pile_2", "Gold_Pile_3", "Gold_Pile_4", "Gold_Pile_5", "Coin_Pile"]
GEAR = ["Barrel_Oga_1", "Barrel_Oga_2", "Crate_Big", "Crate_Small", "Bucket_Crate", "Whetstone", "Tool_Shovel", "Beer_Barrel", "Tv_Sack", "Pr_Basket"]
WEBS = ["Web_Round_Up", "Web_Square_Up", "Web_Round_Flat", "Web_Square_Flat"]
BONES = ["Dungeon_BonePile_%d" % i for i in range(1, 7)] + ["Dungeon_Skull_1", "Dungeon_Skull_2", "Dungeon_CrossBones"]


def wall_line(x0, z0, x1, z1, gap=None, tall=True):
    """Fileira de pedras (as paredes do labirinto) ao longo de uma divisa; `gap` = ponto médio da porta (vão de ~6,4 m)."""
    horiz = abs(z1 - z0) < 1e-6
    a, b = (x0, x1) if horiz else (z0, z1)
    lo, hi = min(a, b), max(a, b)
    n = max(int((hi - lo) / 2.0), 1)
    for i in range(n):
        t = lo + (hi - lo) * (i + 0.5) / n + rng.uniform(-0.25, 0.25)
        if gap is not None and abs(t - gap) < 3.2:
            continue
        x, z = (t, z0) if horiz else (x0, t)
        sc = rng.uniform(2.0, 3.2) if tall else rng.uniform(1.5, 2.4)
        decor.append({"piece": rng.choice(ROCKS), "position": [round(x, 2), round(z + (rng.uniform(-0.3, 0.3) if horiz else 0), 2)] if horiz else [round(x + rng.uniform(-0.3, 0.3), 2), round(z, 2)],
                      "rotation": rng.randrange(0, 360, 15), "scale": round(sc, 2)})


def link_gap(a, b):
    key = (a, b) if (a, b) in door_of else (b, a) if (b, a) in door_of else None
    return door_of[key][1] if key else None


# paredes das divisas da grade
for c in range(NC):
    for r in range(-1, NR):                                 # linha horizontal entre a linha r (sul) e r+1 (norte)
        z = cz(r) - RS / 2 if r >= 0 else -6.0
        gap = None
        if r == -1:
            gap = cx(c) if c == START[0] else None
        elif r == NR - 1:
            gap = cx(c) if c == END[0] else None
        elif frozenset(((c, r), (c, r + 1))) in passages:
            gap = cx(c)
        wall_line(cx(c) - RS / 2, z, cx(c) + RS / 2, z, gap, tall=False)
for r in range(NR):
    for c in range(-1, NC):                                 # linha vertical entre a coluna c (oeste) e c+1 (leste)
        x = cx(c) + RS / 2 if c >= 0 else cx(0) - RS / 2
        if c == -1:
            gap = cz(r) if any(v[4] == (0, r) and v[5] == "west" for v in SPECIAL.values()) else None
        elif c == NC - 1:
            gap = cz(r) if any(v[4] == (NC - 1, r) and v[5] == "east" for v in SPECIAL.values()) else None
            x = cx(NC - 1) + RS / 2
        else:
            gap = cz(r) if frozenset(((c, r), (c + 1, r))) in passages else None
        wall_line(x, cz(r) - RS / 2, x, cz(r) + RS / 2, gap, tall=True)
# paredes da entrada e das salas especiais
wall_line(-10, -6, -10, 6, None, True)
wall_line(10, -6, 10, 6, None, True)
wall_line(-10, 6, 10, 6, None, False)
for k, v in SPECIAL.items():
    x, z, w, h = v[:4]
    side = v[5]
    gz = door_of[("m_%d_%d" % v[4], k)][1][1]
    wall_line(x - w / 2, z - h / 2, x + w / 2, z - h / 2, None, False)
    wall_line(x - w / 2, z + h / 2, x + w / 2, z + h / 2, None, False)
    if side == "east":
        wall_line(x + w / 2, z - h / 2, x + w / 2, z + h / 2, None, True)
        wall_line(x - w / 2, z - h / 2, x - w / 2, z + h / 2, gz, True)
    else:
        wall_line(x - w / 2, z - h / 2, x - w / 2, z + h / 2, None, True)
        wall_line(x + w / 2, z - h / 2, x + w / 2, z + h / 2, gz, True)
wall_line(-4, TOP, -4, TOP - 14, None, True)
wall_line(4, TOP, 4, TOP - 14, None, True)
for x0 in (-20, 20):
    wall_line(x0, TOP - 14, x0, TOP - 48, None, True)
wall_line(-20, TOP - 48, 20, TOP - 48, None, False)
wall_line(-20, TOP - 14, 20, TOP - 14, 0.0, False)


def put(piece, x, z, rot=None, scale=1.0, solid=None, y=None, r=0.8, free=2.0, force=False, wall=1.2, rails=1.6):
    if room_at(x, z, -wall) is None:
        return False
    if not force and (near_interest(x, z, free) or near_taken(x, z, r) or rail_dist(x, z) < rails):
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


def scatter_in(cxx, czz, w, h, pieces, n, scale=(1.0, 1.0), solid=None, r=0.9, tries=40, margin=1.8, **kw):
    done = 0
    for _ in range(n):
        for _t in range(tries):
            x, z = cxx + rng.uniform(-w / 2 + margin, w / 2 - margin), czz + rng.uniform(-h / 2 + margin, h / 2 - margin)
            s = rng.uniform(*scale)
            if put(rng.choice(pieces) if isinstance(pieces, list) else pieces, x, z, scale=s, solid=[solid[0] * s, solid[1] * s] if solid else None, r=r * s, **kw):
                done += 1
                break
    return done


lights = 0


def light(x, z, color, rng_=9.0, energy=1.5, y=1.2):
    global lights
    decor.append({"light": list(color), "position": [round(x, 1), round(z, 1)], "y": y, "range": rng_, "energy": energy})
    lights += 1


def crystal_cluster(x, z, n, spread, big=(1.0, 2.2), lit=True, tag=None):
    tag, color = (tag, BLUE if tag == "B" else PURPLE) if tag else (("B", BLUE) if rng.random() < 0.6 else ("P", PURPLE))
    for _ in range(n):
        ang, dist = rng.uniform(0, math.tau), rng.uniform(0, spread)
        px, pz = x + math.cos(ang) * dist, z + math.sin(ang) * dist
        s = rng.uniform(*big)
        put("Crystal_%s_%d" % (tag, rng.randint(1, 28)), px, pz, scale=s, solid=[s * 0.5, s * 0.5] if s > 1.6 else None, r=0.5 * s, free=1.0, rails=1.0)
    if lit:
        light(x, z, color, 9.0, 1.5)


# cristais, ouro, pedras preciosas e equipamentos nas salas do labirinto
for r in range(NR):
    for c in range(NC):
        x, z = cell_center((c, r))
        is_leaf = (c, r) in leaves
        if rng.random() < 0.42 and lights < 38:
            crystal_cluster(x + rng.uniform(-3.5, 3.5), z + rng.uniform(-3.5, 3.5), rng.randint(3, 6), 1.8)
        elif rng.random() < 0.55:
            crystal_cluster(x + rng.uniform(-3.5, 3.5), z + rng.uniform(-3.5, 3.5), rng.randint(2, 4), 1.4, lit=False)
        scatter_in(x, z, RS, RS, ROCKS, rng.randint(2, 4), scale=(0.35, 0.9), r=0.7)
        scatter_in(x, z, RS, RS, ["Crystal_Gem"], rng.randint(1, 3), scale=(3.0, 5.0), r=0.5, free=1.0)
        if is_leaf:                                          # becos: tesouro, ossos e teias
            scatter_in(x, z, RS, RS, GOLD, 3, scale=(1.0, 1.6), r=0.9)
            scatter_in(x, z, RS, RS, BONES, 2, scale=(2.0, 3.0), r=0.7)
            scatter_in(x, z, RS, RS, WEBS, 2, scale=(1.8, 2.8), r=1.0)
        elif rng.random() < 0.4:
            scatter_in(x, z, RS, RS, GEAR, rng.randint(1, 3), scale=(0.9, 1.2), r=0.9)
        if rng.random() < 0.15:
            scatter_in(x, z, RS, RS, WEBS, 1, scale=(1.8, 2.8), r=1.0)
# lampiões ao longo da linha principal, a cada três salas, e carroças ao lado dos trilhos
for i, c in enumerate(main_path):
    if i % 3 == 1:
        x, z = cell_center(c)
        if put("Pr_LampPost", x + 2.6, z + 2.6, rot=0, solid=[0.6, 0.6], r=0.8, free=1.0, rails=1.0):
            light(x + 2.6, z + 2.6, (1.0, 0.7, 0.35), 8.0, 1.2, 2.2)
    if i % 4 == 2:
        x, z = cell_center(c)
        put("Cart_Wood", x - 2.8, z - 2.2, rot=rng.choice((0, 90, 180)), solid=[2.0, 1.2], r=1.6, free=1.0, y=0.05, rails=1.2)
for c in decoys:                                              # carroça virada onde o trilho acaba
    x, z = cell_center(c)
    put("Cart_Wood", x, z, rot=rng.randrange(0, 360, 15), solid=[2.0, 1.2], r=1.8, free=1.0, y=0.05, rails=0.0, force=True)
    put("Crystal_Gem", x + 1.8, z, scale=4.0, r=0.3, free=0.5, rails=0.0, force=True)
# ---- Entrada
decor += [{"piece": "Pr_LampPost", "position": [-3, 3], "solid": [0.6, 0.6]}, {"piece": "Whetstone", "position": [-4, 4], "scale": 2.0}, {"piece": "Cart_Wood", "position": [0, -3], "rotation": 0, "y": 0.05, "solid": [1.2, 2.0]}]
light(-3, 3, (1.0, 0.7, 0.35), 8.0, 1.2, 2.2)
scatter_in(0, 0, 20, 12, GEAR, 6, scale=(0.9, 1.2), r=0.9)
# ---- Acampamento dos Anões: fogueira, barracas de barris, carroças, ouro
x, z = sp("camp")
put("Bonfire_Cauldron", x, z, rot=0, solid=[1.2, 2.2], r=1.6, free=0.5, rails=0.0, force=True)   # fogueira com caldeirão (tools/assets/build_bonfire.py)
decor.append({"piece": "Fire_Flame", "position": [x, z], "y": 0.1, "scale": 0.9, "flicker": True})
light(x, z, (1.0, 0.6, 0.25), 12.0, 1.8, 1.2)
scatter_in(x, z, 18, 16, GEAR, 12, scale=(1.0, 1.3), r=1.0)
scatter_in(x, z, 18, 16, GOLD, 4, scale=(1.0, 1.5), r=0.9)
scatter_in(x, z, 18, 16, ["Cart_Wood"], 2, solid=(2.0, 1.2), r=1.6, y=0.05)
crystal_cluster(x + 6, z + 5, 5, 1.6, tag="B")
# ---- Gruta das Carroças (mini-chefe 1): carroças quebradas, ossos, pedras e cristais
x, z = sp("troll_cave")
scatter_in(x, z, 24, 20, ["Cart_Wood"], 5, solid=(2.0, 1.2), r=1.8, y=0.05)
scatter_in(x, z, 24, 20, BONES, 14, scale=(2.2, 3.4), r=0.8)
scatter_in(x, z, 24, 20, ROCKS, 10, scale=(0.8, 1.6), solid=(0.7, 0.7), r=1.0)
scatter_in(x, z, 24, 20, GEAR, 8, scale=(1.0, 1.3), r=1.0)
crystal_cluster(x - 8, z - 6, 6, 2.0, tag="P")
crystal_cluster(x + 8, z - 6, 6, 2.0, tag="P")
# ---- Salão dos Cristais (mini-chefe 2): cristais gigantes e luz azul
x, z = sp("crystal_hall")
for dx, dz in ((-9, -7), (9, -7), (-9, 6), (9, 6), (0, -9)):
    s = rng.uniform(3.0, 3.8)
    put("Crystal_B_%d" % rng.choice((3, 4, 12, 16, 21)), x + dx, z + dz, scale=s, solid=[s * 0.6, s * 0.6], r=2.0, free=1.0, rails=0.0, force=True)
    light(x + dx, z + dz, BLUE, 9.0, 1.6, 1.5)
light(x, z, PURPLE, 14.0, 2.4, 2.0)
scatter_in(x, z, 24, 20, ["Crystal_Gem"], 12, scale=(3.5, 5.5), r=0.6, free=1.2)
scatter_in(x, z, 24, 20, ROCKS, 8, scale=(0.5, 1.2), r=0.8)
scatter_in(x, z, 24, 20, GOLD, 4, scale=(1.0, 1.5), r=0.9)
# ---- Casa do Joalheiro: bancada, ouro, pedras preciosas
x, z = sp("gem_house")
scatter_in(x, z, 16, 14, ["Crystal_Gem"], 14, scale=(3.5, 5.5), r=0.6, free=1.0)
scatter_in(x, z, 16, 14, GOLD + ["Gold_Bed"], 8, scale=(1.0, 1.5), r=0.9)
scatter_in(x, z, 16, 14, ["Workbench", "Anvil", "Barrel_Oga_1", "Crate_Small", "Tv_Sack", "Weapon_Rack"], 8, scale=(1.0, 1.3), solid=(1.0, 1.0), r=1.0)
light(x, z, (1.0, 0.75, 0.4), 10.0, 1.6, 1.8)
crystal_cluster(x - 5, z - 4, 4, 1.4, tag="B")
# ---- Câmara Secreta: tesouro
x, z = sp("secret")
scatter_in(x, z, 14, 14, GOLD + ["Gold_Bed"], 10, scale=(1.3, 1.9), r=1.0)
scatter_in(x, z, 14, 14, ["Crystal_Gem"], 12, scale=(4.0, 6.0), r=0.6, free=1.0)
crystal_cluster(x, z - 4, 5, 1.6, tag="P")
# ---- Túnel e Coração da Mina: cristais gigantes e a luz roxa
for z in (TOP - 3, TOP - 11):
    light(-2.5, z, (1.0, 0.7, 0.35), 6.5, 1.0, 1.8)
nx, nz = 0, TOP - 14 - 17
for dx, dz in ((-14, -12), (14, -12), (-15, 4), (15, 4), (-8, 12), (8, 12), (0, -14)):
    s = rng.uniform(3.0, 4.2)
    put("Crystal_%s_%d" % (rng.choice("BP"), rng.choice((3, 4, 12, 16, 21))), nx + dx, nz + dz, scale=s, solid=[s * 0.6, s * 0.6], r=2.2, free=1.0, rails=0.0, force=True)
light(nx, nz, PURPLE, 22.0, 3.0, 2.2)
for dx, dz in ((-12, 6), (12, 6), (-12, -8), (12, -8)):
    light(nx + dx, nz + dz, BLUE, 12.0, 2.0, 1.5)
scatter_in(nx, nz, 40, 34, ["Crystal_Gem"], 16, scale=(4.0, 6.0), r=0.6, free=1.2)
scatter_in(nx, nz, 40, 34, GOLD, 8, scale=(1.3, 1.9), r=1.0)
scatter_in(nx, nz, 40, 34, ROCKS, 10, scale=(0.6, 1.4), r=0.8)
scatter_in(nx, nz, 40, 34, BONES, 6, scale=(2.2, 3.2), r=0.7)

# ---- anões mineiros de cenário (o corpo do Arqueiro masculino, com pá): acampamento, casa do joalheiro, Salão dos Cristais e passeando pelos trilhos
def dwarf(x, z, pose="idle", rot=None, weapon=False, path=None, speed=0.8):
    d = {"role": "dwarf_miner", "position": [round(x, 1), round(z, 1)], "rotation": rot if rot is not None else rng.randrange(0, 360, 15), "pose": pose}
    if weapon:
        d["weapon"] = "Tool_Shovel"
    if path:
        d["path"] = [round(path[0], 1), round(path[1], 1)]
        d["speed"] = speed
    crowd.append(d)


x, z = sp("camp")
for k in range(5):
    a = math.tau * k / 5
    dwarf(x + 3.0 * math.cos(a), z + 3.0 * math.sin(a), rng.choice(("sit", "idle", "sit")), rot=int(math.degrees(a) + 90) % 360, weapon=(k % 2 == 0))
x, z = sp("gem_house")
for k in range(3):
    dwarf(x - 4 + 3 * k, z - 3, rng.choice(("sit", "idle")), rot=rng.randrange(0, 360, 15))
x, z = sp("crystal_hall")
for dx, dz in ((-4, 7), (4, 7), (0, 8)):
    dwarf(x + dx, z + dz, "idle", rot=180, weapon=True)
walkers = 0
for (key, (x0, z0, x1, z1)) in list(rail_edges.items()):
    if key[0] == "special" or walkers >= 24 or rng.random() > 0.7:
        continue
    t = rng.uniform(0.25, 0.75)
    px, pz = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
    if room_at(px, pz, -2.0) is None or any(math.hypot(px - ix, pz - iz) < 3.0 for ix, iz in interest_things) or (px, pz) == (0.0, 0.0):
        continue
    horiz = abs(z1 - z0) < 1e-6
    off = rng.choice((-1.6, 1.6))
    a = (px + (0 if horiz else off), pz + (off if horiz else 0))
    b = (a[0] + (rng.uniform(2.5, 4.5) * rng.choice((-1, 1)) if horiz else 0), a[1] + (0 if horiz else rng.uniform(2.5, 4.5) * rng.choice((-1, 1))))
    dwarf(a[0], a[1], "walk", weapon=rng.random() < 0.6, path=b, speed=round(rng.uniform(0.7, 1.0), 2))
    walkers += 1

breakables = []
cells = list(seen)
rng.shuffle(cells)
for c in cells:
    if len(breakables) >= 42:
        break
    x, z = cell_center(c)
    px, pz = round(x + rng.choice((-3.8, 3.8)), 1), round(z + rng.choice((-3.8, 3.8)), 1)
    if not near_interest(px, pz, 2.5) and not near_taken(px, pz, 1.0) and rail_dist(px, pz) > 1.2:
        breakables.append({"id": "b%d" % (len(breakables) + 1), "monster": "crate" if len(breakables) % 2 == 0 else "barrel", "position": [px, pz], "table": "breakable_potion"})
        taken.append((px, pz, 1.0))
breakables.append({"id": "coin_bag", "monster": "coin_bag", "position": [4.0, 1.5], "table": "coin_bag"})
for i, p in enumerate((cell_center(main_path[2]), cell_center(main_path[len(main_path) // 2]), cell_center(main_path[-3]), sp("camp"), sp("gem_house"), sp("crystal_hall")), start=2):
    breakables.append({"id": "coin_bag_%d" % i, "monster": "coin_bag", "position": [round(p[0] + 3.5, 1), round(p[1] - 3.5, 1)], "table": "coin_bag"})

arenas["mine_01_crystal_vein"] = {
    "_comment": "Mina de Cristais, ampliada e feita labirinto (Lowpoly Crystals Pack, iPoly3D, CC0; Rocks, Nobiax, CC0; Low Poly Rocks, para, CC0; Rails, yd): grade de 9 x 11 salas de 12 m como o Esgoto, com paredes de pedras, "
                "cristais e ouro, e os trilhos como caminho (linha principal e ramais). Ramais: Acampamento dos Anões (Capataz), Gruta das Carroças (a carroça desperta o Chefe Troll), Salão dos Cristais (o Cristal Pulsante desperta a "
                "Besta de Quartzo), Casa do Joalheiro e Câmara Secreta. Túnel do portão (Guarda-Chaves, duas chaves) -> Coração da Mina (Golem de Cristal, chefe final, com a saída). Gerado por tools/assets/build_mine.py.",
    "name_key": "ARENA_MINE", "player_class": "mage", "map_id": "map_mine", "area_level": 5, "final": True, "victory_groups": ["mn_boss"], "wake_radius": 10.0, "alert_radius": 5.0,
    "rooms": rooms, "encounters": encounters, "hazards": [], "entries": {"start": [0, 3], "mine": [0, 3]}, "props": props, "quest_spots": [], "breakables": breakables,
    "style": {"_comment": "Mina: chão de terra escuro; as paredes são fileiras de pedras (decor), sem muro do kit.", "walls": [""], "floor": "Ground_Dirt", "low": "", "ground": [0.05, 0.045, 0.05], "tint": [0.55, 0.5, 0.55]},
    "decor": decor, "crowd": crowd, "passive": True}


# ---------------------------------------------------------------- NPCs e missões
def dwarf_body(hair, color):
    return {"class": "archer", "sex": "male", "hair": hair, "hair_color": color, "pose": "idle", "outfit": {}}


npcs["mn_apprentice"] = {"name_key": "NPC_MN_APPRENTICE", "color": [0.55, 0.4, 0.25], "dialogues": [
    {"when": {"quest_new": "mn_clear"}, "lines": ["DLG_MNAPP_1", "DLG_MNAPP_2", "DLG_MNAPP_3"], "offer": "mn_clear"},
    {"when": {"quest_active": "mn_clear"}, "lines": ["DLG_MNAPP_ACTIVE"]}, {"when": {}, "lines": ["DLG_MNAPP_DONE"]}], "body": dwarf_body(["Hair_Buzzed", "Hair_Beard"], [0.5, 0.25, 0.1])}
npcs["mn_foreman"] = {"name_key": "NPC_MN_FOREMAN", "color": [0.5, 0.35, 0.2], "dialogues": [
    {"when": {"quest_new": "mn_tusk"}, "lines": ["DLG_MNFORE_1", "DLG_MNFORE_2", "DLG_MNFORE_3"], "offer": "mn_tusk"},
    {"when": {"quest_active": "mn_tusk"}, "lines": ["DLG_MNFORE_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_MNFORE_DONE"]}], "body": dwarf_body(["Hair_Beard"], [0.6, 0.3, 0.1])}
npcs["mn_ore_cart"] = {"name_key": "NPC_MN_ORE_CART", "color": [0.45, 0.35, 0.25], "dialogues": [
    {"when": {"quest_active": "mn_tusk"}, "lines": ["DLG_MNCART_1", "DLG_MNCART_2"]}, {"when": {}, "lines": ["DLG_MNCART_LOCKED"]}]}
npcs["mn_jeweler"] = {"name_key": "NPC_MN_JEWELER", "color": [0.6, 0.55, 0.3], "dialogues": [
    {"when": {"quest_new": "mn_quartz"}, "lines": ["DLG_MNJEW_1", "DLG_MNJEW_2", "DLG_MNJEW_3"], "offer": "mn_quartz"},
    {"when": {"quest_active": "mn_quartz"}, "lines": ["DLG_MNJEW_ACTIVE"], "service": "turn_in"},
    {"when": {"quest_done": "mn_quartz"}, "lines": ["DLG_MNJEW_DONE"]}, {"when": {}, "lines": ["DLG_MNJEW_WAIT"]}], "body": dwarf_body(["Hair_SimpleParted", "Hair_Beard"], [0.6, 0.55, 0.5])}
npcs["mn_crystal"] = {"name_key": "NPC_MN_CRYSTAL", "color": [0.7, 0.4, 1.0], "dialogues": [
    {"when": {"quest_active": "mn_quartz"}, "lines": ["DLG_MNCRY_1", "DLG_MNCRY_2"]}, {"when": {}, "lines": ["DLG_MNCRY_LOCKED"]}]}
npcs["mn_gatekeeper"] = {"name_key": "NPC_MN_GATEKEEPER", "color": [0.4, 0.4, 0.45], "dialogues": [
    {"when": {"quest_new": "mn_gate"}, "lines": ["DLG_MNGUARD_1", "DLG_MNGUARD_2", "DLG_MNGUARD_3"], "offer": "mn_gate"},
    {"when": {"quest_active": "mn_gate"}, "lines": ["DLG_MNGUARD_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_MNGUARD_DONE"]}], "body": dwarf_body(["Hair_Beard"], [0.12, 0.1, 0.1])}
quests["mn_clear"] = {"name_key": "QUEST_MN_CLEAR", "desc_key": "QUEST_MN_CLEAR_DESC", "type": "village", "giver": "mn_apprentice", "area": "mine_01_crystal_vein", "clear": clear_ids,
                      "target_element": "earth", "reward": {"gold": 400, "xp": 800}}
quests["mn_tusk"] = {"name_key": "QUEST_MN_TUSK", "desc_key": "QUEST_MN_TUSK_DESC", "type": "village", "giver": "mn_foreman", "area": "mine_01_crystal_vein", "target_element": "earth",
                     "reward": {"gold": 450, "xp": 900}, "item": "troll_tusk", "gives": "key_pickaxe"}
quests["mn_quartz"] = {"name_key": "QUEST_MN_QUARTZ", "desc_key": "QUEST_MN_QUARTZ_DESC", "type": "village", "giver": "mn_jeweler", "area": "mine_01_crystal_vein", "target_element": "water",
                       "reward": {"gold": 450, "xp": 900}, "item": "quartz_core", "gives": "key_lantern"}
quests["mn_gate"] = {"name_key": "QUEST_MN_GATE", "desc_key": "QUEST_MN_GATE_DESC", "type": "village", "giver": "mn_gatekeeper", "area": "mine_01_crystal_vein",
                     "items": ["key_pickaxe", "key_lantern"], "opens_gate": "boss_gate", "target_element": "earth", "reward": {"gold": 550, "xp": 1100}}
T = {
    "MONSTER_MN_QUARTZ_BEAST": ("Besta de Quartzo", "Quartz Beast", "Bestia de Cuarzo"),
    "NPC_MN_APPRENTICE": ("Aprendiz de Mineiro", "Mining Apprentice", "Aprendiz de Minero"),
    "NPC_MN_FOREMAN": ("Capataz Brokk", "Foreman Brokk", "Capataz Brokk"),
    "NPC_MN_ORE_CART": ("Carroça Abandonada", "Abandoned Ore Cart", "Carreta Abandonada"),
    "NPC_MN_JEWELER": ("Joalheiro Dolgrim", "Jeweler Dolgrim", "Joyero Dolgrim"),
    "NPC_MN_CRYSTAL": ("Cristal Pulsante", "Pulsing Crystal", "Cristal Pulsante"),
    "NPC_MN_GATEKEEPER": ("Guarda-Chaves Thrain", "Keywarden Thrain", "Guardallaves Thrain"),
    "VALUABLE_TROLL_TUSK": ("Presa do Chefe Troll", "Troll Chief's Tusk", "Colmillo del Jefe Troll"),
    "VALUABLE_QUARTZ_CORE": ("Núcleo de Quartzo", "Quartz Core", "Núcleo de Cuarzo"),
    "VALUABLE_KEY_PICKAXE": ("Chave da Picareta", "Pickaxe Key", "Llave del Pico"),
    "VALUABLE_KEY_LANTERN": ("Chave da Lanterna", "Lantern Key", "Llave de la Linterna"),
    "TOAST_ORE_CART_AWAKENS": ("A carroça treme sobre os trilhos: o Chefe Troll acorda!", "The cart shakes on its rails: the Troll Chief awakens!", "La carreta tiembla sobre los rieles: ¡el Jefe Troll despierta!"),
    "TOAST_CRYSTAL_AWAKENS": ("O cristal pulsa e racha: a Besta de Quartzo se solta!", "The crystal pulses and cracks: the Quartz Beast breaks free!", "El cristal late y se agrieta: ¡la Bestia de Cuarzo se libera!"),
    "QUEST_MN_CLEAR": ("Limpar as Galerias", "Clear the Galleries", "Limpiar las galerías"),
    "QUEST_MN_CLEAR_DESC": ("O Aprendiz de Mineiro, na entrada, pede que os dois primeiros bandos que ocupam as galerias perto dos trilhos sejam derrubados, para a turma poder trabalhar.",
                            "The Mining Apprentice, at the entrance, asks that the first two packs holding the galleries near the rails be brought down, so the crew can work.",
                            "El Aprendiz de Minero, en la entrada, pide que se derriben las dos primeras bandas que ocupan las galerías junto a los rieles, para que la cuadrilla pueda trabajar."),
    "QUEST_MN_TUSK": ("A Presa do Chefe Troll", "The Troll Chief's Tusk", "El colmillo del Jefe Troll"),
    "QUEST_MN_TUSK_DESC": ("O Capataz Brokk, no Acampamento dos Anões (leste, perto da entrada), quer a presa do Chefe Troll, que dorme numa carroça abandonada na Gruta das Carroças (oeste). Toque a carroça com a missão ativa, derrote o Chefe Troll e traga a presa: em troca vem a Chave da Picareta, uma das duas do portão do Coração da Mina.",
                           "Foreman Brokk, at the Dwarves' Camp (east, near the entrance), wants the tusk of the Troll Chief, who sleeps in an abandoned ore cart in the Cart Cave (west). Touch the cart with the quest active, defeat the Troll Chief and bring the tusk: in return you get the Pickaxe Key, one of the two for the Mine Heart's gate.",
                           "El Capataz Brokk, en el Campamento de los Enanos (este, cerca de la entrada), quiere el colmillo del Jefe Troll, que duerme en una carreta abandonada en la Cueva de las Carretas (oeste). Toca la carreta con la misión activa, derrota al Jefe Troll y trae el colmillo: a cambio recibes la Llave del Pico, una de las dos del portón del Corazón de la Mina."),
    "QUEST_MN_QUARTZ": ("O Núcleo de Quartzo", "The Quartz Core", "El núcleo de cuarzo"),
    "QUEST_MN_QUARTZ_DESC": ("O Joalheiro Dolgrim, na Casa do Joalheiro (oeste, no alto do labirinto), quer o núcleo de quartzo que a Besta de Quartzo guarda no Salão dos Cristais (leste). Toque o Cristal Pulsante com a missão ativa, derrote a fera e traga o núcleo para receber a Chave da Lanterna, a outra do portão do Coração da Mina.",
                             "Jeweler Dolgrim, in the Jeweler's House (west, high in the maze), wants the quartz core the Quartz Beast guards in the Crystal Hall (east). Touch the Pulsing Crystal with the quest active, defeat the beast and bring the core to receive the Lantern Key, the other one for the Mine Heart's gate.",
                             "El Joyero Dolgrim, en la Casa del Joyero (oeste, en lo alto del laberinto), quiere el núcleo de cuarzo que guarda la Bestia de Cuarzo en el Salón de los Cristales (este). Toca el Cristal Pulsante con la misión activa, derrota a la fiera y trae el núcleo para recibir la Llave de la Linterna, la otra del portón del Corazón de la Mina."),
    "QUEST_MN_GATE": ("O Portão do Coração da Mina", "The Mine Heart's Gate", "El portón del Corazón de la Mina"),
    "QUEST_MN_GATE_DESC": ("O Guarda-Chaves Thrain, no túnel ao norte do labirinto (siga os trilhos), só abre o portão para quem trouxer as duas chaves: a da Picareta (Capataz) e a da Lanterna (Joalheiro). Atrás dele fica o Coração da Mina, onde o Golem de Cristal espera.",
                           "Keywarden Thrain, in the tunnel north of the maze (follow the rails), only opens the gate for those with both keys: the Pickaxe (Foreman) and the Lantern (Jeweler). Beyond lies the Mine Heart, where the Crystal Golem waits.",
                           "El Guardallaves Thrain, en el túnel al norte del laberinto (sigan los rieles), solo abre el portón a quien traiga las dos llaves: la del Pico (Capataz) y la de la Linterna (Joyero). Tras él está el Corazón de la Mina, donde espera el Gólem de Cristal."),
    "DLG_MNAPP_1": ("Ah, visitas! Cuidado com os trilhos: eles são o único caminho seguro nesta mina. Fora deles o labirinto se fecha, e eu já perdi três picaretas e um tio nele.",
                    "Ah, visitors! Mind the rails: they are the only safe way in this mine. Off them the maze closes in, and I have lost three pickaxes and an uncle in it.",
                    "¡Ah, visitas! Cuidado con los rieles: son el único camino seguro en esta mina. Fuera de ellos el laberinto se cierra, y ya perdí tres picos y un tío en él."),
    "DLG_MNAPP_2": ("Os dois primeiros bandos, aqui perto, tomaram as galerias da frente. Sem elas livres, a turma não consegue puxar as carroças.",
                    "The first two packs, right here, took the front galleries. Without them clear, the crew cannot haul the carts.",
                    "Las dos primeras bandas, aquí cerca, tomaron las galerías de delante. Sin ellas libres, la cuadrilla no puede arrastrar las carretas."),
    "DLG_MNAPP_3": ("Derrubem os dois e eu pago. Depois falem com o Capataz Brokk, no acampamento a leste: ele sabe como abrir o portão do Coração da Mina.",
                    "Bring both down and I will pay. Then talk to Foreman Brokk, at the camp to the east: he knows how to open the Mine Heart's gate.",
                    "Derriben las dos y pago. Luego hablen con el Capataz Brokk, en el campamento al este: él sabe cómo abrir el portón del Corazón de la Mina."),
    "DLG_MNAPP_ACTIVE": ("As galerias da frente ficam ao lado dos trilhos. Os bandos fazem barulho: dá para ouvir de longe.", "The front galleries are beside the rails. The packs make noise: you can hear them from afar.", "Las galerías de delante están junto a los rieles. Las bandas hacen ruido: se oyen de lejos."),
    "DLG_MNAPP_DONE": ("Que alívio! Agora a turma volta ao trabalho. Sigam os trilhos para o norte, e não saiam deles sem lanterna.", "What a relief! Now the crew goes back to work. Follow the rails north, and do not leave them without a lantern.", "¡Qué alivio! Ahora la cuadrilla vuelve al trabajo. Sigan los rieles al norte, y no salgan de ellos sin linterna."),
    "DLG_MNFORE_1": ("Brokk, capataz desta mina há quarenta anos. O portão do Coração só abre com duas chaves, e uma delas está com um troll que dorme numa carroça velha, na Gruta das Carroças, lá no oeste.",
                     "Brokk, foreman of this mine for forty years. The Heart's gate only opens with two keys, and one of them is held by a troll sleeping in an old cart, in the Cart Cave, far to the west.",
                     "Brokk, capataz de esta mina hace cuarenta años. El portón del Corazón solo abre con dos llaves, y una de ellas la tiene un troll que duerme en una carreta vieja, en la Cueva de las Carretas, allá al oeste."),
    "DLG_MNFORE_2": ("Ele me roubou uma presa de marfim que eu usava como amuleto de sorte, e desde então a mina só dá desgraça. A presa ficou presa na boca dele, a besta.",
                     "He stole an ivory tusk I used as a lucky charm, and since then the mine has given only misfortune. The tusk is stuck in his mouth, the beast.",
                     "Me robó un colmillo de marfil que usaba como amuleto de la suerte, y desde entonces la mina solo da desgracias. El colmillo quedó en su boca, la bestia."),
    "DLG_MNFORE_3": ("Toquem a carroça, derrubem o Chefe Troll e tragam a presa. Eu dou a Chave da Picareta. Sigam os trilhos para a Gruta: eles chegam lá.",
                     "Touch the cart, bring down the Troll Chief and bring the tusk. I give the Pickaxe Key. Follow the rails to the Cave: they lead there.",
                     "Toquen la carreta, derriben al Jefe Troll y traigan el colmillo. Doy la Llave del Pico. Sigan los rieles hasta la Cueva: llegan allí."),
    "DLG_MNFORE_ACTIVE": ("A Gruta das Carroças fica a oeste, num ramal dos trilhos. A presa é amarelada e do tamanho do seu braço. Tragam-na e a chave é de vocês.",
                          "The Cart Cave is to the west, on a branch of the rails. The tusk is yellowed and as long as your arm. Bring it and the key is yours.",
                          "La Cueva de las Carretas está al oeste, en un ramal de los rieles. El colmillo es amarillento y del largo de su brazo. Tráiganlo y la llave es suya."),
    "DLG_MNFORE_DONE": ("A minha presa! A sorte volta à mina. A Chave da Picareta é de vocês: levem-na ao Guarda-Chaves, no túnel ao norte, junto com a da Lanterna.",
                        "My tusk! Luck returns to the mine. The Pickaxe Key is yours: take it to the Keywarden, in the tunnel to the north, together with the Lantern one.",
                        "¡Mi colmillo! La suerte vuelve a la mina. La Llave del Pico es suya: llévenla al Guardallaves, en el túnel al norte, junto con la de la Linterna."),
    "DLG_MNCART_1": ("A madeira da carroça está fria, mas o ferro dos trilhos vibra, como se algo enorme respirasse debaixo do minério.",
                     "The cart's wood is cold, but the iron of the rails hums, as if something huge breathed under the ore.",
                     "La madera de la carreta está fría, pero el hierro de los rieles vibra, como si algo enorme respirara bajo el mineral."),
    "DLG_MNCART_2": ("O Chefe Troll acorda!", "The Troll Chief awakens!", "¡El Jefe Troll despierta!"),
    "DLG_MNCART_LOCKED": ("Uma carroça de minério abandonada sobre os trilhos. Nada responde ao seu toque.", "An abandoned ore cart on the rails. Nothing answers your touch.", "Una carreta de mineral abandonada sobre los rieles. Nada responde a tu toque."),
    "DLG_MNJEW_1": ("Trinta anos lapidando as pedras desta mina, e a mais bela nunca chegou às minhas mãos: o Núcleo de Quartzo, o coração do cristal gigante do Salão dos Cristais, a leste.",
                    "Thirty years cutting this mine's stones, and the finest never reached my hands: the Quartz Core, the heart of the giant crystal in the Crystal Hall, to the east.",
                    "Treinta años puliendo las piedras de esta mina, y la más bella nunca llegó a mis manos: el Núcleo de Cuarzo, el corazón del cristal gigante del Salón de los Cristales, al este."),
    "DLG_MNJEW_2": ("O cristal pulsa como um coração vivo, e dele nasceu uma fera de quartzo que o protege. Ela só acorda quando alguém toca o Cristal Pulsante com más intenções.",
                    "The crystal pulses like a living heart, and from it was born a quartz beast that guards it. It only wakes when someone touches the Pulsing Crystal with ill intent.",
                    "El cristal late como un corazón vivo, y de él nació una fiera de cuarzo que lo protege. Solo despierta cuando alguien toca el Cristal Pulsante con malas intenciones."),
    "DLG_MNJEW_3": ("Toquem o cristal, derrubem a Besta de Quartzo e tragam o núcleo. Em troca eu dou a Chave da Lanterna, a outra que abre o portão do Coração da Mina.",
                    "Touch the crystal, bring down the Quartz Beast and bring me the core. In return I give the Lantern Key, the other one that opens the Mine Heart's gate.",
                    "Toquen el cristal, derriben a la Bestia de Cuarzo y tráiganme el núcleo. A cambio doy la Llave de la Linterna, la otra que abre el portón del Corazón de la Mina."),
    "DLG_MNJEW_ACTIVE": ("O Salão dos Cristais fica a leste, num ramal dos trilhos, depois de muitas curvas. O núcleo brilha em azul e é quente ao toque. Tragam-no para mim.",
                         "The Crystal Hall is to the east, on a branch of the rails, after many turns. The core glows blue and is warm to the touch. Bring it to me.",
                         "El Salón de los Cristales está al este, en un ramal de los rieles, tras muchas curvas. El núcleo brilla en azul y está tibio al tacto. Tráiganmelo."),
    "DLG_MNJEW_DONE": ("O núcleo! É ainda mais lindo do que eu sonhei. A Chave da Lanterna é de vocês: levem-na ao Guarda-Chaves, junto com a da Picareta.",
                       "The core! It is even lovelier than I dreamed. The Lantern Key is yours: take it to the Keywarden, together with the Pickaxe one.",
                       "¡El núcleo! Es aún más hermoso de lo que soñé. La Llave de la Linterna es suya: llévenla al Guardallaves, junto con la del Pico."),
    "DLG_MNJEW_WAIT": ("Cada pedra tem uma história. Voltem quando quiserem ouvir a de alguma.", "Every stone has a story. Come back when you want to hear one.", "Cada piedra tiene una historia. Vuelvan cuando quieran oír alguna."),
    "DLG_MNCRY_1": ("O cristal pulsa, quente, em tom roxo, e rachaduras finas correm por dentro dele. Algo se move lá no fundo.",
                    "The crystal pulses, warm, in purple, and thin cracks run inside it. Something moves deep within.",
                    "El cristal late, tibio, en tono púrpura, y finas grietas recorren su interior. Algo se mueve en el fondo."),
    "DLG_MNCRY_2": ("A Besta de Quartzo se solta!", "The Quartz Beast breaks free!", "¡La Bestia de Cuarzo se libera!"),
    "DLG_MNCRY_LOCKED": ("Um cristal roxo, imóvel, que brilha de leve. Nada responde ao seu toque.", "A purple crystal, motionless, glowing softly. Nothing answers your touch.", "Un cristal púrpura, inmóvil, que brilla suavemente. Nada responde a tu toque."),
    "DLG_MNGUARD_1": ("Alto. Este portão fecha o Coração da Mina, e no Coração mora o Golem de Cristal, que nasceu de todo o minério que arrancamos. Eu guardo as chaves há mais tempo do que o portão tem ferrugem.",
                      "Halt. This gate closes the Mine Heart, and in the Heart lives the Crystal Golem, born of all the ore we tore out. I have kept the keys longer than the gate has had rust.",
                      "Alto. Este portón cierra el Corazón de la Mina, y en el Corazón vive el Gólem de Cristal, nacido de todo el mineral que arrancamos. Guardo las llaves desde hace más tiempo del que el portón tiene óxido."),
    "DLG_MNGUARD_2": ("O portão só abre com DUAS chaves: a da Picareta e a da Lanterna. A primeira está com o Capataz Brokk, no acampamento a leste; a segunda, com o Joalheiro Dolgrim, na casa dele, a oeste.",
                      "The gate only opens with TWO keys: the Pickaxe and the Lantern. The first is with Foreman Brokk, at the camp to the east; the second, with Jeweler Dolgrim, in his house to the west.",
                      "El portón solo abre con DOS llaves: la del Pico y la de la Linterna. La primera la tiene el Capataz Brokk, en el campamento al este; la segunda, el Joyero Dolgrim, en su casa al oeste."),
    "DLG_MNGUARD_3": ("Cada um cobra um preço: uma presa, um núcleo de cristal. Tragam as duas chaves a mim e eu abro a passagem.",
                      "Each charges a price: a tusk, a crystal core. Bring both keys to me and I will open the way.",
                      "Cada uno cobra un precio: un colmillo, un núcleo de cristal. Tráiganme las dos llaves y abro el paso."),
    "DLG_MNGUARD_ACTIVE": ("Só abro com as duas chaves, Picareta e Lanterna, na mesma bolsa. O Capataz fica a leste; o Joalheiro, a oeste. Sigam os trilhos.",
                           "I only open with both keys, Pickaxe and Lantern, in the same bag. The Foreman is to the east; the Jeweler, to the west. Follow the rails.",
                           "Solo abro con las dos llaves, Pico y Linterna, en la misma bolsa. El Capataz está al este; el Joyero, al oeste. Sigan los rieles."),
    "DLG_MNGUARD_DONE": ("As duas chaves! O portão está aberto. Cuidado: o Golem de Cristal não sente dor, e cada pedaço dele que cai vira lâmina.",
                         "Both keys! The gate is open. Beware: the Crystal Golem feels no pain, and every piece that falls from him becomes a blade.",
                         "¡Las dos llaves! El portón está abierto. Cuidado: el Gólem de Cristal no siente dolor, y cada pedazo suyo que cae se vuelve hoja."),
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
    for dst, src, mul in (("key_pickaxe", "key_spades", (1.5, 0.95, 0.45)), ("key_lantern", "key_clubs", (1.5, 1.35, 0.5)), ("troll_tusk", "lamassu_horn", (1.1, 1.0, 0.8)),
                          ("quartz_core", "rough_gem", (0.6, 0.9, 1.5))):
        im = Image.open(ICONS + src + ".png").convert("RGBA")
        r_, g_, b_, a_ = im.split()
        Image.merge("RGBA", (r_.point(lambda v: min(255, int(v * mul[0]))), g_.point(lambda v: min(255, int(v * mul[1]))), b_.point(lambda v: min(255, int(v * mul[2]))), a_)).save(ICONS + dst + ".png")
except Exception as exc:
    print("aviso: ícones não gerados:", exc)

for path, data in ((ARENAS, arenas), (MONSTERS, monsters), (NPCS, npcs), (QUESTS, quests), (VALUABLES, valuables)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
print("OK mine: %d salas, %d m2, %d peças, %d anões, %d encontros, %d luzes, caminho principal %d salas, %d trilhos" % (len(rooms), AREA_M2, len(decor), len(crowd), len(encounters), lights, len(main_path), len(rail_segments)))
