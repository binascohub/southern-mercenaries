"""Mapa dos Tios Fungo da Floresta: acima (ao norte, z menor) da sala do Rei Golem, um caminho de passagem (sala "ck", 12 x 24 m, trilha de barro) e, no fim dele, a
Clareira dos Fungos (sala "fungus", 30 x 60 m) com 8 bandos de 2 Tios Fungo (fungus_uncle, o modelo e os dados do Esgoto), plantas e carvalhos. A sala do Rei Golem
ganha uma porta ao norte, alinhada com o caminho. Roda por último, depois de add_forest_spacing.py (usa as coordenadas finais; é chamado no fim de tools/assets/build_maps.py).
Idempotente.
uso: python3 tools/assets/add_forest_fungus_map.py   (a partir da raiz do projeto)"""
import json, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
king = next(r for r in forest["rooms"] if r["id"] == "reptiles")
kx = king["center"][0]
kz0 = king["center"][1] - king["size"][1] / 2          # a borda norte da sala do Rei Golem
CK_H, CK_W = 24.0, 12.0
FU, FU_H = 30.0, 60.0      # a clareira: 30 m de largura e 60 m de comprimento (30 m a mais para cima, ao norte)
ck_c = [kx, kz0 - CK_H / 2]
fu_c = [kx, kz0 - CK_H - FU_H / 2]
fu_z0 = kz0 - CK_H - FU_H
inside = lambda p: abs(p[0] - kx) <= FU / 2 + 1.0 and fu_z0 - 1.0 <= p[1] < kz0 - 0.01
forest["rooms"] = [r for r in forest["rooms"] if r["id"] not in ("ck", "fungus")]
forest["decor"] = [d for d in forest["decor"] if "position" not in d or not inside(d["position"])]
forest["encounters"] = [e for e in forest["encounters"] if not e["id"].startswith("f_fungus")]
if "north" not in king["doors"]:
    king["doors"].append("north")
forest["rooms"].append({"id": "ck", "center": ck_c, "size": [CK_W, CK_H], "doors": ["south", "north"], "wall_height": king.get("wall_height", 0.8)})
forest["rooms"].append({"id": "fungus", "center": fu_c, "size": [FU, FU_H], "doors": ["south"], "wall_height": king.get("wall_height", 0.8)})
rng = random.Random("forest-fungus-map")
PIECES = ["Pl_Bamboo"] * 14 + ["Pl_Bush"] * 10 + ["Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Weed4", "Pl_Weed5"] * 6 + ["Pl_Hemp"] * 4 + ["Pl_Flower"] * 3 + \
    ["Pl_Shrub1", "Pl_Shrub2", "Pl_Shrub3", "Pl_Shrub4", "Pl_Shrub5"] * 2
# Trilha de barro: da porta da sala do Rei Golem pelo caminho todo e até o meio da clareira.
BANDS = [(-8.0, 22.0), (8.0, 22.0), (-8.0, 7.0), (8.0, 7.0), (-8.0, -8.0), (8.0, -8.0), (-8.0, -22.0), (8.0, -22.0)]      # (em relação ao centro: z maior = mais ao sul)
n = 0
z = kz0 - 0.5
while z > fu_c[1]:
    forest["decor"].append({"piece": "Trail_Mud", "rotation": rng.randrange(0, 360, 15), "position": [round(kx + rng.uniform(-0.25, 0.25), 2), round(z, 2)],
                            "scale": round(rng.uniform(0.7, 0.9), 2), "y": round(0.012 + 0.002 * (n % 5), 3)})
    n += 1
    z -= 1.1
spots = [(fu_c[0] + dx, fu_c[1] + dz) for dx, dz in BANDS]
count = 0
for cx, cz, w, h in ((ck_c[0], ck_c[1], CK_W, CK_H), (fu_c[0], fu_c[1], FU, FU_H)):
    for _ in range(round(w * h * 0.18)):
        x, zz = round(cx + rng.uniform(-w / 2 + 1.0, w / 2 - 1.0), 1), round(cz + rng.uniform(-h / 2 + 1.0, h / 2 - 1.0), 1)
        if abs(x - kx) < 2.2 and zz > fu_c[1] - 1.0:     # a trilha fica livre
            continue
        if any(abs(x - ex) < 3.5 and abs(zz - ez) < 3.5 for ex, ez in spots):     # os bandos ficam sem mato em cima
            continue
        forest["decor"].append({"piece": PIECES[count % len(PIECES)], "position": [x, zz], "rotation": rng.randrange(360), "scale": round(rng.uniform(0.9, 1.4), 2)})
        count += 1
placed = []
for _ in range(4000):      # carvalhos na clareira, longe da trilha e dos bandos (no máximo 10)
    if len(placed) >= 10:
        break
    x, zz = round(fu_c[0] + rng.uniform(-FU / 2 + 4.0, FU / 2 - 4.0), 1), round(fu_c[1] + rng.uniform(-FU_H / 2 + 4.0, FU_H / 2 - 4.0), 1)
    if abs(x - kx) < 4.0 or any(abs(x - ex) < 6.0 and abs(zz - ez) < 6.0 for ex, ez in spots) or any(abs(x - px) < 9.0 and abs(zz - pz) < 9.0 for px, pz in placed):
        continue
    placed.append((x, zz))
    scale = round(rng.uniform(0.8, 1.4), 2)
    side = round(1.1 * scale, 1)
    forest["decor"].append({"piece": "Oak_Tree", "position": [x, zz], "rotation": rng.randrange(360), "scale": scale, "solid": [side, side]})
forest["breakables"] = [b for b in forest["breakables"] if not b["id"].startswith("coin_bag_f") and not b["id"].startswith("deer_f")]
for i, (dx, dz) in enumerate([(-11.0, 15.0), (11.0, -2.0), (-11.0, -16.0), (11.0, -28.0)]):      # cervos na clareira (tabela "breakable_meat")
    forest["breakables"].append({"id": "deer_f%d" % (i + 1), "monster": "deer_buck" if i % 2 == 0 else "deer_doe", "position": [round(fu_c[0] + dx, 1), round(fu_c[1] + dz, 1)], "table": "breakable_meat"})
for i, (dx, dz) in enumerate([(6.0, 14.0), (-6.0, 0.0), (6.0, -15.0)]):      # três bolsas de moedas na clareira (tabela "coin_bag")
    forest["breakables"].append({"id": "coin_bag_f%d" % (i + 1), "monster": "coin_bag", "position": [round(fu_c[0] + dx, 1), round(fu_c[1] + dz, 1)], "table": "coin_bag"})
for i, (dx, dz) in enumerate(BANDS):
    forest["encounters"].append({"id": "f_fungus_%s" % "abcdefgh"[i], "position": [round(fu_c[0] + dx, 1), round(fu_c[1] + dz, 1)], "monsters": [{"monster": "fungus_uncle", "count": 2}]})
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK mapa dos Tios Fungo: caminho em", ck_c, "clareira em", fu_c, "- plantas:", count)
