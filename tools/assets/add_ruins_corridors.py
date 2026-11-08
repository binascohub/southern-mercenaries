"""Ruínas (ruins_01_city): caminhos estreitos entre as salas.
As salas das Ruínas encostavam umas nas outras (a passagem era só o vão de 6 m da divisa). Aqui elas se afastam D = 12 m em cada ligação e
o espaço que abre vira um corredor estreito de W = 5 m (uma sala "c_*" com muro dos dois lados), como os caminhos de passagem da Floresta.
As salas só se deslocam, com tudo que está dentro (cenário, adereços, encontros, caixas, pontos de partida, invocações dos altares);
o Pátio Alto, que recebe três corredores (Praça Oeste, Avenida, Praça Leste), estica para os lados: o miolo (|x| < 20) se espalha e as pontas andam D.
Cidadela, corredor do portão e Cofre Real só andam junto com o Pátio (já são murados e ligados por arcos).
Roda no fim de build_ruins.py, antes de fix_ruins_walls.py (que desenha os muros dos corredores). Grava "_spacing" na área e não faz nada se ela já existe.
uso: python3 tools/assets/add_ruins_corridors.py   (a partir da raiz do projeto)"""
import json, random

ARENAS = "data/arenas.json"
D = 12.0      # quanto cada ligação afasta as salas (= comprimento do corredor)
W = 5.0       # largura do corredor
YARD_CORE = 20.0

arenas = json.load(open(ARENAS, encoding="utf-8"))
ruins = arenas["ruins_01_city"]
if ruins.get("_spacing"):
    print("OK ruins: corredores já aplicados")
    raise SystemExit
rooms = {r["id"]: r for r in ruins["rooms"]}
ORIG = {rid: (r["center"][0], r["center"][1], r["size"][0], r["size"][1]) for rid, r in rooms.items()}

SHIFT = {"approach": (0, D), "forum": (0, 0), "bairro_w": (-D, 0), "bairro_e": (D, 0), "avenue": (0, -D),
         "plaza_w": (-D, -D), "plaza_e": (D, -D), "yard": (0, -2 * D), "citadel": (0, -2 * D), "gate_lane": (0, -2 * D), "vault": (0, -2 * D)}
assert set(SHIFT) == set(rooms), set(rooms) ^ set(SHIFT)


def owner(x, z):
    """Sala original que contém o ponto (a mais justa; na divisa entre duas, a de centro mais perto)."""
    best, best_d = None, None
    for rid, (cx, cz, w, h) in ORIG.items():
        dx, dz = abs(x - cx) - w / 2, abs(z - cz) - h / 2
        out = max(dx, dz)
        if out <= 1.5:
            d = (out, abs(x - cx) / w + abs(z - cz) / h)
            if best is None or d < best_d:
                best, best_d = rid, d
    return best


def move(x, z):
    rid = owner(x, z)
    if rid is None:
        return x, z, False
    dx, dz = SHIFT[rid]
    if rid == "yard":
        cx = ORIG["yard"][0]
        t = x - cx
        t = t * (YARD_CORE + D) / YARD_CORE if abs(t) < YARD_CORE else t + (D if t > 0 else -D)
        return round(cx + t, 2), round(z + dz, 2), True
    return round(x + dx, 2), round(z + dz, 2), True


def move_pos(obj, key="position"):
    if key in obj:
        x, z, _ = move(obj[key][0], obj[key][1])
        obj[key] = [x, z]


# Muros de borda desenhados por fix_ruins_walls: saem (ele os refaz depois, nas bordas novas).
ruins["decor"] = [d for d in ruins["decor"] if not d.get("edge_fix")]
lost = 0
for d in ruins["decor"]:
    if owner(*d["position"]) is None:
        lost += 1
    move_pos(d)
for key in ("encounters", "breakables", "quest_spots", "hazards"):
    for item in ruins.get(key, []):
        move_pos(item)
for p in ruins["props"]:
    move_pos(p)
    if "summon" in p:
        move_pos(p["summon"])
    for extra in p.get("extra_summons", []):
        move_pos(extra["summon"])
for name, pos in ruins["entries"].items():
    ruins["entries"][name] = list(move(pos[0], pos[1])[:2])
ruins["_chest_spots"] = [list(move(x, z)[:2]) for x, z in ruins["_chest_spots"]]

# Salas: centro deslocado; o Pátio fica 2D mais largo, com os vãos das praças acompanhando.
for rid, r in rooms.items():
    dx, dz = SHIFT[rid]
    r["center"] = [r["center"][0] + dx, r["center"][1] + dz]
yard = rooms["yard"]
yard["size"] = [yard["size"][0] + 2 * D, yard["size"][1]]
new_doors = []
for door in yard["doors"]:
    side, _, off = door.partition(":")
    if off and abs(float(off)) >= YARD_CORE:
        off = "%g" % (float(off) + (D if float(off) > 0 else -D))
    new_doors.append(side + (":" + off if off else ""))
yard["doors"] = new_doors


def door_point(rid, side):
    """Meio do vão da porta `side` da sala (já deslocada)."""
    r = rooms[rid]
    cx, cz = r["center"]
    w, h = r["size"]
    off = 0.0
    for door in r["doors"]:
        s, _, o = door.partition(":")
        if s == side:
            off = float(o) if o else 0.0
    return {"north": (cx + off, cz - h / 2), "south": (cx + off, cz + h / 2), "west": (cx - w / 2, cz + off), "east": (cx + w / 2, cz + off)}[side]


# (sala de um lado, porta dela, sala do outro, porta dela, nome)
LINKS = [("forum", "south", "approach", "north", "c_acesso"), ("forum", "west", "bairro_w", "east", "c_bairro_w"),
         ("forum", "east", "bairro_e", "west", "c_bairro_e"), ("forum", "north", "avenue", "south", "c_avenida"),
         ("bairro_w", "north", "plaza_w", "south", "c_praca_w"), ("bairro_e", "north", "plaza_e", "south", "c_praca_e"),
         ("plaza_w", "north", "yard", "south", "c_patio_w"), ("avenue", "north", "yard", "south", "c_patio"),
         ("plaza_e", "north", "yard", "south", "c_patio_e")]
rng = random.Random(4242)
corridors = []
for a, sa, b, sb, cid in LINKS:
    ax, az = door_point(a, sa)
    if b == "yard":   # o Pátio tem três vãos no sul: usa o que fica em frente à sala
        y = rooms["yard"]
        south = [y["center"][0] + (float(d.partition(":")[2]) if ":" in d else 0.0) for d in y["doors"] if d.startswith("south")]
        assert any(abs(ax - x) < 0.01 for x in south), (cid, ax, south)
        bx, bz = ax, y["center"][1] + y["size"][1] / 2
    else:
        bx, bz = door_point(b, sb)
    vertical = sa in ("north", "south")
    if vertical:
        assert abs(ax - bx) < 0.01, (cid, ax, bx)
        length = abs(az - bz)
        center, size, doors = [ax, (az + bz) / 2], [W, length], ["north", "south"]
    else:
        assert abs(az - bz) < 0.01, (cid, az, bz)
        length = abs(ax - bx)
        center, size, doors = [(ax + bx) / 2, az], [length, W], ["west", "east"]
    assert abs(length - D) < 0.01, (cid, length)
    corridors.append({"id": cid, "center": center, "size": size, "doors": doors, "wall_height": 0.8})
    # Chão de laje e entulho baixo no corredor (sem bloquear a passagem).
    along = [(-D / 2 + 1.0 + 2.0 * i) for i in range(int(D // 2))]
    for t in along:
        x, z = (center[0], center[1] + t) if vertical else (center[0] + t, center[1])
        ruins["decor"].append({"piece": "Floor_UnevenBrick", "position": [round(x, 2), round(z, 2)], "rotation": 0, "y": 0.02})
    for t in (-D / 4, D / 4):
        x, z = (center[0] + W / 2 - 0.5, center[1] + t) if vertical else (center[0] + t, center[1] + W / 2 - 0.5)
        ruins["decor"].append({"piece": "Tv_Torch", "position": [round(x, 2), round(z, 2)], "rotation": 0, "scale": 1.4})
        ruins["decor"].append({"light": [1.0, 0.6, 0.25], "position": [round(x, 2), round(z, 2)], "y": 1.6, "range": 7.0, "energy": 1.1, "flicker": True})
    for _ in range(3):
        t = rng.uniform(-D / 2 + 1.5, D / 2 - 1.5)
        s = rng.choice((-1, 1)) * (W / 2 - 0.6)
        x, z = (center[0] + s, center[1] + t) if vertical else (center[0] + t, center[1] + s)
        ruins["decor"].append({"piece": rng.choice(["Pl_Weed1", "Pl_Weed2", "Pl_Grass1", "Dungeon_Skull_1", "Pl_Shrub2"]),
                               "position": [round(x, 2), round(z, 2)], "rotation": rng.randrange(360)})
ruins["rooms"] = ruins["rooms"] + corridors
ruins["_spacing"] = True

json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK ruins: %d corredores de %g m x %g m (peças fora de sala, mantidas no lugar: %d)" % (len(corridors), D, W, lost))
