"""Save point das Docas (docks_01_pier) longe da entrada: o cristal sai do píer de chegada e vai para o Cais (wharf), na frente do corredor do portão
do Kraken, num ponto livre (~17 m dos bandos do Cais). Quem toca o cristal passa a voltar ali (checkpoint). Mesmo esquema do Esgoto e da Floresta:
a entrada "savepoint" e "save_point": "savepoint" (o cristal nasce 2,2 m à direita da entrada). Idempotente. Roda no fim de build_maps.py.
uso: python3 tools/assets/docks_save_point.py   (a partir da raiz do projeto)"""
import json

ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
docks = arenas["docks_01_pier"]
docks["entries"]["savepoint"] = [2.0, -114.0]
docks["save_point"] = "savepoint"
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK docas: save point no Cais", docks["entries"]["savepoint"])
