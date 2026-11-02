extends Node
## Música de fundo (assets/audio/music/<nome>.wav ou .ogg, geradas por tools/assets/build_music.py), em laço, com troca suave entre faixas.
## "town" = cidade (e tela inicial), "tavern" = taverna, "tense" = mapas com monstros. Sem arquivo = silêncio.

const DIR := "res://assets/audio/music/"
const LEVEL_DB := -12.0
const FADE := 1.2
## Som ambiente por cima da música (assets/audio/music/ambience_<nome>.ogg, em laço); sem arquivo, silêncio.
const AMBIENCE_DB := -9.0

var current := ""
var _a := AudioStreamPlayer.new()
var _b := AudioStreamPlayer.new()
var _front: AudioStreamPlayer
var ambience := ""
var _ambient := AudioStreamPlayer.new()


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for p in [_a, _b]:
		p.volume_db = -80.0
		add_child(p)
	_front = _a
	_ambient.volume_db = -80.0
	add_child(_ambient)


## Faixa de uma área: taverna e cidades tocam as alegres; as demais (com monstros), a tensa.
func track_for_area(area_id: String, is_town: bool) -> String:
	if area_id == "tavern":
		return "tavern"
	return "town" if is_town else "tense"


## Ambiente de uma área: o Esgoto (sewers_*) e o Cemitério (cemetery_*) têm o seu; as demais, nenhum ("").
func ambience_for_area(area_id: String) -> String:
	if area_id.begins_with("sewers_"):
		return "sewer"
	return "cemetery" if area_id.begins_with("cemetery_") else ""


func play_ambience(id: String) -> void:
	if id == ambience or DisplayServer.get_name() == "headless":
		return
	ambience = id
	var stream := _load("ambience_" + id) if id != "" else null
	if _ambient.playing:
		var out := create_tween()
		out.tween_property(_ambient, "volume_db", -80.0, FADE)
		out.tween_callback(_ambient.stop)
		if stream != null:
			out.tween_callback(func() -> void: _start_ambient(stream))
	elif stream != null:
		_start_ambient(stream)


func _start_ambient(stream: AudioStream) -> void:
	_ambient.stream = stream
	_ambient.volume_db = -80.0
	_ambient.play()
	create_tween().tween_property(_ambient, "volume_db", AMBIENCE_DB, FADE)


func play(track: String) -> void:
	if track == current or DisplayServer.get_name() == "headless":
		return
	current = track
	var stream := _load(track)
	var old := _front
	_front = _b if _front == _a else _a
	if stream != null:
		_front.stream = stream
		_front.volume_db = -80.0
		_front.play()
		create_tween().tween_property(_front, "volume_db", LEVEL_DB, FADE)
	if old.playing:
		var fade := create_tween()
		fade.tween_property(old, "volume_db", -80.0, FADE)
		fade.tween_callback(old.stop)


func _load(track: String) -> AudioStream:
	for ext in ["ogg", "wav"]:
		var path := "%s%s.%s" % [DIR, track, ext]
		if ResourceLoader.exists(path):
			var stream: AudioStream = load(path)
			if stream is AudioStreamWAV:
				stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
				stream.loop_begin = 0
				stream.loop_end = stream.data.size() / 2  # 16 bits, mono: uma amostra a cada 2 bytes
			elif stream is AudioStreamOggVorbis:
				stream.loop = true
			return stream
	return null
