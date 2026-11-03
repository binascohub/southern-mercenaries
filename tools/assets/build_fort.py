"""Mapa do Forte (fort_01_gate), ampliado: mesma estrutura da Floresta (partida, duas áreas de mini-chefe, guardião do portão e chefe final) com outro caminho.
Grade de 54 x 54 células de 2,5 m (antes 34 x 34) com a pedra e o piso do 3D Dungeon Tileset (Skorpio, CC BY-SA 3.0; peças Fort_<máscara>), como o mapa anterior.
Caminho: a Guarnição (partida, ao sul) sobe para o Pátio de Armas; dali saem três rotas paralelas para a Galeria, que corta o mapa de leste a oeste:
  oeste: Quartel Oeste -> Ossuário (o Exilado pede a Lâmina do Senhor Elfo e desperta o Senhor Elfo Sombrio),
  leste: Quartel Leste -> Salão do Trono (a Penitente pede o Anel da Rainha e desperta a Rainha das Súcubos),
  meio: Salão das Colunas (com duas câmaras sem saída) -> Galeria.
Da Galeria, o corredor do portão (o Carcereiro só abre com as duas chaves) leva ao Salão do Barão (chefe final, com a saída para a Capital).
O Comandante (relíquia do Padre) anda solto no Pátio de Armas. Sorteio com semente fixa; idempotente; chamado no fim de tools/assets/build_maps.py
(antes de set_map_order.py). Também põe NPCs, missões, itens, textos pt/en/es e ícones.
uso: python3 tools/assets/build_fort.py   (a partir da raiz do projeto)"""
import json, math, os, random, re
ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES = ("data/arenas.json", "data/monsters.json", "data/npcs.json", "data/quests.json", "data/valuables.json")
arenas, monsters, npcs, quests, valuables = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES))
rng = random.Random("fort-v2")
COLS, ROWS, CELL = 54, 54, 2.5
grid = [["#"] * COLS for _ in range(ROWS)]


def carve(c0, r0, c1, r1):
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            grid[r][c] = "."


# retângulos (c0, r0, c1, r1), inclusive; coluna cresce para leste, linha cresce para o sul
F_ROOMS = {
    "start": (21, 47, 32, 52), "armory": (13, 38, 40, 44), "barracks_w": (2, 37, 10, 45), "barracks_e": (43, 37, 51, 45),
    "cross": (20, 28, 33, 34), "ossuary": (2, 24, 11, 32), "throne": (42, 24, 51, 32), "gallery": (2, 15, 51, 19),
    "chamber_w": (13, 28, 17, 33), "chamber_e": (36, 28, 40, 33), "vault_w": (10, 10, 16, 13), "vault_e": (37, 10, 43, 13),
    "gate_lane": (24, 9, 27, 14), "boss": (15, 1, 38, 8)}
F_LINKS = [(25, 45, 28, 46), (11, 40, 12, 43), (41, 40, 42, 43), (25, 35, 28, 37), (5, 33, 6, 36), (47, 33, 48, 36), (5, 20, 6, 23), (47, 20, 48, 23),
           (25, 20, 28, 27), (18, 30, 19, 31), (34, 30, 35, 31), (12, 14, 13, 14), (40, 14, 41, 14)]
for rect in list(F_ROOMS.values()) + F_LINKS:
    carve(*rect)
_flood, _stack = set(), [(26, 50)]
while _stack:
    c, r = _stack.pop()
    if (c, r) in _flood or not (0 <= c < COLS and 0 <= r < ROWS) or grid[r][c] == "#":
        continue
    _flood.add((c, r))
    _stack += [(c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)]
assert _flood == {(c, r) for r in range(ROWS) for c in range(COLS) if grid[r][c] != "#"}, "há piso do Forte sem ligação com a partida"
FLOOR_CELLS = len(_flood)


def is_rock(c, r):
    return c < 0 or r < 0 or c >= COLS or r >= ROWS or grid[r][c] == "#"


def cp(c, r):
    return [round((c - COLS / 2 + 0.5) * CELL, 2), round((r - ROWS / 2 + 0.5) * CELL, 2)]


def room_pos(name, dc=0.0, dr=0.0):
    c0, r0, c1, r1 = F_ROOMS[name]
    return cp((c0 + c1) / 2 + dc, (r0 + r1) / 2 + dr)


def to_cell(x, z):
    return int(math.floor(x / CELL + COLS / 2)), int(math.floor(z / CELL + ROWS / 2))


def floor_clear(x, z, margin=1):
    c, r = to_cell(x, z)
    return all(not is_rock(c + i, r + j) for i in range(-margin, margin + 1) for j in range(-margin, margin + 1))


# ---------------------------------------------------------------- pedra do pacote (peças Fort_<máscara>) e colisão
decor = []
available = set(f[5:13] for f in os.listdir("assets/models/maps/fort") if f.startswith("Fort_") and f.endswith(".gltf") and f != "Fort_Floor.gltf")
NEIGH = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
for r in range(ROWS):
    for c in range(COLS):
        if grid[r][c] != "#":
            continue
        bits = [is_rock(c + dx, r + dz) for dx, dz in NEIGH]
        for i in (1, 3, 5, 7):
            bits[i] = bits[i] and bits[(i - 1) % 8] and bits[(i + 1) % 8]
        mask = "".join("1" if b else "0" for b in bits)
        if mask == "11111111" and not any(not is_rock(c + dx, r + dz) for dx in range(-2, 3) for dz in range(-2, 3)):
            continue
        rotation = 0
        if mask not in available:
            for k in (1, 2, 3):
                turned = "".join(mask[(i - 2 * k) % 8] for i in range(8))
                if turned in available:
                    mask, rotation = turned, -90 * k
                    break
            else:
                mask = "11111111" if mask.count("1") > 6 else "00000000"
        entry = {"piece": "Fort_" + mask, "position": cp(c, r)}
        if rotation:
            entry["rotation"] = rotation
        decor.append(entry)
for r in range(ROWS):
    c = 0
    while c < COLS:
        if grid[r][c] == "#":
            c0 = c
            while c < COLS and grid[r][c] == "#":
                c += 1
            x0, z = cp(c0, r)
            x1, _ = cp(c - 1, r)
            decor.append({"collider": [round(x1 - x0 + CELL, 2), CELL], "position": [round((x0 + x1) / 2, 2), z]})
        else:
            c += 1

# ---------------------------------------------------------------- monstros novos e itens
def clone(name, base, **changes):
    m = json.loads(json.dumps(monsters[base]))
    m.pop("_comment", None)
    m.pop("quest_drop", None)
    m.update(changes)
    monsters[name] = m


monsters["succubus_queen"].update({"quest_drop": "queen_ring"})
monsters["dark_elf_lord"].update({"quest_drop": "dark_blade"})
clone("fort_baron", "sphinx", _comment="Chefe final do Forte: o Barão Infernal, demônio que governa o Salão do Barão atrás do portão; investidas e pisões (modelo do demônio chefe).",
      name_key="MONSTER_FORT_BARON", max_health=1300, damage=44, size=3.8, element="fire", look="demon_boss", color=[1.0, 0.75, 0.75], chest_loot="chest")
valuables.update({
    "dark_blade": {"name_key": "VALUABLE_DARK_BLADE", "value": 0, "maps": [], "quest_item": True, "model": "Sword_D"},
    "queen_ring": {"name_key": "VALUABLE_QUEEN_RING", "value": 0, "maps": [], "quest_item": True, "model": "Crystal_Gem"},
    "key_ruby": {"name_key": "VALUABLE_KEY_RUBY", "value": 0, "maps": [], "quest_item": True, "model": "Key_Hearts"},
    "key_onyx": {"name_key": "VALUABLE_KEY_ONYX", "value": 0, "maps": [], "quest_item": True, "model": "Key_Spades"}})

# ---------------------------------------------------------------- objetos do mapa
SUMMON_QUEEN = {"id": "fo_succubus_queen", "position": cp(46, 27), "spread": 3.0, "toast": "TOAST_PENITENT_AWAKENS", "monsters": [{"monster": "succubus_queen", "count": 1, "rank": "miniboss"}]}
SUMMON_LORD = {"id": "fo_dark_elf_lord", "position": cp(7, 27), "spread": 3.0, "toast": "TOAST_EXILE_AWAKENS", "monsters": [{"monster": "dark_elf_lord", "count": 1, "rank": "miniboss"}]}
props = [
    {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": cp(22, 50), "to": "capital_01_aurenhold", "entry": "fort", "expedition_end": False},
    {"id": "victory_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": cp(26.5, 1.6), "to": "capital_01_aurenhold", "entry": "fort", "after_victory": True, "group": True},
    {"id": "fort_sergeant", "kind": "npc", "npc": "fort_sergeant", "position": cp(30, 50), "rotation": 270},
    {"id": "fort_exile", "kind": "npc", "npc": "fort_exile", "position": cp(4, 31), "rotation": 90, "summon": SUMMON_LORD, "needs_quest": "fort_sigil"},
    {"id": "fort_penitent", "kind": "npc", "npc": "fort_penitent", "position": cp(49, 31), "rotation": 270, "summon": SUMMON_QUEEN, "needs_quest": "fort_ring"},
    {"id": "boss_gate", "kind": "gate", "name_key": "PROP_BOSS_GATE", "position": cp(25.5, 11), "rotation": 0, "scale": 2.5, "block": 10.0, "count": 2, "opened_by": "fort_gate"},
    {"id": "fort_gatekeeper", "kind": "npc", "npc": "fort_gatekeeper", "position": cp(25.5, 13), "rotation": 0}]
chests = [("fort_chest_1", cp(15, 30), "chest"), ("fort_chest_2", cp(38, 30), "chest"), ("fort_chest_3", cp(13, 11.5), "chest"), ("fort_chest_4", cp(40, 11.5), "chest"),
          ("fort_chest_5", cp(3, 17), "chest"), ("fort_chest_6", cp(50, 17), "chest"),
          ("fort_potions_1", cp(3, 43), "potion_chest"), ("fort_potions_2", cp(50, 43), "potion_chest"), ("fort_potions_3", cp(22, 29), "potion_chest"), ("fort_potions_4", cp(31, 29), "potion_chest"),
          ("fort_potions_5", cp(3, 25), "potion_chest"), ("fort_potions_6", cp(50, 25), "potion_chest"), ("fort_potions_7", cp(17, 3), "potion_chest"), ("fort_potions_8", cp(36, 3), "potion_chest")]
for cid, pos, loot in chests:
    p = {"id": cid, "kind": "chest", "position": pos, "loot": loot}
    if loot == "potion_chest":
        p["model"] = "Chest_Mini"
    props.append(p)
E = lambda eid, pos, *mons: {"id": eid, "position": pos, "monsters": [{"monster": m, "count": c} for m, c in mons]}
encounters = [
    E("fo_yard_a", cp(19, 41), ("dark_elf", 3), ("plague_bat", 2)), E("fo_yard_b", cp(34, 41), ("succubus", 2), ("dark_elf", 1)),
    E("fo_commander", cp(26.5, 40.5), ("fort_commander", 1), ("dark_elf", 2)),
    E("fo_barracks_w", cp(6, 41), ("dark_elf", 3), ("plague_bat", 2)), E("fo_barracks_e", cp(47, 41), ("succubus", 3)),
    E("fo_corr_w", cp(5.5, 34.5), ("plague_bat", 3)), E("fo_corr_e", cp(47.5, 34.5), ("plague_bat", 3)),
    E("fo_ossuary", cp(9, 30), ("succubus", 2), ("dark_elf", 2)), E("fo_throne", cp(44, 30), ("venom_scorpion", 3), ("mutant_frog", 2)),
    E("fo_cross_a", cp(23, 31), ("dark_elf", 3)), E("fo_cross_b", cp(30, 31), ("succubus", 3)), E("fo_cross_c", cp(26.5, 24), ("plague_bat", 4)),
    E("fo_gallery_a", cp(8, 17), ("dark_elf", 3)), E("fo_gallery_b", cp(18, 17), ("venom_scorpion", 3)), E("fo_gallery_c", cp(33, 17), ("mutant_frog", 3)), E("fo_gallery_d", cp(45, 17), ("succubus", 3)),
    E("fo_up_w", cp(5.5, 21.5), ("plague_bat", 3)), E("fo_up_e", cp(47.5, 21.5), ("plague_bat", 3)),
    E("fo_mimic_w", cp(14, 31), ("chest_mimic", 1)), E("fo_mimic_e", cp(39, 31), ("chest_mimic", 1)),
    E("fo_mimic_vw", cp(12, 11.5), ("chest_mimic", 1)), E("fo_mimic_ve", cp(41, 11.5), ("chest_mimic", 1)),
    E("fo_guard_a", cp(20, 6), ("dark_elf", 2), ("succubus", 1)), E("fo_guard_b", cp(33, 6), ("dark_elf", 2), ("succubus", 1)),
    E("fo_boss", cp(26.5, 3.6), ("fort_baron", 1))]
interest = [p["position"] for p in props] + [e["position"] for e in encounters] + [SUMMON_QUEEN["position"], SUMMON_LORD["position"], cp(26, 50)]
for l0, r0, l1, r1 in F_LINKS:
    interest.append(cp((l0 + l1) / 2, (r0 + r1) / 2))
interest += [cp(25.5, 11), cp(25.5, 13)]

taken = []


def near_interest(x, z, rad):
    return any(math.hypot(x - ix, z - iz) < rad for ix, iz in interest)


def near_taken(x, z, rad):
    return any(math.hypot(x - tx, z - tz) < tr + rad for tx, tz, tr in taken)


def put(piece, x, z, rot=None, scale=1.0, solid=None, y=None, r=0.8, free=2.4, force=False, margin=1):
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


def scatter(name, pieces, n, scale=(1.0, 1.0), solid=None, r=0.9, tries=50, inset=1, **kw):
    c0, r0, c1, r1 = F_ROOMS[name]
    done = 0
    for _ in range(n):
        for _t in range(tries):
            x, z = cp(rng.uniform(c0 + inset, c1 - inset), rng.uniform(r0 + inset, r1 - inset))
            s = rng.uniform(*scale)
            if put(rng.choice(pieces) if isinstance(pieces, list) else pieces, x, z, scale=s, solid=[solid[0] * s, solid[1] * s] if solid else None, r=r * s, **kw):
                done += 1
                break
    return done


def light(x, z, color=(1.0, 0.65, 0.3), rng_=9.5, energy=1.3, y=2.2):
    decor.append({"light": list(color), "position": [round(x, 2), round(z, 2)], "y": y, "range": rng_, "energy": energy})


def brazier(c, r, scale=1.4):
    x, z = cp(c, r)
    if put("Tv_Fire", x, z, rot=0, scale=scale, solid=[0.9 * scale, 0.7 * scale], r=1.2, free=0.5):
        decor.append({"piece": "Fire_Flame", "position": [x, z], "y": 0.2, "scale": round(scale * 0.9, 2), "flicker": True})
        light(x, z, (1.0, 0.6, 0.25), 10.0, 1.5, 1.2)


# --- luzes quentes: uma por sala (quatro na partida); vermelhas nas salas dos mini-chefes; roxa no Salão do Barão
for name in F_ROOMS:
    if name in ("start", "ossuary", "throne", "boss"):
        continue
    light(*room_pos(name), rng_=10.0 if name in ("armory", "gallery") else 9.0)
for c, r in ((23, 49), (30, 49), (23, 51), (30, 51)):
    light(*cp(c, r), rng_=8.0, energy=1.0)
for name in ("ossuary", "throne"):
    light(*room_pos(name), (0.85, 0.3, 0.25), 11.0, 1.2)
light(*room_pos("boss"), (0.7, 0.4, 0.9), 14.0, 1.5, 2.4)
for dc in (-7, 7):
    light(*room_pos("armory", dc), rng_=9.0)
    light(*room_pos("gallery", dc * 3), rng_=9.0)

# --- portões em arco do castelo (3D Castle Dungeon Tileset, rubberduck, CC0) nas passagens; colunas, altares e plataformas
for kind, span, fixed in (("v", range(25, 29), 45), ("h", range(40, 44), 11), ("h", range(40, 44), 41), ("v", range(25, 29), 36), ("v", (5, 6), 34), ("v", (47, 48), 34), ("v", (5, 6), 21), ("v", (47, 48), 21),
                          ("v", range(25, 29), 22), ("h", (30, 31), 18), ("h", (30, 31), 34), ("v", (12, 13), 14), ("v", (40, 41), 14)):
    for k in span:
        if kind == "v":
            decor.append({"piece": "Castle_GateBig", "position": cp(k, fixed)})
        else:
            decor.append({"piece": "Castle_GateBig", "position": cp(fixed, k), "rotation": 90})
col = lambda c, r, n="Column": decor.append({"piece": "Castle_" + n, "position": cp(c, r), "solid": [0.9, 0.9]})
for c in (15, 19, 23, 30, 34, 38):                    # Pátio de Armas: duas fileiras de colunas
    col(c, 39), col(c, 43)
for c, r in ((22, 29), (31, 29), (22, 33), (31, 33)):  # Salão das Colunas
    col(c, r)
for c in (3, 9, 16, 20, 31, 35, 44, 50):               # Galeria
    col(c, 17)
for c in (18, 22, 31, 35):                             # Salão do Barão
    col(c, 3), col(c, 6)
for c, r in ((22, 51), (31, 51)):
    col(c, r, "EdgeColumn")
for c in (17, 36):
    decor.append({"piece": "Castle_Altar", "position": cp(c, 1.6), "solid": [1.2, 1.2]})
decor += [{"piece": "Castle_Dais", "position": cp(46, 25)}, {"piece": "Castle_Altar", "position": cp(48, 25), "solid": [1.2, 1.2]}]
decor += [{"piece": "Castle_Tiles", "position": [round(cp(26, 40)[0] + i * 1.3, 2), round(cp(26, 40)[1] + j * 1.3, 2)]} for i in range(4) for j in range(3)]
# --- Labirinto (3D Walls & Props, deadkir, CC0): caixões no Ossuário, barris e caixotes na partida e nos quartéis, escudo com espada caídos perto do chefe
for c, r in ((3, 25), (6, 25), (9, 25), (3, 28), (3, 29)):
    decor.append({"piece": "Lab_Coffin", "position": cp(c, r), "rotation": 0 if r == 25 else 90, "solid": [2.0, 0.9] if r == 25 else [0.9, 2.0]})
for c, r in ((22, 47), (31, 47), (22, 48), (31, 48), (3, 38), (9, 38), (44, 38), (50, 38)):
    decor.append({"piece": "Lab_Barrel", "position": cp(c, r), "solid": [0.6, 0.6]})
for c, r in ((22, 52), (31, 52), (3, 44), (9, 44), (44, 44), (50, 44)):
    decor.append({"piece": "Lab_Crate", "position": cp(c, r), "rotation": rng.randrange(0, 360, 15), "solid": [0.6, 0.6]})
decor.append({"piece": "Lab_ShieldSword", "position": cp(22, 6), "rotation": 25})
for name in ("armory", "gallery", "cross", "chamber_w", "chamber_e", "vault_w", "vault_e", "barracks_w", "barracks_e", "ossuary", "throne", "boss", "start"):
    c0, r0, c1, r1 = F_ROOMS[name]
    for _ in range(3 if name in ("armory", "gallery", "boss") else 2):
        x, z = cp(rng.uniform(c0 + 1, c1 - 1), rng.uniform(r0 + 1, r1 - 1))
        kind = rng.choice(("barrels", "crate", "coffin", "ruin", "column"))
        if kind == "barrels":
            put("Lab_Barrel", x, z, solid=[0.6, 0.6], r=0.8)
            put("Lab_Barrel", x + 0.7, z, solid=[0.6, 0.6], r=0.8)
        elif kind == "crate":
            put("Lab_Crate", x, z, solid=[0.6, 0.6], r=0.8)
        elif kind == "coffin":
            put("Lab_Coffin", x, z, rot=0, solid=[2.0, 0.9], r=1.4)
        elif kind == "ruin":
            put(rng.choice(("Lab_WallBroken", "Lab_WallLong")), x, z, rot=0, solid=[1.3, 0.32], r=1.2)
            put("Lab_ColumnBroken", x - 1.2, z + 0.3, solid=[0.32, 0.32], r=0.6)
        else:
            put("Lab_ColumnBig", x, z, solid=[0.63, 0.63], r=0.8)
# --- canhões de navio (a boca para +Z com rotação 0): dois na partida apontados ao forte (norte), dois no Salão do Barão apontados à porta (sul)
for c, r, rot in ((24, 52, 180), (29, 52, 180), (18, 8, 0), (35, 8, 0)):
    decor.append({"piece": "Ship_Cannon", "position": cp(c, r), "rotation": rot, "solid": [0.8, 1.5]})
# --- forcas (Gibbet, CC BY?): no Pátio de Armas e no Ossuário
for name, n in (("armory", 4), ("ossuary", 2), ("throne", 2), ("gallery", 3)):
    scatter(name, ["Gibbet"], n, solid=(1.0, 1.0), r=1.3, inset=2)
# --- acampamento e arsenal: braseiros, estandartes, armas, escudos, barris, ossos, teias, tesouros
for name, cells in (("armory", ((17, 39), (36, 39), (17, 43), (36, 43), (26, 38))), ("barracks_w", ((4, 40), (8, 42))), ("barracks_e", ((45, 40), (49, 42))),
                    ("start", ((24, 48), (29, 48))), ("cross", ((24, 31), (29, 31))), ("ossuary", ((8, 30), (5, 27))), ("throne", ((44, 28), (49, 27))),
                    ("gallery", ((7, 17), (13, 17), (24, 17), (29, 17), (40, 17), (46, 17))), ("boss", ((17, 4), (36, 4), (21, 7), (32, 7)))):
    for c, r in cells:
        brazier(c, r)
for name, n in (("armory", 14), ("gallery", 16), ("boss", 10), ("barracks_w", 8), ("barracks_e", 8), ("start", 6), ("cross", 8)):
    scatter(name, ["War_Banner"], max(2, n // 4), scale=(1.1, 1.3), r=1.0, inset=1, rot=0)
    scatter(name, ["Weapon_Rack", "Shield_A", "Shield_B", "Shield_C", "Shield_D", "Sword_A", "Sword_B", "Sword_C", "Barrel_Oga_1", "Crate_Big", "Crate_Small", "Tv_Sack"], n, scale=(1.0, 1.3), r=0.9)
for name, n in (("ossuary", 14), ("throne", 8), ("boss", 18), ("vault_w", 6), ("vault_e", 6), ("chamber_w", 6), ("chamber_e", 6), ("gallery", 12), ("armory", 8)):
    scatter(name, ["Dungeon_BonePile_%d" % i for i in range(1, 7)] + ["Dungeon_CrossBones", "Dungeon_Skull_1", "Dungeon_Skull_2", "Dungeon_Pelvis", "Dungeon_Ribcage"], n, scale=(2.2, 3.2), r=0.8)
scatter("boss", ["Dungeon_SkullPile"], 4, scale=(3.0, 4.2), r=1.2)
for name, n in (("ossuary", 6), ("throne", 4), ("cross", 4), ("chamber_w", 3), ("chamber_e", 3), ("vault_w", 3), ("vault_e", 3), ("boss", 5), ("gallery", 6)):
    scatter(name, ["Web_Round_Up", "Web_Round_Flat", "Web_Square_Up", "Web_Square_Flat"], n, scale=(1.5, 2.2), r=1.0)
for name in ("chamber_w", "chamber_e", "vault_w", "vault_e", "boss"):
    scatter(name, ["Coin_Pile", "Chest_Large", "Cage_Small"], 3, scale=(1.3, 1.7), r=1.2)
# --- tochas de parede (Wall mounted torch, scribe, CC BY 3.0): presas na face da pedra voltada para o piso, com 6 m entre elas; metade com luz de chama
wt_rng = random.Random("fort2_wall_torches")
wt_cells = []
for r in range(ROWS):
    for c in range(COLS):
        if grid[r][c] == "#":
            continue
        for dx, dz in ((0, -1), (1, 0), (-1, 0)):
            if is_rock(c + dx, r + dz) and 0 < c + dx < COLS - 1 and 0 < r + dz < ROWS - 1:
                wt_cells.append((c, r, dx, dz))
wt_rng.shuffle(wt_cells)
wt_placed = []
for c, r, dx, dz in wt_cells:
    x, z = cp(c, r)
    if any(math.hypot(x - px, z - pz) < 6.0 for px, pz, _, _ in wt_placed):
        continue
    wt_placed.append((x, z, dx, dz))
    if len(wt_placed) == 70:
        break
for i, (x, z, dx, dz) in enumerate(wt_placed):
    decor.append({"piece": "Wall_Torch", "position": [round(x + dx * (CELL / 2 - 0.02), 2), round(z + dz * (CELL / 2 - 0.02), 2)], "rotation": round(math.degrees(math.atan2(-dx, -dz)))})
    if i % 2 == 0:
        decor.append({"light": [1.0, 0.6, 0.25], "position": [round(x - dx * 0.2, 2), round(z - dz * 0.2, 2)], "y": 1.9, "range": 5.5, "energy": 0.9})
# --- ratos pequenos de cenário
fr = random.Random("fort2_rats")
floor_cells = [(c, r) for r in range(ROWS) for c in range(COLS) if grid[r][c] != "#"]
rats = []
while len(rats) < 36:
    c, r = fr.choice(floor_cells)
    c2, r2 = c + fr.randint(-3, 3), r + fr.randint(-3, 3)
    if (c2, r2) == (c, r) or not (0 <= c2 < COLS and 0 <= r2 < ROWS) or grid[r2][c2] == "#":
        continue
    if any(grid[r + round((r2 - r) * t / 6)][c + round((c2 - c) * t / 6)] == "#" for t in range(7)):
        continue
    a, b = cp(c, r), cp(c2, r2)
    rats.append({"role": "rat", "position": [round(a[0] + fr.uniform(-0.8, 0.8), 2), round(a[1] + fr.uniform(-0.8, 0.8), 2)], "path": b, "speed": round(fr.uniform(1.2, 2.2), 1), "pose": "walk"})

breakables = [{"id": "coin_bag", "monster": "coin_bag", "position": [round(cp(26, 50)[0] + 4.0, 1), round(cp(26, 50)[1] - 1.5, 1)], "table": "coin_bag"}]
for i, (c, r) in enumerate(((20, 41), (33, 41), (6, 38), (47, 38), (8, 27), (45, 27), (26.5, 31), (14, 17), (40, 17), (26.5, 6)), start=2):
    breakables.append({"id": "coin_bag_%d" % i, "monster": "coin_bag", "position": cp(c, r), "table": "coin_bag"})

arenas["fort_01_gate"] = {
    "_comment": "Forte, ampliado (3D Dungeon Tileset, Skorpio, CC BY-SA 3.0): grade de 54 x 54 células de 2,5 m com pedra e piso do pacote (Fort_<máscara>); a colisão é uma caixa por trecho de pedra. Estrutura da Floresta com outro "
                "caminho: Guarnição (partida) -> Pátio de Armas -> três rotas para a Galeria (oeste: Quartel -> Ossuário, onde o Exilado desperta o Senhor Elfo Sombrio; leste: Quartel -> Salão do Trono, onde a Penitente "
                "desperta a Rainha das Súcubos; meio: Salão das Colunas) -> corredor do portão (Carcereiro, duas chaves) -> Salão do Barão (Barão Infernal, chefe final, com a saída). O Comandante anda solto no Pátio de Armas. "
                "Gerado por tools/assets/build_fort.py.",
    "name_key": "ARENA_FORT", "player_class": "mage", "map_id": "map_fort", "area_level": 10, "final": True, "victory_groups": ["fo_boss"], "wake_radius": 10.0, "alert_radius": 5.0,
    "rooms": [{"id": "fort", "center": [0, 0], "size": [COLS * CELL, ROWS * CELL], "doors": [], "wall_height": 0.8, "torch": False}],
    "encounters": encounters, "hazards": [], "entries": {"start": cp(26, 50)}, "props": props, "quest_spots": [], "breakables": breakables,
    "style": {"_comment": "Forte: piso de pedra do pacote; a pedra vem das peças Fort_* em decor.", "walls": [""], "floor": "Fort_Floor", "low": "", "ground": [0.07, 0.07, 0.08]},
    "decor": decor, "crowd": rats, "passive": True}


# ---------------------------------------------------------------- NPCs e missões
def body(sex, hair, color):
    return {"sex": sex, "hair": [hair], "hair_color": color, "pose": "idle", "outfit": {"body": "cloth"}}


npcs["fort_sergeant"] = {"name_key": "NPC_FORT_SERGEANT", "color": [0.5, 0.35, 0.3], "dialogues": [
    {"when": {"quest_new": "fort_purge"}, "lines": ["DLG_FSERGEANT_1", "DLG_FSERGEANT_2", "DLG_FSERGEANT_3"], "offer": "fort_purge"},
    {"when": {"quest_active": "fort_purge"}, "lines": ["DLG_FSERGEANT_ACTIVE"]}, {"when": {}, "lines": ["DLG_FSERGEANT_DONE"]}], "body": body("male", "Hair_Buzzed", [0.2, 0.15, 0.1])}
npcs["fort_exile"] = {"name_key": "NPC_FORT_EXILE", "color": [0.5, 0.55, 0.65], "dialogues": [
    {"when": {"quest_new": "fort_sigil"}, "lines": ["DLG_FEXILE_1", "DLG_FEXILE_2", "DLG_FEXILE_3"], "offer": "fort_sigil"},
    {"when": {"quest_active": "fort_sigil"}, "lines": ["DLG_FEXILE_ACTIVE"], "service": "turn_in"},
    {"when": {"quest_done": "fort_sigil"}, "lines": ["DLG_FEXILE_DONE"]}, {"when": {}, "lines": ["DLG_FEXILE_WAIT"]}], "body": body("male", "Hair_Beard", [0.3, 0.28, 0.25])}
npcs["fort_penitent"] = {"name_key": "NPC_FORT_PENITENT", "color": [0.75, 0.55, 0.8], "dialogues": [
    {"when": {"quest_new": "fort_ring"}, "lines": ["DLG_FPENITENT_1", "DLG_FPENITENT_2", "DLG_FPENITENT_3"], "offer": "fort_ring"},
    {"when": {"quest_active": "fort_ring"}, "lines": ["DLG_FPENITENT_ACTIVE"], "service": "turn_in"},
    {"when": {"quest_done": "fort_ring"}, "lines": ["DLG_FPENITENT_DONE"]}, {"when": {}, "lines": ["DLG_FPENITENT_WAIT"]}], "body": body("female", "Hair_Long", [0.2, 0.1, 0.25])}
npcs["fort_gatekeeper"] = {"name_key": "NPC_FORT_GATEKEEPER", "color": [0.35, 0.35, 0.4], "dialogues": [
    {"when": {"quest_new": "fort_gate"}, "lines": ["DLG_FGUARD_1", "DLG_FGUARD_2", "DLG_FGUARD_3"], "offer": "fort_gate"},
    {"when": {"quest_active": "fort_gate"}, "lines": ["DLG_FGUARD_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_FGUARD_DONE"]}], "body": body("male", "Hair_Beard", [0.1, 0.1, 0.12])}
quests["fort_purge"] = {"name_key": "QUEST_FORT_PURGE", "desc_key": "QUEST_FORT_PURGE_DESC", "type": "village", "giver": "fort_sergeant", "area": "fort_01_gate",
                        "clear": ["fo_barracks_w", "fo_barracks_e"], "target_element": "fire", "reward": {"gold": 450, "xp": 900}}
quests["fort_sigil"] = {"name_key": "QUEST_FORT_SIGIL", "desc_key": "QUEST_FORT_SIGIL_DESC", "type": "village", "giver": "fort_exile", "area": "fort_01_gate", "target_element": "air",
                        "reward": {"gold": 500, "xp": 1000}, "item": "dark_blade", "gives": "key_onyx"}
quests["fort_ring"] = {"name_key": "QUEST_FORT_RING", "desc_key": "QUEST_FORT_RING_DESC", "type": "village", "giver": "fort_penitent", "area": "fort_01_gate", "target_element": "fire",
                       "reward": {"gold": 500, "xp": 1000}, "item": "queen_ring", "gives": "key_ruby"}
quests["fort_gate"] = {"name_key": "QUEST_FORT_GATE", "desc_key": "QUEST_FORT_GATE_DESC", "type": "village", "giver": "fort_gatekeeper", "area": "fort_01_gate",
                       "items": ["key_ruby", "key_onyx"], "opens_gate": "boss_gate", "target_element": "fire", "reward": {"gold": 600, "xp": 1200}}
T = {
    "MONSTER_FORT_BARON": ("Barão Infernal", "Infernal Baron", "Barón Infernal"),
    "NPC_FORT_SERGEANT": ("Sargento da Guarnição", "Garrison Sergeant", "Sargento de la Guarnición"),
    "NPC_FORT_GATEKEEPER": ("Carcereiro do Forte", "Fort Jailer", "Carcelero del Fuerte"),
    "VALUABLE_DARK_BLADE": ("Lâmina do Senhor Elfo", "Elf Lord's Blade", "Hoja del Señor Elfo"),
    "VALUABLE_QUEEN_RING": ("Anel da Rainha", "Queen's Ring", "Anillo de la Reina"),
    "VALUABLE_KEY_RUBY": ("Chave de Rubi", "Ruby Key", "Llave de Rubí"),
    "VALUABLE_KEY_ONYX": ("Chave de Ônix", "Onyx Key", "Llave de Ónix"),
    "QUEST_FORT_PURGE": ("Limpar os Quartéis", "Clear the Barracks", "Limpiar los cuarteles"),
    "QUEST_FORT_PURGE_DESC": ("O Sargento da Guarnição pede que os dois quartéis, o Oeste e o Leste (logo depois do Pátio de Armas), sejam limpos dos soldados amaldiçoados que ainda os ocupam.",
                              "The Garrison Sergeant asks that both barracks, West and East (just past the Armory Yard), be cleared of the cursed soldiers still holding them.",
                              "El Sargento de la Guarnición pide que los dos cuarteles, Oeste y Este (justo después del Patio de Armas), se limpien de los soldados malditos que aún los ocupan."),
    "QUEST_FORT_SIGIL": ("A Lâmina do Senhor Elfo", "The Elf Lord's Blade", "La hoja del Señor Elfo"),
    "QUEST_FORT_SIGIL_DESC": ("O Exilado, no Ossuário a oeste, quer de volta a lâmina que o Senhor Elfo Sombrio lhe tomou. A fala dele desperta o Senhor Elfo Sombrio; derrote-o e traga a lâmina: em troca vem a Chave de Ônix, uma das duas do portão do Barão.",
                              "The Exile, in the Ossuary to the west, wants back the blade the Dark Elf Lord took from him. His words wake the Dark Elf Lord; defeat him and bring the blade: in return you get the Onyx Key, one of the two for the Baron's gate.",
                              "El Exiliado, en el Osario al oeste, quiere recuperar la hoja que le quitó el Señor Elfo Oscuro. Sus palabras despiertan al Señor Elfo Oscuro; derrótalo y trae la hoja: a cambio recibes la Llave de Ónix, una de las dos del portón del Barón."),
    "QUEST_FORT_RING": ("O Anel da Rainha", "The Queen's Ring", "El anillo de la Reina"),
    "QUEST_FORT_RING_DESC": ("A Penitente, no Salão do Trono a leste, jurou devolver o anel que a Rainha das Súcubos usa. A fala dela desperta a Rainha; derrote-a e traga o anel para receber a Chave de Rubi, a outra do portão do Barão.",
                             "The Penitent, in the Throne Hall to the east, swore to return the ring the Succubus Queen wears. Her words wake the Queen; defeat her and bring the ring to receive the Ruby Key, the other one for the Baron's gate.",
                             "La Penitente, en el Salón del Trono al este, juró devolver el anillo que lleva la Reina de las Súcubos. Sus palabras despiertan a la Reina; derrótala y trae el anillo para recibir la Llave de Rubí, la otra del portón del Barón."),
    "QUEST_FORT_GATE": ("O Portão do Barão", "The Baron's Gate", "El portón del Barón"),
    "QUEST_FORT_GATE_DESC": ("O Carcereiro do Forte, no corredor ao norte da Galeria, só abre o portão para quem trouxer as duas chaves: a de Ônix (Exilado) e a de Rubi (Penitente). Atrás dele fica o Salão do Barão Infernal.",
                             "The Fort Jailer, in the lane north of the Gallery, only opens the gate for those with both keys: the Onyx (Exile) and the Ruby (Penitent). Beyond lies the Infernal Baron's Hall.",
                             "El Carcelero del Fuerte, en el pasillo al norte de la Galería, solo abre el portón a quien traiga las dos llaves: la de Ónix (Exiliado) y la de Rubí (Penitente). Tras él está el Salón del Barón Infernal."),
    "DLG_FSERGEANT_1": ("Bem-vindos à Guarnição. Era daqui que o reino vigiava o sul, até o Barão abrir as portas lá embaixo e a guarnição inteira se levantar de novo, de olhos vazios.",
                        "Welcome to the Garrison. This is where the kingdom watched the south, until the Baron opened the doors below and the whole garrison rose again, eyes empty.",
                        "Bienvenidos a la Guarnición. Desde aquí el reino vigilaba el sur, hasta que el Barón abrió las puertas de abajo y toda la guarnición se levantó de nuevo, con los ojos vacíos."),
    "DLG_FSERGEANT_2": ("Os dois quartéis, o Oeste e o Leste, ficam depois do Pátio de Armas, e ainda estão cheios deles. Enquanto não forem limpos, nada passa pelas rotas do norte.",
                        "The two barracks, West and East, lie past the Armory Yard, and are still full of them. Until they are cleared, nothing gets through the northern routes.",
                        "Los dos cuarteles, Oeste y Este, quedan tras el Patio de Armas, y aún están llenos de ellos. Mientras no se limpien, nada pasa por las rutas del norte."),
    "DLG_FSERGEANT_3": ("Limpem os dois e eu pago pelo trabalho. Depois disso, o Exilado e a Penitente têm contas a acertar, cada um num canto do forte, e são eles que guardam as chaves do portão do Barão.",
                        "Clear both and I will pay for the work. After that, the Exile and the Penitent have scores to settle, each in a corner of the fort, and they keep the keys to the Baron's gate.",
                        "Limpien los dos y pagaré el trabajo. Después, el Exiliado y la Penitente tienen cuentas pendientes, cada uno en un rincón del fuerte, y ellos guardan las llaves del portón del Barón."),
    "DLG_FSERGEANT_ACTIVE": ("Os quartéis ficam a oeste e a leste do Pátio de Armas, atrás dos portões de arco. Ouçam os passos antes de abrir a porta.",
                             "The barracks are west and east of the Armory Yard, behind the arched gates. Listen for the footsteps before you open the door.",
                             "Los cuarteles están al oeste y al este del Patio de Armas, tras los portones en arco. Escuchen los pasos antes de abrir la puerta."),
    "DLG_FSERGEANT_DONE": ("Os quartéis estão calmos pela primeira vez em anos. Sigam pelo oeste ou pelo leste: a Galeria os espera lá em cima.",
                           "The barracks are calm for the first time in years. Go west or east: the Gallery awaits you up there.",
                           "Los cuarteles están en calma por primera vez en años. Sigan por el oeste o por el este: la Galería los espera arriba."),
    "DLG_FEXILE_1": ("Cavaleiro caído, é o que sou. Servi o Barão até ele me expulsar por recusar a ordem de queimar a vila. Agora vivo entre os caixões do Ossuário, como o resto dos esquecidos.",
                     "A fallen knight, that is what I am. I served the Baron until he cast me out for refusing the order to burn the village. Now I live among the Ossuary's coffins, like the rest of the forgotten.",
                     "Un caballero caído, eso soy. Serví al Barón hasta que me expulsó por negarme a quemar la aldea. Ahora vivo entre los ataúdes del Osario, como el resto de los olvidados."),
    "DLG_FEXILE_2": ("O Senhor Elfo Sombrio, líder dos besteiros, me tomou a lâmina na noite em que me expulsaram. Ele a guarda aqui no fundo do Ossuário, como troféu, e dorme de olhos abertos.",
                     "The Dark Elf Lord, captain of the crossbowmen, took my blade the night I was cast out. He keeps it here at the back of the Ossuary as a trophy, and sleeps with his eyes open.",
                     "El Señor Elfo Oscuro, líder de los ballesteros, me quitó la hoja la noche en que me expulsaron. La guarda aquí al fondo del Osario, como trofeo, y duerme con los ojos abiertos."),
    "DLG_FEXILE_3": ("Vou chamá-lo para vocês. Derrubem-no e tragam a lâmina: eu dou a Chave de Ônix, uma das duas que abrem o portão do Barão, no corredor ao norte da Galeria.",
                     "I will call him for you. Bring him down and bring the blade: I give the Onyx Key, one of the two that open the Baron's gate, in the lane north of the Gallery.",
                     "Lo llamaré para ustedes. Derríbenlo y traigan la hoja: doy la Llave de Ónix, una de las dos que abren el portón del Barón, en el pasillo al norte de la Galería."),
    "DLG_FEXILE_ACTIVE": ("A lâmina é longa e escura, de punho de osso. Ele a leva às costas. Derrubem-no e eu a reconheço de longe.",
                          "The blade is long and dark, with a bone hilt. He carries it on his back. Bring him down and I will know it from afar.",
                          "La hoja es larga y oscura, con empuñadura de hueso. La lleva a la espalda. Derríbenlo y la reconoceré de lejos."),
    "DLG_FEXILE_DONE": ("Minha lâmina! Enfim posso morrer como cavaleiro. A Chave de Ônix é de vocês: levem-na ao Carcereiro, junto com a de Rubi.",
                        "My blade! At last I can die as a knight. The Onyx Key is yours: take it to the Jailer, together with the Ruby one.",
                        "¡Mi hoja! Por fin puedo morir como caballero. La Llave de Ónix es suya: llévenla al Carcelero, junto con la de Rubí."),
    "DLG_FEXILE_WAIT": ("Os caixões estão quietos hoje. Voltem quando precisarem de uma história.", "The coffins are quiet today. Come back when you need a story.", "Los ataúdes están quietos hoy. Vuelvan cuando necesiten una historia."),
    "DLG_FPENITENT_1": ("Rezo aqui todos os dias, diante do trono vazio. Fui dama da corte da Rainha das Súcubos, e ajudei a seduzir metade do reino para o Barão. Hoje carrego esse peso.",
                        "I pray here every day, before the empty throne. I was a lady of the Succubus Queen's court, and I helped seduce half the kingdom for the Baron. Today I carry that weight.",
                        "Rezo aquí todos los días, ante el trono vacío. Fui dama de la corte de la Reina de las Súcubos, y ayudé a seducir a medio reino para el Barón. Hoy cargo ese peso."),
    "DLG_FPENITENT_2": ("A Rainha usa um anel que era meu, um anel de rubi, presente da minha mãe. Enquanto ele estiver no dedo dela, eu não consigo me perdoar. Ela dorme no fundo do salão, e sonha com o poder.",
                        "The Queen wears a ring that was mine, a ruby ring, a gift from my mother. While it is on her finger, I cannot forgive myself. She sleeps at the back of the hall, and dreams of power.",
                        "La Reina lleva un anillo que era mío, un anillo de rubí, regalo de mi madre. Mientras esté en su dedo, no puedo perdonarme. Duerme al fondo del salón, y sueña con el poder."),
    "DLG_FPENITENT_3": ("Vou acordá-la para vocês. Derrubem a Rainha e tragam o anel: eu dou a Chave de Rubi, a outra do portão do Barão.",
                        "I will wake her for you. Bring down the Queen and bring the ring: I give the Ruby Key, the other for the Baron's gate.",
                        "La despertaré para ustedes. Derriben a la Reina y traigan el anillo: doy la Llave de Rubí, la otra del portón del Barón."),
    "DLG_FPENITENT_ACTIVE": ("O anel é pequeno e brilha como sangue fresco. Ela o aperta contra o peito. Derrubem-na com cuidado: ela canta antes de atacar.",
                             "The ring is small and shines like fresh blood. She clasps it to her chest. Bring her down carefully: she sings before she strikes.",
                             "El anillo es pequeño y brilla como sangre fresca. Lo aprieta contra el pecho. Derríbenla con cuidado: canta antes de atacar."),
    "DLG_FPENITENT_DONE": ("O anel de minha mãe! Talvez agora eu consiga rezar em paz. A Chave de Rubi é de vocês: levem-na ao Carcereiro, junto com a de Ônix.",
                           "My mother's ring! Perhaps now I can pray in peace. The Ruby Key is yours: take it to the Jailer, together with the Onyx one.",
                           "¡El anillo de mi madre! Quizá ahora pueda rezar en paz. La Llave de Rubí es suya: llévenla al Carcelero, junto con la de Ónix."),
    "DLG_FPENITENT_WAIT": ("O trono continua vazio, mas as velas ainda ardem. Vão em paz.", "The throne is still empty, but the candles still burn. Go in peace.", "El trono sigue vacío, pero las velas aún arden. Vayan en paz."),
    "DLG_FGUARD_1": ("Alto. Este portão fecha o Salão do Barão, e no Salão manda o Barão Infernal. Fui seu carcereiro por tanto tempo que esqueci o que era a luz do dia.",
                     "Halt. This gate closes the Baron's Hall, and in the Hall the Infernal Baron rules. I was his jailer so long I forgot what daylight was.",
                     "Alto. Este portón cierra el Salón del Barón, y en el Salón manda el Barón Infernal. Fui su carcelero tanto tiempo que olvidé lo que era la luz del día."),
    "DLG_FGUARD_2": ("O portão só abre com DUAS chaves: a de Ônix e a de Rubi. A primeira está com o Exilado, no Ossuário a oeste; a segunda, com a Penitente, no Salão do Trono a leste.",
                     "The gate only opens with TWO keys: the Onyx and the Ruby. The first is with the Exile, in the Ossuary to the west; the second, with the Penitent, in the Throne Hall to the east.",
                     "El portón solo abre con DOS llaves: la de Ónix y la de Rubí. La primera la tiene el Exiliado, en el Osario al oeste; la segunda, la Penitente, en el Salón del Trono al este."),
    "DLG_FGUARD_3": ("Cada um cobra um preço: uma lâmina, um anel. Tragam as duas chaves a mim e eu abro a passagem.",
                     "Each charges a price: a blade, a ring. Bring both keys to me and I will open the way.",
                     "Cada uno cobra un precio: una hoja, un anillo. Tráiganme las dos llaves y abro el paso."),
    "DLG_FGUARD_ACTIVE": ("Só abro com as duas chaves, Ônix e Rubi, na mesma bolsa. O Exilado fica a oeste, no Ossuário; a Penitente, a leste, no Salão do Trono.",
                          "I only open with both keys, Onyx and Ruby, in the same bag. The Exile is to the west, in the Ossuary; the Penitent, to the east, in the Throne Hall.",
                          "Solo abro con las dos llaves, Ónix y Rubí, en la misma bolsa. El Exiliado está al oeste, en el Osario; la Penitente, al este, en el Salón del Trono."),
    "DLG_FGUARD_DONE": ("As duas chaves! O portão está aberto. Cuidado: o Barão Infernal não recebe visitas, e as que recebe não voltam.",
                        "Both keys! The gate is open. Beware: the Infernal Baron does not receive visitors, and those he does never return.",
                        "¡Las dos llaves! El portón está abierto. Cuidado: el Barón Infernal no recibe visitas, y las que recibe no regresan."),
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
    for dst, src, mul in (("key_ruby", "key_hearts", (1.4, 0.5, 0.5)), ("key_onyx", "key_spades", (0.45, 0.45, 0.6)), ("dark_blade", "bone_dagger", (0.55, 0.5, 0.75)),
                          ("queen_ring", "royal_seal_ring", (1.4, 0.55, 0.7))):
        im = Image.open(ICONS + src + ".png").convert("RGBA")
        r_, g_, b_, a_ = im.split()
        Image.merge("RGBA", (r_.point(lambda v: min(255, int(v * mul[0]))), g_.point(lambda v: min(255, int(v * mul[1]))), b_.point(lambda v: min(255, int(v * mul[2]))), a_)).save(ICONS + dst + ".png")
except Exception as exc:
    print("aviso: ícones não gerados:", exc)

for path, data in ((ARENAS, arenas), (MONSTERS, monsters), (NPCS, npcs), (QUESTS, quests), (VALUABLES, valuables)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
print("OK fort: grade %dx%d, %d células de piso (%d m2 de piso), %d peças/colisores, %d encontros, %d m2 da sala" % (COLS, ROWS, FLOOR_CELLS, FLOOR_CELLS * CELL * CELL, len(decor), len(encounters), COLS * CELL * ROWS * CELL))
