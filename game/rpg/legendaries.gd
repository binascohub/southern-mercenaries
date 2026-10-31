# Southern Mercenaries — GPL-3.0-or-later
class_name Legendaries
extends RefCounted
## Lendários (05-itens-e-loot.md, seções 3 e 4): itens com nome, guardados nos
## tesouros dos chefes; o tesouro dá a cada jogador o lendário da classe dele.
## Dados em data/legendaries.json; o item é um equipamento comum com raridade
## "legendary", afixos fixos e o campo "legendary" (o ID, para nome e lore).

## O lendário do tesouro deste chefe para a classe ("" se não houver).
static func for_boss(boss_id: String, class_id: String) -> String:
	for id: String in GameData.legendaries:
		var def: Dictionary = GameData.legendaries[id]
		if def.get("boss", "") == boss_id and def.get("class", "") == class_id:
			return id
	return ""


## Cria o item no nível do tesouro, no tier desse nível (nunca madeira/pano).
static func create(id: String, level: int, rng: RandomNumberGenerator) -> Dictionary:
	var def: Dictionary = GameData.legendaries[id]
	var base: String = def.base
	var tier := maxi(Items.tier_for_level(level), 1)
	var item := Items.equipment(base, Items.material_for_tier(tier, Items.is_weapon(base)), "legendary",
		level, def.affixes.duplicate(), rng)
	item.legendary = id
	return item
