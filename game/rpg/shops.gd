# Southern Mercenaries — GPL-3.0-or-later
class_name Shops
extends RefCounted
## Regras das lojas (04-tortuga-e-missoes.md, seção 2; 05-itens-e-loot.md,
## seção 6; 13-balanceamento.md, seção 5), sem nós. Os dados ficam em
## data/shops.json.
##
## O estoque é calculado igual no servidor e no PC do jogador a partir do
## "navio do dia" da campanha (semente e dia): assim a janela mostra o mesmo
## que o servidor vai vender, e a compra só manda o índice do item.
## Rua Principal: comuns de madeira/pano, ferro e aço da classe, 2x o valor.
## Mercado Pirata: 3 a 6 itens mágicos/raros/únicos por jogador (muda a cada
## navio), 3x o valor, Poções Elementais; compra os valiosos pela variação do dia.

static func shop(id: String) -> Dictionary:
	return GameData.shops.get(id, {})


## Navio novo: chega a cada volta para Tortuga (estoque pirata e preços dos valiosos).
static func new_ship(day: int, rng: RandomNumberGenerator) -> Dictionary:
	return {"day": day, "seed": rng.randi(), "bought": {}}


## Variação do dia no preço de um valioso (80% a 120%, a mesma para todos no dia).
static func valuable_mult(ship: Dictionary, valuable_id: String) -> float:
	var range_: Array = shop("pirate").get("day_variation", [1.0, 1.0])
	var rng := RandomNumberGenerator.new()
	rng.seed = hash([int(ship.get("seed", 0)), valuable_id])
	return snappedf(rng.randf_range(float(range_[0]), float(range_[1])), 0.01)


static func captain_key(ship: Dictionary) -> String:
	var captains: Array = shop("pirate").get("captains", [])
	return String(captains[int(ship.get("seed", 0)) % captains.size()]) if not captains.is_empty() else ""


## Itens à venda para este personagem (índice = posição na lista).
static func stock(shop_id: String, character: CharacterData, ship: Dictionary) -> Array[Dictionary]:
	var def := shop(shop_id)
	var items: Array[Dictionary] = []
	var level := int(character.data.level)
	for id in def.get("consumables", []):
		items.append(Items.stack(Items.CONSUMABLE, String(id)))
	var rng := RandomNumberGenerator.new()
	if def.has("slots"):
		rng.seed = hash([shop_id, character.data.class_id])
		for material in def.materials:
			for slot in def.slots:
				for base_id in GameData.item_bases:
					var base: Dictionary = GameData.item_bases[base_id]
					var classes: Array = base.get("classes", [])
					if base.slot != slot or not (classes.is_empty() or character.data.class_id in classes):
						continue
					var item := Items.equipment(base_id, String(material), "common", 1, {}, rng)
					item.level = Items.required_level(item)
					items.append(item)
	if def.has("rarity_weights"):
		# Mercado Pirata: ofertas deste personagem neste navio.
		rng.seed = hash([int(ship.get("seed", 0)), character.data.id])
		var count := rng.randi_range(int(def.stock[0]), int(def.stock[1]))
		var spread := int(def.level_spread)
		for i in count:
			var rarity := Items.roll_rarity(def.rarity_weights, rng)
			var item_level := clampi(level + rng.randi_range(-spread, spread), 1, GameData.balance.max_level)
			items.append(Items.generate_equipment(item_level, character.data.class_id, rarity, rng))
	return items


## Já comprado neste navio (o Mercado Pirata não repõe equipamento no mesmo dia).
static func sold_out(shop_id: String, index: int, item: Dictionary, character: CharacterData, ship: Dictionary) -> bool:
	if item.kind != Items.EQUIPMENT or not shop(shop_id).has("rarity_weights"):
		return false
	return index in ship.get("bought", {}).get(character.data.id, [])


## Preço de compra: consumíveis por nível (13-balanceamento.md 5.3); equipamento x markup.
static func buy_price(shop_id: String, item: Dictionary, level: int) -> int:
	if item.kind == Items.CONSUMABLE:
		var c: Dictionary = GameData.consumables[item.id]
		return int(c.price_base + c.price_per_level * level)
	return roundi(Items.value(item) * float(shop(shop_id).get("markup", 1.0)))


## Quanto a loja paga pelo item da bolsa (pilha inteira); -1 = não compra.
static func sell_price(shop_id: String, item: Dictionary, level: int, ship: Dictionary) -> int:
	var count := int(item.get("count", 1))
	match item.kind:
		Items.VALUABLE:
			if not shop(shop_id).get("buys_valuables", false):
				return -1
			return roundi(Items.value(item) * valuable_mult(ship, item.id)) * count
		Items.CONSUMABLE:
			return roundi(buy_price(shop_id, item, level) * GameData.shops.sell_fraction) * count
		Items.EQUIPMENT:
			return roundi(Items.value(item) * GameData.shops.sell_fraction)
	return -1
