# Southern Mercenaries — GPL-3.0-or-later
class_name Refine
extends RefCounted
## Refino de equipamentos (05-1-refino.md), sem nós: pergaminho do mesmo
## material e do tipo do item (arma/armadura), +1 a +3 seguro, +4 e +5 com
## risco. Na falha, o pergaminho normal quebra o item em cristais (únicos e
## lendários só voltam a +0); o abençoado só volta a +0. O sorteio é sempre no
## servidor. Números em data/refine.json.

static func rules() -> Dictionary:
	return GameData.refine


static func is_weapon(item: Dictionary) -> bool:
	return GameData.item_bases.get(item.get("base", ""), {}).get("slot", "") == "weapon"


## Pergaminho que serve para o item ("" = item que não refina).
static func scroll_for(item: Dictionary, blessed: bool) -> String:
	if item.get("kind", "") != Items.EQUIPMENT or GameData.materials[item.material].tier == 0:
		return ""
	return "%sscroll_refine_%s_%s" % ["blessed_" if blessed else "", "weapon" if is_weapon(item) else "armor", item.material]


## Motivo para não refinar ("" = pode).
static func refuse_reason(item: Dictionary) -> String:
	if scroll_for(item, false) == "":
		return "REFINE_NO_TIER0"
	if int(item.refine) >= int(rules().max):
		return "REFINE_MAX"
	return ""


## Chance de dar certo o próximo +.
static func chance(item: Dictionary) -> float:
	return float(rules().chances.get(str(int(item.refine) + 1), 0.0))


## Tenta o refino (muda o item). Retorna "ok", "reset" (voltou a +0) ou "broken".
static func attempt(item: Dictionary, blessed: bool, rng: RandomNumberGenerator) -> String:
	if rng.randf() < chance(item):
		item.refine = int(item.refine) + 1
		return "ok"
	if blessed or item.rarity in rules().protected_rarities:
		item.refine = 0
		return "reset"
	return "broken"


## Cristais do material ao quebrar ou cristalizar: 1 + nível/2 + refino (proposta).
static func crystals_for(item: Dictionary) -> int:
	return 1 + int(item.level) / 2 + int(item.refine)


## Ouro para o ferreiro fazer um pergaminho com 10 cristais.
static func craft_gold(scroll_id: String) -> int:
	return roundi(float(GameData.consumables[scroll_id].price_base) * float(rules().craft_gold_fraction))
