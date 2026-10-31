# Southern Mercenaries — GPL-3.0-or-later
class_name Breakables
extends RefCounted
## Barris e caixotes (03-2-areas.md, seção 1, decisão do autor), sem nós: o
## objeto é um Enemy parado ("breakable") que quebra com qualquer golpe. Ao
## quebrar, o servidor sorteia uma vez o que sai (data/loot.json, "breakable"):
## nada, ouro, poção de vida ou de recurso, um valioso ou monstros escondidos.

## O que sai deste objeto.
static func roll(rng: RandomNumberGenerator) -> String:
	return Items.roll_rarity(GameData.loot.breakable.outcomes, rng)  # sorteio por peso


## Chave na campanha ("área:id") dos objetos já quebrados.
static func key(area_id: String, id: String) -> String:
	return "%s:%s" % [area_id, id]
