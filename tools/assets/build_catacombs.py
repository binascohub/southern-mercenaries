"""Mapa das Catacumbas (catacombs_01_depths), novo (era só um nome na ordem dos mapas): mesma estrutura do Esgoto/Floresta (partida, duas áreas de mini-chefe com NPCs, guardião do
portão que pede duas chaves e chefe final), com outro caminho, em salas de parede de pedra do kit (como o Esgoto) numa grade de blocos de 12 m:
  Portão da Cripta (partida) -> Nave dos Ossos (centro) e, a partir dela, TRÊS rotas até a Galeria dos Condenados:
    oeste: Ala das Celas -> Sala de Tortura -> Poço do Carrasco (a gaiola do Carrasco, tocada com a missão do Carcereiro Cego, desperta o Carrasco das Catacumbas),
    leste: Ala das Celas -> Ossuário -> Capela dos Acorrentados (a Prisioneira, com a missão dela, desperta a Alma Acorrentada),
    meio: Salão das Correntes -> Pátio do Tribunal.
  Da Galeria, o corredor do portão (o Diretor só abre com as duas chaves) leva à Cripta do Rei Acorrentado (chefe final, com a saída para a Capital).
  Salas laterais sem saída: o Cofre (oeste) e a Cela Secreta (leste).
Decoração: celas de grades de ferro (Fence_Iron) com presos sentados ou encolhidos, ossos, correntes e grilhões (Prison_*, feitos por tools/assets/build_chains.py), forcas, caixões,
instrumentos de tortura, braseiros e teias. Sorteio com semente fixa; idempotente; chamado no fim de tools/assets/build_maps.py (antes de set_map_order.py).
uso: python3 tools/assets/build_catacombs.py   (a partir da raiz do projeto)"""
import json, math, random, re
ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES = ("data/arenas.json", "data/monsters.json", "data/npcs.json", "data/quests.json", "data/valuables.json")
arenas, monsters, npcs, quests, valuables = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES))
rng = random.Random("catacombs-v1")
U, DOOR = 12.0, 6.0


def block(c0, r0, c1, r1):
    return (((c0 + c1) / 2 - 4) * U, -((r0 + r1) / 2) * U, (c1 - c0 + 1) * U, (r1 - r0 + 1) * U)


B = {"entry": (3, 0, 5, 0), "nave": (3, 1, 5, 3), "cells_w": (0, 1, 2, 3), "cells_e": (6, 1, 8, 3), "torture": (0, 4, 2, 6), "ossuary": (6, 4, 8, 6), "chain_hall": (3, 4, 5, 6),
     "court": (3, 7, 5, 8), "pit_w": (0, 7, 2, 8), "chapel": (6, 7, 8, 8), "gallery": (0, 9, 8, 9), "gate_lane": (4, 10, 4, 11), "crypt": (2, 12, 6, 15),
     "vault_w": (-1, 2, -1, 3), "secret": (9, 2, 9, 3)}
ROOMS = [(rid,) + block(*b) for rid, b in B.items()]
LINKS = [("entry", "nave", "north"), ("nave", "cells_w", "west"), ("nave", "cells_e", "east"), ("nave", "chain_hall", "north"), ("cells_w", "torture", "north"), ("cells_e", "ossuary", "north"),
         ("torture", "chain_hall", "east"), ("ossuary", "chain_hall", "west"), ("torture", "pit_w", "north"), ("ossuary", "chapel", "north"), ("chain_hall", "court", "north"),
         ("pit_w", "gallery", "north"), ("chapel", "gallery", "north"), ("court", "gallery", "north"), ("gallery", "gate_lane", "north"), ("gate_lane", "crypt", "north"),
         ("cells_w", "vault_w", "west"), ("cells_e", "secret", "east")]
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
    r = {"id": rid, "center": [cx, cz], "size": [w, h], "doors": doors[rid], "wall_height": 3.0, "narrow": True}
    if rid in ("entry", "nave", "chain_hall", "gallery", "crypt", "pit_w", "chapel", "court"):
        r["torch"] = True
    rooms.append(r)
for i, (_, ax, az, aw, ah) in enumerate(ROOMS):
    for _, bx, bz, bw, bh in ROOMS[i + 1:]:
        assert abs(ax - bx) >= (aw + bw) / 2 - 1e-6 or abs(az - bz) >= (ah + bh) / 2 - 1e-6, "salas sobrepostas"
AREA_M2 = sum(r[3] * r[4] for r in ROOMS)


def room_at(x, z, pad=0.0):
    for r in rooms:
        if abs(x - r["center"][0]) < r["size"][0] / 2 + pad and abs(z - r["center"][1]) < r["size"][1] / 2 + pad:
            return r
    return None


def rp(rid, dx=0.0, dz=0.0):
    return [round(by_id[rid][1] + dx, 1), round(by_id[rid][2] + dz, 1)]


# ---------------------------------------------------------------- monstros novos e itens
def clone(name, base, **changes):
    m = json.loads(json.dumps(monsters[base]))
    m.pop("_comment", None)
    m.pop("quest_drop", None)
    m.update(changes)
    monsters[name] = m


clone("ct_headsman", "ruin_warden", _comment="Mini-chefe das Catacumbas (Poço do Carrasco): o Carrasco, ogro de capuz que desce da gaiola quando o Carcereiro Cego pede; investidas.",
      name_key="MONSTER_CT_HEADSMAN", max_health=340, damage=28, size=3.0, element="earth", look="ogre", color=[0.7, 0.55, 0.55], quest_drop="headsman_axe")
clone("ct_soul", "ruin_warden", _comment="Mini-chefe das Catacumbas (Capela): a Alma Acorrentada, espírito preso a grilhões que a Prisioneira solta; investidas.",
      name_key="MONSTER_CT_SOUL", max_health=320, damage=26, size=2.4, element="water", look="shadow_spirit", color=[0.55, 0.75, 1.0], quest_drop="soul_shackle")
clone("ct_king", "sphinx", _comment="Chefe final das Catacumbas: o Rei Acorrentado, rei morto preso em correntes que guarda a Cripta atrás do portão; investidas e pisões.",
      name_key="MONSTER_CT_KING", max_health=1200, damage=40, size=3.8, element="water", look="undead", color=[0.75, 0.85, 1.0], chest_loot="chest")
valuables.update({
    "headsman_axe": {"name_key": "VALUABLE_HEADSMAN_AXE", "value": 0, "maps": [], "quest_item": True, "model": "Axe_Bronze"},
    "soul_shackle": {"name_key": "VALUABLE_SOUL_SHACKLE", "value": 0, "maps": [], "quest_item": True, "model": "Crystal_Gem"},
    "key_iron": {"name_key": "VALUABLE_KEY_IRON", "value": 0, "maps": [], "quest_item": True, "model": "Key_Spades"},
    "key_bone": {"name_key": "VALUABLE_KEY_BONE", "value": 0, "maps": [], "quest_item": True, "model": "Key_Clubs"}})

# ---------------------------------------------------------------- objetos e encontros
SUMMON_HEADSMAN = {"id": "ct_headsman", "position": rp("pit_w", 0, 6), "spread": 3.0, "toast": "TOAST_GIBBET_AWAKENS", "monsters": [{"monster": "ct_headsman", "count": 1, "rank": "miniboss"}]}
SUMMON_SOUL = {"id": "ct_soul", "position": rp("chapel", 6, 4), "spread": 3.0, "toast": "TOAST_SOUL_AWAKENS", "monsters": [{"monster": "ct_soul", "count": 1, "rank": "miniboss"}]}
props = [
    {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "capital_01_aurenhold", "entry": "catacombs", "expedition_end": False},
    {"id": "victory_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [0, -183.5], "to": "capital_01_aurenhold", "entry": "catacombs", "after_victory": True, "group": True},
    {"id": "ct_monk", "kind": "npc", "npc": "ct_monk", "position": [-24.0, -12.0], "rotation": 200},
    {"id": "ct_jailer", "kind": "npc", "npc": "ct_jailer", "position": rp("nave", 8, 6), "rotation": 160},
    {"id": "ct_gibbet", "kind": "npc", "npc": "ct_gibbet", "kit": "Gibbet", "rotation": 0, "position": rp("pit_w", 0, 0), "solid": [1.6, 1.6], "summon": SUMMON_HEADSMAN, "needs_quest": "ct_axe"},
    {"id": "ct_prisoner", "kind": "npc", "npc": "ct_prisoner", "position": rp("chapel", -4, 0), "rotation": 90, "summon": SUMMON_SOUL, "needs_quest": "ct_soul"},
    {"id": "boss_gate", "kind": "gate", "name_key": "PROP_BOSS_GATE", "position": [0.0, -122.0], "rotation": 0, "scale": 3.0, "block": 12.0, "count": 2, "opened_by": "ct_gate"},
    {"id": "ct_warden", "kind": "npc", "npc": "ct_warden", "position": [0.0, -118.0], "rotation": 0}]
chest_spots = [(rp("vault_w", 0, -5), "chest"), (rp("secret", 0, -5), "chest"), (rp("cells_w", -14, -13), "chest"), (rp("cells_e", 14, -13), "chest"), (rp("torture", 13, 12), "chest"),
               (rp("ossuary", -13, 12), "chest"), (rp("crypt", -24, 18), "chest"), (rp("crypt", 24, 18), "chest"), (rp("gallery", -44, 0), "chest"), (rp("gallery", 44, 0), "chest"),
               (rp("entry", 14, 2), "potion_chest"), (rp("nave", -14, 14), "potion_chest"), (rp("chain_hall", 14, 14), "potion_chest"), (rp("court", -14, 8), "potion_chest"),
               (rp("pit_w", 13, 8), "potion_chest"), (rp("chapel", -13, 8), "potion_chest"), (rp("cells_w", 14, 14), "potion_chest"), (rp("cells_e", -14, 14), "potion_chest")]
for i, (pos, loot) in enumerate(chest_spots, start=1):
    p = {"id": "ct_chest_%d" % i, "kind": "chest", "position": pos, "loot": loot}
    if loot == "potion_chest":
        p["model"] = "Chest_Mini"
    props.append(p)
E = lambda eid, pos, *mons: {"id": eid, "position": pos, "monsters": [{"monster": m, "count": c} for m, c in mons]}
encounters = [
    E("ct_nave_a", rp("nave", -10, 4), ("skeleton", 4)), E("ct_nave_b", rp("nave", 10, -6), ("zombie", 3)), E("ct_nave_c", rp("nave", 0, -2), ("skeleton", 3), ("plague_bat", 3)),
    E("ct_cells_w", rp("cells_w", 0, 12), ("zombie", 3), ("shadow_spirit", 2)), E("ct_cells_w2", rp("cells_w", 10, -12), ("zombie", 3)), E("ct_mimic_cw", rp("cells_w", -12, 12), ("chest_mimic", 1)),
    E("ct_cells_e", rp("cells_e", 0, 12), ("skeleton", 3), ("night_demon", 1)), E("ct_cells_e2", rp("cells_e", -10, -12), ("skeleton", 4)), E("ct_mimic_ce", rp("cells_e", 12, 12), ("chest_mimic", 1)),
    E("ct_torture_a", rp("torture", -10, -10), ("champ_warrior", 2)), E("ct_torture_b", rp("torture", 10, 6), ("barbarian_monster", 2)), E("ct_torture_c", rp("torture", -10, 10), ("shadow_spirit", 2)),
    E("ct_ossuary_a", rp("ossuary", 10, -10), ("zombie", 4)), E("ct_ossuary_b", rp("ossuary", -10, 6), ("stalker", 2)), E("ct_ossuary_c", rp("ossuary", 10, 10), ("skeleton", 3)),
    E("ct_chain_a", rp("chain_hall", -10, -10), ("shadow_spirit", 3)), E("ct_chain_b", rp("chain_hall", 10, 4), ("demon_twelve", 2)), E("ct_chain_c", rp("chain_hall", -6, 12), ("champ_warrior", 2)),
    E("ct_court_a", rp("court", -10, 0), ("skeleton", 4)), E("ct_court_b", rp("court", 10, 0), ("night_demon", 2)),
    E("ct_pit", rp("pit_w", 10, -4), ("zombie", 3)), E("ct_chapel", rp("chapel", 0, -6), ("skeleton", 3)),
    E("ct_gallery_a", rp("gallery", -36, 0), ("zombie", 3)), E("ct_gallery_b", rp("gallery", -14, 0), ("skeleton", 3)), E("ct_gallery_c", rp("gallery", 14, 0), ("shadow_spirit", 3)),
    E("ct_gallery_d", rp("gallery", 36, 0), ("zombie", 3)),
    E("ct_vault", rp("vault_w", 0, 4), ("skeleton", 2)), E("ct_secret", rp("secret", 0, 4), ("troll_mauler", 1)), E("ct_mimic_secret", rp("secret", 0, -4), ("chest_mimic", 1)),
    E("ct_crypt_a", rp("crypt", -16, 14), ("skeleton", 3), ("zombie", 2)), E("ct_crypt_b", rp("crypt", 16, 14), ("skeleton", 3), ("zombie", 2)), E("ct_mimic_crypt", rp("crypt", -24, 8), ("chest_mimic", 1)),
    E("ct_king", [0, -174], ("ct_king", 1))]
interest = [p["position"] for p in props] + [e["position"] for e in encounters] + [SUMMON_HEADSMAN["position"], SUMMON_SOUL["position"], [0, 3]] + [list(d) for d in door_points]
decor, crowd, taken = [], [], []


def near_interest(x, z, rad):
    return any(math.hypot(x - ix, z - iz) < rad for ix, iz in interest)


def near_taken(x, z, rad):
    return any(math.hypot(x - tx, z - tz) < tr + rad for tx, tz, tr in taken)


def put(piece, x, z, rot=None, scale=1.0, solid=None, y=None, r=0.8, free=2.2, force=False, wall=1.9):
    if room_at(x, z, -wall) is None:
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


def scatter(rid, pieces, n, scale=(1.0, 1.0), solid=None, r=0.9, tries=50, margin=2.5, **kw):
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


def light(x, z, color=(1.0, 0.6, 0.3), rng_=9.0, energy=1.2, y=2.2):
    decor.append({"light": list(color), "position": [round(x, 1), round(z, 1)], "y": y, "range": rng_, "energy": energy, "flicker": True})


def brazier(x, z, scale=1.5):
    if put("Tv_Fire", x, z, rot=0, scale=scale, solid=[0.9 * scale, 0.7 * scale], r=1.2, free=1.0):
        decor.append({"piece": "Fire_Flame", "position": [round(x, 2), round(z, 2)], "y": 0.2, "scale": round(scale * 0.9, 2), "flicker": True})
        light(x, z, (1.0, 0.55, 0.25), 10.0, 1.4, 1.2)


def candle_cluster(x, z):
    if put("CandleStick_Triple", x, z, rot=0, r=0.5, free=1.0):
        light(x, z, (1.0, 0.8, 0.5), 5.0, 0.7, 1.0)


def fence_line(x0, z0, x1, z1, gaps=()):
    """Linha de grades de ferro (Fence_Iron, peça de 2,06 m) com colisão; gaps = intervalos [a, b] ao longo do eixo sem grade (portas das celas)."""
    horiz = abs(z1 - z0) < 1e-6
    a, b = (x0, x1) if horiz else (z0, z1)
    lo, hi = min(a, b), max(a, b)
    segs, cur = [], lo
    for ga, gb in sorted(gaps):
        if ga > cur:
            segs.append((cur, ga))
        cur = max(cur, gb)
    if cur < hi:
        segs.append((cur, hi))
    for s0, s1 in segs:
        n = max(1, round((s1 - s0) / 2.06))
        step = (s1 - s0) / n
        for i in range(n):
            t = s0 + step * (i + 0.5)
            x, z = (t, z0) if horiz else (x0, t)
            decor.append({"piece": "Fence_Iron", "position": [round(x, 2), round(z, 2)], "rotation": 0 if horiz else 90, "scale": round(step / 2.06, 2),
                          "solid": [round(step, 2), 0.3] if horiz else [0.3, round(step, 2)]})
            taken.append((x, z, 0.8))


blocks = []
BONES = ["Dungeon_BonePile_%d" % i for i in range(1, 7)] + ["Dungeon_CrossBones", "Dungeon_Pelvis", "Dungeon_Arm", "Dungeon_Leg", "Dungeon_Skull_1", "Dungeon_Skull_2", "Dungeon_Spine", "Dungeon_Bone"]
BIG_BONES = ["Dungeon_SkullPile", "Dungeon_Ribcage"]
WEBS = ["Web_Round_Up", "Web_Round_Flat", "Web_Square_Up", "Web_Square_Flat"]
CARGO = ["Barrel_Oga_1", "Barrel_Oga_2", "Crate_Big", "Crate_Small", "Tv_Sack", "Bucket_Wooden_1", "Pr_Basket"]


def cell_block(rid, ncells=3, depth=5.0):
    """Um bloco de celas (ncells de 6 m, `depth` de fundo) de grades de ferro, com presos nas celas fechadas e ossos/correntes nas abertas; devolve False se não achou lugar."""
    cx, cz, w, h = by_id[rid][1:]
    W = ncells * 6.0
    for _ in range(300):
        x0 = round(rng.uniform(cx - w / 2 + 5, cx + w / 2 - 5 - W) * 2) / 2
        z0 = round(rng.uniform(cz - h / 2 + 5, cz + h / 2 - 5 - depth) * 2) / 2
        if any(x0 - 3 < bx1 and x0 + W + 3 > bx0 and z0 - 3 < bz1 and z0 + depth + 3 > bz0 for bx0, bz0, bx1, bz1 in blocks):
            continue
        if any(x0 - 2.5 < ix < x0 + W + 2.5 and z0 - 2.5 < iz < z0 + depth + 2.5 for ix, iz in interest):
            continue
        if any(x0 - 5 < dx < x0 + W + 5 and z0 - 5 < dz < z0 + depth + 5 for dx, dz in door_points):
            continue
        break
    else:
        return False
    blocks.append((x0, z0, x0 + W, z0 + depth))
    gaps = []
    open_cells = [rng.random() < 0.3 for _ in range(ncells)]
    for k in range(ncells):
        if open_cells[k]:
            gaps.append((x0 + 6 * k + 2.0, x0 + 6 * k + 4.0))
    fence_line(x0, z0 + depth, x0 + W, z0 + depth, gaps)      # frente (sul), com as portas das celas abertas
    fence_line(x0, z0, x0 + W, z0)                              # fundo
    for k in range(ncells + 1):
        fence_line(x0 + 6 * k, z0, x0 + 6 * k, z0 + depth)      # divisórias
    for k in range(ncells):
        mx, mz = x0 + 6 * k + 3, z0 + depth / 2
        if open_cells[k]:
            put("Prison_BallChain", mx - 0.4, mz + 0.4, rot=rng.choice((0, 180)), r=0.4, free=0.5, force=True)
            for dx, dz in ((-1.8, -1.2), (1.5, 0.8)):
                put(rng.choice(BONES), mx + dx, mz + dz, scale=rng.uniform(2.2, 3.2), r=0.3, free=0.5, force=True)
        else:
            crowd.append({"role": "beggar", "position": [round(mx, 1), round(mz - 0.4, 1)], "rotation": 0, "pose": rng.choice(("sit", "sit", "crouch"))})
            put("Prison_BallChain", mx + 1.2, mz + 0.9, rot=0, r=0.4, free=0.5, force=True)
            put(rng.choice(BONES), mx - 1.8, mz - 1.2, scale=rng.uniform(2.2, 3.0), r=0.3, free=0.5, force=True)
            put("Bucket_Wooden_1", mx + 1.8, mz - 1.4, r=0.3, free=0.5, force=True)
    return True


def wall_decor(rid, side, piece="Prison_WallShackles", n=3, y=0.5, scale=1.0, skip=()):
    """Peças coladas numa parede (n espaçadas), longe das portas; `side`: n, w ou e (a parede sul é só a borda aberta)."""
    cx, cz, w, h = by_id[rid][1:]
    for i in range(n):
        t = (i + 1) / (n + 1) - 0.5
        if side == "n":
            x, z, rot = cx + t * w, cz - h / 2 + 1.55, 180
        elif side == "w":
            x, z, rot = cx - w / 2 + 0.55, cz + t * h, 270
        else:
            x, z, rot = cx + w / 2 - 0.55, cz + t * h, 90
        if any(math.hypot(x - dx, z - dz) < 5.0 for dx, dz in door_points) or any(math.hypot(x - sx, z - sz) < 3.0 for sx, sz in skip):
            continue
        decor.append({"piece": piece, "position": [round(x, 2), round(z, 2)], "rotation": rot, "y": y, "scale": scale})


# --- ambientação: uma luz fria em cada sala, tochas, braseiros nas salas grandes
for rid, cx, cz, w, h in ROOMS:
    light(cx, cz, (0.65, 0.7, 1.0) if rid in ("ossuary", "crypt", "chapel") else (1.0, 0.65, 0.35), 12.0 if min(w, h) > 20 else 9.0, 1.1, 2.4)
for rid in ("cells_w", "cells_e"):
    for _ in range(3):
        cell_block(rid)
for rid in ("torture", "ossuary"):
    for _ in range(2):
        cell_block(rid, ncells=2, depth=5.0)
cell_block("nave", ncells=2, depth=5.0)
for rid in ("cells_w", "cells_e"):                           # presos soltos nos corredores, sentados no chão
    cx, cz, w, h = by_id[rid][1:]
    for _ in range(4):
        x, z = cx + rng.uniform(-w / 2 + 3, w / 2 - 3), cz + rng.uniform(-h / 2 + 3, h / 2 - 3)
        if not near_interest(x, z, 3.0) and not near_taken(x, z, 1.5):
            crowd.append({"role": "beggar", "position": [round(x, 1), round(z, 1)], "rotation": rng.randrange(0, 360, 15), "pose": "crouch"})
            taken.append((x, z, 1.2))
            put("Prison_BallChain", x + 0.8, z + 0.3, rot=rng.randrange(0, 360, 15), r=0.4, free=0.2, force=True)
# --- paredes: grilhões nas alas das celas, no Poço, na Capela, na Sala de Tortura e ao longo da Galeria; correntes penduradas nas salas das correntes e do tribunal
for rid, n in (("cells_w", 5), ("cells_e", 5), ("torture", 5), ("ossuary", 4), ("pit_w", 4), ("chapel", 4), ("chain_hall", 5), ("court", 4), ("nave", 4)):
    for side in "nwe":
        wall_decor(rid, side, "Prison_WallShackles", n, y=0.55)
wall_decor("gallery", "n", "Prison_WallShackles", 8, y=0.55)
wall_decor("crypt", "n", "Prison_WallShackles", 6, y=0.55)
for rid in ("chain_hall", "court", "crypt", "gallery", "nave"):
    for side in "nwe":
        wall_decor(rid, side, "Prison_ChainHang", 4 if rid != "gallery" else 6, y=0.0, scale=1.0)
# --- Nave dos Ossos (hub): colunas de ossos, braseiros, caixões, pilares e teias
for dx, dz in ((-12, -10), (12, -10), (-12, 10), (12, 10)):
    brazier(by_id["nave"][1] + dx, by_id["nave"][2] + dz)
scatter("nave", BONES, 26, scale=(2.4, 3.4), r=0.8)
scatter("nave", BIG_BONES, 6, scale=(3.0, 4.2), r=1.4)
scatter("nave", ["Lab_Coffin"], 4, rot=0, solid=(2.0, 0.9), r=1.4)
scatter("nave", ["Lab_ColumnBig", "Lab_ColumnBroken"], 6, solid=(0.63, 0.63), r=0.8)
scatter("nave", WEBS, 8, scale=(1.5, 2.3), r=1.0)
scatter("nave", CARGO, 8, scale=(0.9, 1.2), r=0.9)
# --- Alas das celas, Sala de Tortura, Ossuário
for rid in ("cells_w", "cells_e"):
    scatter(rid, BONES, 20, scale=(2.4, 3.4), r=0.8)
    scatter(rid, ["Gibbet"], 3, solid=(1.0, 1.0), r=1.6)
    scatter(rid, ["Prison_BallChain"], 5, r=0.6)
    scatter(rid, WEBS, 8, scale=(1.5, 2.3), r=1.0)
    scatter(rid, CARGO, 8, scale=(0.9, 1.2), r=0.9)
    cx, cz = by_id[rid][1:3]
    for dx, dz in ((-13, -13), (13, -13), (-13, 13), (13, 13)):
        brazier(cx + dx, cz + dz, 1.3)
cx, cz = by_id["torture"][1:3]
for dx, dz in ((-12, -12), (12, -12), (-12, 12), (12, 12)):
    brazier(cx + dx, cz + dz)
scatter("torture", ["Weapon_Rack", "Anvil", "Cauldron", "Workbench", "Vl_ChoppingBlock", "Axe_Bronze", "Sword_B"], 18, scale=(1.0, 1.4), solid=(1.0, 1.0), r=1.1)
scatter("torture", ["Gibbet"], 4, solid=(1.0, 1.0), r=1.6)
scatter("torture", ["Prison_BallChain", "Prison_ChainHang"], 8, r=0.6)
scatter("torture", BONES, 26, scale=(2.4, 3.4), r=0.8)
scatter("torture", BIG_BONES, 4, scale=(3.0, 4.0), r=1.4)
scatter("torture", WEBS, 6, scale=(1.5, 2.3), r=1.0)
cx, cz = by_id["ossuary"][1:3]
for dx, dz in ((-12, -12), (12, -12), (-12, 12), (12, 12)):
    brazier(cx + dx, cz + dz, 1.3)
    candle_cluster(cx + dx * 0.5, cz + dz * 0.5)
scatter("ossuary", BONES, 60, scale=(2.6, 3.8), r=0.8)
scatter("ossuary", BIG_BONES, 14, scale=(3.2, 4.5), r=1.5)
scatter("ossuary", ["Lab_Coffin"], 8, rot=0, solid=(2.0, 0.9), r=1.4)
scatter("ossuary", ["Lab_ColumnBig", "Lab_ColumnBroken", "Lab_WallBroken"], 8, solid=(0.7, 0.7), r=1.0)
scatter("ossuary", ["CandleStick_Triple", "Tv_Candle"], 10, r=0.6, free=1.0)
scatter("ossuary", WEBS, 10, scale=(1.5, 2.3), r=1.0)
# --- Salão das Correntes, Pátio do Tribunal
cx, cz = by_id["chain_hall"][1:3]
for dx, dz in ((-12, -12), (12, -12), (-12, 12), (12, 12)):
    brazier(cx + dx, cz + dz)
for dx, dz in ((-6, -6), (6, -6), (-6, 6), (6, 6)):
    put("Lab_ColumnBig", cx + dx, cz + dz, solid=[0.63, 0.63], r=0.9, free=1.0)
scatter("chain_hall", ["Prison_ChainHang", "Prison_BallChain"], 12, r=0.9)
scatter("chain_hall", ["Gibbet"], 3, solid=(1.0, 1.0), r=1.6)
scatter("chain_hall", BONES, 24, scale=(2.4, 3.4), r=0.8)
scatter("chain_hall", WEBS, 8, scale=(1.5, 2.3), r=1.0)
cx, cz = by_id["court"][1:3]
decor.append({"piece": "Castle_Dais", "position": [cx, cz - 6.0]})
decor.append({"piece": "Castle_Altar", "position": [cx, cz - 7.0], "solid": [1.2, 1.2]})
for dx in (-9, 9):
    for dz in (-4, 4):
        put("Tv_Bench", cx + dx, cz + dz, rot=0, solid=[1.6, 0.7], r=1.2, free=1.0)
for dx, dz in ((-14, -8), (14, -8), (-14, 8), (14, 8)):
    brazier(cx + dx, cz + dz, 1.3)
scatter("court", ["Castle_Column"], 4, solid=(0.9, 0.9), r=1.0)
scatter("court", BONES, 14, scale=(2.4, 3.2), r=0.8)
scatter("court", ["Prison_BallChain", "Prison_ChainHang"], 6, r=0.8)
# --- Poço do Carrasco e Capela dos Acorrentados (praças dos mini-chefes)
cx, cz = by_id["pit_w"][1:3]
for dx, dz in ((-14, -8), (14, -8), (-14, 8), (14, 8), (0, -9)):
    brazier(cx + dx, cz + dz, 1.5)
scatter("pit_w", ["Vl_ChoppingBlock", "Anvil", "Weapon_Rack", "Axe_Bronze", "Cauldron"], 12, scale=(1.0, 1.4), solid=(1.0, 1.0), r=1.1)
scatter("pit_w", BONES, 30, scale=(2.6, 3.6), r=0.8)
scatter("pit_w", BIG_BONES, 6, scale=(3.2, 4.4), r=1.4)
scatter("pit_w", ["Prison_BallChain", "Prison_ChainHang"], 8, r=1.0)
scatter("pit_w", ["Gibbet"], 3, solid=(1.0, 1.0), r=1.6)
cx, cz = by_id["chapel"][1:3]
decor.append({"piece": "Castle_Dais", "position": [cx + 12, cz - 5.0]})
decor.append({"piece": "Castle_Altar", "position": [cx + 12, cz - 6.0], "solid": [1.2, 1.2]})
for dx, dz in ((-14, -8), (14, 6), (-14, 8), (0, -9)):
    brazier(cx + dx, cz + dz, 1.3)
for dx, dz in ((-6, -4), (-6, 4), (6, -4), (6, 4)):
    put("Castle_Column", cx + dx, cz + dz, solid=[0.9, 0.9], r=1.0, free=1.0)
    candle_cluster(cx + dx + 1.0, cz + dz)
scatter("chapel", ["Tv_Bench"], 6, rot=0, solid=(1.6, 0.7), r=1.2)
scatter("chapel", BONES, 24, scale=(2.4, 3.4), r=0.8)
scatter("chapel", ["Prison_BallChain", "Prison_ChainHang", "CandleStick_Triple"], 10, r=0.8, free=1.0)
scatter("chapel", WEBS, 8, scale=(1.5, 2.3), r=1.0)
# --- Galeria dos Condenados: colunatas, braseiros, ossos, correntes
cx, cz, w, h = by_id["gallery"][1:]
for i in range(-4, 5):
    for dz in (-3.8, 3.8):
        put("Castle_Column", cx + i * 12.0 + 6.0, cz + dz, solid=[0.9, 0.9], r=1.0, free=1.0, force=True)
for x in (-48, -24, 24, 48):
    brazier(x, cz, 1.4)
scatter("gallery", BONES, 36, scale=(2.4, 3.4), r=0.8, margin=2.2)
scatter("gallery", ["Prison_BallChain", "Prison_ChainHang"], 10, r=0.9, margin=2.2)
scatter("gallery", ["Gibbet"], 3, solid=(1.0, 1.0), r=1.6, margin=2.2)
scatter("gallery", WEBS, 12, scale=(1.5, 2.3), r=1.0, margin=2.2)
# --- corredor do portão e Cripta do Rei Acorrentado
for z in (-117, -125, -133):
    for x in (-4.6, 4.6):
        put("Tv_Torch", x, z, scale=1.5, r=0.5, free=1.0)
        light(x, z, (1.0, 0.6, 0.3), 6.5, 0.8, 1.8)
cx, cz = by_id["crypt"][1:3]
for dx in (-24, 24):
    for dz in (-14, 0, 14):
        brazier(cx + dx, cz + dz, 1.8)
for ax in (-10, 10):
    decor.append({"piece": "Castle_Dais", "position": [ax, -181.0]})
    decor.append({"piece": "Castle_Altar", "position": [ax, -183.0], "solid": [1.2, 1.2]})
for dx in (-12, 12):
    for dz in (-18, -6, 6, 18):
        put("Castle_Column", cx + dx, cz + dz, solid=[0.9, 0.9], r=1.0, free=1.0)
for dx, dz in ((-22, -16), (22, -16), (-22, 12), (22, 12)):
    put("Lab_Coffin", cx + dx, cz + dz, rot=0, solid=[2.0, 0.9], r=1.4)
scatter("crypt", BONES, 50, scale=(2.6, 3.8), r=0.8)
scatter("crypt", BIG_BONES, 12, scale=(3.2, 4.6), r=1.5)
scatter("crypt", ["Prison_BallChain", "Prison_ChainHang"], 12, r=1.0)
scatter("crypt", ["Gibbet"], 4, solid=(1.0, 1.0), r=1.6)
scatter("crypt", ["Coin_Pile", "Chest_Large", "Cage_Small"], 10, scale=(1.3, 1.8), r=1.3)
scatter("crypt", WEBS, 12, scale=(1.5, 2.3), r=1.0)
for rid in ("vault_w", "secret"):
    cx, cz = by_id[rid][1:3]
    scatter(rid, ["Coin_Pile", "Cage_Small", "Chest_Large"], 4, scale=(1.3, 1.7), r=1.2)
    scatter(rid, BONES, 6, scale=(2.2, 3.0), r=0.8)
# --- nave de entrada
for dx in (-12, 12):
    brazier(dx, 0, 1.2)
scatter("entry", CARGO, 6, scale=(0.9, 1.2), r=0.9)
scatter("entry", BONES, 6, scale=(2.2, 3.0), r=0.8)

def in_block(x, z, m=1.5):
    return any(bx0 - m < x < bx1 + m and bz0 - m < z < bz1 + m for bx0, bz0, bx1, bz1 in blocks)


def clear_of_blocks(p):
    """Um ponto perto de p que não cai dentro de um bloco de celas (para bolsas de moedas)."""
    for dx, dz in ((0, 0), (6, 0), (-6, 0), (0, 6), (0, -6), (8, 8), (-8, 8), (8, -8), (-8, -8), (12, 0), (-12, 0)):
        q = [round(p[0] + dx, 1), round(p[1] + dz, 1)]
        if room_at(q[0], q[1], -3.0) is not None and not in_block(*q) and not near_interest(q[0], q[1], 2.5):
            return q
    return p


breakables = []
for rid, n in (("entry", 2), ("nave", 6), ("cells_w", 8), ("cells_e", 8), ("torture", 6), ("ossuary", 6), ("chain_hall", 6), ("court", 4), ("pit_w", 4), ("chapel", 4), ("gallery", 8), ("crypt", 6)):
    cx, cz, w, h = by_id[rid][1:]
    for _ in range(n):
        for _t in range(100):
            x, z = round(cx + rng.uniform(-w / 2 + 3, w / 2 - 3), 1), round(cz + rng.uniform(-h / 2 + 3, h / 2 - 3), 1)
            if not near_interest(x, z, 3.0) and not near_taken(x, z, 1.2) and not in_block(x, z):
                breakables.append({"id": "b%d" % (len(breakables) + 1), "monster": "crate" if len(breakables) % 2 == 0 else "barrel", "position": [x, z], "table": "breakable_potion"})
                taken.append((x, z, 1.0))
                break
breakables.append({"id": "coin_bag", "monster": "coin_bag", "position": [4.0, 1.5], "table": "coin_bag"})
for i, p in enumerate((rp("nave", 12, -12), rp("cells_w", 4, 6), rp("cells_e", -4, 6), rp("chain_hall", 0, 8), rp("court", 0, 8), rp("gallery", 0, -3), rp("crypt", 0, 4), rp("pit_w", -10, 8), rp("chapel", 10, 8)), start=2):
    breakables.append({"id": "coin_bag_%d" % i, "monster": "coin_bag", "position": clear_of_blocks(p), "table": "coin_bag"})

arenas["catacombs_01_depths"] = {
    "_comment": "Catacumbas (novo): salas de parede de pedra do kit numa grade de blocos de 12 m, estrutura do Esgoto/Floresta com outro caminho. Portão da Cripta -> Nave dos Ossos; três rotas até a Galeria dos Condenados: oeste "
                "(Ala das Celas -> Sala de Tortura -> Poço do Carrasco, onde a gaiola desperta o Carrasco), leste (Ala das Celas -> Ossuário -> Capela dos Acorrentados, onde a Prisioneira desperta a Alma Acorrentada) e meio "
                "(Salão das Correntes -> Pátio do Tribunal); corredor do portão (Diretor, duas chaves) -> Cripta do Rei Acorrentado (chefe final, com a saída). Salas laterais sem saída: Cofre e Cela Secreta. "
                "Gerado por tools/assets/build_catacombs.py.",
    "name_key": "ARENA_CATACOMBS", "player_class": "mage", "map_id": "map_catacombs", "area_level": 11, "final": True, "victory_groups": ["ct_king"], "wake_radius": 12.0, "alert_radius": 5.0,
    "rooms": rooms, "encounters": encounters, "hazards": [], "entries": {"start": [0, 3], "catacombs": [0, 3]}, "props": props, "quest_spots": [], "breakables": breakables,
    "style": {"_comment": "Catacumbas: tijolos irregulares do kit em tom frio de pedra, piso de tijolos; a parede sul fica aberta para a câmera. Teias, morcegos e grades de piso; sem lixo.",
              "walls": ["Wall_UnevenBrick_Straight", "Wall_UnevenBrick_Straight", "Wall_UnevenBrick_Window_Wide_Round", "Wall_UnevenBrick_Straight", "Wall_UnevenBrick_Door_Round"],
              "floor": "Floor_UnevenBrick", "low": "", "ground": [0.04, 0.04, 0.06], "tint": [0.6, 0.62, 0.72], "grime": True, "puddles": False, "trash": False, "spiders": True,
              "grates": True, "bats": True, "stone_trim": True, "wood_tone": [0.192, 0.145, 0.11]},
    "decor": decor, "crowd": crowd, "passive": True}


# ---------------------------------------------------------------- NPCs e missões
def body(sex, hair, color):
    return {"sex": sex, "hair": [hair], "hair_color": color, "pose": "idle", "outfit": {"body": "cloth"}}


npcs["ct_monk"] = {"name_key": "NPC_CT_MONK", "color": [0.45, 0.4, 0.35], "dialogues": [
    {"when": {"quest_new": "ct_purge"}, "lines": ["DLG_CTMONK_1", "DLG_CTMONK_2", "DLG_CTMONK_3"], "offer": "ct_purge"},
    {"when": {"quest_active": "ct_purge"}, "lines": ["DLG_CTMONK_ACTIVE"]}, {"when": {}, "lines": ["DLG_CTMONK_DONE"]}], "body": body("male", "Hair_Buzzed", [0.5, 0.48, 0.45])}
npcs["ct_jailer"] = {"name_key": "NPC_CT_JAILER", "color": [0.35, 0.33, 0.3], "dialogues": [
    {"when": {"quest_new": "ct_axe"}, "lines": ["DLG_CTJAILER_1", "DLG_CTJAILER_2", "DLG_CTJAILER_3"], "offer": "ct_axe"},
    {"when": {"quest_active": "ct_axe"}, "lines": ["DLG_CTJAILER_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_CTJAILER_DONE"]}], "body": body("male", "Hair_Beard", [0.45, 0.42, 0.4])}
npcs["ct_gibbet"] = {"name_key": "NPC_CT_GIBBET", "color": [0.4, 0.35, 0.3], "dialogues": [
    {"when": {"quest_active": "ct_axe"}, "lines": ["DLG_CTGIBBET_1", "DLG_CTGIBBET_2"]}, {"when": {}, "lines": ["DLG_CTGIBBET_LOCKED"]}]}
npcs["ct_prisoner"] = {"name_key": "NPC_CT_PRISONER", "color": [0.55, 0.5, 0.6], "dialogues": [
    {"when": {"quest_new": "ct_soul"}, "lines": ["DLG_CTPRISONER_1", "DLG_CTPRISONER_2", "DLG_CTPRISONER_3"], "offer": "ct_soul"},
    {"when": {"quest_active": "ct_soul"}, "lines": ["DLG_CTPRISONER_ACTIVE"], "service": "turn_in"},
    {"when": {"quest_done": "ct_soul"}, "lines": ["DLG_CTPRISONER_DONE"]}, {"when": {}, "lines": ["DLG_CTPRISONER_WAIT"]}], "body": body("female", "Hair_Long", [0.3, 0.28, 0.3])}
npcs["ct_warden"] = {"name_key": "NPC_CT_WARDEN", "color": [0.3, 0.3, 0.36], "dialogues": [
    {"when": {"quest_new": "ct_gate"}, "lines": ["DLG_CTWARDEN_1", "DLG_CTWARDEN_2", "DLG_CTWARDEN_3"], "offer": "ct_gate"},
    {"when": {"quest_active": "ct_gate"}, "lines": ["DLG_CTWARDEN_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_CTWARDEN_DONE"]}], "body": body("male", "Hair_SimpleParted", [0.1, 0.1, 0.12])}
quests["ct_purge"] = {"name_key": "QUEST_CT_PURGE", "desc_key": "QUEST_CT_PURGE_DESC", "type": "village", "giver": "ct_monk", "area": "catacombs_01_depths", "clear": ["ct_cells_w", "ct_cells_e"],
                      "target_element": "water", "reward": {"gold": 500, "xp": 1000}}
quests["ct_axe"] = {"name_key": "QUEST_CT_AXE", "desc_key": "QUEST_CT_AXE_DESC", "type": "village", "giver": "ct_jailer", "area": "catacombs_01_depths", "target_element": "earth",
                    "reward": {"gold": 550, "xp": 1100}, "item": "headsman_axe", "gives": "key_iron"}
quests["ct_soul"] = {"name_key": "QUEST_CT_SOUL", "desc_key": "QUEST_CT_SOUL_DESC", "type": "village", "giver": "ct_prisoner", "area": "catacombs_01_depths", "target_element": "water",
                     "reward": {"gold": 550, "xp": 1100}, "item": "soul_shackle", "gives": "key_bone"}
quests["ct_gate"] = {"name_key": "QUEST_CT_GATE", "desc_key": "QUEST_CT_GATE_DESC", "type": "village", "giver": "ct_warden", "area": "catacombs_01_depths",
                     "items": ["key_iron", "key_bone"], "opens_gate": "boss_gate", "target_element": "water", "reward": {"gold": 650, "xp": 1300}}
T = {
    "ARENA_CATACOMBS": ("Catacumbas", "Catacombs", "Catacumbas"),
    "PROP_TO_CATACOMBS": ("Caminho para as Catacumbas", "Path to the Catacombs", "Camino a las Catacumbas"),
    "MONSTER_CT_HEADSMAN": ("Carrasco das Catacumbas", "Catacomb Headsman", "Verdugo de las Catacumbas"),
    "MONSTER_CT_SOUL": ("Alma Acorrentada", "Chained Soul", "Alma Encadenada"),
    "MONSTER_CT_KING": ("Rei Acorrentado", "Chained King", "Rey Encadenado"),
    "NPC_CT_MONK": ("Frade das Catacumbas", "Catacomb Friar", "Fraile de las Catacumbas"),
    "NPC_CT_JAILER": ("Carcereiro Cego", "Blind Jailer", "Carcelero Ciego"),
    "NPC_CT_GIBBET": ("Gaiola do Carrasco", "Headsman's Gibbet", "Jaula del Verdugo"),
    "NPC_CT_PRISONER": ("Prisioneira", "Prisoner", "Prisionera"),
    "NPC_CT_WARDEN": ("Diretor das Catacumbas", "Catacomb Warden", "Director de las Catacumbas"),
    "VALUABLE_HEADSMAN_AXE": ("Machado do Carrasco", "Headsman's Axe", "Hacha del Verdugo"),
    "VALUABLE_SOUL_SHACKLE": ("Grilhão da Alma", "Soul Shackle", "Grillete del Alma"),
    "VALUABLE_KEY_IRON": ("Chave de Ferro", "Iron Key", "Llave de Hierro"),
    "VALUABLE_KEY_BONE": ("Chave de Osso", "Bone Key", "Llave de Hueso"),
    "TOAST_GIBBET_AWAKENS": ("A gaiola range e as correntes se soltam: o Carrasco desce ao Poço!", "The gibbet creaks and its chains fall loose: the Headsman drops into the Pit!", "La jaula cruje y sus cadenas se sueltan: ¡el Verdugo baja al Pozo!"),
    "TOAST_SOUL_AWAKENS": ("Os grilhões se partem: a Alma Acorrentada se solta!", "The shackles snap: the Chained Soul breaks free!", "Los grilletes se rompen: ¡el Alma Encadenada se libera!"),
    "QUEST_CT_PURGE": ("Limpar as Celas", "Clear the Cells", "Limpiar las celdas"),
    "QUEST_CT_PURGE_DESC": ("O Frade das Catacumbas pede que as duas Alas das Celas, a oeste e a leste da Nave dos Ossos, sejam limpas dos mortos que ainda vigiam os presos.",
                            "The Catacomb Friar asks that both Cell Wings, west and east of the Nave of Bones, be cleared of the dead who still guard the prisoners.",
                            "El Fraile de las Catacumbas pide que las dos Alas de Celdas, al oeste y al este de la Nave de los Huesos, se limpien de los muertos que aún vigilan a los presos."),
    "QUEST_CT_AXE": ("O Machado do Carrasco", "The Headsman's Axe", "El hacha del Verdugo"),
    "QUEST_CT_AXE_DESC": ("O Carcereiro Cego, na Nave dos Ossos, quer o machado do Carrasco para fechar as contas dele. Tocar a gaiola do Poço do Carrasco (oeste, depois da Sala de Tortura), com a missão ativa, desperta o Carrasco das Catacumbas; derrote-o e traga o machado: em troca vem a Chave de Ferro, uma das duas do portão do Rei Acorrentado.",
                          "The Blind Jailer, in the Nave of Bones, wants the Headsman's axe to settle his accounts. Touch the gibbet in the Headsman's Pit (west, past the Torture Room) with the quest active to wake the Catacomb Headsman; defeat him and bring the axe: in return you get the Iron Key, one of the two for the Chained King's gate.",
                          "El Carcelero Ciego, en la Nave de los Huesos, quiere el hacha del Verdugo para saldar sus cuentas. Toca la jaula del Pozo del Verdugo (oeste, tras la Sala de Tortura) con la misión activa para despertar al Verdugo de las Catacumbas; derrótalo y trae el hacha: a cambio recibes la Llave de Hierro, una de las dos del portón del Rey Encadenado."),
    "QUEST_CT_SOUL": ("O Grilhão da Alma", "The Soul Shackle", "El grillete del alma"),
    "QUEST_CT_SOUL_DESC": ("A Prisioneira, na Capela dos Acorrentados (leste, depois do Ossuário), está presa há séculos a um grilhão que prende também uma alma. A fala dela desperta a Alma Acorrentada; derrote-a e traga o grilhão para receber a Chave de Osso, a outra do portão do Rei Acorrentado.",
                           "The Prisoner, in the Chapel of the Chained (east, past the Ossuary), has been held for centuries by a shackle that also binds a soul. Her words wake the Chained Soul; defeat it and bring the shackle to receive the Bone Key, the other one for the Chained King's gate.",
                           "La Prisionera, en la Capilla de los Encadenados (este, tras el Osario), lleva siglos presa de un grillete que también ata un alma. Sus palabras despiertan al Alma Encadenada; derrótala y trae el grillete para recibir la Llave de Hueso, la otra del portón del Rey Encadenado."),
    "QUEST_CT_GATE": ("O Portão do Rei Acorrentado", "The Chained King's Gate", "El portón del Rey Encadenado"),
    "QUEST_CT_GATE_DESC": ("O Diretor das Catacumbas, no corredor ao norte da Galeria dos Condenados, só abre o portão para quem trouxer as duas chaves: a de Ferro (Carcereiro Cego) e a de Osso (Prisioneira). Atrás dele fica a Cripta do Rei Acorrentado.",
                           "The Catacomb Warden, in the lane north of the Gallery of the Condemned, only opens the gate for those with both keys: the Iron (Blind Jailer) and the Bone (Prisoner). Beyond lies the Chained King's Crypt.",
                           "El Director de las Catacumbas, en el pasillo al norte de la Galería de los Condenados, solo abre el portón a quien traiga las dos llaves: la de Hierro (Carcelero Ciego) y la de Hueso (Prisionera). Tras él está la Cripta del Rey Encadenado."),
    "DLG_CTMONK_1": ("Que a paz acompanhe vocês, mesmo aqui embaixo. Eu rezo pelos presos das Catacumbas, que morreram atrás das grades sem nunca terem sido julgados.",
                     "Peace be with you, even down here. I pray for the prisoners of the Catacombs, who died behind bars without ever being tried.",
                     "Que la paz los acompañe, incluso aquí abajo. Rezo por los presos de las Catacumbas, que murieron tras las rejas sin haber sido juzgados."),
    "DLG_CTMONK_2": ("As duas Alas das Celas, a oeste e a leste da Nave dos Ossos, ainda estão cheias de mortos de guarda. Eles não deixam nenhuma alma passar em paz.",
                     "Both Cell Wings, west and east of the Nave of Bones, are still full of the dead on guard. They let no soul pass in peace.",
                     "Las dos Alas de Celdas, al oeste y al este de la Nave de los Huesos, siguen llenas de muertos de guardia. No dejan pasar ningún alma en paz."),
    "DLG_CTMONK_3": ("Limpem as duas e eu pago pelo trabalho. Depois disso, o Carcereiro Cego e a Prisioneira têm contas a acertar, e são eles que guardam as chaves do portão do Rei.",
                     "Clear both and I will pay for the work. After that, the Blind Jailer and the Prisoner have scores to settle, and they keep the keys to the King's gate.",
                     "Limpien las dos y pagaré el trabajo. Después, el Carcelero Ciego y la Prisionera tienen cuentas pendientes, y ellos guardan las llaves del portón del Rey."),
    "DLG_CTMONK_ACTIVE": ("As Alas das Celas ficam à esquerda e à direita da Nave dos Ossos. Ouçam as correntes: onde elas arrastam, há um morto de guarda.",
                          "The Cell Wings lie left and right of the Nave of Bones. Listen for the chains: where they drag, a dead guard stands.",
                          "Las Alas de Celdas están a la izquierda y a la derecha de la Nave de los Huesos. Escuchen las cadenas: donde arrastran, hay un muerto de guardia."),
    "DLG_CTMONK_DONE": ("As celas estão em silêncio pela primeira vez em séculos. Sigam adiante: a Galeria dos Condenados os espera.",
                        "The cells are silent for the first time in centuries. Go on: the Gallery of the Condemned awaits you.",
                        "Las celdas están en silencio por primera vez en siglos. Sigan adelante: la Galería de los Condenados los espera."),
    "DLG_CTJAILER_1": ("Não enxergo desde o dia em que o Rei me tirou os olhos, mas conheço cada cela de cor. Fui o carcereiro destas Catacumbas por quarenta anos, e o Carrasco era meu único amigo.",
                       "I have not seen since the day the King took my eyes, but I know every cell by heart. I was jailer of these Catacombs for forty years, and the Headsman was my only friend.",
                       "No veo desde el día en que el Rey me quitó los ojos, pero conozco cada celda de memoria. Fui carcelero de estas Catacumbas cuarenta años, y el Verdugo era mi único amigo."),
    "DLG_CTJAILER_2": ("Ele morreu no Poço, a oeste, depois da Sala de Tortura, e voltou pendurado numa gaiola, com o machado nas costas, ainda querendo trabalho. Não é vida para um amigo.",
                       "He died in the Pit, to the west, past the Torture Room, and came back hanging in a gibbet, axe on his back, still wanting work. That is no life for a friend.",
                       "Murió en el Pozo, al oeste, tras la Sala de Tortura, y volvió colgado de una jaula, con el hacha a la espalda, aún queriendo trabajo. No es vida para un amigo."),
    "DLG_CTJAILER_3": ("Toquem a gaiola, derrubem o Carrasco e tragam o machado. Em troca eu dou a Chave de Ferro, uma das duas que abrem o portão do Rei Acorrentado, no corredor ao norte da Galeria.",
                       "Touch the gibbet, bring down the Headsman and bring me the axe. In return I give the Iron Key, one of the two that open the Chained King's gate, in the lane north of the Gallery.",
                       "Toquen la jaula, derriben al Verdugo y tráiganme el hacha. A cambio doy la Llave de Hierro, una de las dos que abren el portón del Rey Encadenado, en el pasillo al norte de la Galería."),
    "DLG_CTJAILER_ACTIVE": ("O Poço do Carrasco fica a oeste: passem pela Ala das Celas e pela Sala de Tortura. O machado é pesado e tem um cabo de osso. Eu o reconheço pelo cheiro.",
                            "The Headsman's Pit is to the west: go through the Cell Wing and the Torture Room. The axe is heavy and has a bone handle. I know it by the smell.",
                            "El Pozo del Verdugo está al oeste: pasen por el Ala de Celdas y la Sala de Tortura. El hacha es pesada y tiene mango de hueso. La reconozco por el olor."),
    "DLG_CTJAILER_DONE": ("O machado do meu amigo! Agora ele pode descansar. A Chave de Ferro é de vocês: levem-na ao Diretor, junto com a de Osso.",
                          "My friend's axe! Now he can rest. The Iron Key is yours: take it to the Warden, together with the Bone one.",
                          "¡El hacha de mi amigo! Ahora podrá descansar. La Llave de Hierro es suya: llévenla al Director, junto con la de Hueso."),
    "DLG_CTGIBBET_1": ("A gaiola balança sem vento, e as correntes tilintam como se alguém respirasse lá dentro. Algo enorme se mexe sobre as ossadas.",
                       "The gibbet sways without wind, and the chains chime as if someone breathed inside. Something huge stirs among the bones.",
                       "La jaula se balancea sin viento, y las cadenas tintinean como si alguien respirara dentro. Algo enorme se mueve entre los huesos."),
    "DLG_CTGIBBET_2": ("O Carrasco das Catacumbas desce!", "The Catacomb Headsman descends!", "¡El Verdugo de las Catacumbas desciende!"),
    "DLG_CTGIBBET_LOCKED": ("Uma gaiola de ferro, pendurada de uma viga, rangendo. Nada responde ao seu toque.", "An iron gibbet hanging from a beam, creaking. Nothing answers your touch.", "Una jaula de hierro colgada de una viga, crujiendo. Nada responde a tu toque."),
    "DLG_CTPRISONER_1": ("Estou aqui desde antes de vocês nascerem, acorrentada a este altar. Dizem que eu roubei do Rei; nunca roubei nada. Só vi o que não devia.",
                         "I have been here since before you were born, chained to this altar. They say I stole from the King; I never stole anything. I only saw what I should not have.",
                         "Llevo aquí desde antes de que nacieran, encadenada a este altar. Dicen que le robé al Rey; nunca robé nada. Solo vi lo que no debía."),
    "DLG_CTPRISONER_2": ("O grilhão no meu pulso prende também uma alma, a do guarda que me vigiava e morreu de culpa. Ela se arrasta pela Capela e não me deixa dormir.",
                         "The shackle on my wrist also binds a soul, that of the guard who watched me and died of guilt. It drags itself through the Chapel and will not let me sleep.",
                         "El grillete de mi muñeca también ata un alma, la del guardia que me vigilaba y murió de culpa. Se arrastra por la Capilla y no me deja dormir."),
    "DLG_CTPRISONER_3": ("Vou soltá-la para vocês, aqui na Capela. Derrubem a Alma Acorrentada e tragam o grilhão: eu dou a Chave de Osso, a outra do portão do Rei Acorrentado.",
                         "I will free it for you, here in the Chapel. Bring down the Chained Soul and bring the shackle: I give the Bone Key, the other for the Chained King's gate.",
                         "La liberaré para ustedes, aquí en la Capilla. Derriben al Alma Encadenada y traigan el grillete: doy la Llave de Hueso, la otra del portón del Rey Encadenado."),
    "DLG_CTPRISONER_ACTIVE": ("O grilhão é de ferro frio e brilha em azul quando a alma está perto. Derrubem-na com cuidado: ela chora antes de atacar.",
                              "The shackle is cold iron and glows blue when the soul is near. Bring it down carefully: it weeps before it strikes.",
                              "El grillete es de hierro frío y brilla en azul cuando el alma está cerca. Derríbenla con cuidado: llora antes de atacar."),
    "DLG_CTPRISONER_DONE": ("Estou livre! Depois de tantos anos... A Chave de Osso é de vocês: levem-na ao Diretor, junto com a de Ferro.",
                            "I am free! After so many years... The Bone Key is yours: take it to the Warden, together with the Iron one.",
                            "¡Estoy libre! Después de tantos años... La Llave de Hueso es suya: llévenla al Director, junto con la de Hierro."),
    "DLG_CTPRISONER_WAIT": ("As correntes ainda tilintam, mas já não me pesam. Vão em paz.", "The chains still chime, but they no longer weigh on me. Go in peace.", "Las cadenas aún tintinean, pero ya no me pesan. Vayan en paz."),
    "DLG_CTWARDEN_1": ("Alto. Este portão fecha a Cripta, e na Cripta o Rei Acorrentado paga a pena que o reino lhe deve. Eu sou o último que o visita.",
                       "Halt. This gate closes the Crypt, and in the Crypt the Chained King serves the sentence the kingdom owes him. I am the last who visits him.",
                       "Alto. Este portón cierra la Cripta, y en la Cripta el Rey Encadenado cumple la pena que el reino le debe. Soy el último que lo visita."),
    "DLG_CTWARDEN_2": ("O portão só abre com DUAS chaves: a de Ferro e a de Osso. A primeira está com o Carcereiro Cego, na Nave dos Ossos; a segunda, com a Prisioneira, na Capela dos Acorrentados, a leste.",
                       "The gate only opens with TWO keys: the Iron and the Bone. The first is with the Blind Jailer in the Nave of Bones; the second, with the Prisoner in the Chapel of the Chained, to the east.",
                       "El portón solo abre con DOS llaves: la de Hierro y la de Hueso. La primera la tiene el Carcelero Ciego, en la Nave de los Huesos; la segunda, la Prisionera, en la Capilla de los Encadenados, al este."),
    "DLG_CTWARDEN_3": ("Cada uma cobra um preço: um machado, um grilhão. Tragam as duas chaves a mim e eu abro a passagem.",
                       "Each charges a price: an axe, a shackle. Bring both keys to me and I will open the way.",
                       "Cada una cobra un precio: un hacha, un grillete. Tráiganme las dos llaves y abro el paso."),
    "DLG_CTWARDEN_ACTIVE": ("Só abro com as duas chaves, Ferro e Osso, na mesma bolsa. O Carcereiro Cego fica na Nave dos Ossos; a Prisioneira, na Capela, a leste.",
                            "I only open with both keys, Iron and Bone, in the same bag. The Blind Jailer is in the Nave of Bones; the Prisoner, in the Chapel, to the east.",
                            "Solo abro con las dos llaves, Hierro y Hueso, en la misma bolsa. El Carcelero Ciego está en la Nave de los Huesos; la Prisionera, en la Capilla, al este."),
    "DLG_CTWARDEN_DONE": ("As duas chaves! O portão está aberto. Cuidado: o Rei Acorrentado quebrou todas as correntes que o prenderam, menos a da vergonha.",
                          "Both keys! The gate is open. Beware: the Chained King has broken every chain that held him, except the one of shame.",
                          "¡Las dos llaves! El portón está abierto. Cuidado: el Rey Encadenado ha roto todas las cadenas que lo ataron, menos la de la vergüenza."),
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
    for dst, src, mul in (("key_iron", "key_spades", (0.7, 0.75, 0.9)), ("key_bone", "key_clubs", (1.4, 1.35, 1.0)), ("headsman_axe", "bone_dagger", (0.8, 0.5, 0.45)),
                          ("soul_shackle", "crown_jewel", (0.6, 0.85, 1.4))):
        im = Image.open(ICONS + src + ".png").convert("RGBA")
        r_, g_, b_, a_ = im.split()
        Image.merge("RGBA", (r_.point(lambda v: min(255, int(v * mul[0]))), g_.point(lambda v: min(255, int(v * mul[1]))), b_.point(lambda v: min(255, int(v * mul[2]))), a_)).save(ICONS + dst + ".png")
except Exception as exc:
    print("aviso: ícones não gerados:", exc)

for path, data in ((ARENAS, arenas), (MONSTERS, monsters), (NPCS, npcs), (QUESTS, quests), (VALUABLES, valuables)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
print("blocos de celas:", len(blocks))
print("OK catacombs", len(rooms), "salas,", len(decor), "peças de cenário,", len(crowd), "presos/gente,", len(encounters), "encontros, %d m2" % AREA_M2)
