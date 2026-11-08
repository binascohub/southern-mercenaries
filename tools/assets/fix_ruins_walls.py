"""Ruínas (ruins_01_city): desenha as paredes invisíveis.
As salas das Ruínas não têm muro próprio (estilo "walls": [""], "low": ""), mas o jogo continua criando a colisão na borda de cada sala (fora das portas).
build_ruins.py cobre só parte dessas bordas com Ruin_Wall: as divisas entre salas vizinhas (Acesso/Fórum, Fórum/Bairros, Bairros/Praças, Praças/Pátio Alto…)
ficavam sem nada, e no contorno sobravam buracos (perto das portas, onde caiu pedra ou mato). Ali o jogador batia numa parede que não aparecia.
Este script mede, ao longo de cada borda com colisão, os trechos sem peça visível por perto e os fecha com trechos de Ruin_Wall (só a peça: a colisão já existe).
Idempotente (apaga as peças "edge_fix" antes). Roda no fim de build_ruins.py.
uso: python3 tools/assets/fix_ruins_walls.py   (a partir da raiz do projeto)"""
import json, math

ARENAS = "data/arenas.json"
DOOR_WIDTH = 6.0          # game/levels/prototype_arena.gd DOOR_WIDTH
TOL = 1.2                 # um ponto da borda está "à vista" se houver peça sólida a menos disto
SKIP_ROOMS = {"citadel", "vault"}   # muralha própria 2 m para dentro: a borda da sala fica atrás dela, fora do alcance

arenas = json.load(open(ARENAS, encoding="utf-8"))
ruins = arenas["ruins_01_city"]
ruins["decor"] = [d for d in ruins["decor"] if not d.get("edge_fix")]
rooms, decor = ruins["rooms"], ruins["decor"]

rects = []
for d in decor:
    x, z = d["position"]
    if "collider" in d:
        w, h = d["collider"]
        rects.append((x - w / 2, z - h / 2, x + w / 2, z + h / 2))
    elif "piece" in d and not d["piece"].startswith(("Floor_", "Pl_")) and "light" not in d:
        rects.append((x - 0.6, z - 0.6, x + 0.6, z + 0.6))


def seen(x, z):
    for x0, z0, x1, z1 in rects:
        dx, dz = max(x0 - x, 0, x - x1), max(z0 - z, 0, z - z1)
        if dx * dx + dz * dz < TOL * TOL:
            return True
    return False


def pieces(length, door, offset):
    """Os mesmos trechos de parede de _wall_pieces (em volta do vão da porta)."""
    if not door:
        return [(-length / 2, length / 2)]
    gap = min(DOOR_WIDTH, length)
    out = []
    if offset - gap / 2 > -length / 2 + 0.01:
        out.append((-length / 2, offset - gap / 2))
    if length / 2 > offset + gap / 2 + 0.01:
        out.append((offset + gap / 2, length / 2))
    return out


lines = {}   # (eixo, coordenada fixa) -> [(a, b)] em coordenadas do mundo
for r in rooms:
    if r["id"] in SKIP_ROOMS:
        continue
    cx, cz = r["center"]
    w, h = r["size"]
    doors = {}
    for d in r.get("doors", []):
        doors[d.split(":")[0]] = float(d.split(":")[1]) if ":" in d else 0.0
    # (eixo ao longo, linha da colisão, linha onde desenhar, centro ao longo, comprimento)
    sides = {"north": ("x", cz - h / 2, cz - h / 2, cx, w), "south": ("x", cz + h / 2, cz + h / 2, cx, w),
             "west": ("z", cx - w / 2 - 0.5, cx - w / 2, cz, h + 2), "east": ("z", cx + w / 2 + 0.5, cx + w / 2, cz, h + 2)}
    for side, (axis, line, draw, mid, length) in sides.items():
        for a0, a1 in pieces(length, side in doors, doors.get(side, 0.0)):
            run, t = None, a0
            while t <= a1 + 1e-6:
                x, z = (mid + t, line) if axis == "x" else (line, mid + t)
                if not seen(x, z):
                    run = run or [t, t]
                    run[1] = t
                if (seen(x, z) or t + 0.5 > a1 + 1e-6) and run:
                    if run[1] - run[0] >= 1.0:
                        lo, hi = max(a0, run[0] - 0.6), min(a1, run[1] + 0.6)
                        lines.setdefault((axis, round(draw, 2)), []).append((mid + lo, mid + hi))
                    run = None
                t += 0.5

added, total = 0, 0.0
for (axis, draw), spans in sorted(lines.items()):
    spans.sort()
    merged = []
    for a, b in spans:                       # junta trechos da mesma linha (divisa vista pelas duas salas)
        if merged and a <= merged[-1][1] + 0.5:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    for a, b in merged:
        length = b - a
        n = max(1, round(length / 6.0))
        if length / (6.0 * n) > 1.15:
            n += 1
        scale = max(0.5, length / (6.0 * n))
        step = length / n
        for i in range(n):
            t = a + step * (i + 0.5)
            x, z = (t, draw) if axis == "x" else (draw, t)
            decor.append({"piece": "Ruin_Wall", "position": [round(x, 2), round(z, 2)], "rotation": 0 if axis == "x" else 90,
                          "scale": round(scale, 2), "edge_fix": True})
            added += 1
        total += length

json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK ruins: %d trechos de Ruin_Wall nas paredes invisíveis (%.0f m de borda)" % (added, total))
