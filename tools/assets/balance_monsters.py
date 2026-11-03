"""Equaliza a força, o drop e a experiência dos monstros pela ORDEM DOS MAPAS (docs/13-balanceamento.md):
  ordem: 1 Esgoto, 2 Floresta, 3 Docas, 4 Ruínas, 5 Cemitério, 6 Forte, 7 Catacumbas, 8 Deserto, 9 Mina, 10 Bunker, 11 Floresta Escura.
  Nível: área = 1, 3, 5 ... (2 níveis por mapa, máximo 20); o chefe do mapa fica um nível acima (como o do Esgoto).
  Força: todo monstro tem a mesma base da sua categoria (vida 210, dano 16, como o Esgoto) e a vida/dano sobem pelo nível da área (1,12^(nível-1)) e pela categoria (elite x3/x1,5, mini-chefe x6/x1,8).
         O papel do monstro ajusta a base (enxame 0,4/0,5, leve 0,65/0,75, tanque 1,6/0,6); o papel é lido uma vez da vida antiga e guardado em "role".
         O chefe do mapa tem vida = DPS típico do herói naquele nível x duração da luta (2 min no mapa 1 até 4,5 min no mapa 9), dano base 40.
  XP:    cada mapa rende ~2 níveis (1400 x nível + 700); as missões ganham uma fatia fixa e `xp_scale` na área ajusta o XP dos monstros ao resto.
  Drop:  as mesmas tabelas por categoria em todos os mapas (ouro por nível); sem `loot_scale` por mapa. Ouro das missões segue a renda alvo (600 x mapa^1,1).
Idempotente. Chamado no fim de tools/assets/build_maps.py. uso: python3 tools/assets/balance_monsters.py   (a partir da raiz do projeto)"""
import json
ARENAS, MONSTERS, QUESTS, BALANCE = "data/arenas.json", "data/monsters.json", "data/quests.json", "data/balance.json"
arenas, monsters, quests, balance = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, MONSTERS, QUESTS, BALANCE))
ORDER = ["sewers_01_drains", "forest_01_path", "docks_01_pier", "ruins_01_city", "cemetery_01_yard", "fort_01_gate", "catacombs_01_depths", "desert_01_canyon", "mine_01_crystal_vein",
         "bunker_01_entrance", "dark_forest_01_woods"]
LEVELS = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 20]
BASE_HP, BASE_DMG, BOSS_DMG = 210, 16, 40
ROLES = {"swarm": (0.4, 0.5), "light": (0.65, 0.75), "normal": (1.0, 1.0), "tank": (1.6, 0.6)}
DPS = [(1, 29), (4, 49), (8, 77), (12, 108), (16, 149), (20, 202)]  # DPS solo típico do herói por nível (13-balanceamento.md, seção 3)
CAT = balance["category_mults"]
XPCAT = balance["xp_per_monster_level"]


def dps(level):
    for (l0, d0), (l1, d1) in zip(DPS, DPS[1:]):
        if level <= l1:
            return d0 + (d1 - d0) * (level - l0) / (l1 - l0)
    return DPS[-1][1]


def lf(level):
    return 1.12 ** (level - 1)


# --- papel (lido uma vez, da vida antiga) e base por categoria
for mid, m in monsters.items():
    if not isinstance(m, dict) or m.get("category") not in ("common", "elite", "miniboss"):
        continue
    if "role" not in m:
        hp = m["max_health"]
        m["role"] = "swarm" if hp <= 30 else ("light" if hp <= 80 else ("tank" if hp >= 400 and m["category"] == "common" else "normal"))
    hp_mult, dmg_mult = ROLES[m["role"]] if m["category"] == "common" else (1.0, 1.0)
    m["max_health"], m["damage"] = round(BASE_HP * hp_mult), round(BASE_DMG * dmg_mult)

# --- nível das áreas e dos encontros, chefes, XP e ouro por mapa
bosses_of = {}
for k, area_id in enumerate(ORDER):
    L = LEVELS[k]
    area = arenas[area_id]
    area["area_level"] = L
    area.pop("loot_scale", None)
    raw_xp = 0.0
    groups = [(e, e["monsters"]) for e in area["encounters"]]
    for p in area["props"]:
        for s in ([p["summon"]] if p.get("summon") else []) + [x["summon"] for x in p.get("extra_summons", [])]:
            s["level"] = L
            groups.append((s, s["monsters"]))
    for holder, mons in groups:
        boss_here = any(monsters[x["monster"]].get("category") == "boss" for x in mons)
        holder["level"] = min(L + 1, 20) if boss_here else L
        for x in mons:
            cat = x.get("rank") or monsters[x["monster"]].get("category", "common")
            if monsters[x["monster"]].get("category") == "boss":
                bosses_of.setdefault(area_id, []).append(x["monster"])
            raw_xp += x.get("count", 1) * XPCAT.get(cat, 5) * holder["level"]
    # chefe do mapa: vida = DPS x duração da luta; o Leshy (mini-chefe final da Floresta) usa o boss_factor
    minutes = 2.0 + 2.5 * min(k, 8) / 8.0 + 0.25 * max(0, k - 8)
    bl = min(L + 1, 20)
    target = dps(bl) * minutes * 60.0
    finals = bosses_of.get(area_id, []) or (["leshy"] if area_id == "forest_01_path" else [])
    for b in finals:
        m = monsters[b]
        if m.get("category") == "boss":
            bf = float(m.get("boss_factor", 1.0))
            m["max_health"] = round(target / (lf(bl) * bf))
            m["damage"] = BOSS_DMG
        else:  # Leshy
            m["boss_factor"] = round(target / (BASE_HP * CAT["miniboss"]["health"] * lf(bl)), 3)
            m["damage"] = round(BOSS_DMG / CAT["miniboss"]["damage"], 1)
    # XP: 2 níveis por mapa; missões com a sua fatia, monstros com o resto (xp_scale)
    need = 1400 * L + 700
    q_xp = 0.0
    income = 600.0 * (k + 1) ** 1.1
    for qid, q in quests.items():
        if not isinstance(q, dict) or q.get("area") != area_id:
            continue
        if q.get("type") == "main":
            frac, gfrac = 0.15, 0.35
        elif "items" in q:
            frac, gfrac = 0.04, 0.10
        elif q.get("item"):
            frac, gfrac = 0.08, 0.15
        else:
            frac, gfrac = 0.04, 0.08
        q["reward"] = {"gold": int(round(income * gfrac / 10.0) * 10), "xp": int(round(need * frac / 10.0) * 10)}
        q_xp += q["reward"]["xp"]
    monster_share = max(need - q_xp, need * 0.3)
    area["xp_scale"] = round(monster_share / raw_xp, 3) if raw_xp else 1.0
json.dump(monsters, open(MONSTERS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(MONSTERS, "a").write("\n")
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
json.dump(quests, open(QUESTS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(QUESTS, "a").write("\n")
print("OK balanceamento:", {a[:8]: (arenas[a]["area_level"], arenas[a]["xp_scale"]) for a in ORDER})
