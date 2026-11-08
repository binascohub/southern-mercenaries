"""Troca os carvalhos (Oak_Tree, 555 triângulos) pelas árvores realistas (Tree_*, tools/assets/build_realistic_trees.py; "Realistic Trees
Collection", Jungle Jim, CC BY 4.0) em todos os mapas, na mesma posição, giro, escala e bloqueio. A variante sai de um sorteio pela posição:
na Floresta, grandes e médias; nos outros mapas (Fazenda, Ruínas...), só médias. Na Floresta, BUSH_SHARE dos arbustos (Pl_Bush) viram o
arbusto realista (Tree_Bush). Idempotente: a peça trocada guarda a original em "was" e é desfeita antes de sortear de novo.
Roda no fim de tools/assets/build_maps.py (depois de quem põe carvalhos). uso: python3 tools/assets/use_realistic_trees.py"""
import json, random
ARENAS = "data/arenas.json"
LARGE = ["Tree_Large_A", "Tree_Large_B", "Tree_Large_C"]
MEDIUM = ["Tree_Medium_A", "Tree_Medium_B", "Tree_Medium_C"]
BUSH_SHARE = 0.33
FOREST = "forest_01_path"
arenas = json.load(open(ARENAS, encoding="utf-8"))
for aid, arena in arenas.items():
    if not isinstance(arena, dict) or "decor" not in arena:
        continue
    trees = bushes = 0
    for d in arena["decor"]:
        if "was" in d:
            d["piece"] = d.pop("was")
        rng = random.Random("real-tree-%s-%s" % (aid, d.get("position")))
        if d.get("piece") == "Oak_Tree":
            d["was"] = "Oak_Tree"
            d["piece"] = rng.choice(LARGE + MEDIUM if aid == FOREST else MEDIUM)
            trees += 1
        elif aid == FOREST and d.get("piece") == "Pl_Bush" and rng.random() < BUSH_SHARE:
            d["was"] = "Pl_Bush"
            d["piece"] = "Tree_Bush"
            bushes += 1
    if trees or bushes:
        print(aid, trees, "árvores", bushes, "arbustos")
open(ARENAS, "w", encoding="utf-8").write(json.dumps(arenas, indent=2, ensure_ascii=False) + "\n")
