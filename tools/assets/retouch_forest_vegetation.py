"""Refaz a vegetação da Floresta (data/arenas.json, forest_01_path): tira todas as plantas, árvores e pedras soltas do cenário (Pl_*, Oak_Tree, Dead_Tree, Rock_*, menos as fogueiras e a pira,
que têm marca "camp"/"pyre") e as espalha de novo, sala por sala:
  - árvores (Oak_Tree; a Floresta não tem troncos secos nem toras) encostadas nas bordas e em bosques, com pelo menos 4,5 m entre elas e o centro das salas mais livre;
  - moitas de plantas (arbustos, bambus, ervas, cânhamo, flores) em tufos de 4 a 9 peças, mais densas perto das paredes e raras sobre as trilhas;
  - pedras em grupos de 1 a 3 (a Sala das Pedras tem muito mais), longe das trilhas.
Nada fica em cima de: trilhas de barro, portas (corredor livre de 9 m), pontos de partida, objetos e NPCs (props), encontros (monstros), bichos quebráveis, gente da rua e suas rotas, a pira, as fogueiras,
a lagoa dos sapos, o templo e o resto do cenário que não é vegetação. Determinístico (sementes fixas); pode rodar de novo: refaz do zero. Depois de tools/assets/build_maps.py e dos add_forest_*.py.
uso: python3 tools/assets/retouch_forest_vegetation.py   (a partir da raiz do projeto)"""
import json, math, random

ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
f = arenas["forest_01_path"]
VEG_PREFIX = ("Pl_", "Oak_Tree", "Dead_Tree", "Rock_", "RockP_")
rng = random.Random("forest_vegetation_v2")


def is_veg(e):
    p = str(e.get("piece", ""))
    return p.startswith(VEG_PREFIX) and not (e.get("camp") or e.get("pyre") or e.get("swim") or e.get("flap"))


before = len(f["decor"])
keep = [e for e in f["decor"] if not is_veg(e)]
print("vegetação tirada:", before - len(keep), "mantidas:", len(keep))

rooms = f["rooms"]


def rect(r):
    return (r["center"][0] - r["size"][0] / 2, r["center"][0] + r["size"][0] / 2, r["center"][1] - r["size"][1] / 2, r["center"][1] + r["size"][1] / 2)


R = {r["id"]: rect(r) for r in rooms}
# ---- zonas proibidas (círculos: x, z, raio) e retângulos
circles = []
rects_block = []
for e in keep:
    if "position" not in e:
        continue
    p = e["position"]
    pc = str(e.get("piece", ""))
    if pc == "Trail_Mud":
        circles.append((p[0], p[1], 1.5 * float(e.get("scale", 0.8)) + 0.9, "trail"))
    elif e.get("pyre"):
        circles.append((p[0], p[1], 5.0, "pyre"))
    elif e.get("camp") or pc in ("Tv_Fire", "Fire_Flame"):
        circles.append((p[0], p[1], 3.6, "camp"))
    elif "swim" in e:
        circles.append((p[0], p[1], 5.2, "pond"))
    elif "solid" in e or pc.startswith(("Vl_", "Signpost", "Barrel", "Crate", "Bench", "Stool", "Pr_")):
        circles.append((p[0], p[1], 2.2, "deco"))
    elif "collider" in e:
        circles.append((p[0], p[1], max(e["collider"]) / 2 + 2.0, "temple"))
    elif pc.startswith(("Tv_", "Bucket", "Butterfly")):
        circles.append((p[0], p[1], 1.6, "deco"))
for p in f["props"]:
    circles.append((p["position"][0], p["position"][1], 3.0, "prop"))
for e in f["encounters"]:
    circles.append((e["position"][0], e["position"][1], 3.2, "enc"))
for b in f.get("breakables", []):
    circles.append((b["position"][0], b["position"][1], 1.6, "breakable"))
for c in f.get("crowd", []):
    circles.append((c["position"][0], c["position"][1], 1.8, "crowd"))
    if "path" in c:
        a, b = c["position"], c["path"]
        n = max(1, int(math.dist(a, b) // 1.5))
        for i in range(n + 1):
            circles.append((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n, 1.4, "route"))
for p in f["props"]:
    if "route" in p:  # NPC que passeia (a Aelindra): corredor livre ao longo da rota
        a, b = p["route"][0], p["route"][1]
        n = max(1, int(math.dist(a, b) // 1.5))
        for i in range(n + 1):
            circles.append((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n, 2.0, "route"))
for k, v in f["entries"].items():
    circles.append((v[0], v[1], 3.5, "entry"))
# portas: retângulo de 9 m ao longo da parede e 8 m para dentro, de cada sala
for r in rooms:
    x0, x1, z0, z1 = R[r["id"]]
    cx, cz = r["center"]
    for d in r.get("doors", []):
        side = d.split(":")[0]
        off = float(d.split(":")[1]) if ":" in d else 0.0
        if side in ("north", "south"):
            zz = z0 if side == "north" else z1
            rects_block.append((cx + off - 4.5, cx + off + 4.5, zz - 8 if side == "north" else zz - 8, zz + 8))
        else:
            xx = x0 if side == "west" else x1
            rects_block.append((xx - 8, xx + 8, cz + off - 4.5, cz + off + 4.5))
# grade para consulta rápida
CELL = 4.0
grid = {}
for i, c in enumerate(circles):
    gx0, gx1 = int((c[0] - c[2]) // CELL), int((c[0] + c[2]) // CELL)
    gz0, gz1 = int((c[1] - c[2]) // CELL), int((c[1] + c[2]) // CELL)
    for gx in range(gx0, gx1 + 1):
        for gz in range(gz0, gz1 + 1):
            grid.setdefault((gx, gz), []).append(i)


def blocked(x, z, margin=0.0, trail_margin=0.0):
    for rx0, rx1, rz0, rz1 in rects_block:
        if rx0 - margin <= x <= rx1 + margin and rz0 - margin <= z <= rz1 + margin:
            return True
    for i in grid.get((int(x // CELL), int(z // CELL)), []):
        cx, cz, rad, kind = circles[i]
        extra = trail_margin if kind == "trail" else margin
        if math.hypot(x - cx, z - cz) < rad + extra:
            return True
    return False


placed = []  # (x, z, raio) da vegetação nova
pgrid = {}


def free_of_placed(x, z, rad):
    for i in pgrid.get((int(x // 3.0), int(z // 3.0)), []) + sum((pgrid.get((int(x // 3.0) + dx, int(z // 3.0) + dz), []) for dx in (-2, -1, 0, 1, 2) for dz in (-2, -1, 0, 1, 2)), []):
        px, pz, pr = placed[i]
        if math.hypot(x - px, z - pz) < rad + pr:
            return False
    return True


def put(x, z, rad):
    placed.append((x, z, rad))
    pgrid.setdefault((int(x // 3.0), int(z // 3.0)), []).append(len(placed) - 1)


def edge_distance(rid, x, z):
    x0, x1, z0, z1 = R[rid]
    return min(x - x0, x1 - x, z - z0, z1 - z)


# perfil de cada sala: árvores por 100 m², tufos de plantas por 100 m², grupos de pedras por 100 m², quanto prefere a borda (0 = uniforme, 1 = só nas bordas), árvore principal
PROFILE = {
    "village": dict(trees=0.7, tufts=1.6, rocks=0.25, edge=0.9, tree="Oak_Tree"),
    "toads": dict(trees=1.2, tufts=4.0, rocks=0.35, edge=0.6, tree="Oak_Tree"),
    "pira": dict(trees=1.0, tufts=2.2, rocks=0.3, edge=0.85, tree="Oak_Tree"),
    "pira_s": dict(trees=1.0, tufts=2.2, rocks=0.3, edge=0.85, tree="Oak_Tree"),
    "pira_t": dict(trees=1.0, tufts=2.2, rocks=0.3, edge=0.85, tree="Oak_Tree"),
    "bats": dict(trees=1.8, tufts=2.6, rocks=0.5, edge=0.7, tree="Oak_Tree"),
    "hub": dict(trees=1.6, tufts=3.0, rocks=0.5, edge=0.6, tree="Oak_Tree"),
    "reptiles": dict(trees=1.5, tufts=3.2, rocks=0.45, edge=0.55, tree="Oak_Tree"),
    "beasts": dict(trees=2.0, tufts=3.0, rocks=0.5, edge=0.55, tree="Oak_Tree"),
    "pedra": dict(trees=0.8, tufts=1.6, rocks=2.6, edge=0.4, tree="Oak_Tree"),
    "lair": dict(trees=1.8, tufts=1.5, rocks=0.8, edge=0.6, tree="Oak_Tree"),
    "fungus": dict(trees=1.3, tufts=1.6, rocks=0.5, edge=0.6, tree="Oak_Tree"),
}
CORRIDOR = dict(trees=2.6, tufts=3.2, rocks=0.35, edge=0.95, tree="Oak_Tree")
TREE_CLEAR = 4.6
TREE_BAND = 7.0  # árvores só até 7 m das paredes nas salas largas
TUFT_MULT = 1.9  # mais tufos: a Floresta tem de parecer mata fechada fora das trilhas
PLANT_MIX = [("Pl_Bush", 20, 1.0, 1.5), ("Pl_Bamboo", 26, 0.9, 1.5), ("Pl_Shrub1", 6, 0.84, 1.5), ("Pl_Shrub2", 5, 0.84, 1.5), ("Pl_Shrub3", 5, 0.84, 1.5), ("Pl_Shrub4", 5, 0.84, 1.5),
             ("Pl_Shrub5", 5, 0.84, 1.5), ("Pl_Hemp", 8, 0.92, 1.38), ("Pl_Flower", 6, 0.9, 1.4), ("Pl_Swirl", 4, 1.0, 1.5), ("Pl_Weed1", 8, 0.9, 1.9), ("Pl_Weed2", 8, 0.9, 1.9),
             ("Pl_Weed3", 8, 0.9, 1.9), ("Pl_Weed4", 8, 0.9, 1.9), ("Pl_Weed5", 8, 0.9, 1.9)]
EDGE_PLANTS = {"Pl_Bamboo": 2.0, "Pl_Bush": 1.4, "Pl_Hemp": 0.8}   # peso extra perto das paredes
OPEN_PLANTS = {"Pl_Flower": 2.2, "Pl_Weed1": 1.5, "Pl_Weed2": 1.5, "Pl_Weed3": 1.5, "Pl_Weed4": 1.5, "Pl_Weed5": 1.5, "Pl_Swirl": 1.5}  # no meio (mais baixas)
ROCKS = [("Rock_Mossy", 30), ("Rock_1", 18), ("Rock_2", 14), ("Rock_3", 12), ("Rock_4", 12), ("Rock_5", 14)]
ROCK_SOLID = {"Rock_Mossy": (2.2, 1.93)}
new = []


def weighted(items, rng_):
    total = sum(w for _, w, *_ in items)
    r = rng_.random() * total
    for it in items:
        r -= it[1]
        if r <= 0:
            return it
    return items[-1]


def sample_in(rid, edge_pref, rng_, tries=60):
    x0, x1, z0, z1 = R[rid]
    half = min(x1 - x0, z1 - z0) / 2.0
    for _ in range(tries):
        x, z = rng_.uniform(x0 + 1.4, x1 - 1.4), rng_.uniform(z0 + 1.4, z1 - 1.4)
        d = edge_distance(rid, x, z)
        accept = (1 - edge_pref) + edge_pref * max(0.05, 1.0 - d / max(5.0, half * 0.9))
        if rng_.random() < accept:
            return x, z
    return None


counts = {"trees": 0, "tufts": 0, "plants": 0, "rocks": 0}
for r in rooms:
    rid = r["id"]
    prof = PROFILE.get(rid, CORRIDOR)
    x0, x1, z0, z1 = R[rid]
    area = (x1 - x0) * (z1 - z0)
    rr = random.Random("forest_veg_%s" % rid)
    # --- árvores
    n_trees = round(area / 100.0 * prof["trees"])
    tries = 0
    got = 0
    while got < n_trees and tries < n_trees * 40:
        tries += 1
        s = sample_in(rid, prof["edge"], rr)
        if s is None:
            continue
        x, z = s
        if blocked(x, z, 0.8, 1.3) or not free_of_placed(x, z, TREE_CLEAR / 2.0):
            continue
        if min(x1 - x0, z1 - z0) > 14.0 and edge_distance(rid, x, z) > TREE_BAND:
            continue  # copas grandes tapam a visão de cima: árvores só na faixa junto das paredes, o meio das salas fica aberto
        scale = round(rr.uniform(0.85, 1.4), 2)
        piece = prof["tree"]
        e = {"piece": piece, "position": [round(x, 1), round(z, 1)], "rotation": rr.randrange(360), "scale": scale}
        if piece == "Oak_Tree":
            e["solid"] = [1.0, 1.0]
        new.append(e)
        put(x, z, TREE_CLEAR / 2.0)
        got += 1
        counts["trees"] += 1
    # --- rochas
    n_rock = max(1, round(area / 100.0 * prof["rocks"])) if prof["rocks"] > 0 else 0
    tries = 0
    got = 0
    while got < n_rock and tries < n_rock * 40:
        tries += 1
        s = sample_in(rid, min(0.5, prof["edge"]), rr)
        if s is None:
            continue
        x, z = s
        if blocked(x, z, 1.4, 1.8) or not free_of_placed(x, z, 1.8):
            continue
        group = 1 + (rr.random() < 0.5) + (rr.random() < 0.2)
        cx, cz = x, z
        for k in range(group):
            ang = rr.uniform(0, math.tau)
            gx, gz = cx + (math.cos(ang) * rr.uniform(0.9, 1.9) if k else 0), cz + (math.sin(ang) * rr.uniform(0.9, 1.9) if k else 0)
            if k and (blocked(gx, gz, 0.6, 1.4) or not (x0 + 1.2 < gx < x1 - 1.2 and z0 + 1.2 < gz < z1 - 1.2)):
                continue
            name = weighted(ROCKS if rid != "pedra" else [("Rock_Mossy", 55), ("Rock_1", 10), ("Rock_2", 10), ("Rock_3", 8), ("Rock_4", 8), ("Rock_5", 9)], rr)[0]
            sc = round(rr.uniform(0.9, 1.5) if name != "Rock_Mossy" else rr.uniform(0.7, 1.4), 2)
            e = {"piece": name, "position": [round(gx, 1), round(gz, 1)], "rotation": rr.randrange(360), "scale": sc}
            base = ROCK_SOLID.get(name, (0.8, 0.8))
            e["solid"] = [round(base[0] * sc, 1), round(base[1] * sc, 1)]
            new.append(e)
            put(gx, gz, 1.4 * sc)
            counts["rocks"] += 1
        got += 1
    # --- tufos de plantas
    n_tufts = round(area / 100.0 * prof["tufts"] * TUFT_MULT)
    tries = 0
    got = 0
    while got < n_tufts and tries < n_tufts * 30:
        tries += 1
        s = sample_in(rid, prof["edge"] * 0.8, rr)
        if s is None:
            continue
        x, z = s
        if blocked(x, z, 0.5, 0.9):
            continue
        edge_d = edge_distance(rid, x, z)
        near_edge = edge_d < 5.0
        members = []
        for _ in range(rr.randint(4, 9)):
            ang, dist = rr.uniform(0, math.tau), rr.uniform(0.0, 1.7)
            px, pz = x + math.cos(ang) * dist, z + math.sin(ang) * dist
            if not (x0 + 0.9 < px < x1 - 0.9 and z0 + 0.9 < pz < z1 - 0.9) or blocked(px, pz, 0.1, 0.5):
                continue
            mix = [(n, w * (EDGE_PLANTS.get(n, 1.0) if near_edge else OPEN_PLANTS.get(n, 1.0)), lo, hi) for n, w, lo, hi in PLANT_MIX]
            name, _, lo, hi = weighted(mix, rr)
            if not free_of_placed(px, pz, 0.35):
                continue
            e = {"piece": name, "position": [round(px, 1), round(pz, 1)], "rotation": rr.randrange(360)}
            if name != "Pl_Hemp" and name != "Pl_Flower" and name != "Pl_Swirl":
                e["scale"] = round(rr.uniform(lo, hi), 2)
            members.append((e, px, pz))
        for e, px, pz in members:
            new.append(e)
            put(px, pz, 0.35)
            counts["plants"] += 1
        if members:
            got += 1
            counts["tufts"] += 1
print("novos:", counts, "total decor:", len(keep) + len(new))
f["decor"] = keep + new
f["_vegetation"] = "retouch_forest_vegetation.py"
open(ARENAS, "w", encoding="utf-8").write(json.dumps(arenas, indent=2, ensure_ascii=False) + "\n")
