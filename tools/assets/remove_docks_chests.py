"""Docas: tira os baús de tesouro (props `dock_chest_*`); ficam os caixotes e as cerâmicas quebráveis. Idempotente; roda antes do add_crates_pots.py."""
import json

raw = open("data/arenas.json", encoding="utf-8").read()
data = json.loads(raw)
docks = data.get("arenas", data)["docks_01_pier"]
before = len(docks["props"])
docks["props"] = [p for p in docks["props"] if p.get("kind") != "chest"]
open("data/arenas.json", "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent="\t" if raw.startswith("{\n\t") else 2) + ("\n" if raw.endswith("\n") else ""))
print("OK Docas: %d baús removidos" % (before - len(docks["props"])))
