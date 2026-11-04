"""Mapa da Floresta Escura (dark_forest_01_woods), ampliado: mesma estrutura da Floresta (partida com aldeia, duas áreas de mini-chefe com NPCs, guardião do portão com duas chaves e covil do chefe final)
com outro caminho. Mata aberta de grama escura cercada de arbustos e bambus (como a Floresta), com árvores secas, cogumelos, morcegos e cobras como parte do cenário.
Caminho: a Clareira da Borda (partida) abre no Matagal (centro) e dali saem TRÊS rotas até a Mata Seca: oeste (Pântano das Cobras -> Clareira das Serpentes), leste (Bosque dos Cogumelos -> Círculo
de Esporos) e uma direta ao norte; a Mata Seca segue para o Bosque dos Morcegos, o corredor do portão (o Guardião só abre com as duas chaves) e o Covil do Ancião Sombrio (chefe final, com a saída).
  Herbalista Mirta (Bosque dos Cogumelos) pede a Presa da Víbora Anciã: tocar o Totem das Serpentes (Clareira, missão ativa) desperta a Víbora Anciã; entrega a Chave de Musgo.
  Encantador Zhar (Pântano das Cobras) pede a Coroa de Esporos: o Cogumelo Ancestral (Círculo de Esporos) desperta o Rei dos Esporos; entrega a Chave de Espinho.
Cobras (Snake_*, feitas por tools/assets/build_snakes.py): enroscadas e deslizando em círculos; morcegos: papel "bat" do crowd (voam em círculos). Sorteio com semente fixa; idempotente; chamado no fim de
tools/assets/build_maps.py (antes de set_map_order.py). Também põe NPCs, missões, itens, textos pt/en/es e ícones.
uso: python3 tools/assets/build_darkforest.py   (a partir da raiz do projeto)"""
import json, math, random, re
ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES = ("data/arenas.json", "data/monsters.json", "data/npcs.json", "data/quests.json", "data/valuables.json")
arenas, monsters, npcs, quests, valuables = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES))
rng = random.Random("darkforest-v2")
DOOR = 6.0

ROOMS = [("edge", 0, 0, 44, 16), ("thicket", 0, -36, 56, 56), ("bog_w", -52, -36, 48, 40), ("grove_e", 52, -36, 48, 40), ("hollow_w", -52, -76, 48, 40), ("ring_e", 52, -76, 48, 40),
         ("dead_wood", 0, -86, 56, 44), ("bat_grove", 0, -130, 56, 44), ("gate_lane", 0, -166, 12, 28), ("lair", 0, -210, 60, 60)]
LINKS = [("edge", "thicket", "north"), ("thicket", "bog_w", "west"), ("thicket", "grove_e", "east"), ("bog_w", "hollow_w", "north"), ("grove_e", "ring_e", "north"),
         ("hollow_w", "dead_wood", "east"), ("ring_e", "dead_wood", "west"), ("thicket", "dead_wood", "north"), ("dead_wood", "bat_grove", "north"), ("bat_grove", "gate_lane", "north"),
         ("gate_lane", "lair", "north")]
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
    if rid in ("edge", "lair"):
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


clone("fd_viper", "ruin_warden", _comment="Mini-chefe da Floresta Escura (Clareira das Serpentes): a Víbora Anciã, serpente enorme que o Totem das Serpentes desperta; investidas.",
      name_key="MONSTER_FD_VIPER", max_health=360, damage=30, size=3.4, element="earth", look="reptile", color=[0.4, 0.8, 0.4], quest_drop="viper_fang")
clone("fd_spore_king", "ruin_warden", _comment="Mini-chefe da Floresta Escura (Círculo de Esporos): o Rei dos Esporos, cogumelo gigante que o Cogumelo Ancestral desperta; investidas.",
      name_key="MONSTER_FD_SPORE_KING", max_health=380, damage=28, size=3.6, element="water", look="fungus", color=[0.85, 0.65, 1.0], quest_drop="spore_crown")
clone("fd_elder", "sphinx", _comment="Chefe final da Floresta Escura: o Ancião Sombrio, árvore morta e viva que guarda o Covil atrás do portão; investidas e pisões (modelo do monstro da floresta).",
      name_key="MONSTER_FD_ELDER", max_health=1400, damage=46, size=4.6, element="earth", look="forest", color=[0.55, 0.65, 0.8], chest_loot="chest")
valuables.update({
    "viper_fang": {"name_key": "VALUABLE_VIPER_FANG", "value": 0, "maps": [], "quest_item": True, "model": "Dungeon_Bone"},
    "spore_crown": {"name_key": "VALUABLE_SPORE_CROWN", "value": 0, "maps": [], "quest_item": True, "model": "Mushroom_Cluster"},
    "key_moss": {"name_key": "VALUABLE_KEY_MOSS", "value": 0, "maps": [], "quest_item": True, "model": "Key_Clubs"},
    "key_thorn": {"name_key": "VALUABLE_KEY_THORN", "value": 0, "maps": [], "quest_item": True, "model": "Key_Spades"}})

# ---------------------------------------------------------------- objetos e encontros
SUMMON_VIPER = {"id": "fd_viper", "position": rp("hollow_w", 0, 8), "spread": 3.0, "toast": "TOAST_TOTEM_AWAKENS", "monsters": [{"monster": "fd_viper", "count": 1, "rank": "miniboss"}]}
SUMMON_SPORE = {"id": "fd_spore", "position": rp("ring_e", 0, 8), "spread": 3.0, "toast": "TOAST_SPORE_AWAKENS", "monsters": [{"monster": "fd_spore_king", "count": 1, "rank": "miniboss"}]}
props = [
    {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_FARM", "position": [-6, 3], "to": "farm_01_fields", "entry": "dark_forest", "expedition_end": True},
    {"id": "victory_portal", "kind": "exit", "name_key": "PROP_RETURN_FARM", "position": [0, -236.0], "to": "farm_01_fields", "entry": "dark_forest", "after_victory": True, "group": True},
    {"id": "fd_woodcutter", "kind": "npc", "npc": "fd_woodcutter", "position": [20, -60], "rotation": 200},
    {"id": "fd_herbalist", "kind": "npc", "npc": "fd_herbalist", "position": rp("grove_e", -14, 6), "rotation": 160},
    {"id": "fd_totem", "kind": "npc", "npc": "fd_totem", "kit": "Pr_Obelisk1", "rotation": 0, "position": rp("hollow_w"), "solid": [1.4, 1.4], "summon": SUMMON_VIPER, "needs_quest": "fd_fang"},
    {"id": "fd_charmer", "kind": "npc", "npc": "fd_charmer", "position": rp("bog_w", -10, 6), "rotation": 20},
    {"id": "fd_mushroom", "kind": "npc", "npc": "fd_mushroom", "kit": "Mushroom_Cluster", "rotation": 0, "position": rp("ring_e"), "solid": [1.2, 1.2], "summon": SUMMON_SPORE, "needs_quest": "fd_crown"},
    {"id": "boss_gate", "kind": "gate", "name_key": "PROP_BOSS_GATE", "position": [0.0, -172.0], "rotation": 0, "scale": 3.0, "block": 12.0, "count": 2, "opened_by": "fd_gate"},
    {"id": "fd_warden", "kind": "npc", "npc": "fd_warden", "position": [0.0, -168.0], "rotation": 0}]
chest_spots = [rp("edge", -16, -2), rp("thicket", -20, -20), rp("thicket", 22, -48), rp("bog_w", -18, -14), rp("grove_e", 18, -14), rp("hollow_w", -16, 14), rp("ring_e", 16, 14),
               rp("dead_wood", -22, 14), rp("dead_wood", 22, -14), rp("bat_grove", -22, 14), rp("bat_grove", 22, -12), rp("lair", -22, 22), rp("lair", 22, 22)]
for i, pos in enumerate(chest_spots, start=1):
    props.append({"id": "fd_chest_%d" % i, "kind": "chest", "position": pos, "loot": "chest"})
for i, pos in enumerate((rp("thicket", 0, -18), rp("bog_w", 10, 12), rp("grove_e", -10, 12), rp("dead_wood", 0, -4), rp("lair", 0, 22)), start=1):
    props.append({"id": "fd_potions_%d" % i, "kind": "chest", "position": pos, "loot": "potion_chest", "model": "Chest_Mini"})
E = lambda eid, pos, *mons: {"id": eid, "position": pos, "monsters": [{"monster": m, "count": c} for m, c in mons]}
encounters = [
    E("fd_thicket_a", rp("thicket", -14, 6), ("stalker", 3)), E("fd_thicket_b", rp("thicket", 14, -8), ("goblin", 4)), E("fd_thicket_c", rp("thicket", -8, -16), ("plague_bat", 4)),
    E("fd_thicket_d", rp("thicket", 16, 16), ("forest_reptile", 3)),
    E("fd_bog_a", rp("bog_w", -14, -4), ("forest_reptile", 4), ("venom_scorpion", 2)), E("fd_bog_b", rp("bog_w", 12, -8), ("forest_reptile", 3)), E("fd_bog_c", rp("bog_w", -8, 12), ("venom_scorpion", 3)),
    E("fd_mimic_bog", rp("bog_w", 16, 12), ("chest_mimic", 1)),
    E("fd_grove_a", rp("grove_e", 14, -4), ("fungus_uncle", 2)), E("fd_grove_b", rp("grove_e", -12, -10), ("fungus_uncle", 1), ("goblin", 3)), E("fd_grove_c", rp("grove_e", 8, 12), ("goblin", 4)),
    E("fd_mimic_grove", rp("grove_e", -16, 12), ("chest_mimic", 1)),
    E("fd_hollow_a", rp("hollow_w", -14, -8), ("forest_reptile", 3)), E("fd_hollow_b", rp("hollow_w", 14, -6), ("venom_scorpion", 3)),
    E("fd_ring_a", rp("ring_e", 14, -8), ("fungus_uncle", 2)), E("fd_ring_b", rp("ring_e", -14, -6), ("goblin", 4)),
    E("fd_dead_a", rp("dead_wood", -16, -6), ("zombie", 4)), E("fd_dead_b", rp("dead_wood", 16, 8), ("skeleton", 4)), E("fd_dead_c", rp("dead_wood", 0, -14), ("night_demon", 2)),
    E("fd_dead_d", rp("dead_wood", -18, 12), ("shadow_spirit", 2)),
    E("fd_bats_a", rp("bat_grove", -18, -6), ("plague_bat", 5)), E("fd_bats_b", rp("bat_grove", 18, 6), ("plague_bat", 5)), E("fd_bats_c", rp("bat_grove", 0, 0), ("stalker", 3)),
    E("fd_bats_d", rp("bat_grove", -22, 12), ("shadow_spirit", 2)),
    E("fd_lair_a", rp("lair", -18, 8), ("zombie", 3), ("skeleton", 2)), E("fd_lair_b", rp("lair", 18, 8), ("zombie", 3), ("skeleton", 2)), E("fd_mimic_lair", rp("lair", -24, 18), ("chest_mimic", 1)),
    E("fd_boss", rp("lair", 0, -12), ("fd_elder", 1))]
interest = [p["position"] for p in props] + [e["position"] for e in encounters] + [SUMMON_VIPER["position"], SUMMON_SPORE["position"], [0, 3]] + [list(d) for d in door_points]
# caminhos livres: pontos ao longo das retas entre o centro de cada sala e suas portas (as árvores não fecham a passagem)
path_points = []
for a, b, side in LINKS:
    for rid in (a, b):
        cx_, cz_ = by_id[rid][1], by_id[rid][2]
        dp = next(pt for (aa, bb, ss), pt in zip(LINKS, door_points) if (aa, bb, ss) == (a, b, side))
        steps = max(int(math.hypot(dp[0] - cx_, dp[1] - cz_) / 4), 1)
        for k in range(steps + 1):
            path_points.append((cx_ + (dp[0] - cx_) * k / steps, cz_ + (dp[1] - cz_) * k / steps))
decor, crowd, taken = [], [], []


def near_interest(x, z, rad):
    return any(math.hypot(x - ix, z - iz) < rad for ix, iz in interest)


def near_path(x, z, rad):
    return any(math.hypot(x - px, z - pz) < rad for px, pz in path_points)


def near_taken(x, z, rad):
    return any(math.hypot(x - tx, z - tz) < tr + rad for tx, tz, tr in taken)


def put(piece, x, z, rot=None, scale=1.0, solid=None, y=None, r=0.8, free=2.2, force=False, wall=3.2, path=2.8):
    if room_at(x, z, -wall) is None:
        return False
    if not force and (near_interest(x, z, free) or near_taken(x, z, r) or (solid and near_path(x, z, path))):
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


def scatter(rid, pieces, n, scale=(1.0, 1.0), solid=None, r=0.9, tries=40, margin=3.5, **kw):
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


lights = 0


def light(x, z, color=(1.0, 0.6, 0.25), rng_=8.0, energy=1.2, y=1.6, flicker=False):
    global lights
    d = {"light": list(color), "position": [round(x, 1), round(z, 1)], "y": y, "range": rng_, "energy": energy}
    if flicker:
        d["flicker"] = True
    decor.append(d)
    lights += 1


DEAD = ["Dead_Tree"]
BUSH = ["Pl_Bush", "Pl_Hemp", "Pl_Shrub1", "Pl_Shrub2", "Pl_Shrub3", "Pl_Shrub4", "Pl_Shrub5", "Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Weed4", "Pl_Grass1", "Pl_Grass2", "Pl_Swirl"]
MUSH = ["Mushroom_Cluster", "Mushroom_Tall", "Mushroom_Flat"]
ROCKS = ["Mossy_Slab_1", "Mossy_Slab_2", "Mossy_Slab_3", "Mossy_Formation_1", "Mossy_Formation_2", "Rock_1", "Rock_2", "RockP_1", "RockP_2"]
BONES = ["Dungeon_BonePile_%d" % i for i in range(1, 7)] + ["Dungeon_CrossBones", "Dungeon_Skull_1", "Dungeon_Skull_2", "Dungeon_Pelvis", "Dungeon_Spine"]
GRAVES = ["Pr_Cross1", "Pr_Cross2", "Pr_Cross3", "Pr_Cross4", "Pr_Tombstone1", "Pr_Tombstone2", "Pr_Tombstone3"]
WEBS = ["Web_Round_Up", "Web_Square_Up", "Web_Round_Flat", "Web_Square_Flat"]
COILS = ["Snake_Coil_Green", "Snake_Coil_Dark", "Snake_Coil_Red"]
SLITHERS = ["Snake_Slither_Green", "Snake_Slither_Dark", "Snake_Slither_Red"]


def dead_trees(rid, n, scale=(0.5, 0.95)):
    return scatter(rid, DEAD, int(n * 1.7), scale=scale, solid=(1.0, 1.0), r=2.4, margin=3.5, free=3.0)


def snakes(rid, coil, slither):
    scatter(rid, COILS, coil, scale=(2.6, 4.0), solid=(0.5, 0.5), r=0.3, free=2.0, tries=80)
    cx, cz, w, h = by_id[rid][1:]
    done = 0
    for _ in range(slither * 25):
        if done >= slither:
            break
        x, z = cx + rng.uniform(-w / 2 + 5, w / 2 - 5), cz + rng.uniform(-h / 2 + 5, h / 2 - 5)
        radius = round(rng.uniform(1.2, 3.0), 2)
        if room_at(x, z, -(radius + 3.0)) is None or near_interest(x, z, 3.0) or near_taken(x, z, 0.4 + radius * 0.4):
            continue
        decor.append({"piece": rng.choice(SLITHERS), "position": [round(x, 2), round(z, 2)], "y": 0.02, "scale": round(rng.uniform(2.6, 3.6), 2),
                      "swim": {"radius": radius, "speed": round(rng.uniform(0.45, 0.8), 2), "phase": round(rng.uniform(0, 6.28), 2)}})
        taken.append((x, z, radius * 0.5))
        done += 1


def mushrooms(rid, n, big=(2.5, 5.0), glow=0):
    for _ in range(n):
        for _t in range(40):
            cx, cz, w, h = by_id[rid][1:]
            x, z = cx + rng.uniform(-w / 2 + 4, w / 2 - 4), cz + rng.uniform(-h / 2 + 4, h / 2 - 4)
            s = rng.uniform(*big)
            piece = rng.choice(MUSH)
            if put(piece, x, z, scale=s, solid=[0.5 * s, 0.5 * s] if piece == "Mushroom_Cluster" and s > 3.0 else None, r=0.6 * s, free=2.0):
                if glow and lights < 70 and rng.random() < 0.18:
                    light(x, z, rng.choice(((0.4, 1.0, 0.5), (0.7, 0.4, 1.0), (0.3, 0.8, 1.0))), 7.0, 1.2, 0.8)
                break


def bats(rid, n, radius=(2.5, 5.0)):
    cx, cz, w, h = by_id[rid][1:]
    for _ in range(n):
        x, z = cx + rng.uniform(-w / 2 + 6, w / 2 - 6), cz + rng.uniform(-h / 2 + 6, h / 2 - 6)
        crowd.append({"role": "bat", "position": [round(x, 1), round(z, 1)], "rotation": rng.randrange(0, 360), "radius": round(rng.uniform(*radius), 1), "height": round(rng.uniform(1.8, 3.4), 1),
                      "speed": round(rng.uniform(2.4, 3.8), 1)})


# --- Clareira da Borda: fogueira, lenha, lampião, cruzes e placa
put("Tv_Fire", -10, -3, rot=0, scale=1.5, solid=[1.2, 1.0], r=1.6, free=0.5, wall=2.0)
decor.append({"piece": "Fire_Flame", "position": [-10, -3], "y": 0.2, "scale": 1.4, "flicker": True})
light(-10, -3, (1.0, 0.6, 0.25), 12.0, 1.8, 1.2, flicker=True)
for piece, x, z in (("Tv_Firewood", -13, -1), ("Vl_Logs", 14, 4), ("Vl_ChoppingBlock", 12, -2), ("Pr_LampPost", 3, -5), ("Signpost_Medieval", 4, 5)):
    put(piece, x, z, rot=rng.randrange(0, 360, 15), solid=[1.0, 1.0] if piece != "Signpost_Medieval" else None, r=1.2, free=1.0, wall=1.5)
light(3, -5, (1.0, 0.7, 0.35), 8.0, 1.2, 2.2)
dead_trees("edge", 6)
scatter("edge", BUSH, 30, scale=(0.9, 1.4), r=0.6, margin=2.5)
scatter("edge", GRAVES, 4, solid=(0.8, 0.8), r=1.0, margin=2.5)
# --- Matagal (hub): floresta cerrada de árvores secas, cogumelos, mato, cruzes e algumas cobras
dead_trees("thicket", 62)
scatter("thicket", BUSH, 80, scale=(0.9, 1.4), r=0.6)
mushrooms("thicket", 24, big=(1.5, 3.0), glow=1)
scatter("thicket", ROCKS, 14, scale=(0.9, 1.5), solid=(1.0, 1.0), r=1.2)
scatter("thicket", GRAVES, 10, solid=(0.8, 0.8), r=1.0)
scatter("thicket", BONES, 10, scale=(2.4, 3.4), r=0.8)
scatter("thicket", WEBS, 8, scale=(1.8, 2.8), r=1.0)
snakes("thicket", 8, 8)
# --- Pântano das Cobras (oeste): juncos, árvores secas retorcidas, muitas cobras
dead_trees("bog_w", 34)
scatter("bog_w", ["Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Weed4", "Pl_Weed5", "Pl_Grass1", "Pl_Grass2", "Pl_Grass3", "Pl_Swirl"], 120, scale=(1.0, 1.6), r=0.6)
scatter("bog_w", ROCKS, 10, scale=(0.9, 1.5), solid=(1.0, 1.0), r=1.2)
scatter("bog_w", BONES, 10, scale=(2.4, 3.4), r=0.8)
mushrooms("bog_w", 10, big=(1.5, 3.0))
snakes("bog_w", 16, 18)
# --- Bosque dos Cogumelos (leste): cogumelos gigantes que brilham
dead_trees("grove_e", 16)
mushrooms("grove_e", 70, big=(3.0, 7.5), glow=1)
scatter("grove_e", BUSH, 50, scale=(0.9, 1.3), r=0.6)
snakes("grove_e", 4, 4)
bats("grove_e", 4)
# --- Clareira das Serpentes (mini-chefe 1): círculo de obeliscos em volta do totem, cobras enroscadas, ossos
cx, cz = by_id["hollow_w"][1:3]
for k in range(8):
    a = math.tau * (k + 0.5) / 8
    put(("Pr_Obelisk1", "Pr_Obelisk2", "Pr_Obelisk3")[k % 3], cx + 10 * math.cos(a), cz + 10 * math.sin(a), rot=0, solid=[1.3, 1.3], r=1.6, free=1.0)
light(cx, cz, (0.4, 1.0, 0.45), 14.0, 1.8, 1.8)
dead_trees("hollow_w", 20)
snakes("hollow_w", 18, 12)
scatter("hollow_w", BONES, 14, scale=(2.4, 3.4), r=0.8)
scatter("hollow_w", ROCKS, 8, scale=(0.9, 1.5), solid=(1.0, 1.0), r=1.2)
scatter("hollow_w", BUSH, 40, scale=(0.9, 1.4), r=0.6)
# --- Círculo de Esporos (mini-chefe 2): anel de cogumelos em volta do cogumelo ancestral
cx, cz = by_id["ring_e"][1:3]
for k in range(14):
    a = math.tau * (k + 0.5) / 14
    s = rng.uniform(2.6, 3.4)
    put("Mushroom_Cluster", cx + 11 * math.cos(a), cz + 11 * math.sin(a), rot=rng.randrange(0, 360, 15), scale=s, solid=[0.5 * s, 0.5 * s], r=1.6, free=1.0)
light(cx, cz, (0.75, 0.4, 1.0), 14.0, 2.0, 1.6)
mushrooms("ring_e", 44, big=(2.5, 6.0), glow=1)
dead_trees("ring_e", 12)
scatter("ring_e", BUSH, 40, scale=(0.9, 1.4), r=0.6)
snakes("ring_e", 4, 4)
# --- Mata Seca: o mar de árvores mortas, lápides, ossos e teias
dead_trees("dead_wood", 70)
scatter("dead_wood", GRAVES, 18, solid=(0.8, 0.8), r=1.0)
scatter("dead_wood", BONES, 20, scale=(2.4, 3.6), r=0.8)
scatter("dead_wood", WEBS, 14, scale=(1.8, 2.8), r=1.0)
scatter("dead_wood", BUSH, 50, scale=(0.9, 1.3), r=0.6)
scatter("dead_wood", ROCKS, 8, scale=(0.9, 1.5), solid=(1.0, 1.0), r=1.2)
mushrooms("dead_wood", 16, big=(1.5, 3.0))
snakes("dead_wood", 8, 8)
# --- Bosque dos Morcegos: ruínas, árvores secas, ossos, muitos morcegos
dead_trees("bat_grove", 44)
for dx, dz in ((-18, -8), (18, -8), (-18, 10), (18, 10)):
    put("Pr_BrokenPillar1" if dx < 0 else "Pr_BrokenPillar2", by_id["bat_grove"][1] + dx, by_id["bat_grove"][2] + dz, rot=0, solid=[1.2, 1.2], r=1.4, free=1.0)
scatter("bat_grove", BONES, 24, scale=(2.4, 3.6), r=0.8)
scatter("bat_grove", WEBS, 16, scale=(1.8, 2.8), r=1.0)
scatter("bat_grove", BUSH, 40, scale=(0.9, 1.3), r=0.6)
scatter("bat_grove", GRAVES, 8, solid=(0.8, 0.8), r=1.0)
light(*rp("bat_grove"), (0.5, 0.5, 0.9), 14.0, 1.4, 2.4)
# --- corredor do portão: tochas e crânios
for z in (-158, -166, -174):
    for x in (-4.6, 4.6):
        put("Tv_Torch", x, z, scale=1.5, r=0.5, free=1.0, wall=1.0)
        light(x, z, (1.0, 0.6, 0.3), 6.0, 0.9, 1.8, flicker=True)
scatter("gate_lane", ["Dungeon_Skull_1", "Dungeon_Skull_2", "Dungeon_BonePile_1"], 4, scale=(2.4, 3.2), r=0.8, margin=2.5)
# --- Covil do Ancião Sombrio: anel de árvores mortas gigantes, ossos, cogumelos roxos, cobras vermelhas
cx, cz = by_id["lair"][1:3]
for k in range(16):
    a = math.tau * (k + 0.5) / 16
    if abs(math.cos(a)) < 0.2 and math.sin(a) > 0.5:
        continue                                                        # a entrada, ao sul
    s = rng.uniform(1.0, 1.5)
    put("Dead_Tree", cx + 20 * math.cos(a), cz + 20 * math.sin(a) * 0.9 - 3, rot=rng.randrange(0, 360, 15), scale=s, solid=[1.0 * s, 1.0 * s], r=2.5 * s, free=1.0)
light(cx, cz - 8, (0.55, 0.6, 0.9), 16.0, 1.6, 2.4)
dead_trees("lair", 22, scale=(0.8, 1.3))
scatter("lair", BONES, 24, scale=(2.6, 3.8), r=0.8)
scatter("lair", ["Dungeon_SkullPile", "Dungeon_Ribcage"], 6, scale=(3.0, 4.4), r=1.4)
scatter("lair", WEBS, 12, scale=(1.8, 2.8), r=1.0)
mushrooms("lair", 22, big=(2.0, 4.5), glow=1)
snakes("lair", 10, 6)
bats("lair", 8, radius=(3.0, 6.0))
# --- morcegos pelo mapa (papel "bat")
bats("thicket", 8)
bats("bog_w", 6)
bats("hollow_w", 4)
bats("ring_e", 4)
bats("dead_wood", 10)
bats("bat_grove", 22, radius=(3.0, 7.0))
bats("edge", 2)

breakables = []
for rid, n in (("edge", 2), ("thicket", 6), ("bog_w", 4), ("grove_e", 4), ("hollow_w", 3), ("ring_e", 3), ("dead_wood", 5), ("bat_grove", 4), ("lair", 4)):
    cx, cz, w, h = by_id[rid][1:]
    for _ in range(n):
        for _t in range(100):
            x, z = round(cx + rng.uniform(-w / 2 + 4, w / 2 - 4), 1), round(cz + rng.uniform(-h / 2 + 4, h / 2 - 4), 1)
            if not near_interest(x, z, 3.0) and not near_taken(x, z, 1.5):
                breakables.append({"id": "b%d" % (len(breakables) + 1), "monster": "barrel" if len(breakables) % 2 else "crate", "position": [x, z], "table": "breakable_potion"})
                taken.append((x, z, 1.2))
                break
breakables.append({"id": "coin_bag", "monster": "coin_bag", "position": [4.0, 1.5], "table": "coin_bag"})
for i, p in enumerate((rp("thicket", 0, 8), rp("bog_w", 0, -6), rp("grove_e", 0, -6), rp("dead_wood", 6, 6), rp("bat_grove", 0, 8), rp("lair", 0, 14)), start=2):
    breakables.append({"id": "coin_bag_%d" % i, "monster": "coin_bag", "position": p, "table": "coin_bag"})

arenas["dark_forest_01_woods"] = {
    "_comment": "Floresta Escura, ampliada: mata aberta de grama escura cercada de arbustos e bambus (como a Floresta), com árvores secas, cogumelos, morcegos e cobras no cenário. Estrutura da Floresta com outro caminho: "
                "Clareira da Borda (partida) -> Matagal e três rotas até a Mata Seca (oeste: Pântano das Cobras -> Clareira das Serpentes, onde o Totem desperta a Víbora Anciã; leste: Bosque dos Cogumelos -> Círculo de "
                "Esporos, onde o Cogumelo Ancestral desperta o Rei dos Esporos; direta ao norte) -> Bosque dos Morcegos -> corredor do portão (Guardião, duas chaves) -> Covil do Ancião Sombrio (chefe final, com a saída). "
                "Gerado por tools/assets/build_darkforest.py.",
    "name_key": "ARENA_DARK_FOREST", "player_class": "mage", "map_id": "map_dark_forest", "area_level": 8, "outdoor": True, "final": True, "victory_groups": ["fd_boss"], "wake_radius": 10.0, "alert_radius": 5.0,
    "rooms": rooms, "encounters": encounters, "hazards": [], "entries": {"start": [0, 3], "dark_forest": [0, 3]}, "props": props, "quest_spots": [], "breakables": breakables,
    "style": {"_comment": "Floresta Escura: grama escura, cerca viva densa de arbustos e bambus nas divisas, vazio em volta vira grama, tom azulado.", "walls": [""], "floor": "Ground_Grass", "low": "Pl_Bush",
              "fill_grass": True, "hedge_edges": True, "ground": [0.02, 0.035, 0.03], "tint": [0.45, 0.55, 0.6]},
    "decor": decor, "crowd": crowd, "passive": True}


# ---------------------------------------------------------------- NPCs e missões
def body(sex, hair, color):
    return {"sex": sex, "hair": [hair], "hair_color": color, "pose": "idle", "outfit": {"body": "cloth"}}


npcs["fd_woodcutter"] = {"name_key": "NPC_FD_WOODCUTTER", "color": [0.4, 0.3, 0.2], "dialogues": [
    {"when": {"quest_new": "fd_clear"}, "lines": ["DLG_FDWOOD_1", "DLG_FDWOOD_2", "DLG_FDWOOD_3"], "offer": "fd_clear"},
    {"when": {"quest_active": "fd_clear"}, "lines": ["DLG_FDWOOD_ACTIVE"]}, {"when": {}, "lines": ["DLG_FDWOOD_DONE"]}], "body": body("male", "Hair_Beard", [0.3, 0.22, 0.12])}
npcs["fd_herbalist"] = {"name_key": "NPC_FD_HERBALIST", "color": [0.4, 0.55, 0.35], "dialogues": [
    {"when": {"quest_new": "fd_fang"}, "lines": ["DLG_FDHERB_1", "DLG_FDHERB_2", "DLG_FDHERB_3"], "offer": "fd_fang"},
    {"when": {"quest_active": "fd_fang"}, "lines": ["DLG_FDHERB_ACTIVE"], "service": "turn_in"},
    {"when": {"quest_done": "fd_fang"}, "lines": ["DLG_FDHERB_DONE"]}, {"when": {}, "lines": ["DLG_FDHERB_WAIT"]}], "body": body("female", "Hair_Long", [0.35, 0.3, 0.2])}
npcs["fd_totem"] = {"name_key": "NPC_FD_TOTEM", "color": [0.4, 0.5, 0.4], "dialogues": [
    {"when": {"quest_active": "fd_fang"}, "lines": ["DLG_FDTOTEM_1", "DLG_FDTOTEM_2"]}, {"when": {}, "lines": ["DLG_FDTOTEM_LOCKED"]}]}
npcs["fd_charmer"] = {"name_key": "NPC_FD_CHARMER", "color": [0.5, 0.35, 0.5], "dialogues": [
    {"when": {"quest_new": "fd_crown"}, "lines": ["DLG_FDCHARM_1", "DLG_FDCHARM_2", "DLG_FDCHARM_3"], "offer": "fd_crown"},
    {"when": {"quest_active": "fd_crown"}, "lines": ["DLG_FDCHARM_ACTIVE"], "service": "turn_in"},
    {"when": {"quest_done": "fd_crown"}, "lines": ["DLG_FDCHARM_DONE"]}, {"when": {}, "lines": ["DLG_FDCHARM_WAIT"]}], "body": body("male", "Hair_SimpleParted", [0.12, 0.1, 0.12])}
npcs["fd_mushroom"] = {"name_key": "NPC_FD_MUSHROOM", "color": [0.7, 0.45, 1.0], "dialogues": [
    {"when": {"quest_active": "fd_crown"}, "lines": ["DLG_FDMUSH_1", "DLG_FDMUSH_2"]}, {"when": {}, "lines": ["DLG_FDMUSH_LOCKED"]}]}
npcs["fd_warden"] = {"name_key": "NPC_FD_WARDEN", "color": [0.35, 0.4, 0.4], "dialogues": [
    {"when": {"quest_new": "fd_gate"}, "lines": ["DLG_FDWARD_1", "DLG_FDWARD_2", "DLG_FDWARD_3"], "offer": "fd_gate"},
    {"when": {"quest_active": "fd_gate"}, "lines": ["DLG_FDWARD_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_FDWARD_DONE"]}], "body": body("male", "Hair_Beard", [0.45, 0.45, 0.4])}
quests["fd_clear"] = {"name_key": "QUEST_FD_CLEAR", "desc_key": "QUEST_FD_CLEAR_DESC", "type": "village", "giver": "fd_woodcutter", "area": "dark_forest_01_woods", "clear": ["fd_thicket_a", "fd_thicket_b"],
                      "target_element": "earth", "reward": {"gold": 600, "xp": 1200}}
quests["fd_fang"] = {"name_key": "QUEST_FD_FANG", "desc_key": "QUEST_FD_FANG_DESC", "type": "village", "giver": "fd_herbalist", "area": "dark_forest_01_woods", "target_element": "earth",
                     "reward": {"gold": 650, "xp": 1300}, "item": "viper_fang", "gives": "key_moss"}
quests["fd_crown"] = {"name_key": "QUEST_FD_CROWN", "desc_key": "QUEST_FD_CROWN_DESC", "type": "village", "giver": "fd_charmer", "area": "dark_forest_01_woods", "target_element": "water",
                      "reward": {"gold": 650, "xp": 1300}, "item": "spore_crown", "gives": "key_thorn"}
quests["fd_gate"] = {"name_key": "QUEST_FD_GATE", "desc_key": "QUEST_FD_GATE_DESC", "type": "village", "giver": "fd_warden", "area": "dark_forest_01_woods",
                     "items": ["key_moss", "key_thorn"], "opens_gate": "boss_gate", "target_element": "earth", "reward": {"gold": 750, "xp": 1500}}
T = {
    "MONSTER_FD_VIPER": ("Víbora Anciã", "Ancient Viper", "Víbora Ancestral"),
    "MONSTER_FD_SPORE_KING": ("Rei dos Esporos", "Spore King", "Rey de las Esporas"),
    "MONSTER_FD_ELDER": ("Ancião Sombrio", "Shadow Elder", "Anciano Sombrío"),
    "NPC_FD_WOODCUTTER": ("Lenhador Ardo", "Woodcutter Ardo", "Leñador Ardo"),
    "NPC_FD_HERBALIST": ("Herbalista Mirta", "Herbalist Mirta", "Herbolaria Mirta"),
    "NPC_FD_TOTEM": ("Totem das Serpentes", "Serpent Totem", "Tótem de las Serpientes"),
    "NPC_FD_CHARMER": ("Encantador Zhar", "Charmer Zhar", "Encantador Zhar"),
    "NPC_FD_MUSHROOM": ("Cogumelo Ancestral", "Ancestral Mushroom", "Hongo Ancestral"),
    "NPC_FD_WARDEN": ("Guardião da Mata", "Forest Warden", "Guardián del Bosque"),
    "VALUABLE_VIPER_FANG": ("Presa da Víbora Anciã", "Ancient Viper's Fang", "Colmillo de la Víbora Ancestral"),
    "VALUABLE_SPORE_CROWN": ("Coroa de Esporos", "Spore Crown", "Corona de Esporas"),
    "VALUABLE_KEY_MOSS": ("Chave de Musgo", "Moss Key", "Llave de Musgo"),
    "VALUABLE_KEY_THORN": ("Chave de Espinho", "Thorn Key", "Llave de Espina"),
    "TOAST_TOTEM_AWAKENS": ("As pedras sibilam: a Víbora Anciã desce do totem!", "The stones hiss: the Ancient Viper slides down from the totem!", "Las piedras silban: ¡la Víbora Ancestral baja del tótem!"),
    "TOAST_SPORE_AWAKENS": ("Uma nuvem de esporos sobe: o Rei dos Esporos acorda!", "A cloud of spores rises: the Spore King awakens!", "Sube una nube de esporas: ¡el Rey de las Esporas despierta!"),
    "QUEST_FD_CLEAR": ("Limpar o Matagal", "Clear the Thicket", "Limpiar la maleza"),
    "QUEST_FD_CLEAR_DESC": ("O Lenhador Ardo, na Clareira da Borda, pede que os dois primeiros bandos que ocupam o Matagal logo ao norte sejam derrubados, para ele voltar a cortar lenha em paz.",
                            "Woodcutter Ardo, in the Edge Glade, asks that the first two packs holding the Thicket just to the north be brought down, so he can chop wood in peace again.",
                            "El Leñador Ardo, en el Claro del Borde, pide que se derriben las dos primeras bandas que ocupan la Maleza justo al norte, para volver a cortar leña en paz."),
    "QUEST_FD_FANG": ("A Presa da Víbora Anciã", "The Ancient Viper's Fang", "El colmillo de la Víbora Ancestral"),
    "QUEST_FD_FANG_DESC": ("A Herbalista Mirta, no Bosque dos Cogumelos (leste), precisa da presa da Víbora Anciã para preparar o antídoto. Toque o Totem das Serpentes da Clareira (oeste, depois do Pântano das Cobras) com a missão ativa, derrote a Víbora e traga a presa: em troca vem a Chave de Musgo, uma das duas do portão do Ancião Sombrio.",
                           "Herbalist Mirta, in the Mushroom Grove (east), needs the Ancient Viper's fang to brew the antidote. Touch the Serpent Totem in the Glade (west, past the Snake Bog) with the quest active, defeat the Viper and bring the fang: in return you get the Moss Key, one of the two for the Shadow Elder's gate.",
                           "La Herbolaria Mirta, en el Bosque de los Hongos (este), necesita el colmillo de la Víbora Ancestral para preparar el antídoto. Toca el Tótem de las Serpientes del Claro (oeste, tras el Pantano de las Serpientes) con la misión activa, derrota a la Víbora y trae el colmillo: a cambio recibes la Llave de Musgo, una de las dos del portón del Anciano Sombrío."),
    "QUEST_FD_CROWN": ("A Coroa de Esporos", "The Spore Crown", "La corona de esporas"),
    "QUEST_FD_CROWN_DESC": ("O Encantador Zhar, no Pântano das Cobras (oeste), quer a coroa de esporos do Rei dos Esporos para acalmar as cobras. A fala do Cogumelo Ancestral do Círculo de Esporos (leste) desperta o Rei; derrote-o e traga a coroa para receber a Chave de Espinho, a outra do portão do Ancião Sombrio.",
                            "Charmer Zhar, in the Snake Bog (west), wants the Spore King's spore crown to calm the snakes. Touching the Ancestral Mushroom in the Spore Circle (east) wakes the King; defeat him and bring the crown to receive the Thorn Key, the other one for the Shadow Elder's gate.",
                            "El Encantador Zhar, en el Pantano de las Serpientes (oeste), quiere la corona de esporas del Rey de las Esporas para calmar a las serpientes. Tocar el Hongo Ancestral del Círculo de Esporas (este) despierta al Rey; derrótalo y trae la corona para recibir la Llave de Espina, la otra del portón del Anciano Sombrío."),
    "QUEST_FD_GATE": ("O Portão do Ancião", "The Elder's Gate", "El portón del Anciano"),
    "QUEST_FD_GATE_DESC": ("O Guardião da Mata, no corredor ao norte do Bosque dos Morcegos, só abre o portão para quem trouxer as duas chaves: a de Musgo (Herbalista) e a de Espinho (Encantador). Atrás dele fica o Covil do Ancião Sombrio.",
                           "The Forest Warden, in the lane north of the Bat Grove, only opens the gate for those with both keys: the Moss (Herbalist) and the Thorn (Charmer). Beyond lies the Shadow Elder's Lair.",
                           "El Guardián del Bosque, en el pasillo al norte del Bosque de los Murciélagos, solo abre el portón a quien traiga las dos llaves: la de Musgo (Herbolaria) y la de Espina (Encantador). Tras él está la Guarida del Anciano Sombrío."),
    "DLG_FDWOOD_1": ("Cuidado onde pisam: nesta mata nem as árvores estão vivas, e o que se mexe entre elas é pior. Corto lenha aqui na borda, onde ainda dá para respirar.",
                     "Mind your step: in this wood not even the trees are alive, and what moves between them is worse. I chop wood here at the edge, where one can still breathe.",
                     "Cuidado dónde pisan: en este bosque ni los árboles están vivos, y lo que se mueve entre ellos es peor. Corto leña aquí en el borde, donde aún se puede respirar."),
    "DLG_FDWOOD_2": ("Os dois primeiros bandos, aqui no Matagal, ao norte, me cercaram a clareira. Sem eles longe, eu não consigo nem buscar lenha.",
                     "The first two packs, here in the Thicket to the north, have hemmed in my glade. Without them gone I cannot even fetch firewood.",
                     "Las dos primeras bandas, aquí en la Maleza al norte, me cercaron el claro. Sin ellas lejos, ni siquiera puedo buscar leña."),
    "DLG_FDWOOD_3": ("Derrubem os dois e eu pago. Depois falem com a Herbalista Mirta, no bosque de cogumelos a leste, e com o Encantador Zhar, no pântano a oeste: eles guardam as chaves do portão do Ancião.",
                     "Bring both down and I will pay. Then talk to Herbalist Mirta, in the mushroom grove to the east, and to Charmer Zhar, in the bog to the west: they keep the keys to the Elder's gate.",
                     "Derriben las dos y pago. Luego hablen con la Herbolaria Mirta, en el bosque de hongos al este, y con el Encantador Zhar, en el pantano al oeste: ellos guardan las llaves del portón del Anciano."),
    "DLG_FDWOOD_ACTIVE": ("O Matagal fica logo ao norte da clareira. Ouçam as asas: onde há morcegos, há bando.", "The Thicket lies just north of the glade. Listen for wings: where there are bats, there is a pack.", "La Maleza queda justo al norte del claro. Escuchen las alas: donde hay murciélagos, hay banda."),
    "DLG_FDWOOD_DONE": ("Que silêncio bom! Agora escolham: oeste pelas cobras, leste pelos cogumelos ou direto ao norte, pela mata seca. Todos os caminhos chegam lá.", "What a good silence! Now choose: west through the snakes, east through the mushrooms or straight north through the dry wood. All paths lead there.", "¡Qué buen silencio! Ahora elijan: oeste por las serpientes, este por los hongos o directo al norte, por el bosque seco. Todos los caminos llegan allí."),
    "DLG_FDHERB_1": ("Colho cogumelos e ervas há trinta anos, e conheço cada um pelo cheiro. Hoje só preciso de uma coisa: a presa da Víbora Anciã, para o antídoto do veneno desta floresta.",
                     "I have gathered mushrooms and herbs for thirty years and know each by its smell. Today I need only one thing: the Ancient Viper's fang, for the antidote to this forest's poison.",
                     "Recojo hongos y hierbas desde hace treinta años y conozco cada uno por el olor. Hoy solo necesito una cosa: el colmillo de la Víbora Ancestral, para el antídoto del veneno de este bosque."),
    "DLG_FDHERB_2": ("Ela vive na Clareira das Serpentes, a oeste, depois do pântano, enrolada num totem de pedra. Só acorda se alguém toca o totem com a intenção de caçá-la.",
                     "She lives in the Serpent Glade, to the west, past the bog, coiled around a stone totem. She only wakes if someone touches the totem intending to hunt her.",
                     "Vive en el Claro de las Serpientes, al oeste, tras el pantano, enroscada en un tótem de piedra. Solo despierta si alguien toca el tótem con la intención de cazarla."),
    "DLG_FDHERB_3": ("Toquem o totem, derrubem a Víbora e tragam a presa. Eu dou a Chave de Musgo, uma das duas que abrem o portão do Ancião Sombrio, no corredor ao norte do bosque dos morcegos.",
                     "Touch the totem, bring down the Viper and bring me the fang. I give the Moss Key, one of the two that open the Shadow Elder's gate, in the lane north of the bat grove.",
                     "Toquen el tótem, derriben a la Víbora y tráiganme el colmillo. Doy la Llave de Musgo, una de las dos que abren el portón del Anciano Sombrío, en el pasillo al norte del bosque de los murciélagos."),
    "DLG_FDHERB_ACTIVE": ("A Clareira fica a oeste do Matagal, depois do Pântano das Cobras. A presa é verde, curva e do tamanho de uma foice. Tragam-na.", "The Glade is west of the Thicket, past the Snake Bog. The fang is green, curved and the size of a sickle. Bring it.", "El Claro está al oeste de la Maleza, tras el Pantano de las Serpientes. El colmillo es verde, curvo y del tamaño de una hoz. Tráiganlo."),
    "DLG_FDHERB_DONE": ("A presa! Agora o antídoto sai. A Chave de Musgo é de vocês: levem-na ao Guardião, junto com a de Espinho.", "The fang! Now the antidote can be brewed. The Moss Key is yours: take it to the Warden, together with the Thorn one.", "¡El colmillo! Ahora sale el antídoto. La Llave de Musgo es suya: llévenla al Guardián, junto con la de Espina."),
    "DLG_FDHERB_WAIT": ("Os cogumelos brilham mais quando alguém é gentil com eles. Voltem a qualquer hora.", "The mushrooms glow brighter when someone is kind to them. Come back anytime.", "Los hongos brillan más cuando alguien es amable con ellos. Vuelvan cuando quieran."),
    "DLG_FDTOTEM_1": ("As pedras em círculo sibilam baixinho, e algo escorrega entre elas, devagar, deixando um rastro de escamas.", "The ring of stones hisses softly, and something slides between them, slowly, leaving a trail of scales.", "Las piedras en círculo silban bajito, y algo se desliza entre ellas, despacio, dejando un rastro de escamas."),
    "DLG_FDTOTEM_2": ("A Víbora Anciã desce do totem!", "The Ancient Viper slides down from the totem!", "¡La Víbora Ancestral baja del tótem!"),
    "DLG_FDTOTEM_LOCKED": ("Um totem de pedra coberto de musgo. Nada responde ao seu toque.", "A moss-covered stone totem. Nothing answers your touch.", "Un tótem de piedra cubierto de musgo. Nada responde a tu toque."),
    "DLG_FDCHARM_1": ("Shhh, não gritem: elas ouvem tudo. Eu encanto as cobras deste pântano com uma flauta, mas ultimamente elas nem me escutam, agitadas por algo no leste.",
                      "Shh, do not shout: they hear everything. I charm this bog's snakes with a flute, but lately they do not even listen, stirred up by something in the east.",
                      "Shh, no griten: lo oyen todo. Encanto a las serpientes de este pantano con una flauta, pero últimamente ni me escuchan, agitadas por algo en el este."),
    "DLG_FDCHARM_2": ("É o Rei dos Esporos, no Círculo de Esporos: a coroa dele solta um pó que enlouquece qualquer bicho de sangue frio. Sem a coroa, as cobras se acalmam.",
                      "It is the Spore King, in the Spore Circle: his crown sheds a dust that maddens any cold-blooded creature. Without the crown, the snakes calm down.",
                      "Es el Rey de las Esporas, en el Círculo de Esporas: su corona suelta un polvo que enloquece a cualquier bicho de sangre fría. Sin la corona, las serpientes se calman."),
    "DLG_FDCHARM_3": ("Falem com o Cogumelo Ancestral, no círculo, e o Rei acorda. Derrubem-no e tragam a coroa: eu dou a Chave de Espinho, a outra do portão do Ancião.",
                      "Speak to the Ancestral Mushroom in the circle and the King wakes. Bring him down and bring the crown: I give the Thorn Key, the other for the Elder's gate.",
                      "Hablen con el Hongo Ancestral en el círculo y el Rey despierta. Derríbenlo y traigan la corona: doy la Llave de Espina, la otra del portón del Anciano."),
    "DLG_FDCHARM_ACTIVE": ("O Círculo de Esporos fica a leste, depois do Bosque dos Cogumelos. A coroa é roxa e solta fumaça. Não respirem perto dela.", "The Spore Circle is east, past the Mushroom Grove. The crown is purple and gives off smoke. Do not breathe near it.", "El Círculo de Esporas está al este, tras el Bosque de los Hongos. La corona es morada y suelta humo. No respiren cerca de ella."),
    "DLG_FDCHARM_DONE": ("A coroa! As cobras já estão voltando a me ouvir. A Chave de Espinho é de vocês: levem-na ao Guardião, junto com a de Musgo.", "The crown! The snakes are listening to me again. The Thorn Key is yours: take it to the Warden, together with the Moss one.", "¡La corona! Las serpientes vuelven a escucharme. La Llave de Espina es suya: llévenla al Guardián, junto con la de Musgo."),
    "DLG_FDCHARM_WAIT": ("A flauta toca sozinha quando estou calmo. Voltem quando quiserem ouvi-la.", "The flute plays itself when I am calm. Come back when you wish to hear it.", "La flauta suena sola cuando estoy calmo. Vuelvan cuando quieran oírla."),
    "DLG_FDMUSH_1": ("O cogumelo gigante pulsa em roxo, soltando esporos que brilham no ar, e um chapéu enorme se inclina sobre você como se escutasse.", "The giant mushroom pulses purple, releasing spores that glow in the air, and a huge cap leans over you as if listening.", "El hongo gigante late en púrpura, soltando esporas que brillan en el aire, y un sombrero enorme se inclina sobre ti como si escuchara."),
    "DLG_FDMUSH_2": ("O Rei dos Esporos acorda!", "The Spore King awakens!", "¡El Rey de las Esporas despierta!"),
    "DLG_FDMUSH_LOCKED": ("Um cogumelo enorme, imóvel, rodeado de um anel de companheiros. Nada responde ao seu toque.", "A huge mushroom, motionless, ringed by companions. Nothing answers your touch.", "Un hongo enorme, inmóvil, rodeado de un anillo de compañeros. Nada responde a tu toque."),
    "DLG_FDWARD_1": ("Alto. Este portão fecha o Covil, e no Covil mora o Ancião Sombrio, a árvore que já era velha antes desta floresta escurecer. Eu cuido do portão desde que ele ainda tinha folhas.", "Halt. This gate closes the Lair, and in the Lair lives the Shadow Elder, a tree already old before this forest darkened. I have tended the gate since it still had leaves.", "Alto. Este portón cierra la Guarida, y en la Guarida vive el Anciano Sombrío, el árbol que ya era viejo antes de que este bosque oscureciera. Cuido el portón desde que aún tenía hojas."),
    "DLG_FDWARD_2": ("O portão só abre com DUAS chaves: a de Musgo e a de Espinho. A primeira está com a Herbalista Mirta, no bosque de cogumelos a leste; a segunda, com o Encantador Zhar, no pântano a oeste.", "The gate only opens with TWO keys: the Moss and the Thorn. The first is with Herbalist Mirta, in the mushroom grove to the east; the second, with Charmer Zhar, in the bog to the west.", "El portón solo abre con DOS llaves: la de Musgo y la de Espina. La primera la tiene la Herbolaria Mirta, en el bosque de hongos al este; la segunda, el Encantador Zhar, en el pantano al oeste."),
    "DLG_FDWARD_3": ("Cada um cobra um preço: uma presa, uma coroa. Tragam as duas chaves a mim e eu abro a passagem.", "Each charges a price: a fang, a crown. Bring both keys to me and I will open the way.", "Cada uno cobra un precio: un colmillo, una corona. Tráiganme las dos llaves y abro el paso."),
    "DLG_FDWARD_ACTIVE": ("Só abro com as duas chaves, Musgo e Espinho, na mesma bolsa. A Herbalista fica a leste; o Encantador, a oeste.", "I only open with both keys, Moss and Thorn, in the same bag. The Herbalist is to the east; the Charmer, to the west.", "Solo abro con las dos llaves, Musgo y Espina, en la misma bolsa. La Herbolaria está al este; el Encantador, al oeste."),
    "DLG_FDWARD_DONE": ("As duas chaves! O portão está aberto. Cuidado: o Ancião Sombrio não corre, não precisa; todas as raízes desta floresta respondem a ele.", "Both keys! The gate is open. Beware: the Shadow Elder does not run, he does not need to; every root in this forest answers to him.", "¡Las dos llaves! El portón está abierto. Cuidado: el Anciano Sombrío no corre, no lo necesita; todas las raíces de este bosque le responden."),
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
    for dst, src, mul in (("key_moss", "key_clubs", (0.6, 1.2, 0.6)), ("key_thorn", "key_spades", (0.9, 0.7, 1.3)), ("viper_fang", "lamassu_horn", (0.7, 1.2, 0.7)), ("spore_crown", "crown_jewel", (1.1, 0.6, 1.4))):
        im = Image.open(ICONS + src + ".png").convert("RGBA")
        r_, g_, b_, a_ = im.split()
        Image.merge("RGBA", (r_.point(lambda v: min(255, int(v * mul[0]))), g_.point(lambda v: min(255, int(v * mul[1]))), b_.point(lambda v: min(255, int(v * mul[2]))), a_)).save(ICONS + dst + ".png")
except Exception as exc:
    print("aviso: ícones não gerados:", exc)

for path, data in ((ARENAS, arenas), (MONSTERS, monsters), (NPCS, npcs), (QUESTS, quests), (VALUABLES, valuables)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
print("OK darkforest: %d salas, %d m2, %d peças, %d morcegos, %d encontros, %d luzes" % (len(rooms), AREA_M2, len(decor), sum(1 for c in crowd if c["role"] == "bat"), len(encounters), lights))
