"""Baús Monstro no Bunker: o sorteio do build_bunker.py deixou o mapa sem nenhum. Põe um a cada 5 encontros de setor (8 no total),
3 m ao lado do encontro, no nível dele. Idempotente (ids bk_mimic_*). Roda antes do balance_monsters.py."""
import json

raw = open("data/arenas.json", encoding="utf-8").read()
data = json.loads(raw)
root = data.get("arenas", data)
bunker = root["bunker_01_entrance"]
bunker["encounters"] = [e for e in bunker["encounters"] if not e["id"].startswith("bk_mimic_")]
sector = [e for e in bunker["encounters"] if e["id"].startswith("bk_s")]
for i, e in enumerate(sector[2::5], 1):
    x, z = e["position"]
    bunker["encounters"].append({"id": "bk_mimic_%d" % i, "position": [x - 3.0, z + 3.0],
                                 "monsters": [{"monster": "chest_mimic", "count": 1}], "level": e.get("level", 19)})
open("data/arenas.json", "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent="\t" if raw.startswith("{\n\t") else 2) + ("\n" if raw.endswith("\n") else ""))
print("OK bunker: %d baús monstro" % len([e for e in bunker["encounters"] if e["id"].startswith("bk_mimic_")]))
