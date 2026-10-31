# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Carrega os dados do jogo (res://data/*.json). Os dados usam IDs e chaves de
## tradução, nunca texto (00-README.md).

const FILES := {
	"balance": "res://data/balance.json",
	"classes": "res://data/classes.json",
	"monsters": "res://data/monsters.json",
	"arenas": "res://data/arenas.json",
	"materials": "res://data/materials.json",
	"rarities": "res://data/rarities.json",
	"affixes": "res://data/affixes.json",
	"item_bases": "res://data/item_bases.json",
	"consumables": "res://data/consumables.json",
	"valuables": "res://data/valuables.json",
	"loot": "res://data/loot.json",
	"elements": "res://data/elements.json",
	"skills": "res://data/skills.json",
	"companions": "res://data/companions.json",
	"shops": "res://data/shops.json",
	"npcs": "res://data/npcs.json",
	"quests": "res://data/quests.json",
	"bestiary": "res://data/bestiary.json",
	"visitors": "res://data/visitors.json",
	"refine": "res://data/refine.json",
}

var balance: Dictionary
var classes: Dictionary
var monsters: Dictionary
var arenas: Dictionary
var materials: Dictionary
var rarities: Dictionary
var affixes: Dictionary
var item_bases: Dictionary
var consumables: Dictionary
var valuables: Dictionary
var loot: Dictionary
var elements: Dictionary
var skills: Dictionary
var companions: Dictionary
var shops: Dictionary
var npcs: Dictionary
var quests: Dictionary
var bestiary: Dictionary
var visitors: Dictionary
var refine: Dictionary


func _ready() -> void:
	for table in FILES:
		var data := load_json(FILES[table])
		data.erase("_comment")
		set(table, data)


func get_class_data(id: String) -> Dictionary:
	assert(classes.has(id), "Classe desconhecida: %s" % id)
	return classes[id]


func get_monster(id: String) -> Dictionary:
	assert(monsters.has(id), "Monstro desconhecido: %s" % id)
	return monsters[id]


func get_arena(id: String) -> Dictionary:
	assert(arenas.has(id), "Arena desconhecida: %s" % id)
	return arenas[id]


static func load_json(path: String) -> Dictionary:
	var text := FileAccess.get_file_as_string(path)
	if text.is_empty():
		push_error("Arquivo de dados vazio ou ausente: %s" % path)
		return {}
	var data: Variant = JSON.parse_string(text)
	if not data is Dictionary:
		push_error("JSON inválido: %s" % path)
		return {}
	return data
