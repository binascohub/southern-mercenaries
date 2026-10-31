# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Dicas do tutorial (14-tutorial.md, seções 4 e 7). Lê data/tips.json; quando um
## evento do jogo acontece (notify), a dica ligada a ele entra na fila e aparece
## uma vez por personagem, uma por vez (a de maior prioridade primeiro), sem
## pausar o jogo. Vista = guardada em tutorial_seen no personagem (o servidor
## grava; até lá a lista local evita repetir). Desliga em Opções (Settings.tips).

signal tip_shown(id: String, text: String)
signal tip_hidden
## Dica mostrada: o PC avisa o servidor para guardar no personagem.
signal seen(id: String)

var _queue: Array[String] = []
var _current := ""
var _timer := 0.0
var _seen_here := {}


func _ready() -> void:
	Settings.changed.connect(func() -> void:
		if not Settings.tips:
			_queue.clear()
			_hide())


func _process(delta: float) -> void:
	if _current == "":
		return
	_timer -= delta
	if _timer <= 0.0:
		_hide()
		_next()


## Um evento do jogo aconteceu ("start", "enemy_near"…); class_id filtra as dicas de classe.
func notify(event: String, class_id := "") -> void:
	if not Settings.tips:
		return
	var tips: Dictionary = GameData.tips.tips
	for id: String in tips:
		var tip: Dictionary = tips[id]
		if tip.event != event or was_seen(id) or id in _queue or id == _current:
			continue
		if tip.has("class") and tip["class"] != class_id:
			continue
		_queue.append(id)
	_queue.sort_custom(func(a: String, b: String) -> bool:
		return int(tips[a].priority) > int(tips[b].priority))
	_next()


func was_seen(id: String) -> bool:
	if _seen_here.has(id):
		return true
	return Session.character != null and id in Session.character.data.get("tutorial_seen", [])


func current() -> String:
	return _current


## Texto da dica com os botões do dispositivo em uso.
func text(id: String) -> String:
	var tip: Dictionary = GameData.tips.tips.get(id, {})
	if tip.is_empty():
		return ""
	if InputDevice.using_gamepad and tip.has("key_pad"):
		return tr(tip.key_pad)
	var args := {}
	var actions: Array = tip.get("actions", [])
	if tip.get("join", false):
		args.button = "/".join(PackedStringArray(actions.map(func(a: String) -> String:
			return InputDevice.prompt(StringName(a)))))
	else:
		for i in actions.size():
			args["button" if i == 0 else "button%d" % (i + 1)] = InputDevice.prompt(StringName(actions[i]))
	return tr(tip.key).format(args)


## Dicas já vistas, na ordem de data/tips.json (menu de ajuda no diário).
func seen_tips() -> Array[String]:
	var ids: Array[String] = []
	for id: String in GameData.tips.tips:
		if was_seen(id):
			ids.append(id)
	return ids


## Nova partida: esquece a fila (o que foi visto fica no personagem).
func reset() -> void:
	_queue.clear()
	_seen_here.clear()
	_hide()


func _next() -> void:
	while _current == "" and not _queue.is_empty():
		var id: String = _queue.pop_front()
		if was_seen(id):
			continue
		_current = id
		_seen_here[id] = true
		_timer = float(GameData.tips.get("duration", 7.0))
		tip_shown.emit(id, text(id))
		seen.emit(id)


func _hide() -> void:
	if _current != "":
		_current = ""
		tip_hidden.emit()
