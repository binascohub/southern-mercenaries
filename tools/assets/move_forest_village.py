"""Reorganiza a Floresta (data/arenas.json, forest_01_path) depois que build_maps.py a gera: troca de lugar o CONTEÚDO de duas salas, cada uma
com a outra, sem mexer nas salas, portas e trilhas:
  aldeia (partida, NPCs, portal, adereços)  <->  Clareira dos Sapos  (a aldeia sobe para a sala de cima; os sapos descem)
  Toca dos Répteis (Rei Golem + Guardião)   <->  Covil das Bestas    (o Rei Golem vai para a sala do canto direito-baixo)
Tudo que está dentro de uma sala (cenário, adereços, encontros, cervos, bichos de cenário, pontos de partida) é transladado para a outra; o que
cairia fora da sala de destino (cenário solto) é descartado e o resto é empurrado para dentro. As trilhas de terra ficam onde estão (ligam as portas,
que não mudam). Os ids das salas trocam junto ("village" passa a ser a sala de cima). Roda depois de add_minibosses.py (o Rei Golem já existe).
Depois da troca: o acampamento de cima fica só com os NPCs (sem portal nem a placa da aldeia); o ponto de partida e o portal de volta a Tortuga
ficam na sala de baixo (onde o mapa começa) e os sapos vão para a sala dos morcegos, vazia, para não atacarem quem chega.
Idempotente: se a sala "village" já está em cima, não faz nada.
uso: python3 tools/assets/move_forest_village.py   (a partir da raiz do projeto)"""
import json
ARENAS = "data/arenas.json"
PAIRS = [("village", "toads"), ("reptiles", "beasts")]
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
rooms = {r["id"]: r for r in forest["rooms"]}
if rooms["village"]["center"][1] < -40:
    print("OK aldeia já está em cima, nada a fazer")
    raise SystemExit


def rect(r):
    return (r["center"][0] - r["size"][0] / 2, r["center"][0] + r["size"][0] / 2, r["center"][1] - r["size"][1] / 2, r["center"][1] + r["size"][1] / 2)


def inside(pt, box, m=0.0):
    return box[0] + m <= pt[0] <= box[1] - m and box[2] + m <= pt[1] <= box[3] - m


def clamp(pt, box, m):
    return [round(min(max(pt[0], box[0] + m), box[1] - m), 2), round(min(max(pt[1], box[2] + m), box[3] - m), 2)]


# (caixa de origem, caixa de destino, deslocamento) de cada sala
moves = []
for a, b in PAIRS:
    ra, rb = rooms[a], rooms[b]
    d = [rb["center"][0] - ra["center"][0], rb["center"][1] - ra["center"][1]]
    moves.append((rect(ra), rect(rb), d))
    moves.append((rect(rb), rect(ra), [-d[0], -d[1]]))


def move(pt, decor):
    """Nova posição de `pt`, ou None (cenário que não cabe na sala de destino). Fora das salas trocadas não muda."""
    for src, dst, d in moves:
        if inside(pt, src):
            new = [round(pt[0] + d[0], 2), round(pt[1] + d[1], 2)]
            if inside(new, dst, 0.6):
                return new
            return None if decor else clamp(new, dst, 2.0)
    return pt


kept = []
for item in forest["decor"]:
    if str(item.get("piece", "")).startswith("Trail_"):
        kept.append(item)
        continue
    new = move(item["position"], True)
    if new is not None:
        item["position"] = new
        kept.append(item)
dropped = len(forest["decor"]) - len(kept)
forest["decor"] = kept
for key in ("props", "encounters", "breakables", "crowd"):
    for item in forest.get(key, []):
        item["position"] = move(item["position"], False)
        if "path" in item:
            item["path"] = move(item["path"], False)
for name in forest["entries"]:
    forest["entries"][name] = move(forest["entries"][name], False)
for a, b in PAIRS:
    rooms[a]["id"], rooms[b]["id"] = b, a
# Partida e portal de volta na sala de baixo; sem placa de aldeia; sapos na sala dos morcegos.
START, PORTAL = [-22.5, -12.0], [-26.5, -9.0]
for name in forest["entries"]:
    forest["entries"][name] = list(START)
forest["props"] = [p for p in forest["props"] if p["id"] != "village_sign"]
for p in forest["props"]:
    if p["id"] == "return_portal":
        p["position"] = list(PORTAL)
bats = rect(rooms["bats"])
toad_spots = [[0, -44], [24, -44], [0, -52], [24, -52]]
for e, spot in zip([e for e in forest["encounters"] if e["id"].startswith("f_toads")], toad_spots):
    assert inside(spot, bats, 2.0)
    e["position"] = spot
forest["decor"] = [d for d in forest["decor"] if str(d.get("piece", "")).startswith("Trail_")
                   or all(abs(d["position"][0] - x) > 2.2 or abs(d["position"][1] - z) > 2.2 for x, z in (START, PORTAL))]
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK Floresta: aldeia e Rei Golem movidos; cenário descartado:", dropped)
