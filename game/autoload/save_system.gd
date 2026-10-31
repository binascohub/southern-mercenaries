# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Saves em JSON com escrita segura (11-saves.md, seção 6): grava num arquivo
## temporário e renomeia, mantendo os 3 últimos backups (.bak1 a .bak3). Se o
## principal estiver corrompido, carrega o backup mais recente que funcione.
##
##   user://saves/characters/<id>.json
##   user://saves/campaigns/<id>/campaign.json

## true enquanto grava (o HUD mostra "salvando…").
signal saving(active: bool)

const BACKUPS := 3
const CHARACTER_SAVE_DELAY := 1.0

## Pasta raiz; os testes usam outra para não misturar com os saves do jogador.
var root := "user://saves"
## Último save carregado veio de um backup (o principal estava corrompido).
var restored_from_backup := false

var _pending_character: CharacterData
var _pending_timer := 0.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _process(delta: float) -> void:
	if _pending_character == null:
		return
	_pending_timer -= delta
	if _pending_timer <= 0.0:
		save_character(_pending_character)
		_pending_character = null


# --- Personagens --------------------------------------------------------------------

func character_path(id: String) -> String:
	return root.path_join("characters").path_join(id.validate_filename() + ".json")


func save_character(character: CharacterData) -> bool:
	return write_json(character_path(character.data.id), character.data)


## Agrupa várias mudanças seguidas (loot, ouro…) numa só gravação.
func request_character_save(character: CharacterData) -> void:
	if _pending_character == null:
		_pending_timer = CHARACTER_SAVE_DELAY
	_pending_character = character


## Grava agora o que estiver pendente (ao sair da partida ou do jogo).
func flush() -> void:
	if _pending_character:
		save_character(_pending_character)
		_pending_character = null


func load_character(id: String) -> CharacterData:
	return CharacterData.from_dict(read_json(character_path(id)))


## Resumos para a tela de escolha, do mais recente para o mais antigo.
func list_characters() -> Array[Dictionary]:
	var found: Array[Dictionary] = []
	var dir := root.path_join("characters")
	if not DirAccess.dir_exists_absolute(dir):
		return found
	for file in DirAccess.get_files_at(dir):
		if not file.ends_with(".json"):
			continue
		var c := load_character(file.get_basename())
		if c:
			found.append({"id": c.data.id, "name": c.data.name, "class_id": c.data.class_id,
				"level": c.data.level, "modified": FileAccess.get_modified_time(dir.path_join(file))})
	found.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a.modified > b.modified)
	return found


# --- Campanhas ------------------------------------------------------------------

func campaign_path(id: String) -> String:
	return root.path_join("campaigns").path_join(id.validate_filename()).path_join("campaign.json")


func save_campaign(campaign: Dictionary) -> bool:
	campaign.updated = Time.get_datetime_string_from_system(true)
	return write_json(campaign_path(campaign.id), campaign)


func load_campaign(id: String) -> Dictionary:
	return migrate_campaign(read_json(campaign_path(id)))


func list_campaigns() -> Array[Dictionary]:
	var found: Array[Dictionary] = []
	if not DirAccess.dir_exists_absolute(root.path_join("campaigns")):
		return found
	for id in DirAccess.get_directories_at(root.path_join("campaigns")):
		var c := load_campaign(id)
		if not c.is_empty():
			found.append(c)
	found.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a.get("updated", "") > b.get("updated", ""))
	return found


static func new_campaign() -> Dictionary:
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	return {"save_version": GameData.balance.save_version, "id": Items.new_uid(rng),
		"created": Time.get_datetime_string_from_system(true), "area": "prototype_arena",
		"dead_groups": [], "checkpoint": "start", "played_seconds": 0, "participants": []}


# --- Migração (11-saves.md: migrate_vN_to_vN+1) -----------------------------------

func migrate_character(d: Dictionary) -> Dictionary:
	# v1 é a primeira versão; as próximas entram aqui, uma função por versão.
	return d


func migrate_campaign(d: Dictionary) -> Dictionary:
	return d


# --- Escrita segura -------------------------------------------------------------

func write_json(path: String, data: Dictionary) -> bool:
	saving.emit(true)
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var tmp := path + ".tmp"
	var file := FileAccess.open(tmp, FileAccess.WRITE)
	if file == null:
		push_error("Não foi possível gravar %s" % tmp)
		saving.emit(false)
		return false
	file.store_string(JSON.stringify(data, "\t"))
	file.close()
	# Gira os backups: .bak2 -> .bak3, .bak1 -> .bak2, principal -> .bak1.
	for i in range(BACKUPS - 1, 0, -1):
		var older := "%s.bak%d" % [path, i]
		if FileAccess.file_exists(older):
			DirAccess.rename_absolute(older, "%s.bak%d" % [path, i + 1])
	if FileAccess.file_exists(path):
		DirAccess.rename_absolute(path, path + ".bak1")
	var ok := DirAccess.rename_absolute(tmp, path) == OK
	saving.emit(false)
	return ok


func read_json(path: String) -> Dictionary:
	restored_from_backup = false
	var candidates := [path]
	for i in range(1, BACKUPS + 1):
		candidates.append("%s.bak%d" % [path, i])
	for candidate: String in candidates:
		if not FileAccess.file_exists(candidate):
			continue
		var json := JSON.new()
		if json.parse(FileAccess.get_file_as_string(candidate)) != OK:
			continue
		var data: Variant = json.data
		if data is Dictionary and data.has("save_version"):
			restored_from_backup = candidate != path
			if restored_from_backup:
				push_warning("Save corrompido, usando backup: %s" % candidate)
			return data
	return {}
