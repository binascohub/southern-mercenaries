"""Lagoas da Floresta (toad_pond*): contorno irregular (props "shape": harmônicos 2..6 do ângulo, lidos pelo shader da água e pela colisão) e a margem desfeita
por lama, juncos e capim em distâncias variadas. Sorteio com semente fixa; idempotente (as peças da margem levam "_pond" e são refeitas)."""
import json, math, random

raw = open("data/arenas.json", encoding="utf-8").read()
data = json.loads(raw)
forest = data.get("arenas", data)["forest_01_path"]
ponds = [p for p in forest["props"] if p["kind"] == "water" and p.get("round")]
rng = random.Random("forest-ponds")
for p in ponds:
    p["shape"] = [[round(rng.uniform(0.02, 0.1) / (1 + 0.25 * k), 3), round(rng.uniform(0, 6.28), 2)] for k in range(5)]


def edge(p, a):
    return 1.0 + sum(h[0] * math.sin((k + 2) * a + h[1]) for k, h in enumerate(p["shape"]))


def inside_any(x, z, pad=1.0):
    for p in ponds:
        qx, qz = (x - p["position"][0]) / (p["size"][0] / 2), (z - p["position"][1]) / (p["size"][1] / 2)
        if math.hypot(qx, qz) < edge(p, math.atan2(qz, qx)) * pad:
            return True
    return False


forest["decor"] = [d for d in forest["decor"] if "_pond" not in d]
GRASS = ["Pl_Grass1", "Pl_Grass2", "Pl_Grass3", "Pl_Weed1", "Pl_Weed2", "Pl_Hemp", "Pl_Flower"]
added = 0
for p in ponds:
    cx, cz = p["position"]
    hx, hz = p["size"][0] / 2, p["size"][1] / 2
    for _ in range(int(14 + 2.2 * (hx + hz))):
        a = rng.uniform(0, math.tau)
        r = edge(p, a) * rng.uniform(0.96, 1.0) + rng.uniform(0.05, 0.45) ** 1.3 * rng.choice((0.5, 1.0))
        x, z = cx + math.cos(a) * hx * r, cz + math.sin(a) * hz * r
        roll = rng.random()
        if roll < 0.32:
            if inside_any(x, z, 0.9):
                continue
            forest["decor"].append({"piece": "Ground_FarmMudPatch", "position": [round(x, 2), round(z, 2)], "y": round(0.03 + rng.random() * 0.01, 3), "rotation": rng.randrange(0, 360, 5),
                                    "scale": round(rng.uniform(0.35, 0.8), 2), "_pond": p["id"]})
        else:
            if inside_any(x, z, 1.02):
                continue
            piece = rng.choice(GRASS)  # sem pedras: a sala dos sapos da Floresta não tem (teste da Praça da Pira)
            forest["decor"].append({"piece": piece, "position": [round(x, 2), round(z, 2)], "rotation": rng.randrange(0, 360, 15),
                                    "scale": round(rng.uniform(0.8, 1.5), 2), "_pond": p["id"]})
        added += 1
open("data/arenas.json", "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent="\t" if raw.startswith("{\n\t") else 2) + ("\n" if raw.endswith("\n") else ""))
print("OK lagoas da Floresta: %d lagoas com contorno irregular, %d peças de margem" % (len(ponds), added))
