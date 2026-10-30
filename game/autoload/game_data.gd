# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Carrega os dados do jogo (res://data/*.json). Os dados usam IDs e chaves de
## tradução, nunca texto (00-README.md).

const FILES := {
	"balance": "res://data/balance.json",
	"classes": "res://data/classes.json",
	"monsters": "res://data/monsters.json",
	"arenas": "res://data/arenas.json",
}

var balance: Dictionary
var classes: Dictionary
var monsters: Dictionary
var arenas: Dictionary


func _ready() -> void:
	for table in FILES:
		set(table, load_json(FILES[table]))


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
