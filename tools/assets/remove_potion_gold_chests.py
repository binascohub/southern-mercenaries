"""Tira dos mapas os baús de poção (props `chest` com loot potion_chest) e os sacos de moedas (breakables coin_bag).
As poções ficam nos caixotes e as moedas nas cerâmicas (add_crates_pots.py). Idempotente; roda antes do add_crates_pots.py."""
import json

raw = open("data/arenas.json", encoding="utf-8").read()
data = json.loads(raw)
root = data.get("arenas", data)
chests = bags = 0
for arena in root.values():
    if not isinstance(arena, dict):
        continue
    props = arena.get("props", [])
    keep = [p for p in props if not (p.get("kind") == "chest" and p.get("loot") == "potion_chest")]
    chests += len(props) - len(keep)
    arena["props"] = keep
    brk = arena.get("breakables", [])
    keep = [b for b in brk if b.get("table") != "coin_bag" and b.get("monster") != "coin_bag"]
    bags += len(brk) - len(keep)
    arena["breakables"] = keep
open("data/arenas.json", "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent="\t" if raw.startswith("{\n\t") else 2) + ("\n" if raw.endswith("\n") else ""))
print("OK removidos: %d baús de poção, %d sacos de moedas" % (chests, bags))
