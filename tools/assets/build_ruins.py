"""Mapa das Ruínas (ruins_01_city), ampliado: mesma estrutura da Floresta (partida, duas praças de mini-chefe, guardião do portão e chefe final) com outro caminho,
misturando partes COM MUROS e partes ABERTAS.
  Murados: os dois Bairros (o labirinto de ruas Ruins_Layout, Destroyed Walls, LFA, CC BY 3.0, um deles virado 180 graus), a Cidadela (muralha de Ruin_Wall com um
  caminho em S entre dois muros internos), o corredor do portão e o Cofre Real (salão murado).
  Abertos: o Acesso, o Fórum, as duas Praças, a Avenida das Colunas e o Pátio Alto.
Caminho: Acesso -> Fórum; a oeste o Bairro Velho e, ao norte dele, a Praça dos Cavaleiros (a Erudita pede o Coração de Pedra: tocar a estátua do cavaleiro, com a missão
ativa, desperta o Guardião das Ruínas); a leste o Bairro do Mercado e, ao norte, a Praça dos Monólitos (a Sacerdotisa pede o Estandarte do Campeão e desperta o Campeão Caído);
no meio a Avenida das Colunas. Os três caminhos fecham no Pátio Alto -> Cidadela -> corredor do portão (o Porteiro só abre com as duas chaves) -> Cofre Real (Rei Caído,
chefe final, com a saída). Mantém o Leônidas (missão dos goblins) e o Alfa da Matilha (relíquia do Bobo da Corte).
Sorteio com semente fixa; idempotente; chamado no fim de tools/assets/build_maps.py (depois de build_docks.py e antes de set_map_order.py).
uso: python3 tools/assets/build_ruins.py   (a partir da raiz do projeto)"""
import json, math, random, re
ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES = ("data/arenas.json", "data/monsters.json", "data/npcs.json", "data/quests.json", "data/valuables.json")
arenas, monsters, npcs, quests, valuables = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES))
colliders = json.load(open("data/ruins_colliders.json"))["colliders"]
rng = random.Random("ruins-v2")
DOOR = 6.0

ROOMS = [("approach", 0, 0, 56, 12), ("forum", 0, -32, 60, 52), ("bairro_w", -58, -33, 56, 50), ("bairro_e", 58, -33, 56, 50),
         ("plaza_w", -58, -77.5, 56, 39), ("plaza_e", 58, -77.5, 56, 39), ("avenue", 0, -77.5, 16, 39), ("yard", 0, -109, 110, 24),
         ("citadel", 0, -137, 56, 32), ("gate_lane", 0, -165, 10, 24), ("vault", 0, -201, 60, 48)]
LINKS = [("approach", "forum", "north"), ("forum", "bairro_w", "west"), ("forum", "bairro_e", "east"), ("bairro_w", "plaza_w", "north"), ("bairro_e", "plaza_e", "north"),
         ("forum", "avenue", "north"), ("plaza_w", "yard", "north"), ("plaza_e", "yard", "north"), ("avenue", "yard", "north"), ("yard", "citadel", "north"),
         ("citadel", "gate_lane", "north"), ("gate_lane", "vault", "north")]
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
    if rid in ("approach", "forum", "yard", "citadel", "vault"):
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


# ---------------------------------------------------------------- os dois bairros (labirinto de ruas) e suas colisões
DISTRICTS = [("bairro_w", -58, -33, 0), ("bairro_e", 58, -33, 180)]
solids = []                                  # retângulos (cx, cz, w, h) que bloqueiam: paredes dos bairros, muros, colunas, estátuas...
decor = []
for rid, cx, cz, rot in DISTRICTS:
    decor.append({"piece": "Ruins_Layout", "position": [cx, cz], "rotation": rot})
    sign = -1 if rot == 180 else 1
    for c in colliders:
        px, pz = round(cx + sign * c["position"][0], 2), round(cz + sign * c["position"][1], 2)
        decor.append({"collider": c["size"], "position": [px, pz]})
        solids.append((px, pz, c["size"][0], c["size"][1]))


def in_solid(x, z, pad=0.0):
    return any(abs(x - sx) < sw / 2 + pad and abs(z - sz) < sh / 2 + pad for sx, sz, sw, sh in solids)


def add_solid(x, z, w, h):
    solids.append((x, z, w, h))


# ---------------------------------------------------------------- monstros novos (mini-chefes e chefe final) e itens
def clone(name, base, **changes):
    m = json.loads(json.dumps(monsters[base]))
    m.pop("_comment", None)
    m.pop("quest_drop", None)
    m.update(changes)
    monsters[name] = m


monsters["ruin_warden"].update({"_comment": "Mini-chefe das Ruínas (Praça dos Cavaleiros): o Guardião das Ruínas, golem de pedra que acorda quando o cavaleiro de pedra é tocado com a missão do Coração de Pedra; investidas rápidas.",
                                "look": "golem_stone", "color": [0.78, 0.78, 0.85], "size": 2.8, "element": "earth", "max_health": 300, "quest_drop": "stone_heart"})
clone("war_champion", "ruin_warden", _comment="Mini-chefe das Ruínas (Praça dos Monólitos): o Campeão Caído, guerreiro da guerra que a Sacerdotisa desperta; investidas rápidas.",
      name_key="MONSTER_WAR_CHAMPION", max_health=280, damage=24, size=2.4, element="fire", look="champ_warrior", color=[1.0, 1.0, 1.0], quest_drop="champion_banner")
clone("fallen_king", "sphinx", _comment="Chefe final das Ruínas: o Rei Caído, guardião do Cofre Real atrás do portão; investidas e pisões (modelo do rei golem).",
      name_key="MONSTER_FALLEN_KING", max_health=1000, damage=38, size=4.2, element="earth", look="golem_king", color=[0.85, 0.75, 1.0], chest_loot="chest")
valuables.update({
    "stone_heart": {"name_key": "VALUABLE_STONE_HEART", "value": 0, "maps": [], "quest_item": True, "model": "Crystal_Gem"},
    "champion_banner": {"name_key": "VALUABLE_CHAMPION_BANNER", "value": 0, "maps": [], "quest_item": True, "model": "Shield_B"},
    "key_lion": {"name_key": "VALUABLE_KEY_LION", "value": 0, "maps": [], "quest_item": True, "model": "Key_Spades"},
    "key_eagle": {"name_key": "VALUABLE_KEY_EAGLE", "value": 0, "maps": [], "quest_item": True, "model": "Key_Clubs"}})

# ---------------------------------------------------------------- objetos do mapa
SUMMON_STATUE = {"id": "r_statue", "position": [-58.0, -70.0], "spread": 3.0, "toast": "TOAST_STATUE_AWAKENS", "monsters": [{"monster": "ruin_warden", "count": 1, "rank": "miniboss"}]}
SUMMON_CHAMPION = {"id": "r_champion", "position": [62.0, -72.0], "spread": 3.0, "toast": "TOAST_CHAMPION_AWAKENS", "monsters": [{"monster": "war_champion", "count": 1, "rank": "miniboss"}]}


def free_spot(rid, rad=2.5, margin=3.0, avoid=()):
    """Um ponto livre (fora das paredes dos bairros e longe de portas e do que já foi posto) dentro da sala."""
    cx, cz, w, h = by_id[rid][1:]
    for _ in range(400):
        x, z = round(cx + rng.uniform(-w / 2 + margin, w / 2 - margin), 1), round(cz + rng.uniform(-h / 2 + margin, h / 2 - margin), 1)
        if in_solid(x, z, rad) or any(math.hypot(x - px, z - pz) < rad + 2.0 for px, pz in fixed + list(avoid)):
            continue
        if any(math.hypot(x - dx, z - dz) < 6.0 for dx, dz in door_points):
            continue
        return [x, z]
    raise RuntimeError("sem ponto livre em " + rid)


fixed = [(0, 3), (-6, 3), (5, 0), (10, -20), (-58, -77.5), (52, -76), (SUMMON_STATUE["position"][0], SUMMON_STATUE["position"][1]), tuple(SUMMON_CHAMPION["position"]),
         (0, -155), (0, -159), (0, -219.5), (0, -206)]
props = [
    {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "ruins", "expedition_end": True},
    {"id": "victory_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [0, -219.5], "to": "tortuga", "entry": "ruins", "after_victory": True, "group": True},
    {"id": "ruins_spartan", "kind": "npc", "npc": "ruins_spartan", "position": [5, 0]},
    {"id": "ruins_scholar", "kind": "npc", "npc": "ruins_scholar", "position": [10, -20], "rotation": 200},
    {"id": "ruins_knight_statue", "kind": "npc", "npc": "ruins_knight_statue", "kit": "Statue_Knight", "rotation": 0, "position": [-58.0, -77.5], "solid": [1.4, 1.4],
     "summon": SUMMON_STATUE, "needs_quest": "ruins_seal"},
    {"id": "ruins_priestess", "kind": "npc", "npc": "ruins_priestess", "position": [52.0, -76.0], "rotation": 0, "summon": SUMMON_CHAMPION, "needs_quest": "ruins_banner"},
    {"id": "boss_gate", "kind": "gate", "name_key": "PROP_BOSS_GATE", "position": [0.0, -159.0], "rotation": 0, "scale": 3.0, "block": 10.0, "count": 2, "opened_by": "ruins_gate"},
    {"id": "ruins_gatekeeper", "kind": "npc", "npc": "ruins_gatekeeper", "position": [0.0, -155.0], "rotation": 0}]
chest_spots = [free_spot("bairro_w"), free_spot("bairro_e"), free_spot("plaza_w", avoid=[(-58, -77.5)]), free_spot("plaza_e", avoid=[(58, -80)]), free_spot("yard"), free_spot("forum"),
               [-20, -142], [20, -131], [-22, -214], [22, -214]]
for i, p in enumerate(chest_spots, start=1):
    props.append({"id": "ruins_chest_%d" % i, "kind": "chest", "position": p, "loot": "chest"})
E = lambda eid, pos, *mons: {"id": eid, "position": pos, "monsters": [{"monster": m, "count": c} for m, c in mons]}
encounters = [
    E("r_goblins_a", free_spot("bairro_w"), ("goblin", 4)), E("r_lizards_a", free_spot("bairro_w"), ("goblin", 3)), E("r_scorp_w", free_spot("bairro_w"), ("venom_scorpion", 3)),
    E("r_goblins_b", free_spot("bairro_e"), ("goblin", 5)), E("r_lizards_b", free_spot("bairro_e"), ("goblin", 3)), E("r_scorp_e", free_spot("bairro_e"), ("venom_scorpion", 3)),
    E("r_forum_a", [-16, -22], ("goblin", 3)), E("r_forum_b", [18, -40], ("venom_scorpion", 3)), E("r_forum_c", [-14, -46], ("plague_bat", 4)),
    E("r_bats", free_spot("bairro_e"), ("plague_bat", 4)), E("r_bats_w", free_spot("bairro_w"), ("plague_bat", 4)),
    E("r_plaza_w_a", [-76, -88], ("goblin", 3)), E("r_plaza_w_b", [-42, -66], ("venom_scorpion", 2)),
    E("r_plaza_e_a", [76, -88], ("goblin", 3)), E("r_plaza_e_b", [42, -90], ("venom_scorpion", 2)),
    E("r_avenue_a", [0, -68], ("plague_bat", 3)), E("r_avenue_b", [0, -88], ("goblin", 3)),
    E("r_yard_a", [-30, -109], ("goblin", 4)), E("r_yard_b", [30, -109], ("venom_scorpion", 3)), E("r_yard_c", [-12, -104], ("plague_bat", 3)),
    E("r_alpha", [18, -112], ("ruin_alpha", 1)),
    E("r_cit_a", [-14, -126], ("goblin", 4)), E("r_cit_b", [14, -137], ("venom_scorpion", 3)), E("r_cit_c", [-14, -147], ("plague_bat", 4)),
    E("r_vault_a", [-20, -190], ("goblin", 3)), E("r_vault_b", [20, -190], ("goblin", 3)),
    E("r_mimic_w", free_spot("bairro_w"), ("chest_mimic", 1)), E("r_mimic_e", free_spot("bairro_e"), ("chest_mimic", 1)), E("r_mimic_yard", [-44, -114], ("chest_mimic", 1)),
    E("r_mimic_vault", [-26, -218], ("chest_mimic", 1)),
    E("r_boss", [0, -208], ("fallen_king", 1))]
interest = [p["position"] for p in props] + [e["position"] for e in encounters] + [SUMMON_STATUE["position"], SUMMON_CHAMPION["position"], [0, 3]] + [list(d) for d in door_points]


def near_interest(x, z, rad=3.5):
    return any(math.hypot(x - ix, z - iz) < rad for ix, iz in interest)


# ---------------------------------------------------------------- decoração
taken = []


def near_taken(x, z, rad=0.0):
    return any(math.hypot(x - tx, z - tz) < tr + rad for tx, tz, tr in taken)


def parts_colliders(piece, x, z, rot):
    """Os recortes de colisão da peça (tools/assets/ruin_parts), só para rotação 0 ou 180."""
    out = []
    try:
        parts = json.load(open("tools/assets/ruin_parts/%s.json" % piece))
    except OSError:
        return out
    sgn = -1 if rot == 180 else 1
    for p in parts:
        w, h = p["size"]
        if w < 0.2 and h < 0.2:
            continue
        out.append((round(x + sgn * p["center"][0], 2), round(z + sgn * p["center"][1], 2), max(w, 0.3), max(h, 0.3)))
    return out


def put(piece, x, z, rot=None, scale=1.0, solid=None, y=0.0, r=0.8, free=2.0, force=False, parts=False):
    if room_at(x, z, -0.9) is None:
        return False
    if not force and (near_interest(x, z, free) or near_taken(x, z, r) or in_solid(x, z, r * 0.6)):
        return False
    d = {"piece": piece, "position": [round(x, 1), round(z, 1)], "rotation": int(rot if rot is not None else rng.randrange(0, 360, 15))}
    if y:
        d["y"] = y
    if scale != 1.0:
        d["scale"] = round(scale, 2)
    if solid:
        d["solid"] = [round(solid[0], 1), round(solid[1], 1)]
        add_solid(x, z, solid[0], solid[1])
    decor.append(d)
    taken.append((x, z, r))
    if parts:
        for px, pz, pw, ph in parts_colliders(piece, x, z, d["rotation"]):
            decor.append({"collider": [round(pw, 2), round(ph, 2)], "position": [px, pz]})
            add_solid(px, pz, pw, ph)
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


def brazier(x, z, scale=1.8):
    if put("Tv_Fire", x, z, rot=0, scale=scale, solid=[0.9 * scale, 0.7 * scale], r=1.3, free=1.2):
        decor.append({"piece": "Fire_Flame", "position": [round(x, 1), round(z, 1)], "y": 0.2, "scale": round(scale * 0.9, 2), "flicker": True})
        light(x, z, 1.6, 11.0, 1.2)


def column(x, z, kind="Ruin_Column", force=False):
    return put(kind, x, z, solid=[0.8, 0.8], r=1.0, free=1.2, force=force)


def arch(x, z, rot=0, force=True):
    """Arco de 7,2 m com os dois pés bloqueando (o vão do meio fica livre)."""
    if not force and (near_taken(x, z, 3.0)):
        return False
    decor.append({"piece": "Ruin_Arch", "position": [x, z], "rotation": rot})
    taken.append((x, z, 3.0))
    feet = ((-3.07, 0.34), (3.07, 0.34)) if rot == 0 else ((0.34, -3.07), (0.34, 3.07))
    for dx, dz in feet:
        decor.append({"collider": [1.1, 1.1], "position": [round(x + dx, 2), round(z + dz, 2)]})
        add_solid(x + dx, z + dz, 1.1, 1.1)
    return True


def wall(x0, z0, x1, z1, gaps=(), capped=True, skip=0.0):
    """Muro de Ruin_Wall (peças de 6 m) de (x0,z0) a (x1,z1), reto e alinhado a um eixo; gaps = intervalos [a, b] ao longo do eixo sem muro; skip = chance de um trecho caído."""
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
        n = max(1, math.ceil((s1 - s0) / 6.0 - 0.15))
        step = (s1 - s0) / n
        for i in range(n):
            t = s0 + step * (i + 0.5)
            if skip and rng.random() < skip and 0 < i < n - 1:
                continue
            x, z = (t, z0) if horiz else (x0, t)
            sc = min(step / 6.0, 1.08)
            decor.append({"piece": "Ruin_Wall", "position": [round(x, 2), round(z, 2)], "rotation": 0 if horiz else 90, "scale": round(sc, 2)})
            sw = (step - 0.2, 0.7) if horiz else (0.7, step - 0.2)
            add_solid(x, z, sw[0], sw[1])
            decor.append({"collider": [round(sw[0], 2), round(sw[1], 2)], "position": [round(x, 2), round(z, 2)]})
            taken.append((x, z, 1.6))
        if capped:
            for end in (s0, s1):
                x, z = (end, z0) if horiz else (x0, end)
                if not any(abs((x if horiz else z) - g) < 0.01 for ga, gb in gaps for g in (ga, gb)):
                    continue
                decor.append({"piece": "Ruin_Pillar", "position": [round(x, 2), round(z, 2)], "rotation": 0, "solid": [0.8, 0.8]})
                add_solid(x, z, 0.8, 0.8)
                taken.append((x, z, 0.9))


PLANTS = ["Pl_Bush", "Pl_Hemp", "Pl_Shrub1", "Pl_Shrub2", "Pl_Shrub3", "Pl_Shrub4", "Pl_Shrub5", "Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Grass1", "Pl_Grass2", "Pl_Grass3", "Pl_Flower"]
ROCKS = ["Rock_1", "Rock_2", "Rock_3", "RockP_1", "RockP_2", "RockP_3", "Mossy_Slab_1", "Mossy_Slab_2", "Mossy_Slab_3", "Mossy_Slab_4"]
BROKEN = ["Pr_BrokenPillar1", "Pr_BrokenPillar2", "Ruin_PillarStub", "Ruin_WallStub"]
BONES = ["Dungeon_BonePile_%d" % i for i in range(1, 7)] + ["Dungeon_CrossBones", "Dungeon_Pelvis", "Dungeon_Arm", "Dungeon_Leg", "Dungeon_Skull_1", "Dungeon_Skull_2"]
GEAR = ["Shield_A", "Shield_B", "Shield_C", "Shield_D", "Sword_A", "Sword_B", "Weapon_Rack", "Barrel_Oga_1", "Crate_Big", "Crate_Small", "Tv_Sack", "Pr_Barricade", "Pr_CartSmall"]
WEBS = ["Web_Round_Up", "Web_Round_Flat", "Web_Square_Up", "Web_Square_Flat"]


def tiles(cx, cz, w, h, step=2.0, inside=None):
    """Lajes de pedra no chão (2 m) num retângulo (ou onde `inside(x, z)` for verdade)."""
    nx, nz = int(w // step), int(h // step)
    for i in range(nx):
        for j in range(nz):
            x, z = cx - w / 2 + step * (i + 0.5), cz - h / 2 + step * (j + 0.5)
            if (inside is None or inside(x, z)) and room_at(x, z, -0.5) is not None and not in_solid(x, z, 0.3):
                decor.append({"piece": "Floor_UnevenBrick", "position": [round(x, 1), round(z, 1)], "rotation": rng.choice((0, 90, 180, 270)), "y": 0.03})


# --- Acesso: arco de entrada, tochas, estandartes e plantas
arch(0, -5.2)
for x in (-12, 12):
    for z in (3, -3):
        torch(x, z)
for x in (-20, 20):
    put("War_Banner", x, -3, rot=0, scale=1.2, r=0.8)
put("Statue_Knight", -9, -4, rot=0, solid=[1.1, 1.2], r=1.2)
put("Statue_Knight", 9, -4, rot=0, solid=[1.1, 1.2], r=1.2)
scatter("approach", PLANTS, 26, scale=(0.9, 1.3), margin=1.5, r=0.6)
scatter("approach", ROCKS + BROKEN, 8, scale=(0.9, 1.4), margin=2.0, r=1.0, solid=(0.8, 0.8))
# --- Fórum: praça aberta, de lajes, com colunas altas, arcos, fundações de casas caídas, poço, obelisco e uma fogueira de acampamento
tiles(0, -32, 24, 24, inside=lambda x, z: math.hypot(x, z + 32) < 12.5)
put("Pr_Obelisk3", 0, -32, rot=0, solid=[1.4, 1.4], r=2.5, free=1.0)
for k in range(8):
    a = math.tau * (k + 0.5) / 8
    column(14 * math.cos(a), -32 + 14 * math.sin(a), "Ruin_Column" if k % 2 else "Ruin_Pillar")
for x, z, rot in ((-24, -16, 0), (24, -16, 180), (-24, -50, 180), (24, -50, 0)):
    put("Ruin_Foundation", x, z, rot=rot, r=3.5, free=1.0, parts=True)
put("Pr_CoveredWell", -10, -42, rot=0, scale=1.2, solid=[2.1, 2.1], r=2.0)
put("Pr_CartLarge", 20, -30, rot=40, solid=[3.0, 1.8], r=2.0)
put("Pr_CartSmall", -18, -26, rot=300, solid=[2.2, 1.4], r=1.5)
arch(-14, -7, 0)
arch(14, -7, 0)
for x, z in ((-26, -24), (26, -24), (-26, -42), (26, -42), (-8, -52), (8, -52), (-6, -10), (6, -10)):
    torch(x, z)
for x, z in ((-12, -32), (12, -32)):
    brazier(x, z, 1.5)
for x, z in ((-28, -32), (28, -32), (-20, -54), (20, -54)):
    put("War_Banner", x, z, rot=0, scale=1.3, r=0.8)
scatter("forum", PLANTS, 70, scale=(0.9, 1.4), margin=1.5, r=0.6)
scatter("forum", ROCKS + BROKEN, 24, scale=(0.9, 1.5), margin=2.0, r=1.0, solid=(0.8, 0.8))
scatter("forum", ["Oak_Tree", "Dead_Tree"], 5, scale=(0.5, 0.75), margin=3.0, r=2.0, solid=(0.7, 0.7))
scatter("forum", GEAR, 14, scale=(0.9, 1.2), margin=3.0, r=1.0)
scatter("forum", BONES, 10, scale=(2.5, 3.5), margin=3.0, r=0.8)
# --- Bairros murados: plantas e escombros entre as ruas, tochas nas esquinas, teias e ossos
for rid in ("bairro_w", "bairro_e"):
    scatter(rid, PLANTS, 90, scale=(0.9, 1.4), margin=2.0, r=0.6, tries=60)
    scatter(rid, ROCKS + BROKEN, 40, scale=(0.9, 1.5), margin=2.0, r=1.0, tries=60)
    scatter(rid, ["Dead_Tree", "Oak_Tree"], 5, scale=(0.5, 0.75), margin=3.0, r=2.0, tries=60)
    scatter(rid, BONES, 14, scale=(2.5, 3.5), margin=2.0, r=0.8, tries=60)
    scatter(rid, GEAR, 16, scale=(0.9, 1.2), margin=2.0, r=1.0, tries=60)
    scatter(rid, WEBS, 10, scale=(1.5, 2.2), margin=2.0, r=1.2, tries=60)
    for _ in range(14):
        x, z = free_spot(rid, rad=1.2, margin=2.0)
        torch(x, z)
# --- Praça dos Cavaleiros (oeste): coreto em ruínas com o cavaleiro de pedra no meio, colunas em volta, túmulos e armas
cx, cz = -58, -77.5
tiles(cx, cz, 24, 24, inside=lambda x, z: math.hypot(x - cx, z - cz) < 11.5)
decor.append({"piece": "Ruin_Temple2", "position": [cx, cz]})
for dx, dz in ((0, -3.77), (0, 3.79), (-3.73, 0), (3.73, 0)):
    decor.append({"collider": [1.1, 1.1], "position": [cx + dx, cz + dz]})
    add_solid(cx + dx, cz + dz, 1.1, 1.1)
taken.append((cx, cz, 5.5))
decor.append({"light": [1.0, 0.82, 0.5], "position": [cx + 0.6, cz + 0.4], "y": 3.2, "range": 12.0, "energy": 1.4})
for k in range(12):
    a = math.tau * (k + 0.5) / 12
    column(cx + 11 * math.cos(a), cz + 11 * math.sin(a), "Ruin_Column" if k % 3 else "Ruin_Pillar")
for dx, dz, rot in ((-17, -10, 0), (17, -10, 0), (-17, 10, 180), (17, 10, 180)):
    put("Statue_Knight", cx + dx, cz + dz, rot=rot, solid=[1.1, 1.2], r=1.5)
for dx, dz, rot in ((-9, 14, 90), (9, 14, 270)):
    put("Statue_Knight_Lying", cx + dx, cz + dz, rot=rot, solid=[1.9, 1.9], r=2.0)
for dx, dz in ((-14, 0), (14, 0), (0, -15), (0, 15)):
    brazier(cx + dx, cz + dz, 1.6)
scatter("plaza_w", PLANTS, 70, scale=(0.9, 1.4), margin=1.5, r=0.6)
scatter("plaza_w", ROCKS + BROKEN, 24, scale=(0.9, 1.5), margin=2.0, r=1.0, solid=(0.8, 0.8))
scatter("plaza_w", GEAR + BONES, 20, scale=(1.0, 1.4), margin=2.5, r=1.0)
scatter("plaza_w", ["Oak_Tree", "Dead_Tree"], 4, scale=(0.5, 0.75), margin=3.0, r=2.0, solid=(0.7, 0.7))
# --- Praça dos Monólitos (leste): círculo de pedras em pé no fundo, lajes, tochas e a Sacerdotisa
cx, cz = 58, -77.5
tiles(cx, cz, 24, 24, inside=lambda x, z: math.hypot(x - cx, z - cz) < 11.5)
decor.append({"piece": "Ruin_Stones", "position": [cx, cz - 6]})
decor.append({"collider": [8.0, 3.6], "position": [cx, cz - 6 - 1.46]})
add_solid(cx, cz - 7.46, 8.0, 3.6)
taken.append((cx, cz - 6, 5.0))
for k in range(10):
    a = math.tau * (k + 0.5) / 10
    x, z = cx + 11 * math.cos(a), cz + 11 * math.sin(a)
    if z < cz - 3:
        continue
    column(x, z, "Ruin_Pillar" if k % 2 else "Ruin_Column")
for dx, dz in ((-14, -4), (14, -4), (-10, 10), (10, 10), (0, 14)):
    brazier(cx + dx, cz + dz, 1.5)
arch(cx, cz + 17, 0)
for dx in (-15, 15):
    put("War_Banner", cx + dx, cz + 2, rot=0, scale=1.3, r=0.8)
put("Pr_Obelisk1", cx - 6, cz - 14, rot=0, solid=[1.3, 1.3], r=1.5)
put("Pr_Obelisk2", cx + 6, cz - 14, rot=0, solid=[1.3, 1.3], r=1.5)
scatter("plaza_e", PLANTS, 70, scale=(0.9, 1.4), margin=1.5, r=0.6)
scatter("plaza_e", ROCKS + BROKEN, 24, scale=(0.9, 1.5), margin=2.0, r=1.0, solid=(0.8, 0.8))
scatter("plaza_e", GEAR + BONES, 20, scale=(1.0, 1.4), margin=2.5, r=1.0)
scatter("plaza_e", ["Pr_Tombstone1", "Pr_Tombstone2", "Pr_Tombstone3", "Pr_Cross1", "Pr_Cross2"], 14, scale=(1.0, 1.2), margin=2.5, r=1.0, solid=(0.8, 0.8))
# --- Avenida das Colunas: pares de colunas, estátuas e arcos ao longo de uma faixa de lajes
tiles(0, -77.5, 8, 38)
for i, z in enumerate(range(-62, -96, -6)):
    column(-6.2, z, "Ruin_Column" if i % 2 else "Ruin_Pillar", force=True)
    column(6.2, z, "Ruin_Column" if i % 2 else "Ruin_Pillar", force=True)
for z in (-70, -90):
    arch(0, z, 0)
for z in (-64, -76, -88):
    for x in (-7.2, 7.2):
        put("Statue_Knight", x, z, rot=270 if x < 0 else 90, solid=[1.1, 1.2], r=1.4, free=1.0)
for z in (-66, -80, -94):
    torch(-3.4, z)
    torch(3.4, z)
scatter("avenue", PLANTS, 14, scale=(0.9, 1.3), margin=1.0, r=0.6)
scatter("avenue", ROCKS + BROKEN, 5, scale=(0.9, 1.3), margin=1.0, r=1.0, solid=(0.8, 0.8))
# --- Pátio Alto: fundações de salões, fileira de colunas ao norte, braseiros e bandeiras
for x, z, rot in ((-44, -116, 0), (44, -116, 180), (-26, -102, 180), (26, -102, 0)):
    put("Ruin_Foundation", x, z, rot=rot, r=3.5, free=1.0, parts=True)
for x in range(-50, 51, 10):
    column(float(x), -118.5, "Ruin_Column" if (x // 10) % 2 else "Ruin_Pillar", force=True) if abs(x) > 5 else None
for x in (-40, -24, 24, 40):
    brazier(x, -105, 1.7)
for x in (-16, 16, -48, 48):
    put("War_Banner", x, -101, rot=0, scale=1.3, r=0.8)
scatter("yard", PLANTS, 50, scale=(0.9, 1.4), margin=1.5, r=0.6)
scatter("yard", ROCKS + BROKEN, 18, scale=(0.9, 1.5), margin=2.0, r=1.0, solid=(0.8, 0.8))
scatter("yard", GEAR + BONES, 24, scale=(1.0, 1.4), margin=2.5, r=1.0)
scatter("yard", ["Oak_Tree", "Dead_Tree"], 3, scale=(0.5, 0.75), margin=3.0, r=2.0, solid=(0.7, 0.7))
# --- Cidadela (murada): muralha de Ruin_Wall com arcos nas portas e dois muros internos formando um S (o caminho dá a volta)
wall(-26.5, -122.5, 26.5, -122.5, gaps=[(-3.6, 3.6)], skip=0.0)       # sul, com o arco da entrada
wall(-26.5, -151.5, 26.5, -151.5, gaps=[(-3.6, 3.6)], skip=0.0)       # norte, com o arco para o corredor
wall(-26.5, -122.5, -26.5, -151.5)                                    # oeste
wall(26.5, -122.5, 26.5, -151.5)                                      # leste
wall(-26.5, -131.0, 6.0, -131.0)                                      # muro interno A: deixa passar pelo leste
wall(-6.0, -143.0, 26.5, -143.0)                                      # muro interno B: deixa passar pelo oeste
arch(0, -122.5, 0)
arch(0, -151.5, 0)
for x, z in ((-26.5, -122.5), (26.5, -122.5), (-26.5, -151.5), (26.5, -151.5), (6.0, -131.0), (-6.0, -143.0)):
    decor.append({"piece": "Ruin_Column", "position": [x, z], "rotation": 0, "solid": [0.8, 0.8]})
    add_solid(x, z, 0.8, 0.8)
for x, z in ((-18, -127), (18, -127), (-18, -137), (18, -137), (-18, -147), (18, -147), (0, -128), (0, -147)):
    torch(x, z)
for x, z in ((-20, -140), (20, -135), (0, -137)):
    brazier(x, z, 1.6)
scatter("citadel", GEAR + BONES, 26, scale=(1.0, 1.4), margin=2.5, r=1.0)
scatter("citadel", ROCKS + BROKEN, 10, scale=(0.9, 1.4), margin=2.5, r=1.0, solid=(0.8, 0.8))
scatter("citadel", PLANTS, 24, scale=(0.9, 1.3), margin=2.0, r=0.6)
scatter("citadel", WEBS, 5, scale=(1.5, 2.2), margin=2.0, r=1.2)
for x, z in ((-12, -148), (12, -148)):
    put("Statue_Knight", x, z, rot=0, solid=[1.1, 1.2], r=1.5)
# --- corredor do portão: muros dos dois lados (não dá para contornar o portão), estandartes e lanternas
wall(-5.3, -153.0, -5.3, -177.0)
wall(5.3, -153.0, 5.3, -177.0)
for z in (-157, -165, -173):
    torch(-4.2, z)
    torch(4.2, z)
for z in (-163, -170):
    put("War_Banner", -4.2, z, rot=90, scale=1.1, r=0.8, free=1.0)
    put("War_Banner", 4.2, z, rot=270, scale=1.1, r=0.8, free=1.0)
# --- Cofre Real (murado): salão com colunata, tapete de lajes, estátuas, braseiros, ossos e os tesouros do reino
wall(-28.5, -178.5, 28.5, -178.5, gaps=[(-3.6, 3.6)])
wall(-28.5, -223.5, 28.5, -223.5)
wall(-28.5, -178.5, -28.5, -223.5)
wall(28.5, -178.5, 28.5, -223.5)
arch(0, -178.5, 0)
for x, z in ((-28.5, -178.5), (28.5, -178.5), (-28.5, -223.5), (28.5, -223.5)):
    decor.append({"piece": "Ruin_Column", "position": [x, z], "rotation": 0, "solid": [0.8, 0.8]})
    add_solid(x, z, 0.8, 0.8)
tiles(0, -201, 12, 40)
for z in range(-186, -222, -7):
    for x in (-12, 12):
        column(float(x), float(z), "Ruin_Column", force=True)
for z in (-190, -204, -216):
    for x in (-24, 24):
        put("Statue_Knight", x, z, rot=270 if x < 0 else 90, solid=[1.1, 1.2], r=1.5)
for x, z in ((-8, -183), (8, -183), (-8, -198), (8, -198), (-8, -216), (8, -216)):
    brazier(x, z, 1.7)
for x in (-20, 20):
    for z in (-184, -196, -210):
        put("War_Banner", x, z, rot=0, scale=1.3, r=0.9)
put("Pr_Obelisk3", 0, -217, rot=0, solid=[1.4, 1.4], r=2.0)
scatter("vault", BONES, 36, scale=(2.5, 3.5), margin=3.0, r=0.8)
scatter("vault", ["Dungeon_SkullPile", "Dungeon_Ribcage"], 8, scale=(3.0, 4.5), margin=3.5, r=1.2)
scatter("vault", ["Coin_Pile", "Chest_Large", "Cage_Small", "Shield_C", "Shield_D", "Sword_C"], 14, scale=(1.3, 1.8), margin=3.0, r=1.4)
scatter("vault", WEBS, 8, scale=(1.5, 2.4), margin=3.0, r=1.2)
scatter("vault", ROCKS + BROKEN, 10, scale=(0.9, 1.4), margin=3.0, r=1.0, solid=(0.8, 0.8))

# --- muralha caída em volta do mapa: trechos de Ruin_Wall, tocos de coluna, pedras e mato nas bordas que dão para o vazio
for r in rooms:
    cx, cz = r["center"]
    w, h = r["size"]
    for side in "nsew":
        horiz = side in "ns"
        length = w if horiz else h
        n = int(length // 6)
        for i in range(n):
            t = -length / 2 + 6 * (i + 0.5)
            x, z = (cx + t, cz - h / 2 + 0.6) if side == "n" else (cx + t, cz + h / 2 - 0.6) if side == "s" else (cx - w / 2 + 0.6, cz + t) if side == "w" else (cx + w / 2 - 0.6, cz + t)
            ox, oz = (0, -2.0) if side == "n" else (0, 2.0) if side == "s" else (-2.0, 0) if side == "w" else (2.0, 0)
            if room_at(x + ox, z + oz, 0.0) is not None:
                continue                                                  # divisa com outra sala
            if any(math.hypot(x - dx, z - dz) < 5.5 for dx, dz in door_points) or near_interest(x, z, 3.0) or in_solid(x, z, 0.8) or near_taken(x, z, 1.0):
                continue
            roll = rng.random()
            if roll < 0.55:
                decor.append({"piece": "Ruin_Wall", "position": [round(x, 1), round(z, 1)], "rotation": 0 if horiz else 90})
                add_solid(x, z, 5.8 if horiz else 0.7, 0.7 if horiz else 5.8)
                decor.append({"collider": [5.8 if horiz else 0.7, 0.7 if horiz else 5.8], "position": [round(x, 1), round(z, 1)]})
                taken.append((x, z, 1.8))
            elif roll < 0.8:
                put(rng.choice(BROKEN), x, z, solid=[0.8, 0.8], r=1.0, free=1.0)
            else:
                put(rng.choice(ROCKS + PLANTS), x, z, r=0.8, free=1.0)

breakables = []
for i, (rid, n) in enumerate((("approach", 2), ("forum", 8), ("bairro_w", 10), ("bairro_e", 10), ("plaza_w", 4), ("plaza_e", 4), ("avenue", 2), ("yard", 6), ("citadel", 6), ("vault", 6))):
    for _ in range(n):
        x, z = free_spot(rid, rad=1.0, margin=2.5)
        breakables.append({"id": "b%d" % (len(breakables) + 1), "monster": "crate" if len(breakables) % 2 == 0 else "barrel", "position": [x, z], "table": "breakable_potion"})
breakables.append({"id": "coin_bag", "monster": "coin_bag", "position": [4.0, 1.5], "table": "coin_bag"})
for i, p in enumerate(([-16, -38], [20, -50], [-56, -66], [56, -90], [-30, -110], [30, -110], [0, -190], [0, -145]), start=2):
    breakables.append({"id": "coin_bag_%d" % i, "monster": "coin_bag", "position": p, "table": "coin_bag"})

arenas["ruins_01_city"] = {
    "_comment": "Ruínas da cidade destruída na guerra, ampliadas: estrutura da Floresta com outro caminho, mistura de partes murados (Bairro Velho e Bairro do Mercado = labirinto de ruas Ruins_Layout, Destroyed Walls, LFA, CC BY 3.0; "
                "Cidadela; corredor do portão; Cofre Real) e partes abertas (Acesso, Fórum, Praças, Avenida das Colunas, Pátio Alto). Acesso -> Fórum; a oeste o Bairro Velho e a Praça dos Cavaleiros (a estátua do "
                "cavaleiro desperta o Guardião das Ruínas), a leste o Bairro do Mercado e a Praça dos Monólitos (a Sacerdotisa desperta o Campeão Caído), ao meio a Avenida das Colunas; tudo fecha no Pátio Alto -> "
                "Cidadela -> corredor do portão (Porteiro, duas chaves) -> Cofre Real (Rei Caído, chefe final, com a saída). Gerado por tools/assets/build_ruins.py.",
    "name_key": "ARENA_RUINS", "player_class": "mage", "map_id": "map_ruins", "area_level": 5, "outdoor": True, "wake_radius": 10.0, "alert_radius": 5.0,
    "rooms": rooms, "encounters": encounters, "hazards": [], "entries": {"start": [0, 3], "ruins": [0, 3]}, "props": props, "quest_spots": [], "breakables": breakables,
    "style": {"_comment": "Ruínas: sem muro de sala (os muros são peças do cenário), chão de terra.", "walls": [""], "floor": "Ground_Dirt", "low": "", "ground": [0.2, 0.18, 0.14]},
    "decor": decor, "passive": True}


# ---------------------------------------------------------------- NPCs e missões (mesma forma da Floresta, do Deserto e das Docas)
def body(sex, hair, color):
    return {"sex": sex, "hair": [hair], "hair_color": color, "pose": "idle", "outfit": {"body": "cloth"}}


npcs["ruins_scholar"] = {"name_key": "NPC_RUINS_SCHOLAR", "color": [0.45, 0.35, 0.55], "dialogues": [
    {"when": {"quest_new": "ruins_seal"}, "lines": ["DLG_SCHOLAR_1", "DLG_SCHOLAR_2", "DLG_SCHOLAR_3"], "offer": "ruins_seal"},
    {"when": {"quest_active": "ruins_seal"}, "lines": ["DLG_SCHOLAR_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_SCHOLAR_DONE"]}], "body": body("female", "Hair_Long", [0.25, 0.2, 0.3])}
npcs["ruins_knight_statue"] = {"name_key": "NPC_RUINS_KNIGHT_STATUE", "color": [0.6, 0.6, 0.65], "dialogues": [
    {"when": {"quest_active": "ruins_seal"}, "lines": ["DLG_KNIGHT_STATUE_1", "DLG_KNIGHT_STATUE_2"]}, {"when": {}, "lines": ["DLG_KNIGHT_STATUE_LOCKED"]}]}
npcs["ruins_priestess"] = {"name_key": "NPC_RUINS_PRIESTESS", "color": [0.7, 0.55, 0.3], "dialogues": [
    {"when": {"quest_new": "ruins_banner"}, "lines": ["DLG_PRIESTESS_1", "DLG_PRIESTESS_2", "DLG_PRIESTESS_3"], "offer": "ruins_banner"},
    {"when": {"quest_active": "ruins_banner"}, "lines": ["DLG_PRIESTESS_ACTIVE"], "service": "turn_in"},
    {"when": {"quest_done": "ruins_banner"}, "lines": ["DLG_PRIESTESS_DONE"]}, {"when": {}, "lines": ["DLG_PRIESTESS_WAIT"]}], "body": body("female", "Hair_Buns", [0.5, 0.3, 0.15])}
npcs["ruins_gatekeeper"] = {"name_key": "NPC_RUINS_GATEKEEPER", "color": [0.4, 0.4, 0.45], "dialogues": [
    {"when": {"quest_new": "ruins_gate"}, "lines": ["DLG_RGUARD_1", "DLG_RGUARD_2", "DLG_RGUARD_3"], "offer": "ruins_gate"},
    {"when": {"quest_active": "ruins_gate"}, "lines": ["DLG_RGUARD_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_RGUARD_DONE"]}], "body": body("male", "Hair_SimpleParted", [0.15, 0.12, 0.1])}
quests["ruins_seal"] = {"name_key": "QUEST_RUINS_SEAL", "desc_key": "QUEST_RUINS_SEAL_DESC", "type": "village", "giver": "ruins_scholar", "area": "ruins_01_city", "target_element": "earth",
                        "reward": {"gold": 260, "xp": 520}, "item": "stone_heart", "gives": "key_lion"}
quests["ruins_banner"] = {"name_key": "QUEST_RUINS_BANNER", "desc_key": "QUEST_RUINS_BANNER_DESC", "type": "village", "giver": "ruins_priestess", "area": "ruins_01_city", "target_element": "fire",
                          "reward": {"gold": 260, "xp": 520}, "item": "champion_banner", "gives": "key_eagle"}
quests["ruins_gate"] = {"name_key": "QUEST_RUINS_GATE", "desc_key": "QUEST_RUINS_GATE_DESC", "type": "village", "giver": "ruins_gatekeeper", "area": "ruins_01_city",
                        "items": ["key_lion", "key_eagle"], "opens_gate": "boss_gate", "target_element": "earth", "reward": {"gold": 320, "xp": 640}}
T = {
    "MONSTER_RUIN_WARDEN": ("Guardião das Ruínas", "Ruins Guardian", "Guardián de las Ruinas"),
    "MONSTER_WAR_CHAMPION": ("Campeão Caído", "Fallen Champion", "Campeón Caído"),
    "MONSTER_FALLEN_KING": ("Rei Caído", "Fallen King", "Rey Caído"),
    "NPC_RUINS_SCHOLAR": ("Erudita das Ruínas", "Ruins Scholar", "Erudita de las Ruinas"),
    "NPC_RUINS_KNIGHT_STATUE": ("Cavaleiro de Pedra", "Stone Knight", "Caballero de Piedra"),
    "NPC_RUINS_PRIESTESS": ("Sacerdotisa", "Priestess", "Sacerdotisa"),
    "NPC_RUINS_GATEKEEPER": ("Porteiro das Ruínas", "Ruins Gatekeeper", "Portero de las Ruinas"),
    "VALUABLE_STONE_HEART": ("Coração de Pedra", "Stone Heart", "Corazón de Piedra"),
    "VALUABLE_CHAMPION_BANNER": ("Estandarte do Campeão", "Champion's Banner", "Estandarte del Campeón"),
    "VALUABLE_KEY_LION": ("Chave do Leão", "Lion Key", "Llave del León"),
    "VALUABLE_KEY_EAGLE": ("Chave da Águia", "Eagle Key", "Llave del Águila"),
    "TOAST_STATUE_AWAKENS": ("O cavaleiro de pedra se move: o Guardião das Ruínas acorda!", "The stone knight stirs: the Ruins Guardian awakens!", "El caballero de piedra se mueve: ¡el Guardián de las Ruinas despierta!"),
    "TOAST_CHAMPION_AWAKENS": ("Os monólitos tremem: o Campeão Caído se levanta!", "The monoliths shake: the Fallen Champion rises!", "Los monolitos tiemblan: ¡el Campeón Caído se levanta!"),
    "QUEST_RUINS_SEAL": ("O Coração de Pedra", "The Stone Heart", "El corazón de piedra"),
    "QUEST_RUINS_SEAL_DESC": ("A Erudita das Ruínas, no Fórum logo depois da entrada, conta que o cavaleiro de pedra da Praça dos Cavaleiros (oeste, depois do Bairro Velho) guarda um coração de pedra. Toque a estátua com a missão ativa, derrote o Guardião das Ruínas e traga o coração: em troca vem a Chave do Leão, uma das duas do portão do Rei Caído.",
                              "The Ruins Scholar, in the Forum just past the entrance, says the stone knight of the Knights' Plaza (west, past the Old Quarter) guards a stone heart. Touch the statue with the quest active, defeat the Ruins Guardian and bring the heart: in return you get the Lion Key, one of the two for the Fallen King's gate.",
                              "La Erudita de las Ruinas, en el Foro justo tras la entrada, cuenta que el caballero de piedra de la Plaza de los Caballeros (oeste, tras el Barrio Viejo) guarda un corazón de piedra. Toca la estatua con la misión activa, derrota al Guardián de las Ruinas y trae el corazón: a cambio recibes la Llave del León, una de las dos del portón del Rey Caído."),
    "QUEST_RUINS_BANNER": ("O Estandarte do Campeão", "The Champion's Banner", "El estandarte del campeón"),
    "QUEST_RUINS_BANNER_DESC": ("A Sacerdotisa, na Praça dos Monólitos (leste, depois do Bairro do Mercado), quer o estandarte do campeão que morreu na guerra. A fala dela desperta o Campeão Caído; derrote-o e traga o estandarte para receber a Chave da Águia, a outra do portão do Rei Caído.",
                                "The Priestess, in the Monoliths' Plaza (east, past the Market Quarter), wants the banner of the champion who died in the war. Her words wake the Fallen Champion; defeat him and bring the banner to receive the Eagle Key, the other one for the Fallen King's gate.",
                                "La Sacerdotisa, en la Plaza de los Monolitos (este, tras el Barrio del Mercado), quiere el estandarte del campeón que murió en la guerra. Sus palabras despiertan al Campeón Caído; derrótalo y trae el estandarte para recibir la Llave del Águila, la otra del portón del Rey Caído."),
    "QUEST_RUINS_GATE": ("O Portão do Rei", "The King's Gate", "El portón del Rey"),
    "QUEST_RUINS_GATE_DESC": ("O Porteiro das Ruínas, no corredor depois da Cidadela, só abre o portão para quem trouxer as duas chaves: a do Leão (Erudita) e a da Águia (Sacerdotisa). Atrás dele fica o Cofre Real do Rei Caído.",
                              "The Ruins Gatekeeper, in the lane past the Citadel, only opens the gate for those with both keys: the Lion (Scholar) and the Eagle (Priestess). Beyond lies the Fallen King's Royal Vault.",
                              "El Portero de las Ruinas, en el pasillo tras la Ciudadela, solo abre el portón a quien traiga las dos llaves: la del León (Erudita) y la del Águila (Sacerdotisa). Tras él está la Cámara Real del Rey Caído."),
    "DLG_SCHOLAR_1": ("Cuidado onde pisam: cada pedra aqui já foi parede de uma casa. Eu catalogo estas ruínas desde antes da guerra e só agora entendo o que o rei escondeu.",
                      "Mind your step: every stone here was once a house wall. I have catalogued these ruins since before the war and only now understand what the king hid.",
                      "Cuidado dónde pisan: cada piedra aquí fue la pared de una casa. Catalogo estas ruinas desde antes de la guerra y solo ahora entiendo lo que el rey escondió."),
    "DLG_SCHOLAR_2": ("Na Praça dos Cavaleiros, a oeste, há um cavaleiro de pedra com um coração de pedra no peito. Ele dorme, mas obedece a quem o toca com a intenção certa.",
                      "In the Knights' Plaza, to the west, stands a stone knight with a stone heart in his chest. He sleeps, but obeys whoever touches him with the right intent.",
                      "En la Plaza de los Caballeros, al oeste, hay un caballero de piedra con un corazón de piedra en el pecho. Duerme, pero obedece a quien lo toca con la intención correcta."),
    "DLG_SCHOLAR_3": ("Toquem a estátua, derrubem o Guardião e tragam o coração. Em troca eu dou a Chave do Leão, uma das duas que abrem o portão do Rei Caído, ao norte da Cidadela.",
                      "Touch the statue, bring down the Guardian and bring me the heart. In return I give the Lion Key, one of the two that open the Fallen King's gate, north of the Citadel.",
                      "Toquen la estatua, derriben al Guardián y tráiganme el corazón. A cambio doy la Llave del León, una de las dos que abren el portón del Rey Caído, al norte de la Ciudadela."),
    "DLG_SCHOLAR_ACTIVE": ("A Praça dos Cavaleiros fica a oeste do Fórum: atravessem o Bairro Velho, onde as ruas viraram labirinto, e subam. O coração é cinza e pesa como chumbo.",
                           "The Knights' Plaza is west of the Forum: cross the Old Quarter, where the streets became a maze, and go north. The heart is grey and heavy as lead.",
                           "La Plaza de los Caballeros está al oeste del Foro: crucen el Barrio Viejo, donde las calles se volvieron laberinto, y suban. El corazón es gris y pesa como plomo."),
    "DLG_SCHOLAR_DONE": ("O coração! Finalmente posso fechar este capítulo do meu catálogo. A Chave do Leão é de vocês; levem-na ao Porteiro, junto com a da Águia.",
                         "The heart! At last I can close this chapter of my catalogue. The Lion Key is yours; take it to the Gatekeeper, together with the Eagle one.",
                         "¡El corazón! Por fin puedo cerrar este capítulo de mi catálogo. La Llave del León es suya; llévenla al Portero, junto con la del Águila."),
    "DLG_KNIGHT_STATUE_1": ("A pedra está morna sob a mão, e algo bate lá dentro, devagar, como um coração enorme.",
                            "The stone is warm under your hand, and something beats inside, slowly, like an enormous heart.",
                            "La piedra está tibia bajo la mano, y algo late dentro, despacio, como un corazón enorme."),
    "DLG_KNIGHT_STATUE_2": ("O Guardião das Ruínas acorda!", "The Ruins Guardian awakens!", "¡El Guardián de las Ruinas despierta!"),
    "DLG_KNIGHT_STATUE_LOCKED": ("Um cavaleiro de pedra, imóvel, de espada baixa. Nada responde ao seu toque.", "A stone knight, motionless, sword lowered. Nothing answers your touch.", "Un caballero de piedra, inmóvil, con la espada baja. Nada responde a tu toque."),
    "DLG_PRIESTESS_1": ("Acendo velas para os que ficaram sem túmulo. Aqui, entre os monólitos, caiu o maior campeão da guerra, e o estandarte dele nunca foi enterrado com ele.",
                        "I light candles for those left without a grave. Here, among the monoliths, the greatest champion of the war fell, and his banner was never buried with him.",
                        "Enciendo velas por los que quedaron sin tumba. Aquí, entre los monolitos, cayó el mayor campeón de la guerra, y su estandarte nunca fue enterrado con él."),
    "DLG_PRIESTESS_2": ("Mas ele não descansa: a cada lua ele se levanta, procurando o estandarte, e quebra o que encontra. Só uma lâmina o convence a deitar de novo.",
                        "But he does not rest: each moon he rises, searching for the banner, and breaks whatever he finds. Only a blade convinces him to lie down again.",
                        "Pero no descansa: cada luna se levanta buscando el estandarte, y rompe lo que encuentra. Solo una hoja lo convence de acostarse de nuevo."),
    "DLG_PRIESTESS_3": ("Vou chamá-lo para vocês, aqui na praça. Derrubem o Campeão Caído e tragam o estandarte: eu dou a Chave da Águia, a outra do portão do Rei Caído.",
                        "I will call him for you, here in the plaza. Bring down the Fallen Champion and bring the banner: I give the Eagle Key, the other for the Fallen King's gate.",
                        "Lo llamaré para ustedes, aquí en la plaza. Derriben al Campeón Caído y traigan el estandarte: doy la Llave del Águila, la otra del portón del Rey Caído."),
    "DLG_PRIESTESS_ACTIVE": ("O estandarte é vermelho e rasgado, e ele o aperta ao peito. Derrubem-no com respeito e tragam o pano para mim.",
                             "The banner is red and torn, and he clasps it to his chest. Bring him down with respect and bring the cloth to me.",
                             "El estandarte es rojo y rasgado, y lo aprieta contra el pecho. Derríbenlo con respeto y tráiganme la tela."),
    "DLG_PRIESTESS_DONE": ("O estandarte! Agora ele pode descansar. A Chave da Águia é de vocês. Levem-na ao Porteiro, na entrada do corredor ao norte da Cidadela.",
                           "The banner! Now he can rest. The Eagle Key is yours. Take it to the Gatekeeper, at the lane north of the Citadel.",
                           "¡El estandarte! Ahora podrá descansar. La Llave del Águila es suya. Llévenla al Portero, en el pasillo al norte de la Ciudadela."),
    "DLG_PRIESTESS_WAIT": ("As velas ainda queimam. Vão em paz, e voltem se precisarem de uma bênção.", "The candles still burn. Go in peace, and return if you need a blessing.", "Las velas aún arden. Vayan en paz, y vuelvan si necesitan una bendición."),
    "DLG_RGUARD_1": ("Alto. Este portão fecha o Cofre Real, e no Cofre manda o Rei Caído. Ele morreu defendendo o tesouro e se recusou a deixá-lo.",
                     "Halt. This gate closes the Royal Vault, and in the Vault the Fallen King rules. He died defending the treasure and refused to leave it.",
                     "Alto. Este portón cierra la Cámara Real, y en la Cámara manda el Rey Caído. Murió defendiendo el tesoro y se negó a dejarlo."),
    "DLG_RGUARD_2": ("O portão só abre com DUAS chaves: a do Leão e a da Águia. A primeira está com a Erudita, no Fórum; a segunda, com a Sacerdotisa, na Praça dos Monólitos.",
                     "The gate only opens with TWO keys: the Lion and the Eagle. The first is with the Scholar, in the Forum; the second, with the Priestess, in the Monoliths' Plaza.",
                     "El portón solo abre con DOS llaves: la del León y la del Águila. La primera la tiene la Erudita, en el Foro; la segunda, la Sacerdotisa, en la Plaza de los Monolitos."),
    "DLG_RGUARD_3": ("Cada uma cobra um preço: um coração de pedra, um estandarte velho. Tragam as duas chaves a mim e eu abro a passagem.",
                     "Each charges a price: a stone heart, an old banner. Bring both keys to me and I will open the way.",
                     "Cada una cobra un precio: un corazón de piedra, un estandarte viejo. Tráiganme las dos llaves y abro el paso."),
    "DLG_RGUARD_ACTIVE": ("Só abro com as duas chaves, Leão e Águia, na mesma bolsa. A Erudita fica no Fórum; a Sacerdotisa, na Praça dos Monólitos, a leste.",
                          "I only open with both keys, Lion and Eagle, in the same bag. The Scholar is in the Forum; the Priestess, in the Monoliths' Plaza, to the east.",
                          "Solo abro con las dos llaves, León y Águila, en la misma bolsa. La Erudita está en el Foro; la Sacerdotisa, en la Plaza de los Monolitos, al este."),
    "DLG_RGUARD_DONE": ("As duas chaves! O portão está aberto. Cuidado: o Rei Caído nunca perdeu um duelo, e nem a morte lhe tirou a coroa.",
                        "Both keys! The gate is open. Beware: the Fallen King never lost a duel, and not even death took his crown.",
                        "¡Las dos llaves! El portón está abierto. Cuidado: el Rey Caído nunca perdió un duelo, y ni la muerte le quitó la corona."),
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
    for dst, src, mul in (("key_lion", "key_spades", (1.4, 1.1, 0.5)), ("key_eagle", "key_diamonds", (0.6, 0.9, 1.4)), ("stone_heart", "human_heart", (0.55, 0.65, 0.85)),
                          ("champion_banner", "crown_jewel", (1.4, 0.5, 0.45))):
        im = Image.open(ICONS + src + ".png").convert("RGBA")
        r_, g_, b_, a_ = im.split()
        Image.merge("RGBA", (r_.point(lambda v: min(255, int(v * mul[0]))), g_.point(lambda v: min(255, int(v * mul[1]))), b_.point(lambda v: min(255, int(v * mul[2]))), a_)).save(ICONS + dst + ".png")
except Exception as exc:
    print("aviso: ícones não gerados:", exc)

for path, data in ((ARENAS, arenas), (MONSTERS, monsters), (NPCS, npcs), (QUESTS, quests), (VALUABLES, valuables)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
print("OK ruins", len(rooms), "salas,", len(decor), "peças de cenário,", len(encounters), "encontros, %d m2" % sum(r["size"][0] * r["size"][1] for r in rooms))
