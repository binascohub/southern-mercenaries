"""Ruínas: tira os baús de tesouro (props `ruins_chest_*`) e põe no lugar de cada um um grupo de 3 caixotes quebráveis (ids rc_*, tabela breakable_crate:
poção ou Mímico). Idempotente; roda antes do add_crates_pots.py (que só refaz os ids cx_* e pt_*)."""
import json

raw = open("data/arenas.json", encoding="utf-8").read()
data = json.loads(raw)
ruins = data.get("arenas", data)["ruins_01_city"]
spots = [p["position"] for p in ruins["props"] if p["id"].startswith("ruins_chest_")]
if spots:
    ruins["_chest_spots"] = spots  # guarda onde ficavam, para refazer o grupo se o script rodar de novo
spots = ruins.get("_chest_spots", [])
ruins["props"] = [p for p in ruins["props"] if not p["id"].startswith("ruins_chest_")]
ruins["breakables"] = [b for b in ruins["breakables"] if not b["id"].startswith("rc_")]
for i, (x, z) in enumerate(spots, 1):
    for j, (dx, dz) in enumerate(((-0.6, 0.0), (0.6, 0.0), (0.0, 1.1))):
        ruins["breakables"].append({"id": "rc_%d_%d" % (i, j + 1), "monster": "crate", "position": [round(x + dx, 1), round(z + dz, 1)], "table": "breakable_crate"})
open("data/arenas.json", "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent="\t" if raw.startswith("{\n\t") else 2) + ("\n" if raw.endswith("\n") else ""))
print("OK Ruínas: %d grupos de caixotes no lugar dos baús" % len(spots))
