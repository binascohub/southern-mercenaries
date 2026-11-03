"""Ordem dos mapas e dos hubs (docs/03-2-areas.md, seção 2):
  Tortuga   1 Esgoto · 2 Floresta · 3 Docas · 4 Ruínas
  Capital   5 Cemitério · 6 Forte · 7 Catacumbas (ainda sem mapa) · 8 Deserto
  Fazenda   Mina · Bunker · Floresta Escura (nova ordem 9-11 no documento)
Cada mapa volta ao seu hub (portal de retorno e portal do chefe); os antigos portais em cadeia (Floresta -> Ruínas -> Cemitério -> Floresta Escura -> Forte -> Capital)
e o da Fazenda para o Deserto saem. Idempotente; roda depois de build_maps.py e build_desert.py (chamado no fim de tools/assets/build_maps.py).
uso: python3 tools/assets/set_map_order.py   (a partir da raiz do projeto)"""
import json
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))


def exit_prop(pid, name_key, pos, to, entry, **extra):
    return {"id": pid, "kind": "exit", "name_key": name_key, "position": list(pos), "to": to, "entry": entry} | extra


def put_prop(area, prop):
    a = arenas[area]
    a["props"] = [p for p in a["props"] if p["id"] != prop["id"]] + [prop]


def drop_prop(area, pid):
    arenas[area]["props"] = [p for p in arenas[area]["props"] if p["id"] != pid]


def retarget(area, pid, to, entry, **extra):
    for p in arenas[area]["props"]:
        if p["id"] == pid:
            p["to"], p["entry"] = to, entry
            p.update(extra)


# --- Tortuga: Esgoto, Floresta, Docas, Ruínas (+ Fazenda e Capital como hubs)
drop_prop("tortuga", "mine_gate")  # a Mina agora é da Fazenda
put_prop("tortuga", exit_prop("ruins_gate", "PROP_TO_RUINS", (-28.5, 5.9), "ruins_01_city", "start"))
put_prop("tortuga", exit_prop("capital_gate", "PROP_TO_CAPITAL", (27.0, -2.5), "capital_01_aurenhold", "start"))
arenas["tortuga"]["entries"].update({"ruins": [-24.0, 6.0], "capital": [24.0, -2.5]})

# --- portais dos chefes: cada mapa termina no seu hub (nada de cadeia entre mapas)
END = {"forest_01_path": ("to_ruins", "tortuga", "forest"), "ruins_01_city": ("to_cemetery", "tortuga", "ruins"),
       "cemetery_01_yard": ("to_fort", "capital_01_aurenhold", "cemetery"), "fort_01_gate": ("to_capital", "capital_01_aurenhold", "fort"),
       "dark_forest_01_woods": ("to_fort", "farm_01_fields", "dark_forest"), "desert_01_canyon": ("to_farm", "capital_01_aurenhold", "desert")}
for area, (pid, to, entry) in END.items():
    for p in arenas[area]["props"]:
        if p["id"] == pid:
            p.update({"id": "victory_portal", "name_key": "PROP_RETURN_PORTAL", "to": to, "entry": entry, "after_victory": True, "group": True})
# portais de retorno do começo de cada mapa
retarget("ruins_01_city", "return_portal", "tortuga", "ruins")
for area, entry in (("cemetery_01_yard", "cemetery"), ("fort_01_gate", "fort"), ("desert_01_canyon", "desert")):
    retarget(area, "return_portal", "capital_01_aurenhold", entry, name_key="PROP_RETURN_PORTAL")
    arenas[area]["props"] = [dict(p, expedition_end=False) if p["id"] == "return_portal" else p for p in arenas[area]["props"]]
for area, entry in (("mine_01_crystal_vein", "mine"), ("dark_forest_01_woods", "dark_forest")):
    retarget(area, "return_portal", "farm_01_fields", entry, name_key="PROP_RETURN_FARM")
retarget("capital_01_aurenhold", "return_portal", "tortuga", "capital")

# --- Capital: Cemitério, Forte, Catacumbas, Deserto — portões ao sul da praça
for pid, name, x, to, entry in (("cemetery_gate", "PROP_TO_CEMETERY", 4.5, "cemetery_01_yard", "start"), ("fort_gate", "PROP_TO_FORT", 9.5, "fort_01_gate", "start"),
                                ("catacombs_gate", "PROP_TO_CATACOMBS", 14.5, "catacombs_01_depths", "start"), ("desert_gate", "PROP_TO_DESERT", 19.5, "desert_01_canyon", "start")):
    put_prop("capital_01_aurenhold", exit_prop(pid, name, (x, 4.5), to, entry))
arenas["capital_01_aurenhold"]["entries"].update({"cemetery": [4.5, 2.0], "fort": [9.5, 2.0], "catacombs": [14.5, 2.0], "desert": [19.5, 2.0]})

# --- Fazenda: Mina, Bunker, Floresta Escura (o portal do Deserto sai)
drop_prop("farm_01_fields", "desert_gate")
arenas["farm_01_fields"]["entries"].pop("desert", None)
put_prop("farm_01_fields", exit_prop("dark_forest_gate", "PROP_TO_DARK_FOREST", (-24, -14), "dark_forest_01_woods", "start"))
arenas["farm_01_fields"]["entries"].update({"dark_forest": [-22.0, -11.0], "mine": [24.0, -10.0]})
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK ordem dos mapas")
