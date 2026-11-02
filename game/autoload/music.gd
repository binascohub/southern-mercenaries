extends Node
## Música de fundo (assets/audio/music/<nome>.wav ou .ogg, geradas por tools/assets/build_music.py), em laço, com troca suave entre faixas.
## "town" = cidade (e tela inicial), "tavern" = taverna, "tense" = mapas com monstros. Sem arquivo = silêncio.

const DIR := "res://assets/audio/music/"
const LEVEL_DB := -12.0
const FADE := 1.2

var current := ""
var _a := AudioStreamPlayer.new()
var _b := AudioStreamPlayer.new()
var _front: AudioStreamPlayer


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for p in [_a, _b]:
		p.volume_db = -80.0
		add_child(p)
	_front = _a


## Faixa de uma área: taverna e cidades tocam as alegres; as demais (com monstros), a tensa.
func track_for_area(area_id: String, is_town: bool) -> String:
	if area_id == "tavern":
		return "tavern"
	return "town" if is_town else "tense"


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
	for ext in ["wav", "ogg"]:
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
