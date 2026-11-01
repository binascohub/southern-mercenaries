"""Gera o labirinto do Esgoto, área 1 (Bueiros da Rua Principal), em data/arenas.json.
Uma grade de 5 x 6 células de 8 m entre a sala de entrada e o fundo (o resto do mapa
fica como está); as salas vizinhas na horizontal têm 1 m de vão, as da vertical se
encostam. Determinístico (semente fixa): rode de novo para refazer o mapa.
uso: python3 tools/assets/build_sewer_maze.py"""
import json, random
from collections import deque

COLS = [-18, -9, 0, 9, 18]          # x dos centros (8 m de sala + 1 m de vão)
ROWS = [-10, -18, -26, -34, -42, -50]  # z dos centros (as salas se encostam)
START = (2, 0)                      # coluna 2, linha 0 (de frente para a entrada)
END = (2, 5)                        # embaixo, de frente para o fundo
SECRET_CELL = (4, 2)                # a ponta leste leva ao segredo
rng = random.Random(7)

# Labirinto perfeito por árvore crescente (mistura "último" e "qualquer" célula: ramifica
# bastante, com muitos becos) + alguns laços.
open_edges = set()
seen = {START}
active = [START]
def neighbors(c):
    x, z = c
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (x + dx, z + dz)
        if 0 <= n[0] < len(COLS) and 0 <= n[1] < len(ROWS):
            yield n
while active:
    index = rng.randrange(len(active)) if rng.random() < 0.55 else len(active) - 1
    cur = active[index]
    options = [n for n in neighbors(cur) if n not in seen]
    if not options:
        active.pop(index)
        continue
    nxt = rng.choice(options)
    open_edges.add(frozenset((cur, nxt)))
    seen.add(nxt)
    active.append(nxt)
walls = sorted({tuple(sorted((c, n))) for c in seen for n in neighbors(c) if frozenset((c, n)) not in open_edges})
rng.shuffle(walls)
for a, b in walls[:4]:  # laços: não é só um caminho
    open_edges.add(frozenset((a, b)))

def doors_of(c):
    out = []
    for n in neighbors(c):
        if frozenset((c, n)) in open_edges:
            out.append({(1, 0): "east", (-1, 0): "west", (0, 1): "north", (0, -1): "south"}[(n[0] - c[0], n[1] - c[1])])
    return out

# Profundidade (passos desde a entrada) para espalhar os encontros.
depth = {START: 0}
queue = deque([START])
while queue:
    cur = queue.popleft()
    for n in neighbors(cur):
        if frozenset((cur, n)) in open_edges and n not in depth:
            depth[n] = depth[cur] + 1
            queue.append(n)

def center(c):
    return [COLS[c[0]], ROWS[c[1]]]

data = json.load(open("data/arenas.json"))
area = data["sewers_01_drains"]

rooms = [r for r in area["rooms"] if r["id"] in ("entry", "outfall")]
for r in rooms:
    if r["id"] == "outfall":
        r["doors"] = ["south"]  # a porta para o labirinto
cells = []
for c in sorted(depth, key=lambda k: depth[k]):
    doors = doors_of(c)
    if c == START:
        doors.append("south")  # para a sala de entrada (z maior = sul)
    if c == END:
        doors.append("north")  # para o fundo (z menor = norte)
    if c == SECRET_CELL:
        doors.append("east")
    room = {"id": "maze_%d_%d" % c, "center": center(c), "size": [8, 8], "doors": doors}
    if depth[c] % 4 == 0 and c != START:
        room["torch"] = True
    cells.append(room)
rooms = rooms[:1] + cells + [
    {"id": "secret_pipe", "center": [26, ROWS[SECRET_CELL[1]]], "size": [6, 5], "doors": ["west", "east"]},
    {"id": "secret", "center": [35, ROWS[SECRET_CELL[1]]], "size": [10, 10], "doors": ["west"]}] + rooms[1:]
area["rooms"] = rooms

# Encontros: do mais perto ao mais fundo; a Ratazana num beco, longe da entrada.
order = [c for c in sorted(depth, key=lambda k: depth[k]) if c not in (START, END)]
def at(index_fraction):
    return order[min(int(len(order) * index_fraction), len(order) - 1)]
dead_ends = [c for c in order if len(doors_of(c)) == 1 and c != SECRET_CELL]
dead_ends.sort(key=lambda k: -depth[k])
groups = [
    ("s1_lone", at(0.08), [("plague_rat", 1)]),
    ("s1_trio", at(0.2), [("plague_rat", 3)]),
    ("m_pair_a", at(0.35), [("plague_rat", 2)]),
    ("m_pair_b", at(0.5), [("plague_rat", 2)]),
    ("m_trio_b", at(0.65), [("plague_rat", 3)]),
    ("m_mutant", dead_ends[1] if len(dead_ends) > 1 else at(0.8), [("mutant_rat", 1)]),
    ("m_pair_c", at(0.9), [("plague_rat", 2)]),
]
used = set()
encounters = []
for gid, cell, monsters in groups:
    while cell in used and order:  # uma por célula
        cell = order[(order.index(cell) + 1) % len(order)]
    used.add(cell)
    x, z = center(cell)
    encounters.append({"id": gid, "position": [x, z], "monsters": [{"monster": m, "count": n} for m, n in monsters]})
keep = [e for e in area["encounters"] if e["id"] in ("s1_swarm", "s1_mutant")]
secret = {"id": "s1_secret", "position": [37, ROWS[SECRET_CELL[1]]], "monsters": [
    {"monster": "plague_rat", "count": 1, "rank": "elite", "modifier": "toxic"}, {"monster": "plague_rat", "count": 1}]}
area["encounters"] = encounters + keep + [secret]

# Poças: a do meio do labirinto (que o teste usa) e as do fundo ficam; mais três nas células.
hazards = [{"position": [0, -43], "radius": 1.6}, {"position": [1, -49], "radius": 1.3}, {"position": [5, -61], "radius": 2.0}]
free = [c for c in order if c not in used and c != (2, 4)]
rng.shuffle(free)
for c in free[:3]:
    x, z = center(c)
    hazards.append({"position": [x + rng.choice((-2, 2)), z + rng.choice((-2, 2))], "radius": 1.5})
area["hazards"] = hazards

# Objetos: os da entrada e do fundo ficam; os do labirinto são sorteados pelas células.
def in_maze(pos):
    return -54 < pos[1] < -6
area["breakables"] = [b for b in area["breakables"] if not in_maze(b["position"])]
kinds = ["barrel", "crate", "pot", "pot", "barrel", "crate", "pot"]
number = {"barrel": 1, "crate": 1, "pot": 1}
for i, c in enumerate(rng.sample(order, 14)):
    kind = kinds[i % len(kinds)]
    x, z = center(c)
    area["breakables"].append({"id": "m%s%d" % (kind[0], i), "monster": kind,
        "position": [x + rng.choice((-2.8, 2.8)), z + rng.choice((-2.8, 2.8))]})
area["decor"] = [d for d in area["decor"] if "position" in d and not in_maze(d["position"])]
cell_pieces = ["Barrel", "Crate_Wooden", "Cage_Small", "Bucket_Wooden_1", "Rope_1", "Crate_Metal", "Mushroom_Cluster", "Mushroom_Tall", "Shield_Wooden", "Barrel"]
for i, c in enumerate(rng.sample(order, 10)):
    x, z = center(c)
    area["decor"].append({"piece": cell_pieces[i], "position": [x + rng.choice((-3.0, 3.0)), z + rng.choice((-3.0, 3.0))], "rotation": rng.randrange(0, 360, 15)})
for c in rng.sample(order, 7):
    x, z = center(c)
    area["decor"].append({"light": [0.55, 0.75, 0.35], "position": [x, z], "range": 7, "energy": 0.8, "y": 1.0})

# Baús: o secreto fica na câmara leste; mais dois nos becos mais fundos.
props = [p for p in area["props"] if p["id"] != "secret_chest" and not p["id"].startswith("maze_chest")]
props.append({"id": "secret_chest", "kind": "chest", "position": [38, ROWS[SECRET_CELL[1]] - 2], "secret": True, "loot": "chest"})
for i, c in enumerate(dead_ends[:2]):
    x, z = center(c)
    props.append({"id": "maze_chest_%d" % (i + 1), "kind": "chest", "position": [x, z - 2.5], "loot": "chest"})
area["props"] = props
area["quest_spots"] = [[0, -26], [-9, -34], [0, -58], [6, -58]]
area["_comment"] = ("Esgoto, área 1 (03-2-areas.md, seção 3; 14-tutorial.md, seção 3): Bueiros da Rua Principal. "
    "Um LABIRINTO de 5 x 6 salas de 8 m entre a entrada e o fundo (gerado por tools/assets/build_sewer_maze.py), com becos, "
    "laços, baús nos becos mais fundos, grupos de ratos espalhados e poças de lodo. Segredo: a sala do leste, a partir da "
    "ponta leste do labirinto, leva a uma câmara com baú. Estreito: o Cavaleiro desmonta.")
open("data/arenas.json", "w").write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

# Desenho do mapa no terminal.
print("depth max", max(depth.values()), "cells", len(depth), "dead ends", len(dead_ends))
for r in range(len(ROWS)):
    line = ""
    for c in range(len(COLS)):
        line += "S" if (c, r) == START else "E" if (c, r) == END else "#"
        line += "-" if frozenset(((c, r), (c + 1, r))) in open_edges else " "
    print(line)
    line = ""
    for c in range(len(COLS)):
        line += "|" if frozenset(((c, r), (c, r + 1))) in open_edges else " "
        line += " "
    print(line)
