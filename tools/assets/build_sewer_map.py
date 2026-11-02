"""Gera o Esgoto de Tortuga como UM mapa de um andar só (`sewers_01_drains`), no lugar das 4 áreas antigas (Bueiros, Canais, Passagem da Guerra, Ninho).
Substitui tools/assets/build_sewer_maze.py. Determinístico (semente fixa): rode de novo para refazer o mapa (os dados antigos que ele reaproveita estão em
tools/assets/sewer_legacy.json). Também cria os 2 NPCs das missões dos mini-chefes, as 2 missões e os textos (pt/en/es), e apaga as áreas 2 a 4.

O mapa (dobro do labirinto antigo): uma grade de 7 x 9 salas de 8 m (1 m de vão na horizontal, as de cima e de baixo se encostam) entre a sala de entrada e o túnel do
fundo, em 5 SETORES de um monstro cada, mais salas especiais coladas nas bordas (cada parede de sala só aceita uma porta):
  1 Bueiros da Rua Principal   (linhas 0-2)                  Sapos Pestilentos (+ Ratazana nos becos e uma ninhada)
  2 Canais de Lixo             (linhas 3-5, colunas 0-3)      Sapos Ácidos nas poças         -> praça oeste: REI DOS SAPOS (mini-chefe)
  3 Galerias dos Morcegos      (linhas 3-5, colunas 4-6)      Morcegos Pestilentos           -> segredo a leste (baú, elite tóxica); posto do Caçador de Pragas (NPC)
  4 Passagem Secreta da Guerra (linhas 6-8, colunas 4-6)      Jacarés escondidos na água     -> praça leste: GATOR VELHO (mini-chefe)
  5 Câmaras dos Cogumelos      (linhas 6-8, colunas 0-3)      Tios-Cogumelo e Escorpiões
  fundo: túnel + NINHO DA RAINHA (sala do chefe do mapa, com o Tesouro Perdido da Guerra e o portal da vitória).
O Catador do Esgoto (missão do Gator Velho) fica na sala de entrada; o Caçador de Pragas (missão do Rei dos Sapos), no posto do lado leste: os dois, longe dos chefes.
A vitória do mapa é só vencer a Rainha (`victory_groups`): não precisa limpar o resto.
uso: python3 -I tools/assets/build_sewer_map.py   (na raiz do projeto)"""
import json, math, random, re
from collections import deque

ARENAS, QUESTS, NPCS, LEGACY = "data/arenas.json", "data/quests.json", "data/npcs.json", "tools/assets/sewer_legacy.json"
AREA = "sewers_01_drains"
rng = random.Random(21)

NC, NR = 7, 9                       # colunas x linhas de salas
PX, PZ = 9, 8                       # passo entre os centros (8 m de sala + 1 m de vão na horizontal; as de baixo se encostam)
X0, Z0 = -27, -10                   # centro da coluna 0 e da linha 0
START, END = (3, 0), (3, 8)


def cx(c): return X0 + PX * c
def cz(r): return Z0 - PZ * r


def sector(c, r):
    if r <= 2:
        return 1
    if r <= 5:
        return 2 if c <= 3 else 3
    return 5 if c <= 3 else 4


# Salas especiais coladas nas bordas: (célula, lado) -> sala
ATTACH_W = (0, 4)    # praça oeste (Rei dos Sapos), a leste da qual fica a célula (0,4)
ATTACH_E = (6, 7)    # praça leste (Gator Velho)
POST = (6, 1)        # posto do Caçador de Pragas
SECRET = (6, 3)      # passagem do segredo

legacy = json.load(open(LEGACY, encoding="utf-8"))
data = json.load(open(ARENAS, encoding="utf-8"))

# --- labirinto: árvore crescente (muitos becos) com laços só dentro de cada setor, para os setores terem poucas passagens entre si ------------------
def neighbors(c):
    x, z = c
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (x + dx, z + dz)
        if 0 <= n[0] < NC and 0 <= n[1] < NR:
            yield n


open_edges = set()
seen = {START}
active = [START]
while active:
    index = rng.randrange(len(active)) if rng.random() < 0.5 else len(active) - 1
    cur = active[index]
    options = [n for n in neighbors(cur) if n not in seen]
    if not options:
        active.pop(index)
        continue
    nxt = rng.choice(options)
    open_edges.add(frozenset((cur, nxt)))
    seen.add(nxt)
    active.append(nxt)
closed = sorted({tuple(sorted((c, n))) for c in seen for n in neighbors(c) if frozenset((c, n)) not in open_edges})
rng.shuffle(closed)
loops_per_sector = {s: 0 for s in range(1, 6)}
for a, b in closed:
    if sector(*a) == sector(*b) and loops_per_sector[sector(*a)] < 3:
        open_edges.add(frozenset((a, b)))
        loops_per_sector[sector(*a)] += 1

SIDE = {(1, 0): "east", (-1, 0): "west", (0, 1): "north", (0, -1): "south"}  # (dc, dr) -> lado; linha maior = z menor = norte


def doors_of(c):
    out = []
    for n in neighbors(c):
        if frozenset((c, n)) in open_edges:
            out.append(SIDE[(n[0] - c[0], n[1] - c[1])])
    return out


depth = {START: 0}
queue = deque([START])
while queue:
    cur = queue.popleft()
    for n in neighbors(cur):
        if frozenset((cur, n)) in open_edges and n not in depth:
            depth[n] = depth[cur] + 1
            queue.append(n)
assert len(depth) == NC * NR, "labirinto desconexo"

rooms = [{"id": "entry", "center": [0, 0], "size": [14, 12], "doors": ["north"], "torch": True, "narrow": True}]
for c in sorted(depth, key=lambda k: depth[k]):
    doors = doors_of(c)
    if c == START:
        doors.append("south")
    if c == END:
        doors.append("north")
    if c == ATTACH_W:
        doors.append("west")
    if c in (ATTACH_E, POST, SECRET):
        doors.append("east")
    room = {"id": "maze_%d_%d" % c, "center": [cx(c[0]), cz(c[1])], "size": [8, 8], "doors": doors, "narrow": True}
    if depth[c] % 4 == 0 and c != START:
        room["torch"] = True
    rooms.append(room)

# praças e salas ligadas às bordas (centro = célula + 4 de meia sala + 1 de vão + meia largura da sala nova)
PRACA = (22, 18)
praca_w = [cx(ATTACH_W[0]) - 5 - PRACA[0] / 2, cz(ATTACH_W[1])]
praca_e = [cx(ATTACH_E[0]) + 5 + PRACA[0] / 2, cz(ATTACH_E[1])]
post_c = [cx(POST[0]) + 5 + 5, cz(POST[1])]
pipe_c = [cx(SECRET[0]) + 5 + 3, cz(SECRET[1])]
secret_c = [pipe_c[0] + 3 + 0.5 + 0.5 + 5, cz(SECRET[1])]
tunnel_z = cz(END[1]) - 4 - 7
nest_z = tunnel_z - 7 - 17
rooms += [
    {"id": "praca_frog_king", "center": praca_w, "size": list(PRACA), "doors": ["east"], "torch": True},
    {"id": "praca_old_gator", "center": praca_e, "size": list(PRACA), "doors": ["west"], "torch": True},
    {"id": "post", "center": post_c, "size": [10, 8], "doors": ["west"], "torch": True, "narrow": True},
    {"id": "secret_pipe", "center": pipe_c, "size": [6, 5], "doors": ["west", "east"], "narrow": True},
    {"id": "secret", "center": secret_c, "size": [10, 10], "doors": ["west"]},
    {"id": "tunnel", "center": [0, tunnel_z], "size": [5, 14], "doors": ["north", "south"], "narrow": True},
    {"id": "nest", "center": [0, nest_z], "size": [32, 34], "doors": ["south"], "torch": True},
]
NEST_DZ = nest_z - (-36)  # o ninho antigo ficava em (0, -36)

# --- encontros ---------------------------------------------------------------------------------------------------------------------------------------
special_cells = {START, END, ATTACH_W, ATTACH_E, POST, SECRET}
by_sector = {s: [c for c in depth if sector(*c) == s and c not in special_cells] for s in range(1, 6)}
dead_ends = [c for c in depth if len(doors_of(c)) == 1 and c not in special_cells]
used = set()


def pick(s, n, avoid_dead=False, dead=False):
    pool = [c for c in by_sector[s] if c not in used and (not avoid_dead or c not in dead_ends) and (not dead or c in dead_ends)]
    if len(pool) < n:
        pool = [c for c in by_sector[s] if c not in used]
    chosen = rng.sample(pool, min(n, len(pool)))
    used.update(chosen)
    return chosen


encounters, groups = [], []


def add(gid, cell, monsters, level, spread=None):
    e = {"id": gid, "position": [cx(cell[0]), cz(cell[1])], "level": level, "monsters": [{"monster": m, "count": n} for m, n in monsters]}
    if spread:
        e["spread"] = spread
    encounters.append(e)
    groups.append((gid, cell))


# 1 Bueiros: sapos em grupos que crescem com a profundidade; a Ratazana num beco
s1 = sorted(pick(1, 9, avoid_dead=True), key=lambda c: depth[c])
for i, c in enumerate(s1):
    add("sw1_%02d" % (i + 1), c, [("plague_frog", 1 if i == 0 else (3 if i % 3 == 1 else 2))], 1)
for i, c in enumerate(pick(1, 1, dead=True)):
    add("sw1_mutant", c, [("mutant_frog", 1)], 1)
for i, c in enumerate(pick(1, 1, dead=True)):
    add("sw1_swarm", c, [("plague_frog", 8)], 1, spread=2.2)
# 2 Canais: sapos ácidos nas poças (cospem); alguns sapos junto
s2 = pick(2, 6, avoid_dead=True)
for i, c in enumerate(s2):
    add("sw2_%02d" % (i + 1), c, [("acid_toad", 2 if i % 2 == 0 else 3)] + ([("plague_frog", 1)] if i % 3 == 2 else []), 1)
# 3 Galerias: bandos de morcegos
for i, c in enumerate(pick(3, 5, avoid_dead=True)):
    add("sw3_%02d" % (i + 1), c, [("plague_bat", 4 + i % 2)], 1)
# 4 Passagem da Guerra: jacarés escondidos na água, com sapos
s4 = pick(4, 5, avoid_dead=True)
for i, c in enumerate(s4):
    add("sw4_%02d" % (i + 1), c, [("sewer_gator", 1), ("plague_frog", 2)] if i % 2 == 0 else [("sewer_gator", 2)], 2)
# 5 Câmaras dos Cogumelos: tios-cogumelo e escorpiões
for i, c in enumerate(pick(5, 6, avoid_dead=True)):
    add("sw5_%02d" % (i + 1), c, [("fungus_uncle", 1), ("venom_scorpion", 2)] if i % 2 == 0 else [("venom_scorpion", 3)], 2)
# mini-chefes (as missões dos NPCs pedem estes grupos) e a Rainha
encounters.append({"id": "sw_frog_king", "position": praca_w, "level": 1, "spread": 3.4,
                   "monsters": [{"monster": "frog_king", "count": 1}, {"monster": "plague_frog", "count": 3}]})
encounters.append({"id": "sw_old_gator", "position": praca_e, "level": 2, "spread": 3.4,
                   "monsters": [{"monster": "old_gator", "count": 1}, {"monster": "sewer_gator", "count": 2}]})
sec = dict(legacy["secret_elite"])
sec["id"] = "sw_secret"
sec["position"] = [secret_c[0] + 1.5, secret_c[1]]
sec["level"] = 1
encounters.append(sec)
encounters.append({"id": "sw_nest_guard", "position": [0, tunnel_z], "level": 2, "monsters": [{"monster": "plague_frog", "count": 3}]})
encounters.append({"id": "sw_queen", "position": [0, nest_z + (-42 - -36)], "level": 2, "monsters": [{"monster": "demon_rat_queen", "count": 1}]})

# Só os chefes do esgoto (Rei dos Sapos, Gator Velho e a Rainha) ficam, sozinhos; nenhum outro monstro revida.
SEWER_BOSSES = ("frog_king", "old_gator", "demon_rat_queen")
encounters = [dict(e, monsters=[m for m in e["monsters"] if m["monster"] in SEWER_BOSSES]) for e in encounters]
encounters = [e for e in encounters if e["monsters"]]

# --- props -------------------------------------------------------------------------------------------------------------------------------------------
props = [{"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-4, 3], "to": "tortuga", "entry": "sewer", "expedition_end": True},
         {"id": "sewer_scavenger", "kind": "npc", "npc": "sewer_scavenger", "position": [4.5, -1.5], "rotation": 270},
         {"id": "sewer_ratcatcher", "kind": "npc", "npc": "sewer_ratcatcher", "position": [post_c[0] + 1.5, post_c[1]], "rotation": 270},
         {"id": "secret_chest", "kind": "chest", "position": [secret_c[0] + 1, secret_c[1] - 2.0], "secret": True, "loot": "chest"}]
# baús nos becos mais fundos de cada setor (2 a 5)
for s in (2, 3, 4, 5):
    cand = sorted((c for c in dead_ends if sector(*c) == s and c not in used), key=lambda k: -depth[k])
    if cand:
        c = cand[0]
        used.add(c)
        props.append({"id": "maze_chest_%d" % s, "kind": "chest", "position": [cx(c[0]), cz(c[1]) - 2.5], "loot": "chest"})
# água: poças nos canais (sapos ácidos), jacarés na Passagem da Guerra, praça do Gator Velho e ninho
for gid, cell in groups:
    s = sector(*cell)
    if s == 2 and gid.endswith(("01", "03", "05")) or s == 4:
        props.append({"id": "water_%s" % gid, "kind": "water", "position": [cx(cell[0]), cz(cell[1])], "size": [7, 7]})
props.append({"id": "water_old_gator", "kind": "water", "position": [praca_e[0], praca_e[1]], "size": [14, 10]})
props.append({"id": "water_frog_king", "kind": "water", "position": [praca_w[0] + 2, praca_w[1] - 1], "size": [12, 8]})
for p in legacy["nest_props"]:
    q = dict(p)
    q["position"] = [p["position"][0], p["position"][1] + NEST_DZ]
    if q["id"] == "return_portal":
        q["id"] = "victory_portal"
    props.append(q)
# Piso todo de pedra: sem água (nem o lago do Gator Velho).
props = [p for p in props if p["kind"] != "water"]
# brasão da Passagem da Guerra (o Arqueiro reconhece) na entrada do setor 4
crest_cell = (4, 6)
crest = dict(legacy["war_crest"])
crest["position"] = [cx(crest_cell[0]) - 2.5, cz(crest_cell[1]) - 3.2]
props.append(crest)
# cartazes dos setores
SIGN_AT = {1: (3, 0), 2: (2, 3), 3: (4, 3), 4: (5, 6), 5: (2, 6)}
for s, c in SIGN_AT.items():
    props.append({"id": "sign_sector_%d" % s, "kind": "sign", "name_key": "PROP_SEWER_SECTOR_%d" % s, "position": [cx(c[0]) + 2.8, cz(c[1]) + 2.6],
                  "text_key": "SIGN_SEWER_SECTOR_%d" % s})
props.append({"id": "sign_nest", "kind": "sign", "name_key": "PROP_SEWER_NEST", "position": [2.8, tunnel_z - 5.0], "text_key": "SIGN_SEWER_NEST"})

# --- poças de lodo, objetos quebráveis e decoração -------------------------------------------------------------------------------------------------
hazards = []
quotas = {1: 2, 2: 3, 3: 2, 4: 3, 5: 5}
for s, n in quotas.items():
    cells = [c for c in depth if sector(*c) == s and c not in special_cells]
    rng.shuffle(cells)
    for c in cells[:n]:
        hazards.append({"position": [cx(c[0]) + rng.choice((-2, 2)), cz(c[1]) + rng.choice((-2, 2))], "radius": round(rng.choice((1.3, 1.5, 1.8)), 1)})
hazards += [{"position": [p["position"][0], p["position"][1] + NEST_DZ], "radius": p["radius"]} for p in legacy["nest_hazards"]]
# (as manchas verdes de lodo que dão dano voltaram: hazards de cada setor + as do Ninho)

breakables = [dict(b) for b in legacy["entry_breakables"]]
breakables.append({"id": "coin_bag", "monster": "coin_bag", "position": [4.0, 1.5], "table": "coin_bag"})
kinds = ["barrel", "crate", "pot", "pot", "barrel", "crate", "pot"]
cells_all = [c for c in depth if c not in (START, END)]
for i, c in enumerate(rng.sample(cells_all, 30)):
    kind = kinds[i % len(kinds)]
    breakables.append({"id": "m%s%d" % (kind[0], i), "monster": kind, "position": [cx(c[0]) + rng.choice((-2.8, 2.8)), cz(c[1]) + rng.choice((-2.8, 2.8))]})
for b in legacy["nest_breakables"]:
    breakables.append({"id": "n" + b["id"], "monster": b["monster"], "position": [b["position"][0], b["position"][1] + NEST_DZ]})
breakables.append({"id": "pot_post", "monster": "pot", "position": [post_c[0] - 3.4, post_c[1] + 2.8]})

decor = [dict(e) for e in legacy["entry_decor"]]
for e in legacy["nest_decor"]:
    e2 = dict(e)
    e2["position"] = [e["position"][0], e["position"][1] + NEST_DZ]
    decor.append(e2)
SECTOR_PIECES = {1: ["Barrel", "Crate_Wooden", "Bucket_Wooden_1", "Rope_1", "Crate_Metal", "Cage_Small"],
                 2: ["Barrel", "Bucket_Wooden_1", "Crate_Wooden", "Rope_1", "Crate_Metal"],
                 3: ["Cage_Small", "Rope_1", "Crate_Metal", "Barrel", "Mushroom_Flat"],
                 4: ["Shield_Wooden", "Barrel", "Crate_Metal", "Rope_1"],
                 5: ["Mushroom_Cluster", "Mushroom_Tall", "Mushroom_Flat", "Mushroom_Cluster", "Barrel"]}
for c in depth:
    if c in (START, END):
        continue
    s = sector(*c)
    n = 2 if rng.random() < 0.5 else 1
    for _ in range(n):
        decor.append({"piece": rng.choice(SECTOR_PIECES[s]), "position": [cx(c[0]) + rng.choice((-3.0, 3.0)), cz(c[1]) + rng.choice((-3.0, 3.0))],
                      "rotation": rng.randrange(0, 360, 15)})
    if rng.random() < 0.4:
        decor.append({"light": [0.55, 0.75, 0.35], "position": [cx(c[0]), cz(c[1])], "range": 7, "energy": 0.8, "y": 1.0})
# praça do Gator Velho: marcas da guerra (reaproveita as peças da Passagem da Guerra)
dx, dz = praca_e[0] - 0, praca_e[1] - (-68)
for e in legacy["war_decor"]:
    e2 = dict(e)
    if "position" in e2:
        e2["position"] = [round(praca_e[0] + (e["position"][0] / 7.6) * 9.5, 1), round(praca_e[1] + ((e["position"][1] + 33) / 14.0) * 7.0, 1)]
    decor.append(e2)
decor.append({"light": [0.4, 0.7, 0.35], "position": praca_e, "range": 11, "energy": 0.9, "y": 0.6})
decor.append({"light": [0.4, 0.7, 0.35], "position": praca_w, "range": 11, "energy": 0.9, "y": 0.6})
decor.append({"light": [0.4, 0.7, 0.35], "position": secret_c, "range": 9, "energy": 0.8, "y": 0.6})
for piece, pos in (("Mushroom_Cluster", [praca_w[0] - 8.6, praca_w[1] - 7.4]), ("Mushroom_Tall", [praca_w[0] + 8.4, praca_w[1] + 7.2]),
                   ("Barrel", [praca_w[0] - 9.2, praca_w[1] + 7.6]), ("Crate_Wooden", [praca_w[0] + 9.0, praca_w[1] - 7.6])):
    decor.append({"piece": piece, "position": [round(pos[0], 1), round(pos[1], 1)], "rotation": rng.randrange(0, 360, 15)})
for piece, pos in (("Barrel", [post_c[0] + 3.2, post_c[1] - 2.6]), ("Crate_Wooden", [post_c[0] + 3.3, post_c[1] + 2.6]), ("Bucket_Wooden_1", [post_c[0] - 3.6, post_c[1] - 2.6])):
    decor.append({"piece": piece, "position": [round(pos[0], 1), round(pos[1], 1)], "rotation": rng.randrange(0, 360, 15)})

quest_spots = [[cx(c[0]), cz(c[1])] for c in ((1, 2), (5, 4), (2, 7), (5, 6))]

old = data[AREA]
area = {
    "_comment": "Esgoto de Tortuga (03-2-areas.md, seção 3), UM andar só e o dobro do labirinto antigo: grade de 7 x 9 salas de 8 m entre a entrada e o túnel do Ninho, em cinco setores "
                "de um monstro cada (1 Bueiros: sapos; 2 Canais de Lixo: sapos ácidos; 3 Galerias dos Morcegos; 4 Passagem Secreta da Guerra: jacarés; 5 Câmaras dos Cogumelos), "
                "duas praças de mini-chefe (Rei dos Sapos a oeste, Gator Velho a leste, cada um com a missão de um NPC), o posto do Caçador de Pragas, um segredo (baú e elite tóxica) "
                "e, no fundo, o Ninho da Rainha dos Ratos (sala do chefe, Tesouro Perdido da Guerra e portal da vitória). A vitória é só vencer a Rainha. "
                "Gerado por tools/assets/build_sewer_map.py (substitui build_sewer_maze.py).",
    "name_key": old.get("name_key", "ARENA_SEWERS_DRAINS"),
    "player_class": "mage",
    "map_id": "map_sewers",
    "area_level": 1,
    "final": True,
    "victory_key": "HUD_VICTORY_SEWERS",
    "victory_groups": ["sw_queen"],
    "wake_radius": 12.0,
    "alert_radius": 5.0,
    "side_quests_unlock": "sewer_entrance",
    "rooms": rooms,
    "encounters": encounters,
    "hazards": hazards,
    "entries": {"start": [0, 3], "sewer": [0, 3]},
    "props": props,
    "quest_spots": quest_spots,
    "breakables": breakables,
    "style": dict(legacy["style"], puddles=False),
    "decor": decor,
    "passive": True,
}
data[AREA] = area
for gone in ("sewers_02_canals", "sewers_03_war_passage", "sewers_04_nest"):
    data.pop(gone, None)
open(ARENAS, "w", encoding="utf-8").write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
print("área:", len(rooms), "salas,", len(encounters), "encontros,", len(props), "props,", len(decor), "decor,", len(breakables), "quebráveis,", len(hazards), "poças")
print("limites: x", min(r["center"][0] - r["size"][0] / 2 for r in rooms), max(r["center"][0] + r["size"][0] / 2 for r in rooms),
      "z", min(r["center"][1] - r["size"][1] / 2 for r in rooms), max(r["center"][1] + r["size"][1] / 2 for r in rooms))

# --- NPCs e missões dos mini-chefes -------------------------------------------------------------------------------------------------------------------
npcs = json.load(open(NPCS, encoding="utf-8"))
quests = json.load(open(QUESTS, encoding="utf-8"))
npcs["sewer_scavenger"] = {
    "_comment": "Catador do Esgoto (Esgoto, sala de entrada): pede a cabeça do Gator Velho, que domina a Passagem da Guerra, no leste do fundo.",
    "name_key": "NPC_SEWER_SCAVENGER", "color": [0.4, 0.4, 0.3],
    "dialogues": [{"when": {"quest_new": "sewer_old_gator"}, "lines": ["DLG_SEWER_GATOR_1", "DLG_SEWER_GATOR_2", "DLG_SEWER_GATOR_3"], "offer": "sewer_old_gator"},
                  {"when": {"quest_active": "sewer_old_gator"}, "lines": ["DLG_SEWER_GATOR_ACTIVE"]},
                  {"when": {}, "lines": ["DLG_SEWER_GATOR_DONE"]}],
    "body": {"sex": "male", "hair": ["Hair_Buzzed", "Hair_Beard"], "hair_color": [0.22, 0.16, 0.1], "pose": "idle", "outfit": {"body": "cloth"}}}
npcs["sewer_ratcatcher"] = {
    "_comment": "Caçador de Pragas (Esgoto, posto do lado leste): pede o fim do Rei dos Sapos, que reina na praça oeste.",
    "name_key": "NPC_SEWER_RATCATCHER", "color": [0.45, 0.35, 0.25],
    "dialogues": [{"when": {"quest_new": "sewer_frog_king"}, "lines": ["DLG_SEWER_FROG_1", "DLG_SEWER_FROG_2", "DLG_SEWER_FROG_3"], "offer": "sewer_frog_king"},
                  {"when": {"quest_active": "sewer_frog_king"}, "lines": ["DLG_SEWER_FROG_ACTIVE"]},
                  {"when": {}, "lines": ["DLG_SEWER_FROG_DONE"]}],
    "body": {"sex": "female", "hair": ["Hair_Buns"], "hair_color": [0.3, 0.2, 0.12], "pose": "idle", "outfit": {"body": "cloth"}}}
quests["sewer_old_gator"] = {"name_key": "QUEST_SEWER_OLD_GATOR", "desc_key": "QUEST_SEWER_OLD_GATOR_DESC", "type": "village", "giver": "sewer_scavenger", "area": AREA,
                             "clear": ["sw_old_gator"], "target_element": "fire", "reward": {"gold": 220, "xp": 380}}
quests["sewer_frog_king"] = {"name_key": "QUEST_SEWER_FROG_KING", "desc_key": "QUEST_SEWER_FROG_KING_DESC", "type": "village", "giver": "sewer_ratcatcher", "area": AREA,
                             "clear": ["sw_frog_king"], "target_element": "air", "reward": {"gold": 140, "xp": 220}}
if "sewer_treasure" in quests:
    quests["sewer_treasure"]["area"] = AREA
open(NPCS, "w", encoding="utf-8").write(json.dumps(npcs, indent=2, ensure_ascii=False) + "\n")
open(QUESTS, "w", encoding="utf-8").write(json.dumps(quests, indent=2, ensure_ascii=False) + "\n")

# --- textos (pt_BR, en, es): troca os blocos desta geração ---------------------------------------------------------------------------------------------
T = {
    "ARENA_SEWERS_DRAINS": ("Esgoto de Tortuga", "Tortuga Sewers", "Cloacas de Tortuga"),
    "NPC_SEWER_SCAVENGER": ("Catador do Esgoto", "Sewer Scavenger", "Rebuscador de la Alcantarilla"),
    "NPC_SEWER_RATCATCHER": ("Caçador de Pragas", "Pest Hunter", "Cazador de Plagas"),
    "QUEST_SEWER_OLD_GATOR": ("O Gator Velho", "The Old Gator", "El Caimán Viejo"),
    "QUEST_SEWER_OLD_GATOR_DESC": ("O Catador do Esgoto quer a Passagem Secreta da Guerra de volta: derrote o Gator Velho, na praça do lado leste do esgoto.",
                                   "The Sewer Scavenger wants the Secret War Passage back: defeat the Old Gator in the plaza on the east side of the sewer.",
                                   "El Rebuscador de la Alcantarilla quiere recuperar el Pasaje Secreto de la Guerra: derrota al Caimán Viejo en la plaza del lado este de la alcantarilla."),
    "DLG_SEWER_GATOR_1": ("Psiu! Eu catava tralha por aqui, até o Gator Velho tomar a Passagem da Guerra.",
                          "Psst! I used to scavenge around here, until the Old Gator took over the War Passage.",
                          "¡Psst! Yo rebuscaba por aquí, hasta que el Caimán Viejo se adueñó del Pasaje de la Guerra."),
    "DLG_SEWER_GATOR_2": ("Ele só sai da água quando alguém chega perto, e anda sempre com os jacarés menores.",
                          "He only leaves the water when someone gets close, and he always brings the smaller gators.",
                          "Solo sale del agua cuando alguien se acerca, y siempre va con los caimanes menores."),
    "DLG_SEWER_GATOR_3": ("A praça dele fica no lado leste do fundo do labirinto. Derrubem o bicho e a passagem volta a ser nossa.",
                          "His plaza is on the east side, deep in the maze. Bring him down and the passage is ours again.",
                          "Su plaza está en el lado este, al fondo del laberinto. Derríbenlo y el pasaje vuelve a ser nuestro."),
    "DLG_SEWER_GATOR_ACTIVE": ("O Gator Velho ainda manda na Passagem da Guerra. Sigam pelo leste, rumo ao fundo.",
                               "The Old Gator still rules the War Passage. Head east, toward the back.",
                               "El Caimán Viejo aún manda en el Pasaje de la Guerra. Sigan por el este, hacia el fondo."),
    "DLG_SEWER_GATOR_DONE": ("O Velho caiu? Então a Passagem é nossa. Obrigado, de coração.",
                             "The Old One fell? Then the Passage is ours. Thank you, truly.",
                             "¿El Viejo cayó? Entonces el Pasaje es nuestro. Gracias, de corazón."),
    "QUEST_SEWER_FROG_KING": ("O Rei dos Sapos", "The Frog King", "El Rey de los Sapos"),
    "QUEST_SEWER_FROG_KING_DESC": ("O Caçador de Pragas quer acabar com a praga de sapos: derrote o Rei dos Sapos, na praça do lado oeste do esgoto.",
                                   "The Pest Hunter wants to end the frog plague: defeat the Frog King in the plaza on the west side of the sewer.",
                                   "El Cazador de Plagas quiere acabar con la plaga de sapos: derrota al Rey de los Sapos en la plaza del lado oeste de la alcantarilla."),
    "DLG_SEWER_FROG_1": ("Pragas eu conheço bem. Mas esta é diferente: um sapo coroado que manda em todos os outros.",
                         "I know pests well. But this one is different: a crowned frog that commands all the others.",
                         "Conozco bien las plagas. Pero esta es distinta: un sapo coronado que manda sobre todos los demás."),
    "DLG_SEWER_FROG_2": ("O Rei dos Sapos reina numa praça do lado oeste, entre as poças, cercado de sapos.",
                         "The Frog King reigns in a plaza on the west side, among the puddles, surrounded by frogs.",
                         "El Rey de los Sapos reina en una plaza del lado oeste, entre los charcos, rodeado de sapos."),
    "DLG_SEWER_FROG_3": ("Derrubem ele e a praga acaba. Eu pago bem, não precisam nem pedir duas vezes.",
                         "Bring him down and the plague ends. I pay well, you won't need to ask twice.",
                         "Derríbenlo y la plaga se acaba. Pago bien, no hará falta pedirlo dos veces."),
    "DLG_SEWER_FROG_ACTIVE": ("O Rei dos Sapos ainda reina no oeste. Sigam o coaxar: ele está perto das poças grandes.",
                              "The Frog King still reigns in the west. Follow the croaking: he is near the big puddles.",
                              "El Rey de los Sapos aún reina en el oeste. Sigan el croar: está cerca de los charcos grandes."),
    "DLG_SEWER_FROG_DONE": ("Silêncio! Que paz. O esgoto respira de novo.", "Silence! What peace. The sewer breathes again.", "¡Silencio! Qué paz. La alcantarilla respira de nuevo."),
    "PROP_SEWER_SECTOR_1": ("Bueiros da Rua Principal", "Main Street Drains", "Desagües de la Calle Principal"),
    "SIGN_SEWER_SECTOR_1": ("Setor 1 — Bueiros da Rua Principal. Sapos Pestilentos em bandos; fique de olho nos becos.",
                            "Sector 1 — Main Street Drains. Plague frogs in packs; watch the dead ends.",
                            "Sector 1 — Desagües de la Calle Principal. Sapos pestilentes en manadas; atención a los callejones."),
    "PROP_SEWER_SECTOR_2": ("Canais de Lixo", "Garbage Canals", "Canales de Basura"),
    "SIGN_SEWER_SECTOR_2": ("Setor 2 — Canais de Lixo. Sapos Ácidos cospem de longe; a praça do Rei dos Sapos fica ao oeste.",
                            "Sector 2 — Garbage Canals. Acid toads spit from afar; the Frog King's plaza is to the west.",
                            "Sector 2 — Canales de Basura. Los sapos ácidos escupen de lejos; la plaza del Rey de los Sapos está al oeste."),
    "PROP_SEWER_SECTOR_3": ("Galerias dos Morcegos", "Bat Galleries", "Galerías de los Murciélagos"),
    "SIGN_SEWER_SECTOR_3": ("Setor 3 — Galerias dos Morcegos. Bandos de morcegos pestilentos; o posto do Caçador de Pragas fica a leste.",
                            "Sector 3 — Bat Galleries. Flocks of plague bats; the Pest Hunter's post is to the east.",
                            "Sector 3 — Galerías de los Murciélagos. Bandadas de murciélagos pestilentes; el puesto del Cazador de Plagas está al este."),
    "PROP_SEWER_SECTOR_4": ("Passagem Secreta da Guerra", "Secret War Passage", "Pasaje Secreto de la Guerra"),
    "SIGN_SEWER_SECTOR_4": ("Setor 4 — Passagem Secreta da Guerra. Jacarés à espreita na água; a praça do Gator Velho fica ao leste.",
                            "Sector 4 — Secret War Passage. Gators lurk in the water; the Old Gator's plaza is to the east.",
                            "Sector 4 — Pasaje Secreto de la Guerra. Caimanes al acecho en el agua; la plaza del Caimán Viejo está al este."),
    "PROP_SEWER_SECTOR_5": ("Câmaras dos Cogumelos", "Mushroom Chambers", "Cámaras de Hongos"),
    "SIGN_SEWER_SECTOR_5": ("Setor 5 — Câmaras dos Cogumelos. Tios-Cogumelo pesados e escorpiões; o túnel do Ninho sai pelo sul.",
                            "Sector 5 — Mushroom Chambers. Heavy Fungus Uncles and scorpions; the tunnel to the Nest leaves to the south.",
                            "Sector 5 — Cámaras de Hongos. Tíos Hongo pesados y escorpiones; el túnel al Nido sale por el sur."),
    "PROP_SEWER_NEST": ("Ninho da Rainha", "The Queen's Nest", "Nido de la Reina"),
    "SIGN_SEWER_NEST": ("Ninho da Rainha dos Ratos. O Tesouro Perdido da Guerra dorme com ela. Voltem equipados.",
                        "The Rat Queen's Nest. The War's Lost Treasure sleeps with her. Come back prepared.",
                        "Nido de la Reina de las Ratas. El Tesoro Perdido de la Guerra duerme con ella. Vuelvan preparados."),
}
for lang, i in (("pt_BR", 0), ("en", 1), ("es", 2)):
    path = "locale/%s.po" % lang
    po = open(path, encoding="utf-8").read()
    for key, trio in T.items():
        text = trio[i].replace("\\", "\\\\").replace('"', '\\"')
        block = 'msgid "%s"\nmsgstr "%s"\n' % (key, text)
        pattern = re.compile(r'msgid "%s"\nmsgstr "[^\n]*"\n' % re.escape(key))
        if pattern.search(po):
            po = pattern.sub(lambda m: block, po, count=1)
        else:
            po = po.rstrip("\n") + "\n\n" + block
    open(path, "w", encoding="utf-8").write(po)
print("textos:", len(T), "chaves em 3 idiomas")
