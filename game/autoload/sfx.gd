extends Node
## Efeitos sonoros (assets/audio/sfx/<nome>.wav ou .ogg, gerados por tools/assets/build_sfx.py). Nome sem arquivo = silêncio, sem erro.
## `play` toca um som no mundo (com posição, some com a distância) ou na tela (sem posição); `voice` toca a fala de um NPC (uma por vez).

const DIR := "res://assets/audio/sfx/"
const POOL := 12
const MAX_DISTANCE := 38.0

var _cache: Dictionary = {}
var _world: Array[AudioStreamPlayer3D] = []
var _screen: Array[AudioStreamPlayer] = []
var _voice := AudioStreamPlayer.new()


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i in POOL:
		var p3 := AudioStreamPlayer3D.new()
		p3.max_distance = MAX_DISTANCE
		p3.unit_size = 9.0
		add_child(p3)
		_world.append(p3)
		var p2 := AudioStreamPlayer.new()
		add_child(p2)
		_screen.append(p2)
	add_child(_voice)


func _stream(sound: String) -> AudioStream:
	if not _cache.has(sound):
		var found: AudioStream = null
		for ext in ["wav", "ogg"]:
			var path := "%s%s.%s" % [DIR, sound, ext]
			if ResourceLoader.exists(path):
				found = load(path)
				break
		_cache[sound] = found
	return _cache[sound]


## `at` = Vector3.INF toca na tela (sons do próprio herói e da interface); com posição, toca ali no mundo.
func play(sound: String, at := Vector3.INF, volume_db := 0.0, pitch := 1.0) -> void:
	if DisplayServer.get_name() == "headless":
		return
	var stream := _stream(sound)
	if stream == null:
		return
	var scale := pitch * randf_range(0.94, 1.06)
	if at == Vector3.INF:
		for p in _screen:
			if not p.playing:
				p.stream = stream
				p.volume_db = volume_db
				p.pitch_scale = scale
				p.play()
				return
		return
	for p in _world:
		if not p.playing:
			p.stream = stream
			p.global_position = at
			p.volume_db = volume_db
			p.pitch_scale = scale
			p.play()
			return


## Fala de NPC: balbucio sem palavras. Cada NPC tem sempre a mesma voz (npc_talk_1 a 4, escolhida pelo nome).
func voice(speaker: String) -> void:
	if DisplayServer.get_name() == "headless":
		return
	var stream := _stream("npc_talk_%d" % (1 + absi(speaker.hash()) % 4))
	if stream == null:
		return
	_voice.stream = stream
	_voice.volume_db = -3.0
	_voice.pitch_scale = randf_range(0.97, 1.03)
	_voice.play()
