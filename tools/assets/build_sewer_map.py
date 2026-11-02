"""Gera o Esgoto de Tortuga como UM mapa de um andar só (`sewers_01_drains`), no lugar das 4 áreas antigas (Bueiros, Canais, Passagem da Guerra, Ninho).
Substitui tools/assets/build_sewer_maze.py. Determinístico (semente fixa): rode de novo para refazer o mapa (os dados antigos que ele reaproveita estão em
tools/assets/sewer_legacy.json). Também cria os 2 NPCs das missões dos mini-chefes, as 2 missões e os textos (pt/en/es), e apaga as áreas 2 a 4.

O mapa (dobro do labirinto antigo): uma grade de 7 x 9 salas de 8 m (1 m de vão na horizontal, as de cima e de baixo se encostam) entre a sala de entrada e o túnel do
fundo, em 5 SETORES de um monstro cada, mais salas especiais coladas nas bordas (cada parede de sala só aceita uma porta):
  1 Bueiros da Rua Principal   (linhas 0-2)                  Sapos Pestilentos (+ Ratazana nos becos e uma ninhada)
  2 Canais de Lixo             (linhas do meio, lado oeste)      Sapos Ácidos nas poças         -> praça oeste: REI DOS SAPOS (mini-chefe)
  3 Galerias dos Morcegos      (linhas 3-5, colunas 4-6)      Morcegos Pestilentos           -> segredo a leste (baú, elite tóxica); posto do Caçador de Pragas (NPC)
  4 Passagem Secreta da Guerra (linhas 6-8, colunas 4-6)      Jacarés escondidos na água     -> praça leste: GATOR VELHO (mini-chefe)
  5 Câmaras dos Cogumelos      (linhas 6-8, colunas 0-3)      Tios-Cogumelo e Escorpiões
  fundo: túnel + NINHO DA RAINHA (sala do chefe do mapa, com o Tesouro Perdido da Guerra e o portal da vitória).
O Catador do Esgoto (o Homem-Aranha, que dança; missão do Empalado, agora o Monstro de Tábuas) fica na sala de entrada; Itachi (missão do Carniceiro Chifrudo), no posto do lado leste: os dois, longe dos chefes.
A vitória do mapa é só vencer a Rainha (`victory_groups`): não precisa limpar o resto.
uso: python3 -I tools/assets/build_sewer_map.py   (na raiz do projeto)"""
import json, math, random, re
from collections import deque

ARENAS, QUESTS, NPCS, LEGACY = "data/arenas.json", "data/quests.json", "data/npcs.json", "tools/assets/sewer_legacy.json"
AREA = "sewers_01_drains"
rng = random.Random(21)

NC, NR = 11, 13                     # colunas x linhas de salas (maior que a grade 7 x 9 antiga: o esgoto é UM andar só, sem passagens para outros mapas)
RS = 12                             # lado da sala do labirinto, em metros (eram 8)
HALF, GAP = RS // 2, 1
PX, PZ = RS + GAP, RS               # passo entre os centros (a sala + 1 m de vão na horizontal; as de baixo se encostam)
X0, Z0 = -(NC // 2) * PX, -(6 + HALF)   # centro da coluna 0 e da linha 0 (a coluna do meio fica em x = 0; a linha 0 encosta na sala de entrada, em z = -6)
START, END = (NC // 2, 0), (NC // 2, NR - 1)


def cx(c): return X0 + PX * c
def cz(r): return Z0 - PZ * r


def sector(c, r):
    if r < NR // 3:
        return 1
    if r < 2 * NR // 3:
        return 2 if c <= NC // 2 else 3
    return 5 if c <= NC // 2 else 4


# Salas especiais coladas nas bordas: (célula, lado) -> sala
ATTACH_W = (0, NR // 2)    # praça oeste (Empalado), a leste da qual fica a célula (0,4)
ATTACH_E = (NC - 1, NR - 1)    # praça leste (Carniceiro Chifrudo)
POST = (NC - 1, 1)        # posto do Caçador de Pragas
SECRET = (NC - 1, NR // 3 + 1)      # passagem do segredo

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

# Sala da Ossael, no meio do mapa (a célula a oeste do altar): abre as quatro passagens (depois da profundidade, para não mexer nos sorteios do resto) e fica com tocha.
ANGEL_CELL = (NC // 2 - 2, NR // 2)
for _n in neighbors(ANGEL_CELL):
    open_edges.add(frozenset((ANGEL_CELL, _n)))
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
    room = {"id": "maze_%d_%d" % c, "center": [cx(c[0]), cz(c[1])], "size": [RS, RS], "doors": doors, "narrow": True}
    if (depth[c] % 4 == 0 and c != START) or c == ANGEL_CELL:
        room["torch"] = True
    rooms.append(room)

# praças e salas ligadas às bordas (centro = célula + 4 de meia sala + 1 de vão + meia largura da sala nova)
PRACA = (22, 18)
praca_w = [cx(ATTACH_W[0]) - (HALF + GAP) - PRACA[0] / 2, cz(ATTACH_W[1])]
praca_e = [cx(ATTACH_E[0]) + (HALF + GAP) + PRACA[0] / 2, cz(ATTACH_E[1])]
post_c = [cx(POST[0]) + (HALF + GAP) + 5, cz(POST[1])]
pipe_c = [cx(SECRET[0]) + (HALF + GAP) + 3, cz(SECRET[1])]
secret_c = [pipe_c[0] + 3 + 0.5 + 0.5 + 5, cz(SECRET[1])]
tunnel_z = cz(END[1]) - HALF - 7
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
# O Empalado (mini-chefe 1) não nasce no mapa: o altar no centro do esgoto (sala maze_3_6) o invoca ao ser tocado ('summon' no objeto).
# Save point (cristal + checkpoint "altar"): na frente da entrada da sala do altar, do lado da sala por onde o labirinto chega a ela (a de menor profundidade).
ALTAR_CELL = (NC // 2, NR // 2)
_parent = min((n for n in neighbors(ALTAR_CELL) if frozenset((ALTAR_CELL, n)) in open_edges), key=lambda n: depth[n])
_dx, _dz = _parent[0] - ALTAR_CELL[0], -(_parent[1] - ALTAR_CELL[1])  # linha maior = z menor
_door = HALF + GAP if _dx else HALF  # salas lado a lado têm 1 m de vão; as de cima e de baixo se encostam
ALTAR_ENTRY = [round(cx(ALTAR_CELL[0]) + _dx * (_door + 2.5), 1), round(cz(ALTAR_CELL[1]) + _dz * (_door + 2.5), 1)]
FROG_ALTAR = {"id": "sewer_frog_altar", "kind": "npc", "npc": "sewer_frog_altar", "kit": "Altar_Summon", "solid": [2.2, 2.0], "rotation": 0, "position": [0, cz(NR // 2)],
              "needs_key": "book_frog_altar", "summon": {"id": "sw_frog_king", "position": [0, cz(NR // 2) + 3.5], "level": 1, "toast": "TOAST_FROG_ALTAR_AWAKENS",
                         "monsters": [{"monster": "frog_king", "count": 1}]},
              # O Carniceiro Chifrudo não espera mais na praça leste: o Grimório das Brasas (o Azazel o entrega ao abrir a missão) lido neste mesmo altar o invoca (a 3ª fala do altar é a da leitura).
              "extra_summons": [{"needs_key": "book_gator_altar", "dialogue": 2,
                                 "summon": {"id": "sw_old_gator", "position": [0, cz(NR // 2) + 3.5], "level": 2, "toast": "TOAST_GATOR_ALTAR_AWAKENS", "spread": 3.4,
                                            "monsters": [{"monster": "old_gator", "count": 1}, {"monster": "shadow_spirit", "count": 2}]}}]}
sec = dict(legacy["secret_elite"])
sec["id"] = "sw_secret"
sec["position"] = [secret_c[0] + 1.5, secret_c[1]]
sec["level"] = 1
encounters.append(sec)
encounters.append({"id": "sw_nest_guard", "position": [0, tunnel_z], "level": 2, "monsters": [{"monster": "plague_frog", "count": 3}]})
encounters.append({"id": "sw_queen", "position": [0, nest_z + (-42 - -36)], "level": 2, "monsters": [{"monster": "demon_rat_queen", "count": 1}]})

# Troll Mauler (piacenti, CC BY 3.0): o monstro do Setor 1 (Bueiros), um por terço do setor, em células sem sorteio (não mexe nos outros sorteios do mapa).
troll_cells = sorted(by_sector[1], key=lambda c: depth[c])
for i, q in enumerate((0.15, 0.3, 0.45, 0.6, 0.75, 0.9)):
    c = troll_cells[min(int(len(troll_cells) * q), len(troll_cells) - 1)]
    encounters.append({"id": "sw1_troll_%d" % (i + 1), "position": [cx(c[0]), cz(c[1])], "level": 1, "monsters": [{"monster": "troll_mauler", "count": 1}]})

# Mutante (thecubber, CC-BY-SA 3.0): o monstro do Setor 5 (Câmaras dos Cogumelos, canto inferior esquerdo), em bandos de 1 a 2 espalhados pelas células do setor, sem sorteio.
mutant_cells = sorted(by_sector[5], key=lambda c: depth[c])
for i, q in enumerate((0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95)):
    c = mutant_cells[min(int(len(mutant_cells) * q), len(mutant_cells) - 1)]
    encounters.append({"id": "sw5_mutant_%d" % (i + 1), "position": [cx(c[0]), cz(c[1])], "level": 2, "monsters": [{"monster": "mutant", "count": 1 + i % 2}]})

# Monstro Bárbaro (barbarian-monster.glb do autor): o monstro do lado esquerdo do meio do mapa (Setor 2, colunas do oeste, linhas do meio do setor); dois, sem sorteio.
west_middle = sorted([c for c in by_sector[2] if c[0] <= NC // 4], key=lambda c: (abs(c[1] - (NR / 2.0 - 0.5)), c[0]))
for i, c in enumerate(west_middle[:5]):
    encounters.append({"id": "sw2_barbarian_%d" % (i + 1), "position": [cx(c[0]), cz(c[1])], "level": 1, "monsters": [{"monster": "barbarian_monster", "count": 1}]})

# Guerreiro Cogumelo (champ-warrior.glb do autor): o monstro do canto superior esquerdo do mapa (Setor 1, as duas células mais perto do canto), sem sorteio.
corner_cells = sorted(by_sector[1], key=lambda c: (c[0] + c[1], c[0]))
for i, c in enumerate(corner_cells[:2]):
    encounters.append({"id": "sw1_champ_%d" % (i + 1), "position": [cx(c[0]), cz(c[1])], "level": 1, "monsters": [{"monster": "champ_warrior", "count": 1}]})

# Espírito Sombrio (shadow-spirit.glb do autor): o monstro do canto superior direito (Setor 1, colunas do lado leste), em bandos de 1 a 2, sem sorteio.
spirit_cells = sorted((c for c in by_sector[1] if c[0] >= NC - 4), key=lambda c: depth[c])
for i, q in enumerate((0.1, 0.4, 0.7, 0.95)):
    c = spirit_cells[min(int(len(spirit_cells) * q), len(spirit_cells) - 1)]
    encounters.append({"id": "sw1_spirit_%d" % (i + 1), "position": [cx(c[0]), cz(c[1])], "level": 1, "monsters": [{"monster": "shadow_spirit", "count": 1 + i % 2}]})

# Demônio Doze (demon-twelve.glb do autor): o monstro do meio do lado direito (Setor 3, células do leste), em bandos de 1 a 2, sem sorteio.
twelve_cells = sorted((c for c in by_sector[3] if c[0] >= NC - 4), key=lambda c: depth[c])
for i, q in enumerate((0.15, 0.5, 0.85)):
    c = twelve_cells[min(int(len(twelve_cells) * q), len(twelve_cells) - 1)]
    encounters.append({"id": "sw3_twelve_%d" % (i + 1), "position": [cx(c[0]), cz(c[1])], "level": 1, "monsters": [{"monster": "demon_twelve", "count": 1 + i % 2}]})

# Baú Monstro (chest_monster.glb do autor): agressivo, espalhado por todo o mapa — um a cada ~10 células, em células sorteadas por posição (sem usar o rng do resto), longe de encontros, do altar e da sala da Ossael.
_mimic_cells = [c for c in sorted(depth) if c not in special_cells and c not in (ALTAR_CELL, ANGEL_CELL) and depth[c] > 1
                and all(math.hypot(cx(c[0]) - e["position"][0], cz(c[1]) - e["position"][1]) > 9.0 for e in encounters)]
_mimic_cells = [c for i, c in enumerate(sorted(_mimic_cells, key=lambda c: (c[0] * 7 + c[1] * 13) % 11)) if i % 4 == 0][:14]
for i, c in enumerate(sorted(_mimic_cells, key=lambda c: (c[1], c[0]))):
    encounters.append({"id": "sw_mimic_%02d" % (i + 1), "position": [cx(c[0]), cz(c[1])], "level": 1, "monsters": [{"monster": "chest_mimic", "count": 1}]})

# Só os chefes do esgoto (Empalado, Carniceiro Chifrudo e a Rainha), o Troll Mauler do Setor 1, o Monstro Bárbaro do Setor 2 e o Mutante do Setor 5 ficam; nenhum outro monstro revida.
SEWER_BOSSES = ("frog_king", "old_gator", "demon_rat_queen", "troll_mauler", "barbarian_monster", "champ_warrior", "mutant", "shadow_spirit", "demon_twelve", "chest_mimic")
encounters = [dict(e, monsters=[m for m in e["monsters"] if m["monster"] in SEWER_BOSSES]) for e in encounters]
encounters = [e for e in encounters if e["monsters"]]

# --- props -------------------------------------------------------------------------------------------------------------------------------------------
# Ossael (o anjo, NPC do Catador): na sala aberta no meio do mapa (ANGEL_CELL).
ANGEL_AT = [round(cx(ANGEL_CELL[0]), 1), round(cz(ANGEL_CELL[1]) + 1.5, 1)]
props = [{"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-4, 3], "to": "tortuga", "entry": "sewer", "expedition_end": True},
         {"id": "sewer_scavenger", "kind": "npc", "npc": "sewer_scavenger", "position": ANGEL_AT, "rotation": 0},
         {"id": "sewer_ratcatcher", "kind": "npc", "npc": "sewer_ratcatcher", "position": [post_c[0] + 1.5, post_c[1]], "rotation": 270},
         {"id": "secret_chest", "kind": "chest", "position": [secret_c[0] + 1, secret_c[1] - 2.0], "secret": True, "loot": "chest"}]
# baús nos becos mais fundos de cada setor (2 a 5)
for s in (2, 3, 4, 5):
    cand = sorted((c for c in dead_ends if sector(*c) == s and c not in used), key=lambda k: -depth[k])
    if cand:
        c = cand[0]
        used.add(c)
        props.append({"id": "maze_chest_%d" % s, "kind": "chest", "position": [cx(c[0]), cz(c[1]) - 2.5], "loot": "chest"})
# água: poças nos canais (sapos ácidos), jacarés na Passagem da Guerra, praça do Carniceiro Chifrudo e ninho
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
# Sem o Tesouro Perdido da Guerra (pedido do autor): o baú do Ninho não existe mais (a chave da Rainha também não cai).
props = [p for p in props if p.get("id") != "war_treasure"]
# Sem baús no mapa (pedido do autor): o loot vem só do baú que os chefes e mini-chefes deixam ao morrer.
props = [p for p in props if p["kind"] != "chest"]
# Portão do corredor logo abaixo do Ninho da Rainha: só cai com as duas chaves dos mini-chefes (Espadas: Carniceiro Chifrudo; Copas: Empalado / Monstro de Tábuas).
props.append({"id": "nest_gate", "kind": "gate", "name_key": "PROP_NEST_GATE", "position": [0, tunnel_z - 1.0], "rotation": 0, "scale": 2.4, "block": 5.0, "count": 1,
              "needs_keys": ["sewer_key_spades", "sewer_key_hearts"]})
# Piso todo de pedra: sem água (nem o lago do Carniceiro Chifrudo).
props = [p for p in props if p["kind"] != "water"]
# brasão da Passagem da Guerra (o Arqueiro reconhece) na entrada do setor 4
sector_entry = {s: min((c for c in depth if sector(*c) == s), key=lambda c: depth[c]) for s in range(1, 6)}  # a célula mais rasa de cada setor
crest_cell = sector_entry[4]
crest = dict(legacy["war_crest"])
crest["position"] = [cx(crest_cell[0]) - 2.5, cz(crest_cell[1]) - 3.2]
props.append(crest)
# cartazes dos setores
SIGN_AT = sector_entry
for s, c in SIGN_AT.items():
    props.append({"id": "sign_sector_%d" % s, "kind": "sign", "name_key": "PROP_SEWER_SECTOR_%d" % s, "position": [cx(c[0]) + 2.8, cz(c[1]) + 2.6],
                  "text_key": "SIGN_SEWER_SECTOR_%d" % s})
props.append({"id": "sign_nest", "kind": "sign", "name_key": "PROP_SEWER_NEST", "position": [2.8, tunnel_z - 5.0], "text_key": "SIGN_SEWER_NEST"})

props.append(FROG_ALTAR)

# --- poças de lodo, objetos quebráveis e decoração -------------------------------------------------------------------------------------------------
hazards = []
quotas = {1: 4, 2: 6, 3: 4, 4: 6, 5: 9}  # poças verdes de lodo por setor (dobradas a pedido do autor)
for s, n in quotas.items():
    cells = [c for c in depth if sector(*c) == s and c not in special_cells]
    rng.shuffle(cells)
    for c in cells[:n]:
        hazards.append({"position": [cx(c[0]) + rng.choice((-3, 3)), cz(c[1]) + rng.choice((-3, 3))], "radius": round(rng.choice((1.3, 1.5, 1.8)), 1)})
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
# Tesouro Antigo (trasure.rar do autor; tools/assets/build_ancient_treasure.py): montes de moedas com baú aberto espalhados pelo chão da sala do chefe, o maior no fundo (só enfeite, sem baú para abrir).
for x, z, rot, sc in ((0, -206.0, 0, 1.4), (-11.0, -203.0, 20, 1.0), (11.0, -202.0, -25, 1.1), (-13.5, -191.0, 90, 0.9), (13.5, -192.0, 80, 1.0),
                       (-8.5, -182.0, 10, 0.7), (8.5, -181.5, -15, 0.75), (-5.0, -196.0, 35, 0.5), (6.0, -210.0 + 4.5, 160, 0.6)):
    decor.append({"piece": "Ancient_Treasure", "position": [x, z], "rotation": rot, "scale": sc})
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
        decor.append({"piece": rng.choice(SECTOR_PIECES[s]), "position": [cx(c[0]) + rng.choice((-(HALF - 1.0), HALF - 1.0)), cz(c[1]) + rng.choice((-(HALF - 1.0), HALF - 1.0))],
                      "rotation": rng.randrange(0, 360, 15)})
    if rng.random() < 0.4:
        decor.append({"light": [0.55, 0.75, 0.35], "position": [cx(c[0]), cz(c[1])], "range": 9, "energy": 0.8, "y": 1.0})
# praça do Carniceiro Chifrudo: marcas da guerra (reaproveita as peças da Passagem da Guerra)
dx, dz = praca_e[0] - 0, praca_e[1] - (-68)
for e in legacy["war_decor"]:
    e2 = dict(e)
    if "position" in e2:
        e2["position"] = [round(praca_e[0] + (e["position"][0] / 7.6) * 9.5, 1), round(praca_e[1] + ((e["position"][1] + 33) / 14.0) * 7.0, 1)]
    decor.append(e2)
decor.append({"light": [0.4, 0.7, 0.35], "position": praca_e, "range": 11, "energy": 0.9, "y": 0.6})
decor.append({"light": [0.4, 0.7, 0.35], "position": praca_w, "range": 11, "energy": 0.9, "y": 0.6})
decor.append({"light": [0.4, 0.7, 0.35], "position": secret_c, "range": 9, "energy": 0.8, "y": 0.6})
decor.append({"light": [0.4, 0.7, 0.35], "position": FROG_ALTAR["position"], "range": 8, "energy": 1.1, "y": 1.2})
for piece, pos in (("Mushroom_Cluster", [praca_w[0] - 8.6, praca_w[1] - 7.4]), ("Mushroom_Tall", [praca_w[0] + 8.4, praca_w[1] + 7.2]),
                   ("Barrel", [praca_w[0] - 9.2, praca_w[1] + 7.6]), ("Crate_Wooden", [praca_w[0] + 9.0, praca_w[1] - 7.6])):
    decor.append({"piece": piece, "position": [round(pos[0], 1), round(pos[1], 1)], "rotation": rng.randrange(0, 360, 15)})
for piece, pos in (("Barrel", [post_c[0] + 3.2, post_c[1] - 2.6]), ("Crate_Wooden", [post_c[0] + 3.3, post_c[1] + 2.6]), ("Bucket_Wooden_1", [post_c[0] - 3.6, post_c[1] - 2.6])):
    decor.append({"piece": piece, "position": [round(pos[0], 1), round(pos[1], 1)], "rotation": rng.randrange(0, 360, 15)})

quest_spots = [[cx(c[0]), cz(c[1])] for c in ((1, 2), (5, 4), (2, 7), (5, 6))]

# Sem as luzes de cenário coloridas (pedido do autor): ficam só as tochas das salas (room.torch) e o brilho do altar e dos monstros.
decor = [e for e in decor if "light" not in e]
old = data[AREA]
# Save point (cristal): no canto superior direito do mapa (a célula mais ao norte e depois mais a leste, longe de encontros e das salas especiais).
_save_cells = [c for c in depth if c not in special_cells and c != ALTAR_CELL
               and all(math.hypot(cx(c[0]) - e["position"][0], cz(c[1]) - e["position"][1]) > 7.0 for e in encounters)]
_save_cell = min(_save_cells, key=lambda c: (c[1], -c[0]))
SAVE_ENTRY = [round(cx(_save_cell[0]) - 2.0, 1), round(cz(_save_cell[1]), 1)]  # o cristal nasce 2,2 m à direita desta entrada
print("save point (canto superior direito): célula", _save_cell, "entrada", SAVE_ENTRY)
area = {
    "_comment": "Esgoto de Tortuga (03-2-areas.md, seção 3), UM andar só e o dobro do labirinto antigo: grade de 7 x 9 salas de 8 m entre a entrada e o túnel do Ninho, em cinco setores "
                "de um monstro cada (1 Bueiros: sapos; 2 Canais de Lixo; 3 Galerias dos Morcegos; 4 Passagem Secreta da Guerra: jacarés; 5 Câmaras dos Cogumelos), "
                "duas praças de mini-chefe (Empalado a oeste, Carniceiro Chifrudo a leste, cada um com a missão de um NPC), o posto do Caçador de Pragas, um segredo (baú e elite tóxica) "
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
    "entries": {"start": [0, 3], "sewer": [0, 3], "altar": ALTAR_ENTRY, "savepoint": SAVE_ENTRY}, "save_point": "savepoint",  # o cristal fica no canto superior direito do mapa
    "props": props,
    "quest_spots": quest_spots,
    "breakables": breakables,
    "style": dict(legacy["style"], puddles=False, bats=True, trash_density=0.6, trash_no_bottles=True, wood_tone=[0.192, 0.145, 0.11]),  # madeira na cor da mesa redonda da Taverna
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
    "_comment": "Ossael, o Anjo Caveira (angel.glb em NpcModel: esqueleto de asas negras e auréola de espinhos; sala aberta no meio do mapa): guardião dos afogados do esgoto; veio buscar a Garrafa do Tormento Eterno, que o Empalado lhe tomou. Dá a missão (entrega o Livro do Altar, as preces dos afogados, que lido no altar do centro desperta o Empalado); ao receber a garrafa que ele solta, entrega a chave de copas.",
    "name_key": "NPC_SEWER_SCAVENGER", "color": [0.4, 0.4, 0.3],
    "dialogues": [{"when": {"quest_new": "sewer_frog_king"}, "lines": ["DLG_SEWER_FROG_1", "DLG_SEWER_FROG_2", "DLG_SEWER_FROG_3"], "offer": "sewer_frog_king"},
                  {"when": {"quest_active": "sewer_frog_king"}, "lines": ["DLG_SEWER_FROG_ACTIVE"], "service": "turn_in"},
                  {"when": {}, "lines": ["DLG_SEWER_FROG_DONE"]}],
    "body": {"sex": "male", "hair": ["Hair_Buzzed", "Hair_Beard"], "hair_color": [0.22, 0.16, 0.1], "pose": "idle", "outfit": {"body": "cloth"}}}
npcs["sewer_ratcatcher"] = {
    "_comment": "Azazel, o Anjo Flamejante (posto do lado leste; modelo angel_2.glb em NpcModel; antes Itachi): dá a missão da Garrafa das Almas Condenadas: Lúcifer o mandou buscá-la e o Carniceiro Chifrudo, demônio açougueiro, a roubou. O grimório que ele entrega, lido no altar do centro do mapa, chama o demônio; a garrafa que ele solta vale a chave de espadas.",
    "name_key": "NPC_SEWER_RATCATCHER", "color": [0.45, 0.35, 0.25],
    "dialogues": [{"when": {"quest_new": "sewer_old_gator"}, "lines": ["DLG_SEWER_GATOR_1", "DLG_SEWER_GATOR_2", "DLG_SEWER_GATOR_3"], "offer": "sewer_old_gator"},
                  {"when": {"quest_active": "sewer_old_gator"}, "lines": ["DLG_SEWER_GATOR_ACTIVE"], "service": "turn_in"},
                  {"when": {}, "lines": ["DLG_SEWER_GATOR_DONE"]}],
    "body": {"sex": "male", "hair": ["Hair_Long"], "hair_color": [0.03, 0.02, 0.03], "pose": "idle", "outfit": {"body": "cloth"}}}
npcs.pop("sewer_gator_altar", None)  # o Gator Velho é invocado no mesmo altar do Empalado (extra_summons): não há altar próprio
npcs["sewer_frog_altar"] = {
    "_comment": "Altar do Empalado (centro do mapa do Esgoto, sala maze_3_6): tocá-lo desperta o Empalado, o mini-chefe 1 ('summon' no objeto em arenas.json); a missão do Catador termina quando ele cai.",
    "name_key": "NPC_SEWER_FROG_ALTAR", "color": [0.4, 0.5, 0.35], "dialogues": [{"when": {}, "lines": ["DLG_FROG_ALTAR_1", "DLG_FROG_ALTAR_2"]}, {"when": {}, "lines": ["DLG_FROG_ALTAR_LOCKED"]},
                                                                                       {"when": {}, "lines": ["DLG_GATOR_ALTAR_2"]}]}  # 2ª fala: trancado (sem livro); 3ª: a leitura do Grimório das Brasas (Carniceiro Chifrudo); só abrem pelo Town.interact
quests["sewer_old_gator"] = {"name_key": "QUEST_SEWER_OLD_GATOR", "desc_key": "QUEST_SEWER_OLD_GATOR_DESC", "type": "village", "giver": "sewer_ratcatcher", "area": AREA,
                             "grants_key": "book_gator_altar", "grants_item": "gator_book", "grants_toast": "TOAST_GATOR_BOOK_RECEIVED", "item": "souls_bottle", "bestiary": ["old_gator"], "gives_key": "sewer_key_spades", "target_element": "fire", "reward": {"gold": 220, "xp": 380}}  # o Carniceiro Chifrudo solta a garrafa; o Azazel entrega a chave de espadas ao receber
quests["sewer_frog_king"] = {"name_key": "QUEST_SEWER_FROG_KING", "desc_key": "QUEST_SEWER_FROG_KING_DESC", "type": "village", "giver": "sewer_scavenger", "area": AREA,
                             "item": "torment_bottle", "bestiary": ["frog_king"], "grants_key": "book_frog_altar", "grants_item": "altar_book", "gives_key": "sewer_key_hearts", "target_element": "earth", "reward": {"gold": 140, "xp": 220}}
if "sewer_treasure" in quests:
    quests["sewer_treasure"]["area"] = AREA
open(NPCS, "w", encoding="utf-8").write(json.dumps(npcs, indent=2, ensure_ascii=False) + "\n")
open(QUESTS, "w", encoding="utf-8").write(json.dumps(quests, indent=2, ensure_ascii=False) + "\n")

# --- textos (pt_BR, en, es): troca os blocos desta geração ---------------------------------------------------------------------------------------------
T = {
    "ARENA_SEWERS_DRAINS": ("Esgoto de Tortuga", "Tortuga Sewers", "Cloacas de Tortuga"),
    "NPC_SEWER_SCAVENGER": ("Catador do Esgoto", "Sewer Scavenger", "Rebuscador de la Alcantarilla"),
    "NPC_SEWER_RATCATCHER": ("Azazel, o Anjo Flamejante", "Azazel, the Flaming Angel", "Azazel, el Ángel Flamígero"),
    "QUEST_SEWER_OLD_GATOR": ("O Carniceiro Chifrudo", "The Horned Butcher", "El Carnicero Cornudo"),
    "QUEST_SEWER_OLD_GATOR_DESC": ("O Catador do Esgoto quer a Passagem Secreta da Guerra de volta: derrote o Carniceiro Chifrudo, na praça do lado leste do esgoto.",
                                   "The Sewer Scavenger wants the Secret War Passage back: defeat the Horned Butcher in the plaza on the east side of the sewer.",
                                   "El Rebuscador de la Alcantarilla quiere recuperar el Pasaje Secreto de la Guerra: derrota al Carnicero Cornudo en la plaza del lado este de la alcantarilla."),
    "DLG_SEWER_GATOR_1": ("Psiu! Eu catava tralha por aqui, até o Carniceiro Chifrudo tomar a Passagem da Guerra.",
                          "Psst! I used to scavenge around here, until the Horned Butcher took over the War Passage.",
                          "¡Psst! Yo rebuscaba por aquí, hasta que el Carnicero Cornudo se adueñó del Pasaje de la Guerra."),
    "DLG_SEWER_GATOR_2": ("Ele só sai da água quando alguém chega perto, e anda sempre com os jacarés menores.",
                          "He only leaves the water when someone gets close, and he always brings the smaller gators.",
                          "Solo sale del agua cuando alguien se acerca, y siempre va con los caimanes menores."),
    "DLG_SEWER_GATOR_3": ("A praça dele fica no lado leste do fundo do labirinto. Derrubem o bicho e a passagem volta a ser nossa.",
                          "His plaza is on the east side, deep in the maze. Bring him down and the passage is ours again.",
                          "Su plaza está en el lado este, al fondo del laberinto. Derríbenlo y el pasaje vuelve a ser nuestro."),
    "DLG_SEWER_GATOR_ACTIVE": ("O Carniceiro Chifrudo ainda manda na Passagem da Guerra. Sigam pelo leste, rumo ao fundo.",
                               "The Horned Butcher still rules the War Passage. Head east, toward the back.",
                               "El Carnicero Cornudo aún manda en el Pasaje de la Guerra. Sigan por el este, hacia el fondo."),
    "DLG_SEWER_GATOR_DONE": ("O Velho caiu? Então a Passagem é nossa. Obrigado, de coração.",
                             "The Old One fell? Then the Passage is ours. Thank you, truly.",
                             "¿El Viejo cayó? Entonces el Pasaje es nuestro. Gracias, de corazón."),
    "QUEST_SEWER_FROG_KING": ("O Empalado", "The Impaled One", "El Empalado"),
    "QUEST_SEWER_FROG_KING_DESC": ("Itachi quer acabar com a praga de sapos: derrote o Empalado, na praça do lado oeste do esgoto.",
                                   "Itachi wants to end the frog plague: defeat the Impaled One in the plaza on the west side of the sewer.",
                                   "Itachi quiere acabar con la plaga de sapos: derrota al Empalado en la plaza del lado oeste de la alcantarilla."),
    "DLG_SEWER_FROG_1": ("Pragas eu conheço bem. Mas esta é diferente: um sapo coroado que manda em todos os outros.",
                         "I know pests well. But this one is different: a crowned frog that commands all the others.",
                         "Conozco bien las plagas. Pero esta es distinta: un sapo coronado que manda sobre todos los demás."),
    "DLG_SEWER_FROG_2": ("O Empalado reina numa praça do lado oeste, entre as poças, cercado de sapos.",
                         "The Impaled One reigns in a plaza on the west side, among the puddles, surrounded by frogs.",
                         "El Empalado reina en una plaza del lado oeste, entre los charcos, rodeado de sapos."),
    "DLG_SEWER_FROG_3": ("Derrubem ele e a praga acaba. Eu pago bem, não precisam nem pedir duas vezes.",
                         "Bring him down and the plague ends. I pay well, you won't need to ask twice.",
                         "Derríbenlo y la plaga se acaba. Pago bien, no hará falta pedirlo dos veces."),
    "DLG_SEWER_FROG_ACTIVE": ("O Empalado ainda reina no oeste. Sigam o coaxar: ele está perto das poças grandes.",
                              "The Impaled One still reigns in the west. Follow the croaking: he is near the big puddles.",
                              "El Empalado aún reina en el oeste. Sigan el croar: está cerca de los charcos grandes."),
    "DLG_SEWER_FROG_DONE": ("Silêncio! Que paz. O esgoto respira de novo.", "Silence! What peace. The sewer breathes again.", "¡Silencio! Qué paz. La alcantarilla respira de nuevo."),
    "PROP_SEWER_SECTOR_1": ("Bueiros da Rua Principal", "Main Street Drains", "Desagües de la Calle Principal"),
    "SIGN_SEWER_SECTOR_1": ("Setor 1 — Bueiros da Rua Principal. Sapos Pestilentos em bandos; fique de olho nos becos.",
                            "Sector 1 — Main Street Drains. Plague frogs in packs; watch the dead ends.",
                            "Sector 1 — Desagües de la Calle Principal. Sapos pestilentes en manadas; atención a los callejones."),
    "PROP_SEWER_SECTOR_2": ("Canais de Lixo", "Garbage Canals", "Canales de Basura"),
    "SIGN_SEWER_SECTOR_2": ("Setor 2 — Canais de Lixo. A praça do Empalado fica ao oeste; o altar dele, no centro do mapa.",
                            "Sector 2 — Garbage Canals. The Impaled One's plaza is to the west; his altar, in the center of the map.",
                            "Sector 2 — Canales de Basura. La plaza del Empalado está al oeste; su altar, en el centro del mapa."),
    "PROP_SEWER_SECTOR_3": ("Galerias dos Morcegos", "Bat Galleries", "Galerías de los Murciélagos"),
    "SIGN_SEWER_SECTOR_3": ("Setor 3 — Galerias dos Morcegos. Bandos de morcegos pestilentos; o posto do Itachi fica a leste.",
                            "Sector 3 — Bat Galleries. Flocks of plague bats; Itachi's post is to the east.",
                            "Sector 3 — Galerías de los Murciélagos. Bandadas de murciélagos pestilentes; el puesto de Itachi está al este."),
    "PROP_SEWER_SECTOR_4": ("Passagem Secreta da Guerra", "Secret War Passage", "Pasaje Secreto de la Guerra"),
    "SIGN_SEWER_SECTOR_4": ("Setor 4 — Passagem Secreta da Guerra. Jacarés à espreita na água; a praça do Carniceiro Chifrudo fica ao leste.",
                            "Sector 4 — Secret War Passage. Gators lurk in the water; the Horned Butcher's plaza is to the east.",
                            "Sector 4 — Pasaje Secreto de la Guerra. Caimanes al acecho en el agua; la plaza del Carnicero Cornudo está al este."),
    "PROP_SEWER_SECTOR_5": ("Câmaras dos Cogumelos", "Mushroom Chambers", "Cámaras de Hongos"),
    "SIGN_SEWER_SECTOR_5": ("Setor 5 — Câmaras dos Cogumelos. Tios-Cogumelo pesados e escorpiões; o túnel do Ninho sai pelo sul.",
                            "Sector 5 — Mushroom Chambers. Heavy Fungus Uncles and scorpions; the tunnel to the Nest leaves to the south.",
                            "Sector 5 — Cámaras de Hongos. Tíos Hongo pesados y escorpiones; el túnel al Nido sale por el sur."),
    "PROP_SEWER_NEST": ("Ninho da Rainha", "The Queen's Nest", "Nido de la Reina"),
    "SIGN_SEWER_NEST": ("Ninho da Rainha dos Ratos. O Tesouro Perdido da Guerra dorme com ela. Voltem equipados.",
                        "The Rat Queen's Nest. The War's Lost Treasure sleeps with her. Come back prepared.",
                        "Nido de la Reina de las Ratas. El Tesoro Perdido de la Guerra duerme con ella. Vuelvan preparados."),
}
# As duas missões trocaram de dono: o Catador (Homem-Aranha) pede o Empalado (o Monstro de Tábuas, a oeste); Itachi pede o Carniceiro Chifrudo (a leste). Falas na voz de cada um.
T.update({
    "DLG_SEWER_FROG_1": ("Sou o Homem-Aranha. Vim do multiverso e fui parar neste esgoto. Sim, sou um herói, mas até herói precisa de ajuda.",
                         "I am Spider-Man. I came from the multiverse and landed in this sewer. Yes, I am a hero, but even heroes need help.",
                         "Soy el Hombre Araña. Vengo del multiverso y caí en esta alcantarilla. Sí, soy un héroe, pero hasta los héroes necesitan ayuda."),
    "DLG_SEWER_FROG_2": ("O povo chama de Empalado, mas não tem nada de sapo: é um monstro de carne e tábuas, cheio de pregos, na praça do lado oeste. Sozinho eu não dou conta.",
                         "Folks call it the Impaled One, but there is nothing froggy about it: it is a monster of flesh and planks, full of nails, in the plaza on the west side. I cannot take it alone.",
                         "La gente lo llama el Empalado, pero de sapo no tiene nada: es un monstruo de carne y tablas, lleno de clavos, en la plaza del lado oeste. Yo solo no puedo con él."),
    "DLG_SEWER_FROG_3": ("Derrube ele comigo, por favor. Prometo que a ajuda vale a pena: é só seguir para o oeste, até a praça grande.",
                         "Take it down with me, please. I promise the help is worth it: just head west, to the big plaza.",
                         "Derríbalo conmigo, por favor. Prometo que la ayuda vale la pena: solo sigue hacia el oeste, hasta la plaza grande."),
    "DLG_SEWER_FROG_ACTIVE": ("O monstro ainda manda na praça do oeste. Eu ajudo no que puder, mas preciso de vocês para derrubá-lo. Cuidado com a investida!",
                              "The monster still rules the west plaza. I will help however I can, but I need you to bring it down. Watch out for its charge!",
                              "El monstruo aún manda en la plaza del oeste. Ayudo en lo que pueda, pero los necesito para derribarlo. ¡Cuidado con su embestida!"),
    "DLG_SEWER_FROG_DONE": ("Caiu mesmo? Valeu! Até um herói do multiverso precisa de uma equipe. Seu amigo e vizinho do esgoto agradece.",
                            "He really fell? Thanks! Even a hero from the multiverse needs a team. Your friendly neighborhood sewer scavenger appreciates it.",
                            "¿De verdad cayó? ¡Gracias! Hasta un héroe del multiverso necesita un equipo. Tu amigo y vecino de la alcantarilla lo agradece."),
    "DLG_SEWER_GATOR_1": ("Há um jacaré antigo na Passagem Secreta da Guerra. Ninguém passa por lá sem que ele queira.",
                          "There is an ancient gator in the Secret War Passage. No one gets through unless he allows it.",
                          "Hay un caimán antiguo en el Pasaje Secreto de la Guerra. Nadie pasa si él no quiere."),
    "DLG_SEWER_GATOR_2": ("O Carniceiro Chifrudo só sai da água quando alguém chega perto, e nunca vem sozinho.",
                          "The Horned Butcher only leaves the water when someone gets close, and he never comes alone.",
                          "El Carnicero Cornudo solo sale del agua cuando alguien se acerca, y nunca viene solo."),
    "DLG_SEWER_GATOR_3": ("A praça dele fica no lado leste, no fundo do labirinto. Derrubem-no e eu recompenso vocês.",
                          "His plaza is on the east side, deep in the maze. Bring him down and I will reward you.",
                          "Su plaza está en el lado este, al fondo del laberinto. Derríbenlo y los recompenso."),
    "DLG_SEWER_GATOR_ACTIVE": ("O Carniceiro Chifrudo ainda domina a Passagem. Sigam para o leste, rumo ao fundo.",
                               "The Horned Butcher still rules the Passage. Head east, toward the back.",
                               "El Carnicero Cornudo aún domina el Pasaje. Sigan hacia el este, hacia el fondo."),
    "DLG_SEWER_GATOR_DONE": ("A Passagem está livre. Bom trabalho.", "The Passage is free. Good work.", "El Pasaje está libre. Buen trabajo."),
    "QUEST_SEWER_OLD_GATOR_DESC": ("Itachi quer a Passagem Secreta da Guerra livre: derrote o Carniceiro Chifrudo, na praça do lado leste do esgoto.",
                                   "Itachi wants the Secret War Passage cleared: defeat the Horned Butcher in the plaza on the east side of the sewer.",
                                   "Itachi quiere el Pasaje Secreto de la Guerra libre: derrota al Carnicero Cornudo en la plaza del lado este de la alcantarilla."),
    "QUEST_SEWER_FROG_KING_DESC": ("O Catador do Esgoto quer o Empalado fora do caminho: derrote o monstro da praça do lado oeste do esgoto.",
                                   "The Sewer Scavenger wants the Impaled One out of the way: defeat the monster in the plaza on the west side of the sewer.",
                                   "El Rebuscador de la Alcantarilla quiere al Empalado fuera del camino: derrota al monstruo de la plaza del lado oeste de la alcantarilla."),
})
T.update({k: v for k, v in {'NPC_SEWER_FROG_ALTAR': ('Altar do Empalado', "The Impaled One's Altar", 'Altar del Empalado'), 'DLG_FROG_ALTAR_1': ('Um altar de pedra manchado de lodo, no coração do esgoto. Há marcas de garras e de pregos na pedra.', 'A stone altar stained with sludge, in the heart of the sewer. There are claw and nail marks on the stone.', 'Un altar de piedra manchado de lodo, en el corazón de la alcantarilla. Hay marcas de garras y de clavos en la piedra.'), 'DLG_FROG_ALTAR_2': ('Você toca na pedra e o chão estremece: o Empalado acorda na sala do altar.', 'You touch the stone and the floor trembles: the Impaled One wakes in the altar room.', 'Tocas la piedra y el suelo tiembla: el Empalado despierta en la sala del altar.'), 'TOAST_FROG_ALTAR_AWAKENS': ('O altar estremece: o Empalado desperta!', 'The altar trembles: the Impaled One awakens!', 'El altar tiembla: ¡el Empalado despierta!'), 'DLG_SEWER_FROG_2': ('O povo chama de Empalado, mas não tem nada de sapo: é um monstro de carne e tábuas, cheio de pregos. Ele dorme até alguém tocar o altar, no centro do esgoto. Sozinho eu não dou conta.', 'Folks call it the Impaled One, but there is nothing froggy about it: it is a monster of flesh and planks, full of nails. It sleeps until someone touches the altar in the center of the sewer. I cannot take it alone.', 'La gente lo llama el Empalado, pero de sapo no tiene nada: es un monstruo de carne y tablas, lleno de clavos. Duerme hasta que alguien toca el altar, en el centro de la alcantarilla. Yo solo no puedo con él.'), 'DLG_SEWER_FROG_3': ('Derrube ele comigo, por favor. Prometo que a ajuda vale a pena: toquem o altar no centro do esgoto e preparem-se.', 'Take it down with me, please. I promise the help is worth it: touch the altar in the center of the sewer and brace yourselves.', 'Derríbalo conmigo, por favor. Prometo que la ayuda vale la pena: toquen el altar en el centro de la alcantarilla y prepárense.'), 'DLG_SEWER_FROG_ACTIVE': ('O monstro só acorda quando alguém toca o altar, no centro do esgoto. Cuidado com a investida!', 'The monster only wakes when someone touches the altar in the center of the sewer. Watch out for its charge!', 'El monstruo solo despierta cuando alguien toca el altar, en el centro de la alcantarilla. ¡Cuidado con su embestida!'), 'QUEST_SEWER_FROG_KING_DESC': ('O Catador do Esgoto quer o Empalado fora do caminho: toque o altar no centro do esgoto para despertá-lo e derrote o monstro.', 'The Sewer Scavenger wants the Impaled One out of the way: touch the altar in the center of the sewer to wake it and defeat the monster.', 'El Rebuscador de la Alcantarilla quiere al Empalado fuera del camino: toca el altar en el centro de la alcantarilla para despertarlo y derrota al monstruo.')}.items()})
T.update({k: v for k, v in {'TOAST_BOOK_RECEIVED': ('O Catador do Esgoto entregou o Livro do Altar!', 'The Sewer Scavenger handed over the Altar Book!', '¡El Rebuscador de la Alcantarilla entregó el Libro del Altar!'), 'DLG_FROG_ALTAR_LOCKED': ('O altar não reage. Há um vão vazio no centro da pedra, do tamanho de um livro. O Catador do Esgoto deve ter o que falta.', 'The altar does not react. There is an empty gap in the middle of the stone, the size of a book. The Sewer Scavenger must have what is missing.', 'El altar no reacciona. Hay un hueco vacío en el centro de la piedra, del tamaño de un libro. El Rebuscador de la Alcantarilla debe tener lo que falta.'), 'DLG_FROG_ALTAR_1': ('Um altar de pedra manchado de lodo, no coração do esgoto. Há um vão no centro, do tamanho de um livro, e marcas de garras e de pregos ao redor.', 'A stone altar stained with sludge, in the heart of the sewer. There is a gap in the center, the size of a book, with claw and nail marks around it.', 'Un altar de piedra manchado de lodo, en el corazón de la alcantarilla. Hay un hueco en el centro, del tamaño de un libro, y marcas de garras y de clavos alrededor.'), 'DLG_FROG_ALTAR_2': ('Você apoia o Livro do Altar na pedra e lê em voz alta: o chão estremece e o Empalado acorda na sala do altar.', 'You rest the Altar Book on the stone and read aloud: the floor trembles and the Impaled One wakes in the altar room.', 'Apoyas el Libro del Altar en la piedra y lees en voz alta: el suelo tiembla y el Empalado despierta en la sala del altar.'), 'DLG_SEWER_FROG_3': ('Derrube ele comigo, por favor. Leve este livro: ele abre o altar no centro do esgoto. Apoiem-no na pedra, leiam e preparem-se.', 'Take it down with me, please. Take this book: it opens the altar in the center of the sewer. Rest it on the stone, read it aloud, and brace yourselves.', 'Derríbalo conmigo, por favor. Llévate este libro: abre el altar en el centro de la alcantarilla. Apóyenlo en la piedra, léanlo y prepárense.'), 'DLG_SEWER_FROG_ACTIVE': ('O monstro só acorda quando alguém lê o livro no altar, no centro do esgoto. Cuidado com a investida!', 'The monster only wakes when someone reads the book at the altar in the center of the sewer. Watch out for its charge!', 'El monstruo solo despierta cuando alguien lee el libro en el altar, en el centro de la alcantarilla. ¡Cuidado con su embestida!'), 'QUEST_SEWER_FROG_KING_DESC': ('O Catador do Esgoto quer o Empalado fora do caminho: leve o livro dele ao altar no centro do esgoto para despertar o monstro e derrote-o.', 'The Sewer Scavenger wants the Impaled One out of the way: take his book to the altar in the center of the sewer to wake the monster, then defeat it.', 'El Rebuscador de la Alcantarilla quiere al Empalado fuera del camino: lleva su libro al altar en el centro de la alcantarilla para despertar al monstruo y derrótalo.')}.items()})  # o Livro do Altar
T.update({
    "DLG_SEWER_FROG_1": ("Fui anjo, um dia. Caí por estas grades, e as asas ficaram presas no que o esgoto devora. Escuto os sussurros de uma coisa de carne e tábuas, no coração do esgoto.",
                         "I was an angel, once. I fell through these grates, and my wings stayed caught in what the sewer devours. I hear the whispers of a thing of flesh and planks, in the heart of the sewer.",
                         "Fui ángel, una vez. Caí por estas rejas, y mis alas quedaron atrapadas en lo que la cloaca devora. Oigo los susurros de una cosa de carne y tablas, en el corazón de la alcantarilla."),
    "DLG_SEWER_FROG_2": ("O povo o chama de Empalado: foi montado com os ossos e a madeira dos que se afogaram aqui, pregado a pregado, e crava os próprios espinhos em quem chega perto. Ele ainda chora, e o choro dele chama os outros mortos.",
                         "Folks call it the Impaled One: it was assembled from the bones and wood of those who drowned here, nail by nail, and it drives its own spikes into anyone who comes near. It still weeps, and its weeping calls the other dead.",
                         "La gente lo llama el Empalado: lo armaron con los huesos y la madera de quienes se ahogaron aquí, clavo a clavo, y clava sus propias espinas en quien se acerca. Aún llora, y su llanto llama a los demás muertos."),
    "DLG_SEWER_FROG_3": ("Derrubem-no e libertem as almas presas nas tábuas. Em troca, a chave que ele guarda é de vocês. Sigam para o oeste, até a praça grande.",
                         "Bring it down and free the souls trapped in the planks. In return, the key it keeps is yours. Head west, to the big plaza.",
                         "Derríbenlo y liberen las almas presas en las tablas. A cambio, la llave que guarda es suya. Vayan al oeste, hasta la plaza grande."),
    "DLG_SEWER_FROG_ACTIVE": ("Ainda ouço o choro dele no oeste. Cada tábua que cai solta uma alma… e eu a vejo subir. Não me deixem esperando no escuro.",
                              "I can still hear it weeping in the west. Every plank that falls frees a soul… and I watch it rise. Do not leave me waiting in the dark.",
                              "Todavía oigo su llanto en el oeste. Cada tabla que cae suelta un alma… y la veo subir. No me dejen esperando en la oscuridad."),
    "DLG_SEWER_FROG_DONE": ("Silêncio, finalmente. As almas subiram e eu senti cada uma passar por entre as minhas asas quebradas. Obrigado. Levem a chave: ela já pesa menos.",
                            "Silence, at last. The souls rose and I felt each one pass through my broken wings. Thank you. Take the key: it weighs less now.",
                            "Silencio, por fin. Las almas subieron y sentí cada una pasar entre mis alas rotas. Gracias. Lleven la llave: ya pesa menos."),
    "NPC_SEWER_SCAVENGER": ("Ossael, o Anjo Caveira", "Ossael, the Skull Angel", "Ossael, el Ángel Calavera"),
})
# o Catador virou o anjo Ossael: o nome dele some dos outros textos (missão, aviso do livro, altar)
for _k in list(T):
    T[_k] = tuple(t.replace("O Catador do Esgoto", "Ossael").replace("Catador do Esgoto", "Ossael").replace("The Sewer Scavenger", "Ossael").replace("El Rebuscador de la Alcantarilla", "Ossael")
                  .replace("Rebuscador de la Alcantarilla", "Ossael") for t in T[_k])
T.update({
    "DLG_SEWER_GATOR_1": ("Eu ardo desde que o céu me expulsou. O Carniceiro Chifrudo engoliu os meus irmãos que caíram nesta Passagem da Guerra, e ainda guarda os ossos deles na barriga.",
                          "I have burned since the sky cast me out. The Horned Butcher swallowed my brothers who fell in this War Passage, and still keeps their bones in his belly.",
                          "Ardo desde que el cielo me expulsó. El Carnicero Cornudo se tragó a mis hermanos caídos en este Pasaje de la Guerra, y aún guarda sus huesos en el vientre."),
    "DLG_SEWER_GATOR_2": ("Ele só sai da água quando alguém chega perto, e nunca vem sozinho. Escuto os ossos estalando dentro dele a cada passo.",
                          "He only leaves the water when someone gets close, and never comes alone. I hear the bones cracking inside him at every step.",
                          "Solo sale del agua cuando alguien se acerca, y nunca viene solo. Oigo los huesos crujir dentro de él a cada paso."),
    "DLG_SEWER_GATOR_3": ("A praça dele fica no lado leste, no fundo do labirinto. Rasguem a barriga dele por mim, e a chave que ele guarda é de vocês.",
                          "His plaza is on the east side, deep in the maze. Tear his belly open for me, and the key he keeps is yours.",
                          "Su plaza está en el lado este, en el fondo del laberinto. Ábranle el vientre por mí, y la llave que guarda es suya."),
    "DLG_SEWER_GATOR_ACTIVE": ("O Velho ainda domina a Passagem. Sigam para o leste, rumo ao fundo, e deixem o fogo dele… quer dizer, o meu, fazer o resto.",
                               "The Old One still rules the Passage. Head east, deep down, and let his fire… I mean, mine, do the rest.",
                               "El Viejo aún domina el Pasaje. Vayan al este, hacia el fondo, y dejen que su fuego… quiero decir, el mío, haga el resto."),
    "DLG_SEWER_GATOR_DONE": ("A barriga dele se abriu e meus irmãos puderam finalmente ser queimados em paz. Levem a chave. Eu fico com as cinzas.",
                             "His belly burst open and my brothers could finally be burned in peace. Take the key. I keep the ashes.",
                             "Su vientre se abrió y mis hermanos por fin pudieron arder en paz. Lleven la llave. Yo me quedo con las cenizas."),
})
# Azazel entrega o Grimório das Brasas ao abrir a missão (lido no altar do Gator, no centro do mapa, invoca o Carniceiro Chifrudo) e pede a Garrafa das Almas Condenadas, que o Gator solta;
# a chave de espadas vem do Azazel ao receber a garrafa.
# Ossael (quest 'A Garrafa do Tormento Eterno', a do Empalado): o Anjo Caveira veio buscar a garrafa, que o Empalado lhe tomou; entrega o Livro do Altar (as preces dos afogados), lido no altar do centro; ao receber a garrafa que o Empalado solta, entrega a chave de copas.
T.update({
    "QUEST_SEWER_FROG_KING": ('A Garrafa do Tormento Eterno',
        'The Bottle of Eternal Torment',
        'La Botella del Tormento Eterno'),
    "QUEST_SEWER_FROG_KING_DESC": ('Ossael, o Anjo Caveira, quer a Garrafa do Tormento Eterno, que o Empalado lhe tomou: leve o Livro do Altar ao altar do centro do esgoto, leia-o para despertar o monstro, derrote-o e leve a garrafa à Ossael para receber a chave de copas.',
        'Ossael, the Skull Angel, wants the Bottle of Eternal Torment, which the Impaled One took from him: take the Altar Book to the altar in the center of the sewer, read it to wake the monster, defeat it, and bring the bottle to Ossael to receive the heart key.',
        'Ossael, el Ángel Calavera, quiere la Botella del Tormento Eterno, que el Empalado le quitó: lleva el Libro del Altar al altar del centro de la alcantarilla, léelo para despertar al monstruo, derrótalo y llévale la botella a Ossael para recibir la llave de corazones.'),
    "VALUABLE_TORMENT_BOTTLE": ('Garrafa do Tormento Eterno',
        'Bottle of Eternal Torment',
        'Botella del Tormento Eterno'),
    "DLG_SEWER_FROG_1": ('Meus ossos já foram um anjo, guardião dos afogados deste esgoto, e vim buscar a Garrafa do Tormento Eterno, onde se guarda o sofrimento deles para que possam descansar. Falhei: uma coisa de carne e tábuas me tomou a carne, as penas brancas e a garrafa, e pregou as almas dos meus afogados na própria madeira. Só restaram ossos e estas asas negras.',
        'These bones were once an angel, guardian of the drowned of this sewer, and I came to fetch the Bottle of Eternal Torment, where their suffering is kept so they can rest. I failed: a thing of flesh and planks took my flesh, my white feathers and the bottle, and nailed the souls of my drowned into its own wood. Only bones and these black wings remain.',
        'Estos huesos fueron un ángel, guardián de los ahogados de esta alcantarilla, y vine a buscar la Botella del Tormento Eterno, donde se guarda su sufrimiento para que puedan descansar. Fallé: una cosa de carne y tablas me quitó la carne, las plumas blancas y la botella, y clavó las almas de mis ahogados en su propia madera. Solo quedan huesos y estas alas negras.'),
    "DLG_SEWER_FROG_2": ('O povo o chama de Empalado: foi montado com os ossos e as tábuas das passarelas, pregado a pregado, e crava os próprios espinhos em quem chega perto. Ele leva a minha garrafa pregada no peito e dorme sob o altar de pedra, no centro do esgoto; só acorda quando alguém lê o livro certo. O choro dele chama os outros mortos.',
        'Folks call it the Impaled One: it was assembled from bones and the planks of the walkways, nail by nail, and it drives its own spikes into whoever comes close. It carries my bottle nailed to its chest and sleeps under the stone altar in the center of the sewer; it only wakes when someone reads the right book. Its weeping calls the other dead.',
        'La gente lo llama el Empalado: lo armaron con huesos y las tablas de las pasarelas, clavo a clavo, y clava sus propias púas en quien se acerca. Lleva mi botella clavada en el pecho y duerme bajo el altar de piedra, en el centro de la alcantarilla; solo despierta cuando alguien lee el libro correcto. Su llanto llama a los demás muertos.'),
    "DLG_SEWER_FROG_3": ('Levem o Livro do Altar, as preces dos afogados. Apoiem-no na pedra e leiam em voz alta. Derrubem o Empalado e tragam-me a Garrafa do Tormento Eterno; em troca, a chave de copas que eu guardo é de vocês.',
        'Take the Altar Book, the prayers of the drowned. Rest it on the stone and read it aloud. Bring the Impaled One down and bring me the Bottle of Eternal Torment; in return, the heart key I keep is yours.',
        'Llévense el Libro del Altar, las oraciones de los ahogados. Apóyenlo en la piedra y léanlo en voz alta. Derriben al Empalado y tráiganme la Botella del Tormento Eterno; a cambio, la llave de corazones que guardo es suya.'),
    "DLG_SEWER_FROG_ACTIVE": ('Ainda sem a garrafa? O Empalado só desperta quando as preces são lidas no altar, no centro do esgoto. Cada tábua que cai solta uma alma… Tragam-me a Garrafa do Tormento Eterno, pregada no peito dele.',
        'Still no bottle? The Impaled One only wakes when the prayers are read at the altar in the center of the sewer. Every plank that falls frees a soul… Bring me the Bottle of Eternal Torment, nailed to its chest.',
        '¿Aún sin la botella? El Empalado solo despierta cuando se leen las oraciones en el altar, en el centro de la alcantarilla. Cada tabla que cae suelta un alma… Tráiganme la Botella del Tormento Eterno, clavada en su pecho.'),
    "DLG_SEWER_FROG_DONE": ('A garrafa… o tormento deles termina aqui, e as almas sobem. Cada uma passou por entre as minhas asas negras antes de partir. Obrigado. Levem a chave de copas: ela é de vocês. Eu fico aqui, de guarda, enquanto houver afogados.',
        'The bottle… their torment ends here, and the souls rise. Each one passed between my black wings before leaving. Thank you. Take the heart key: it is yours. I will stay here, on guard, as long as there are drowned.',
        'La botella… su tormento termina aquí, y las almas suben. Cada una pasó entre mis alas negras antes de partir. Gracias. Lleven la llave de corazones: es suya. Yo me quedo aquí, de guardia, mientras haya ahogados.'),
    "DLG_FROG_ALTAR_1": ('Um altar de pedra manchado de lodo, no coração do esgoto. Há um vão no centro, do tamanho de um livro, e preces dos afogados riscadas na pedra, com marcas de garras e de pregos ao redor.',
        'A stone altar stained with sludge, in the heart of the sewer. There is a gap in the center, the size of a book, with the prayers of the drowned scratched into the stone, and claw and nail marks around it.',
        'Un altar de piedra manchado de lodo, en el corazón de la alcantarilla. Hay un hueco en el centro, del tamaño de un libro, con las oraciones de los ahogados rayadas en la piedra y marcas de garras y de clavos alrededor.'),
    "DLG_FROG_ALTAR_2": ('Você apoia o Livro do Altar na pedra e lê as preces em voz alta: o chão estremece, as tábuas rangem e o Empalado acorda na sala do altar, com a garrafa pregada no peito.',
        'You rest the Altar Book on the stone and read the prayers aloud: the floor trembles, the planks creak and the Impaled One wakes in the altar room, the bottle nailed to its chest.',
        'Apoyas el Libro del Altar en la piedra y lees las oraciones en voz alta: el suelo tiembla, las tablas crujen y el Empalado despierta en la sala del altar, con la botella clavada en el pecho.'),
    "VALUABLE_ALTAR_BOOK_DESC": ('Dado por Ossael. As preces dos afogados: fazem o altar do centro do Esgoto reagir. Leve o grupo até ele e fale com a pedra para despertar o Empalado. Não se vende nem se perde.',
        'Given by Ossael. The prayers of the drowned: they make the altar in the center of the Sewer react. Bring the group to it and speak to the stone to wake the Impaled One. It cannot be sold or lost.',
        'Dado por Ossael. Las oraciones de los ahogados: hacen reaccionar el altar del centro de la Alcantarilla. Lleva al grupo hasta él y habla con la piedra para despertar al Empalado. No se vende ni se pierde.'),
    "BEAST_IMPALED_ONE": ('Empalado',
        'Impaled One',
        'Empalado'),
    "BEAST_IMPALED_ONE_LEGEND": ('Monstro de carne, ossos e tábuas das passarelas, pregado a pregado com as almas dos afogados dentro e a Garrafa do Tormento Eterno no peito. Dorme sob o altar do centro do esgoto e crava os próprios espinhos em quem chega perto.',
        'A monster of flesh, bone and walkway planks, nailed together with the souls of the drowned inside and the Bottle of Eternal Torment on its chest. It sleeps under the altar in the center of the sewer and drives its own spikes into whoever comes close.',
        'Un monstruo de carne, huesos y tablas de las pasarelas, clavado con las almas de los ahogados dentro y la Botella del Tormento Eterno en el pecho. Duerme bajo el altar del centro de la alcantarilla y clava sus propias púas en quien se acerca.'),
    "BEAST_IMPALED_ONE_HINT": ('Ele embiste em linha reta: desvie na hora da investida e bata quando ele parar cravado. Madeira velha queima: o fogo o fere mais.',
        'It charges in a straight line: dodge the charge and strike when it stops, stuck fast. Old wood burns: fire hurts it more.',
        'Embiste en línea recta: esquiva la embestida y golpea cuando se quede clavado. La madera vieja arde: el fuego lo hiere más.'),
})
T.update({
    "VALUABLE_SOULS_BOTTLE": ("Garrafa das Almas Condenadas", "Bottle of Condemned Souls", "Botella de las Almas Condenadas"),
    "VALUABLE_GATOR_BOOK": ("Grimório das Brasas", "Grimoire of Embers", "Grimorio de las Brasas"),
    "VALUABLE_GATOR_BOOK_DESC": ("Dado por Azazel. Faz o altar do centro do Esgoto reagir: leve o grupo até ele e fale com a pedra para despertar o Carniceiro Chifrudo. Não se vende nem se perde.",
                                 "Given by Azazel. Makes the altar in the center of the Sewer react: bring the group to it and speak to the stone to wake the Horned Butcher. It cannot be sold or lost.",
                                 "Dado por Azazel. Hace reaccionar el altar del centro de la Alcantarilla: lleva al grupo hasta él y habla con la piedra para despertar al Carnicero Cornudo. No se vende ni se pierde."),
    "DLG_GATOR_ALTAR_2": ("Você apoia o Grimório das Brasas no vão da pedra e lê em voz alta: a pedra esquenta, a água ferve e o Carniceiro Chifrudo emerge, com as almas gritando na barriga.",
                          "You rest the Grimoire of Embers in the gap of the stone and read aloud: the stone heats up, the water boils and the Horned Butcher emerges, with the souls screaming in his belly.",
                          "Apoyas el Grimorio de las Brasas en el hueco de la piedra y lees en voz alta: la piedra se calienta, el agua hierve y el Carnicero Cornudo emerge, con las almas gritando en su vientre."),
    "DLG_FROG_ALTAR_LOCKED": ("O altar não reage. Há um vão vazio no centro da pedra, do tamanho de um livro. Ossael ou Azazel devem ter o que falta.",
                              "The altar does not react. There is an empty gap in the middle of the stone, the size of a book. Ossael or Azazel must have what is missing.",
                              "El altar no reacciona. Hay un hueco vacío en el centro de la piedra, del tamaño de un libro. Ossael o Azazel deben tener lo que falta."),
    "TOAST_GATOR_ALTAR_AWAKENS": ("O altar ferve: o Carniceiro Chifrudo desperta!", "The altar boils: the Horned Butcher awakens!", "El altar hierve: ¡el Carnicero Cornudo despierta!"),
    "TOAST_GATOR_BOOK_RECEIVED": ("Azazel entregou o Grimório das Brasas!", "Azazel handed over the Grimoire of Embers!", "¡Azazel entregó el Grimorio de las Brasas!"),
    "DLG_SEWER_GATOR_1": ("Eu ardo desde que o céu me expulsou, e Lúcifer me mandou até aqui buscar a Garrafa das Almas Condenadas. O Carniceiro Chifrudo a engoliu na Passagem da Guerra antes que eu pudesse tocá-la.",
                          "I have burned since the sky cast me out, and Lucifer sent me here to fetch the Bottle of Condemned Souls. The Horned Butcher swallowed it in the War Passage before I could touch it.",
                          "Ardo desde que el cielo me expulsó, y Lucifer me envió aquí a buscar la Botella de las Almas Condenadas. El Carnicero Cornudo se la tragó en el Pasaje de la Guerra antes de que pudiera tocarla."),
    "DLG_SEWER_GATOR_2": ("Ele não sai da água por vontade própria, e nunca vem sem os jacarés menores. A garrafa está na barriga dele: escuto as almas gritando a cada respiração.",
                          "He does not leave the water on his own, and never comes without the smaller gators. The bottle is in his belly: I hear the souls screaming with every breath.",
                          "No sale del agua por voluntad propia, y nunca viene sin los caimanes menores. La botella está en su vientre: oigo a las almas gritar con cada respiración."),
    "DLG_SEWER_GATOR_3": ("Levem este grimório. Apoiem-no no altar queimado, no centro do esgoto, e leiam: ele arranca o Velho da água. Rasguem a barriga dele e tragam a garrafa; em troca, a chave que eu guardo é de vocês.",
                          "Take this grimoire. Rest it on the scorched altar in the center of the sewer and read it aloud: it drags the Old One out of the water. Tear his belly open and bring me the bottle; in return, the key I keep is yours.",
                          "Llévense este grimorio. Apóyenlo en el altar quemado, en el centro de la alcantarilla, y léanlo: arranca al Viejo del agua. Ábranle el vientre y tráiganme la botella; a cambio, la llave que guardo es suya."),
    "DLG_SEWER_GATOR_ACTIVE": ("Ainda sem a garrafa? Apoiem o grimório no altar queimado, no centro do esgoto, e chamem o Velho. Tragam a Garrafa das Almas Condenadas e deixem o fogo, o meu, fazer o resto.",
                               "Still no bottle? Rest the grimoire on the scorched altar in the center of the sewer and call the Old One. Bring me the Bottle of Condemned Souls and let the fire, mine, do the rest.",
                               "¿Aún sin la botella? Apoyen el grimorio en el altar quemado, en el centro de la alcantarilla, y llamen al Viejo. Tráiganme la Botella de las Almas Condenadas y dejen que el fuego, el mío, haga el resto."),
    "DLG_SEWER_GATOR_DONE": ("A garrafa… as almas cantam lá dentro. Lúcifer ficará satisfeito. Levem a chave: ela é de vocês. Eu levo as almas, e as cinzas.",
                             "The bottle… the souls sing inside. Lucifer will be pleased. Take the key: it is yours. I take the souls, and the ashes.",
                             "La botella… las almas cantan dentro. Lucifer quedará satisfecho. Lleven la llave: es suya. Yo me llevo las almas, y las cenizas."),
    "QUEST_SEWER_OLD_GATOR_DESC": ("Azazel quer a Garrafa das Almas Condenadas que Lúcifer o mandou buscar: leve o Grimório das Brasas ao altar queimado do centro do esgoto para invocar o Carniceiro Chifrudo, derrote-o e leve a garrafa ao Azazel para receber a chave de espadas.",
                                   "Azazel wants the Bottle of Condemned Souls that Lucifer sent him to fetch: take the Grimoire of Embers to the scorched altar in the center of the sewer to summon the Horned Butcher, defeat him, and bring the bottle to Azazel to receive the spade key.",
                                   "Azazel quiere la Botella de las Almas Condenadas que Lucifer le mandó a buscar: lleva el Grimorio de las Brasas al altar quemado del centro de la alcantarilla para invocar al Carnicero Cornudo, derrótalo y llévale la botella a Azazel para recibir la llave de picas."),
})
# Quest do Azazel reescrita para o Carniceiro Chifrudo (o demônio que roubou a Garrafa das Almas Condenadas; antes era o Gator Velho): história, nome, falas, altar e bestiário.
T.update({
    "QUEST_SEWER_OLD_GATOR": ('A Garrafa das Almas Condenadas',
        'The Bottle of Condemned Souls',
        'La Botella de las Almas Condenadas'),
    "DLG_SEWER_GATOR_1": ('Eu ardo desde que o céu me expulsou. Lúcifer me mandou buscar a Garrafa das Almas Condenadas, a joia da adega dele, e um açougueiro do próprio inferno a roubou: o Carniceiro Chifrudo, que trincha almas a cutelo e fugiu para estes esgotos.',
        'I have burned since the sky cast me out. Lucifer sent me to fetch the Bottle of Condemned Souls, the jewel of his cellar, and a butcher from hell itself stole it: the Horned Butcher, who carves souls with a cleaver and fled to these sewers.',
        'Ardo desde que el cielo me expulsó. Lucifer me mandó a buscar la Botella de las Almas Condenadas, la joya de su bodega, y un carnicero del propio infierno la robó: el Carnicero Cornudo, que trincha almas a cuchillo y huyó a estas alcantarillas.'),
    "DLG_SEWER_GATOR_2": ('Ele não sai do esconderijo por vontade própria, e não anda só: os Espíritos Sombrios das almas que ele trinchou o seguem, gritando. A garrafa ele leva presa ao cinto; escuto as almas lá dentro a cada passo dele.',
        'He does not leave his hideout on his own, and never walks alone: the Shadow Spirits of the souls he carved follow him, screaming. He wears the bottle on his belt; I hear the souls inside at every step he takes.',
        'No sale de su escondite por voluntad propia, y no anda solo: los Espíritus Sombríos de las almas que trinchó lo siguen, gritando. Lleva la botella en el cinto; oigo las almas dentro a cada paso suyo.'),
    "DLG_SEWER_GATOR_3": ('Levem este grimório, escrito nas minhas brasas. Apoiem-no no altar queimado, no centro do esgoto, e leiam: ele chama o Carniceiro pelo nome. Derrubem-no e tragam-me a garrafa; em troca, a chave que eu guardo é de vocês.',
        'Take this grimoire, written in my embers. Rest it on the scorched altar in the center of the sewer and read it aloud: it calls the Butcher by name. Bring him down and bring me the bottle; in return, the key I keep is yours.',
        'Llévense este grimorio, escrito en mis brasas. Apóyenlo en el altar quemado, en el centro de la alcantarilla, y léanlo: llama al Carnicero por su nombre. Derríbenlo y tráiganme la botella; a cambio, la llave que guardo es suya.'),
    "DLG_SEWER_GATOR_ACTIVE": ('Ainda sem a garrafa? Leiam o grimório no altar queimado, no centro do esgoto, e chamem o Carniceiro. Tragam-me a Garrafa das Almas Condenadas e deixem o fogo, o meu, fazer o resto.',
        'Still no bottle? Read the grimoire at the scorched altar in the center of the sewer and call the Butcher. Bring me the Bottle of Condemned Souls and let the fire, mine, do the rest.',
        '¿Aún sin la botella? Lean el grimorio en el altar quemado, en el centro de la alcantarilla, y llamen al Carnicero. Tráiganme la Botella de las Almas Condenadas y dejen que el fuego, el mío, haga el resto.'),
    "DLG_SEWER_GATOR_DONE": ('A garrafa… as almas cantam lá dentro, a salvo do cutelo dele. Lúcifer ficará satisfeito. Levem a chave: ela é de vocês. Eu levo as almas, e as cinzas.',
        'The bottle… the souls sing inside, safe from his cleaver. Lucifer will be pleased. Take the key: it is yours. I take the souls, and the ashes.',
        'La botella… las almas cantan dentro, a salvo de su cuchillo. Lucifer quedará satisfecho. Lleven la llave: es suya. Yo me llevo las almas, y las cenizas.'),
    "QUEST_SEWER_OLD_GATOR_DESC": ('Azazel quer a Garrafa das Almas Condenadas, que Lúcifer o mandou buscar e que o Carniceiro Chifrudo roubou: leve o Grimório das Brasas ao altar queimado do centro do esgoto para chamar o demônio, derrote-o e leve a garrafa ao Azazel para receber a chave de espadas.',
        'Azazel wants the Bottle of Condemned Souls, which Lucifer sent him to fetch and the Horned Butcher stole: take the Grimoire of Embers to the scorched altar in the center of the sewer to call the demon, defeat him, and bring the bottle to Azazel to receive the spade key.',
        'Azazel quiere la Botella de las Almas Condenadas, que Lucifer le mandó a buscar y que el Carnicero Cornudo robó: lleva el Grimorio de las Brasas al altar quemado del centro de la alcantarilla para llamar al demonio, derrótalo y llévale la botella a Azazel para recibir la llave de picas.'),
    "DLG_GATOR_ALTAR_2": ('Você apoia o Grimório das Brasas no vão da pedra e lê em voz alta: a pedra esquenta, o ar fede a enxofre e o Carniceiro Chifrudo surge das brasas, de cutelo em punho, com as almas gritando atrás dele.',
        'You rest the Grimoire of Embers in the gap of the stone and read aloud: the stone heats up, the air reeks of sulfur and the Horned Butcher steps out of the embers, cleaver in hand, the souls screaming behind him.',
        'Apoyas el Grimorio de las Brasas en el hueco de la piedra y lees en voz alta: la piedra se calienta, el aire apesta a azufre y el Carnicero Cornudo sale de las brasas, cuchillo en mano, con las almas gritando tras él.'),
    "TOAST_GATOR_ALTAR_AWAKENS": ('O altar ferve: o Carniceiro Chifrudo surge das brasas!',
        'The altar boils: the Horned Butcher steps out of the embers!',
        'El altar hierve: ¡el Carnicero Cornudo sale de las brasas!'),
    "VALUABLE_GATOR_BOOK_DESC": ('Dado por Azazel. Faz o altar do centro do Esgoto reagir: leve o grupo até ele e fale com a pedra para chamar o Carniceiro Chifrudo. Não se vende nem se perde.',
        'Given by Azazel. Makes the altar in the center of the Sewer react: bring the group to it and speak to the stone to call the Horned Butcher. It cannot be sold or lost.',
        'Dado por Azazel. Hace reaccionar el altar del centro de la Alcantarilla: lleva al grupo hasta él y habla con la piedra para llamar al Carnicero Cornudo. No se vende ni se pierde.'),
    "BEAST_HORNED_BUTCHER": ('Carniceiro Chifrudo',
        'Horned Butcher',
        'Carnicero Cornudo'),
    "BEAST_HORNED_BUTCHER_LEGEND": ('Açougueiro do inferno que fugiu para o esgoto com a Garrafa das Almas Condenadas. Trincha almas a cutelo, e os Espíritos Sombrios delas o seguem, gritando.',
        'A butcher from hell who fled to the sewer with the Bottle of Condemned Souls. He carves souls with a cleaver, and their Shadow Spirits follow him, screaming.',
        'Carnicero del infierno que huyó a la alcantarilla con la Botella de las Almas Condenadas. Trincha almas a cuchillo, y los Espíritus Sombríos de ellas lo siguen, gritando.'),
    "BEAST_HORNED_BUTCHER_HINT": ('Ele investe de cabeça baixa: saia da frente quando ele rugir e bata quando o cutelo ficar preso. A água o fere mais.',
        'He charges head down: step aside when he roars and strike when his cleaver gets stuck. Water hurts him more.',
        'Embiste con la cabeza baja: apártate cuando ruja y golpea cuando el cuchillo se le quede atascado. El agua lo hiere más.'),
})
for _k in list(T):
    T[_k] = tuple(t.replace("Itachi", "Azazel") for t in T[_k])
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
