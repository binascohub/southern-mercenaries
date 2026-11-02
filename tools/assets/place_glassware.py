"""Coloca as garrafas e copos do Cups and bottles little pack (Glass_*.glb) nas mesas da Taverna e do rei (Capital) em data/arenas.json.
Idempotente: tira primeiro todo Glass_* de cada área e põe de novo. Em cada tampo, cada peça vai para o ponto mais folgado em relação ao que já está lá
(frutas, pratos, velas, garrafas do kit). As peças vêm em tamanho real e o mundo do jogo é ~1,8x maior (maçã de 18 cm), por isso entram com "scale": 1.8.
uso: python3 -I tools/assets/place_glassware.py   (na raiz do projeto)"""
import json, math
SCALE = 1.8
p = 'data/arenas.json'
d = json.loads(open(p, encoding='utf-8').read())
R = {'Bottle': 0.09, 'Food_Meat': 0.25, 'Food_Bread': 0.24, 'Food_Bread_Half': 0.16, 'Food_Cheese': 0.16, 'Food_Cheese_Wheel': 0.19, 'Food_Sausage': 0.2,
     'Food_Sausage_Single': 0.1, 'Dw_Platter': 0.26, 'Table_Plate': 0.2, 'Dw_Plate': 0.14, 'Dw_Bowl': 0.14, 'Dw_Pitcher': 0.12, 'CandleStick_Triple': 0.1,
     'Tv_Lamp': 0.1, 'Tv_Plate': 0.14, 'Tv_Candle': 0.08}
NEW_R = {'Glass_Bottle': 0.06, 'Glass_Cup': 0.06, 'Glass_Tumbler': 0.05, 'Glass_Shot': 0.04, 'Glass_Stein': 0.09}


def rad(piece, new=False):
    t = NEW_R if new else R
    for k, v in t.items():
        if piece.startswith(k):
            return v * (SCALE if new else 1.0)
    return 0.0 if piece in ('Table_Large', 'Tv_Table_Round', 'Chandelier', 'Chandelier_Royal') else (0.1 * SCALE if new else 0.14)


def place(area, center, shape, y, items):
    decor = d[area]['decor']
    cx, cz = center

    def inside(x, z):
        if shape[0] == 'rect':
            return abs(x - cx) <= shape[1] and abs(z - cz) <= shape[2]
        return math.hypot(x - cx, z - cz) <= shape[1]
    occ = [(e['position'][0], e['position'][1], rad(e['piece'])) for e in decor if 'piece' in e and 'position' in e
           and e['piece'] not in ('Table_Large', 'Tv_Table_Round') and abs(e['position'][0] - cx) < 2.2 and abs(e['position'][1] - cz) < 1.4
           and y - 0.15 <= e.get('y', 0) <= y + 0.4]
    out = []
    for n, piece in enumerate(items):
        r = rad(piece, True)
        best = None
        x = cx - 2.0
        while x <= cx + 2.0:
            z = cz - 1.2
            while z <= cz + 1.2:
                if inside(x, z):
                    clear = min([math.hypot(x - ox, z - oz) - orad - r for ox, oz, orad in occ] + [9])
                    score = (round(clear, 3), -math.hypot(x - cx, z - cz))
                    if best is None or score > best[0]:
                        best = (score, x, z)
                z += 0.05
            x += 0.05
        _, bx, bz = best
        e = {"piece": piece, "position": [round(bx, 2), round(bz, 2)], "y": y, "rotation": (n * 67 + int(bx * 100)) % 360, "scale": SCALE}
        out.append(e)
        occ.append((bx, bz, r))
    return out


W, C, M, B = 'Bottle_2', 'Bottle_1', 'Bottle_4', 'Bottle_3'
CC, CW, T, TW, S, ST = 'Glass_Cup_Champagne', 'Glass_Cup_Wine', 'Glass_Tumbler', 'Glass_Tumbler_Whiskey', 'Glass_Shot', 'Glass_Stein'
JOBS = {
    'tavern': [((-2.8, -3.6), ('rect', 1.2, 0.4), 0.81, [W, CW, CW]), ((0.0, -3.6), ('rect', 1.2, 0.4), 0.81, [M, TW, TW]),
               ((2.8, -3.6), ('rect', 1.2, 0.4), 0.81, [B, B, ST]), ((-6.5, 1.5), ('rect', 1.2, 0.4), 0.81, [W, B, CW, T]),
               ((-1.5, -0.4), ('rect', 1.2, 0.4), 0.81, [B, S, S, ST]), ((7.2, 3.2), ('circ', 0.7), 0.75, [M, TW, TW]),
               ((-1.6, 3.6), ('circ', 0.7), 0.75, [W, CW, CW])],
    'capital_01_aurenhold': [((0.0, -45.0), ('rect', 1.3, 0.45), 0.9, [C, W, CC, CC, CC, CW, CW]),
                             ((0.0, -42.2), ('rect', 1.3, 0.45), 0.9, [C, C, W, CC, CC, CC, CW, CW])],
}
for area, jobs in JOBS.items():
    d[area]['decor'] = [e for e in d[area]['decor'] if not str(e.get('piece', '')).startswith('Glass_')]
    new = []
    for ctr, shape, y, items in jobs:
        new += place(area, ctr, shape, y, items)
    d[area]['decor'].extend(new)
    print(area, len(new), "peças")
open(p, 'w', encoding='utf-8').write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
