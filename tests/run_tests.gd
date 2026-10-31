# Southern Mercenaries — GPL-3.0-or-later
extends SceneTree
## Testes sem interface, rodados no CI:
##   godot --headless --path . --script res://tests/run_tests.gd
## Verifica traduções (.po dos 3 idiomas completos, chaves usadas existem) e dados.

const LANGS := ["en", "es", "pt_BR"]
const TEMPLATE := "res://locale/messages.pot"
const CODE_DIRS := ["res://game", "res://data"]
## Strings em MAIÚSCULAS no código/dados que não são chaves de tradução.
const NOT_KEYS := ["ACTION_"]

var _failures := 0


func _init() -> void:
	var keys := _check_translations()
	_check_loaded_translations()
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


## Traduções em gettext (decisão do autor, 01-escopo.md seção 6): o modelo
## messages.pot e um .po por idioma, todos com as mesmas chaves e preenchidos.
func _check_translations() -> Dictionary:
	var keys := _read_po(TEMPLATE)
	if keys.is_empty():
		_fail("modelo vazio: " + TEMPLATE)
	for lang in LANGS:
		var path := "res://locale/%s.po" % lang
		var texts := _read_po(path)
		for key in keys:
			if not texts.has(key):
				_fail("%s sem a chave %s" % [path, key])
			elif texts[key].strip_edges() == "":
				_fail("tradução vazia: %s (%s)" % [key, lang])
		for key in texts:
			if not keys.has(key):
				_fail("%s tem chave fora do modelo: %s" % [path, key])
	return keys


## O jogo carrega mesmo os .po (project.godot) e cada idioma traduz as chaves.
func _check_loaded_translations() -> void:
	var expected := {"en": "Play solo", "es": "Jugar solo", "pt_BR": "Jogar sozinho"}
	for lang in LANGS:
		TranslationServer.set_locale(lang)
		var text := TranslationServer.translate("MENU_PLAY_SOLO")
		if text != expected[lang]:
			_fail("idioma %s não carregou: MENU_PLAY_SOLO = %s" % [lang, text])


## Lê pares msgid/msgstr (com linhas de continuação). Ignora o cabeçalho.
func _read_po(path: String) -> Dictionary:
	var entries := {}
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		_fail("não abriu " + path)
		return entries
	var current := ""
	var msgid := ""
	var msgstr := ""
	var lines := file.get_as_text().split("\n")
	lines.append("")
	for line in lines:
		line = line.strip_edges()
		if line.begins_with("msgid "):
			_store(entries, msgid, msgstr, path)
			msgid = _unquote(line.substr(6))
			msgstr = ""
			current = "id"
		elif line.begins_with("msgstr "):
			msgstr = _unquote(line.substr(7))
			current = "str"
		elif line.begins_with("\""):
			if current == "id":
				msgid += _unquote(line)
			elif current == "str":
				msgstr += _unquote(line)
	_store(entries, msgid, msgstr, path)
	return entries


func _store(entries: Dictionary, msgid: String, msgstr: String, path: String) -> void:
	if msgid == "":
		return
	if entries.has(msgid):
		_fail("chave duplicada em %s: %s" % [path, msgid])
	entries[msgid] = msgstr


static func _unquote(text: String) -> String:
	return text.trim_prefix("\"").trim_suffix("\"").c_unescape()


## Toda string "CHAVE_EM_MAIUSCULAS" no código e nos dados precisa existir no modelo.
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
		for field in ["name_key", "max_health", "move_speed", "damage", "attack_range", "element"]:
			if not monsters[id].has(field):
				_fail("monstro %s sem %s" % [id, field])
	# Elementos: ciclo fechado (cada um vence exatamente um) e estados/combos que existem.
	var elements := _json("res://data/elements.json")
	var beaten := []
	for id in elements.elements:
		var e: Dictionary = elements.elements[id]
		if not elements.elements.has(e.beats) or e.beats == id or e.beats in beaten:
			_fail("ciclo de elementos quebrado em %s" % id)
		beaten.append(e.beats)
		if not elements.states.has(e.basic_state):
			_fail("estado básico inexistente em %s" % id)
	for id in elements.combos:
		var combo: Dictionary = elements.combos[id]
		if not elements.states.has(combo.needs) or not elements.elements.has(combo.element):
			_fail("combo %s mal definido" % id)
	for id in monsters:
		if not elements.elements.has(monsters[id].get("element", "")):
			_fail("monstro %s com elemento inexistente" % id)
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
