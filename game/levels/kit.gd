# Southern Mercenaries — GPL-3.0-or-later
class_name Kit
extends RefCounted
## Peças de cenário e objetos (Quaternius, CC0: Medieval Village MegaKit e
## Fantasy Props MegaKit; exportadas por tools/assets/export_kit.py) e o
## galeão pirata feito para o jogo (assets/models/ships/). As
## áreas são montadas com elas por cima das caixas de colisão: paredes de 2 m,
## pisos de 2×2 m, móveis, barracas, barris. Sem a peça (testes sem
## importação), quem chama mantém o visual simples.

const DIRS: Array[String] = ["res://assets/models/village/", "res://assets/models/props/", "res://assets/models/ships/", "res://assets/models/maps/", "res://assets/models/maps/fort/", "res://assets/models/maps/docks/"]
## Largura de uma parede e lado de um piso do kit (metros).
const WALL_WIDTH := 2.0
const FLOOR_SIZE := 2.0

static var _cache := {}


static func has(piece_name: String) -> bool:
	return _scene(piece_name) != null


## Uma cópia da peça (null se não existir).
static func piece(piece_name: String) -> Node3D:
	var scene := _scene(piece_name)
	return scene.instantiate() as Node3D if scene else null


static func _scene(piece_name: String) -> PackedScene:
	if _cache.has(piece_name):
		return _cache[piece_name]
	var found: PackedScene = null
	for dir in DIRS:
		for ext in [".gltf", ".glb"]:
			var path: String = dir + piece_name + ext
			if ResourceLoader.exists(path):
				found = load(path) as PackedScene
				break
		if found:
			break
	_cache[piece_name] = found
	return found
