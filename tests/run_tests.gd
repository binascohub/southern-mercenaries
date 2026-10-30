# Southern Mercenaries — GPL-3.0-or-later
extends SceneTree
## Testes sem interface, rodados no CI:
##   godot --headless --path . --script res://tests/run_tests.gd
## Verifica traduções (3 idiomas completos, chaves usadas existem) e dados.

const LANGS := ["en", "es", "pt_BR"]
const CSV := "res://locale/texts.csv"
const CODE_DIRS := ["res://game", "res://data"]
## Strings em MAIÚSCULAS no código/dados que não são chaves de tradução.
const NOT_KEYS := ["ACTION_"]

var _failures := 0


func _init() -> void:
	var keys := _check_csv()
	_check_keys_used(keys)
	_check_data()
	if _failures == 0:
		print("OK: todos os testes passaram")
	else:
		printerr("FALHOU: %d problema(s)" % _failures)
	quit(1 if _failures else 0)


func _fail(message: String) -> void:
	_failures += 1
	printerr("  ✗ " + message)


func _check_csv() -> Dictionary:
	var keys := {}
	var file := FileAccess.open(CSV, FileAccess.READ)
	if file == null:
		_fail("não abriu " + CSV)
		return keys
	var header := file.get_csv_line()
	if Array(header) != ["keys"] + LANGS:
		_fail("cabeçalho do CSV deve ser keys,%s" % ",".join(LANGS))
	while not file.eof_reached():
		var row := file.get_csv_line()
		if row.size() == 1 and row[0] == "":
			continue
		if row.size() != header.size():
			_fail("linha com colunas erradas: %s" % [row])
			continue
		if keys.has(row[0]):
			_fail("chave duplicada: " + row[0])
		keys[row[0]] = true
		for i in range(1, row.size()):
			if row[i].strip_edges() == "":
				_fail("tradução vazia: %s (%s)" % [row[0], header[i]])
	return keys


## Toda string "CHAVE_EM_MAIUSCULAS" no código e nos dados precisa existir no CSV.
func _check_keys_used(keys: Dictionary) -> void:
	var regex := RegEx.create_from_string("\"([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)\"")
	for dir in CODE_DIRS:
		for path in _files(dir):
			if not (path.ends_with(".gd") or path.ends_with(".json")):
				continue
			var text := FileAccess.get_file_as_string(path)
			for m in regex.search_all(text):
				var key := m.get_string(1)
				if key in NOT_KEYS or keys.has(key):
					continue
				_fail("chave sem tradução: %s em %s" % [key, path])
	# Ações remapeáveis viram ACTION_<NOME> no menu de controles.
	var controls := FileAccess.get_file_as_string("res://game/autoload/controls.gd")
	var block := controls.get_slice("const REMAPPABLE", 1).get_slice("]", 0)
	for m in RegEx.create_from_string("&\"(\\w+)\"").search_all(block):
		var key := "ACTION_" + m.get_string(1).to_upper()
		if not keys.has(key):
			_fail("ação sem tradução: " + key)


func _check_data() -> void:
	var classes := _json("res://data/classes.json")
	var monsters := _json("res://data/monsters.json")
	var arenas := _json("res://data/arenas.json")
	for id in classes:
		for field in ["name_key", "max_health", "max_resource", "attributes", "basic_attack", "strong_attack", "evade"]:
			if not classes[id].has(field):
				_fail("classe %s sem %s" % [id, field])
	for id in monsters:
		for field in ["name_key", "max_health", "move_speed", "damage", "attack_range"]:
			if not monsters[id].has(field):
				_fail("monstro %s sem %s" % [id, field])
	for id in arenas:
		if not classes.has(arenas[id].get("player_class", "")):
			_fail("arena %s usa classe inexistente" % id)
		for encounter in arenas[id].get("encounters", []):
			for group in encounter.monsters:
				if not monsters.has(group.monster):
					_fail("arena %s usa monstro inexistente: %s" % [id, group.monster])


func _json(path: String) -> Dictionary:
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not data is Dictionary:
		_fail("JSON inválido: " + path)
		return {}
	return data


func _files(dir: String) -> Array[String]:
	var found: Array[String] = []
	for name in DirAccess.get_files_at(dir):
		found.append(dir.path_join(name))
	for sub in DirAccess.get_directories_at(dir):
		found.append_array(_files(dir.path_join(sub)))
	return found
