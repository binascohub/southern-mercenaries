# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Saves em JSON com escrita segura (11-saves.md, seção 6): grava num arquivo
## temporário e renomeia, mantendo os 3 últimos backups (.bak1 a .bak3). Se o
## principal estiver corrompido, carrega o backup mais recente que funcione.
##
##   user://saves/characters/<id>.json
##   user://saves/campaigns/<id>/campaign.json + thumb.png
##
## Durante a partida a gravação vai para uma thread (não trava o jogo); a
## cena principal só monta o texto. Ler, gravar sem thread e flush() esperam
## as gravações pendentes, então nunca se lê um save pela metade. Espaços de
## save limitados (seção 3): 12 personagens e 6 campanhas por PC (balance.json).

## true enquanto grava (o HUD mostra "salvando…").
signal saving(active: bool)

const BACKUPS := 3
const CHARACTER_SAVE_DELAY := 1.0
const THUMB_SIZE := Vector2i(256, 144)

## Pasta raiz; os testes usam outra para não misturar com os saves do jogador.
var root := "user://saves"
## Último save carregado veio de um backup (o principal estava corrompido).
var restored_from_backup := false

var _pending_character: CharacterData
var _pending_timer := 0.0

# Thread de gravação: fila de [caminho, bytes, backups]; _busy conta os da
# fila mais o que está sendo gravado.
var _thread: Thread
var _mutex := Mutex.new()
var _semaphore := Semaphore.new()
var _queue: Array = []
var _busy := 0
var _quit := false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_thread = Thread.new()
	_thread.start(_worker)


func _exit_tree() -> void:
	flush()
	_mutex.lock()
	_quit = true
	_mutex.unlock()
	_semaphore.post()
	_thread.wait_to_finish()


func _process(delta: float) -> void:
	if _pending_character == null:
		return
	_pending_timer -= delta
	if _pending_timer <= 0.0:
		save_character(_pending_character, true)
		_pending_character = null


# --- Personagens --------------------------------------------------------------------

func character_path(id: String) -> String:
	return root.path_join("characters").path_join(id.validate_filename() + ".json")


func save_character(character: CharacterData, background := false) -> bool:
	character.seal()
	return write_json(character_path(character.data.id), character.data, background)


## Agrupa várias mudanças seguidas (loot, ouro…) numa só gravação.
func request_character_save(character: CharacterData) -> void:
	if _pending_character == null:
		_pending_timer = CHARACTER_SAVE_DELAY
	_pending_character = character


## Grava agora o que estiver pendente e espera a thread terminar (ao sair da
## partida ou do jogo).
func flush() -> void:
	if _pending_character:
		save_character(_pending_character, true)
		_pending_character = null
	wait_for_writes()


func load_character(id: String) -> CharacterData:
	return CharacterData.from_dict(read_json(character_path(id)))


## Resumos para a tela de escolha, do mais recente para o mais antigo.
func list_characters() -> Array[Dictionary]:
	var found: Array[Dictionary] = []
	var dir := root.path_join("characters")
	wait_for_writes()
	if not DirAccess.dir_exists_absolute(dir):
		return found
	for file in DirAccess.get_files_at(dir):
		if not file.ends_with(".json"):
			continue
		var c := load_character(file.get_basename())
		if c:
			found.append({"id": c.data.id, "name": c.data.name, "class_id": c.data.class_id,
				"level": c.data.level, "element": c.data.element, "modified": FileAccess.get_modified_time(dir.path_join(file))})
	found.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a.modified > b.modified)
	return found


func delete_character(id: String) -> void:
	wait_for_writes()
	_delete_with_backups(character_path(id))


# --- Campanhas ------------------------------------------------------------------

func campaign_path(id: String) -> String:
	return root.path_join("campaigns").path_join(id.validate_filename()).path_join("campaign.json")


func thumbnail_path(id: String) -> String:
	return campaign_path(id).get_base_dir().path_join("thumb.png")


func save_campaign(campaign: Dictionary, background := false) -> bool:
	campaign.updated = Time.get_datetime_string_from_system(true)
	return write_json(campaign_path(campaign.id), campaign, background)


func load_campaign(id: String) -> Dictionary:
	return migrate_campaign(read_json(campaign_path(id)))


func list_campaigns() -> Array[Dictionary]:
	var found: Array[Dictionary] = []
	wait_for_writes()
	if not DirAccess.dir_exists_absolute(root.path_join("campaigns")):
		return found
	for id in DirAccess.get_directories_at(root.path_join("campaigns")):
		var c := load_campaign(id)
		if not c.is_empty():
			found.append(c)
	found.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a.get("updated", "") > b.get("updated", ""))
	return found


func delete_campaign(id: String) -> void:
	wait_for_writes()
	var dir := campaign_path(id).get_base_dir()
	_delete_with_backups(campaign_path(id))
	_delete_with_backups(thumbnail_path(id))
	DirAccess.remove_absolute(dir)


## Miniatura da campanha (lista de Carregar campanha), reduzida e gravada na thread.
func save_thumbnail(id: String, image: Image) -> void:
	if image == null or image.is_empty():
		return
	var thumb := image.duplicate() as Image
	thumb.resize(THUMB_SIZE.x, THUMB_SIZE.y, Image.INTERPOLATE_BILINEAR)
	_enqueue(thumbnail_path(id), thumb.save_png_to_buffer(), 0)


func load_thumbnail(id: String) -> Image:
	wait_for_writes()
	var path := thumbnail_path(id)
	if not FileAccess.file_exists(path):
		return null
	var image := Image.new()
	return image if image.load_png_from_buffer(FileAccess.get_file_as_bytes(path)) == OK else null


static func new_campaign() -> Dictionary:
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	return {"save_version": GameData.balance.save_version, "id": Items.new_uid(rng),
		"created": Time.get_datetime_string_from_system(true), "area": "prototype_arena",
		"dead_groups": [], "checkpoint": "start", "checkpoints_reached": [],
		"played_seconds": 0, "participants": [], "hero_names": {}}


# --- Espaços de save (11-saves.md, seção 3) ---------------------------------------

static func slot_limit(kind: String) -> int:
	var slots: Dictionary = GameData.balance.get("save_slots", {})
	return int(slots.get(kind, 12 if kind == "characters" else 6))


func can_create_character() -> bool:
	return list_characters().size() < slot_limit("characters")


func can_create_campaign() -> bool:
	return list_campaigns().size() < slot_limit("campaigns")


## Tempo de jogo como "h:mm" (lista de campanhas).
static func format_played(seconds: float) -> String:
	var minutes := int(seconds) / 60
	return "%d:%02d" % [minutes / 60, minutes % 60]


# --- Migração (11-saves.md: migrate_vN_to_vN+1) -----------------------------------

func migrate_character(d: Dictionary) -> Dictionary:
	# v1 é a primeira versão; as próximas entram aqui, uma função por versão.
	# Campos que entraram depois na v1 (Fase 4): personagens antigos ficam com Fogo.
	if not d.is_empty() and not d.has("element"):
		d.element = "fire"
	if not d.is_empty() and not d.has("element_potion"):
		d.element_potion = ""
	# Fase 5: habilidades. A básica do elemento vem no rank 1 e no atalho 1.
	if not d.is_empty() and not d.has("skills"):
		d.skills = {"element_1": 1}
		d.skill_slots = ["element_1", "", "", ""]
	return d


func migrate_campaign(d: Dictionary) -> Dictionary:
	if d.is_empty():
		return d
	# Campos que entraram depois na v1 (Fase 3): valores padrão.
	for key: String in ["checkpoints_reached", "participants", "dead_groups"]:
		if not d.has(key):
			d[key] = []
	if not d.has("hero_names"):
		d.hero_names = {}
	return d


# --- Escrita segura -------------------------------------------------------------

## Grava o dicionário como JSON. Com `background`, só monta o texto aqui e a
## thread grava (retorna true); sem, espera a fila e grava agora.
func write_json(path: String, data: Dictionary, background := false) -> bool:
	var bytes := JSON.stringify(data, "\t").to_utf8_buffer()
	if background:
		_enqueue(path, bytes, BACKUPS)
		return true
	wait_for_writes()
	saving.emit(true)
	var ok := _write_bytes(path, bytes, BACKUPS)
	saving.emit(false)
	return ok


## Espera a thread gravar tudo o que está na fila.
func wait_for_writes() -> void:
	while true:
		_mutex.lock()
		var busy := _busy
		_mutex.unlock()
		if busy == 0:
			return
		OS.delay_msec(1)


func read_json(path: String) -> Dictionary:
	wait_for_writes()
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


func _enqueue(path: String, bytes: PackedByteArray, backups: int) -> void:
	_mutex.lock()
	var replaced := false
	# Uma gravação do mesmo arquivo ainda na fila é trocada pela mais nova.
	for job: Array in _queue:
		if job[0] == path:
			job[1] = bytes
			replaced = true
	if not replaced:
		_queue.append([path, bytes, backups])
		_busy += 1
	_mutex.unlock()
	if not replaced:
		saving.emit(true)
		_semaphore.post()


func _worker() -> void:
	while true:
		_semaphore.wait()
		_mutex.lock()
		if _queue.is_empty():
			var stop := _quit
			_mutex.unlock()
			if stop:
				return
			continue
		var job: Array = _queue.pop_front()
		_mutex.unlock()
		_write_bytes(job[0], job[1], job[2])
		_mutex.lock()
		_busy -= 1
		var idle := _busy == 0
		_mutex.unlock()
		if idle:
			saving.emit.call_deferred(false)


## Temporário + renomear; gira os backups (.bak2 -> .bak3, .bak1 -> .bak2,
## principal -> .bak1). Roda na thread ou na cena principal (nunca as duas juntas).
func _write_bytes(path: String, bytes: PackedByteArray, backups: int) -> bool:
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var tmp := path + ".tmp"
	var file := FileAccess.open(tmp, FileAccess.WRITE)
	if file == null:
		push_error("Não foi possível gravar %s" % tmp)
		return false
	file.store_buffer(bytes)
	file.close()
	for i in range(backups - 1, 0, -1):
		var older := "%s.bak%d" % [path, i]
		if FileAccess.file_exists(older):
			DirAccess.rename_absolute(older, "%s.bak%d" % [path, i + 1])
	if FileAccess.file_exists(path):
		if backups > 0:
			DirAccess.rename_absolute(path, path + ".bak1")
		else:
			DirAccess.remove_absolute(path)
	return DirAccess.rename_absolute(tmp, path) == OK


func _delete_with_backups(path: String) -> void:
	for candidate in [path, path + ".tmp"] + range(1, BACKUPS + 1).map(func(i: int) -> String: return "%s.bak%d" % [path, i]):
		if FileAccess.file_exists(candidate):
			DirAccess.remove_absolute(candidate)
