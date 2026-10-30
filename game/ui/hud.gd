# Southern Mercenaries — GPL-3.0-or-later
class_name Hud
extends CanvasLayer
## HUD: vida, recurso, esquiva, encontros vencidos, aliados e dicas de botões que acompanham
## o dispositivo em uso. Todo texto vem de chaves de tradução.

## Valores de Result da arena (NONE, VICTORY, DEFEAT).
const RESULT_NONE := 0
const RESULT_VICTORY := 1
const RESULT_DEFEAT := 2

var _player: Player
var _health_bar: ProgressBar
var _health_label: Label
var _resource_bar: ProgressBar
var _resource_label: Label
var _evade_label: Label
var _progress_label: Label
var _hints: Label
var _banner: Label
var _banner_sub: Label
var _gamepad_lost: PanelContainer
var _allies: Label
var _hosting: Label
var _progress := [0, 0]
var _result := 0
var _connecting := false
var _local_alive := true


func _ready() -> void:
	_build()
	InputDevice.device_changed.connect(func(_pad: bool) -> void: _refresh_texts())
	Controls.bindings_changed.connect(_refresh_texts)
	Settings.changed.connect(_refresh_texts)
	_refresh_texts()


func bind_player(player: Player) -> void:
	_player = player
	player.health_changed.connect(_on_health)
	player.resource_changed.connect(_on_resource)
	_on_health(player.health, player.max_health)
	_on_resource(player.resource, player.max_resource)
	_resource_bar.tooltip_text = player.data.resource_key


func set_progress(cleared: int, total: int) -> void:
	_progress = [cleared, total]
	_refresh_texts()


func show_result(result: int) -> void:
	_result = result
	_refresh_texts()


## Mostra os IPs deste PC para quem quiser entrar pelo endereço.
func show_hosting(addresses: Array[String]) -> void:
	var address := ", ".join(addresses) if not addresses.is_empty() else "127.0.0.1"
	_hosting.text = tr("HUD_HOSTING").format({"address": address, "port": NetworkManager.game_port})


func show_connecting(value: bool) -> void:
	_connecting = value
	_refresh_texts()


func show_gamepad_lost(value: bool) -> void:
	_gamepad_lost.visible = value


func is_gamepad_lost_visible() -> bool:
	return _gamepad_lost.visible


func _process(_delta: float) -> void:
	if _player == null or not is_instance_valid(_player):
		return
	var cd := _player.evade_cooldown_left()
	_evade_label.text = tr("HUD_EVADE_READY") if cd <= 0.0 \
		else tr("HUD_EVADE_COOLDOWN").format({"seconds": "%.1f" % cd})
	var lines: Array[String] = []
	var revive_nearby := false
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p == _player:
			continue
		var status := "%d / %d" % [ceili(p.health), roundi(p.max_health)] if p.alive else tr("HUD_ALLY_DOWN")
		lines.append("%s: %s" % [tr("HUD_PLAYER_N").format({"n": p.slot + 1}), status])
		if not p.alive and _player.alive \
				and p.global_position.distance_to(_player.global_position) <= GameData.balance.revive_range:
			revive_nearby = true
	_allies.text = "\n".join(lines)
	var hints := tr("HUD_HINTS").format({
		"attack": InputDevice.prompt(&"attack"),
		"evade": InputDevice.prompt(&"evade"),
		"menu": InputDevice.prompt(&"menu"),
	})
	if revive_nearby:
		hints = tr("HUD_HOLD_TO_REVIVE").format({"action": InputDevice.prompt(&"interact")})
	_hints.text = hints
	if _player.alive != _local_alive:
		_local_alive = _player.alive
		_refresh_texts()


func _on_health(current: float, maximum: float) -> void:
	_health_bar.max_value = maximum
	_health_bar.value = current
	_health_label.text = "%d / %d" % [ceili(current), roundi(maximum)]


func _on_resource(current: float, maximum: float) -> void:
	_resource_bar.max_value = maximum
	_resource_bar.value = current
	_resource_label.text = "%d / %d" % [floori(current), roundi(maximum)]


func _notification(what: int) -> void:
	if what == NOTIFICATION_TRANSLATION_CHANGED and is_node_ready():
		_refresh_texts()


func _refresh_texts() -> void:
	_progress_label.text = tr("HUD_ENCOUNTERS").format({"cleared": _progress[0], "total": _progress[1]})
	var title := ""
	var sub := ""
	if _connecting:
		title = tr("NET_CONNECTING")
	elif _result == RESULT_VICTORY:
		title = tr("HUD_VICTORY")
		sub = tr("HUD_PRESS_TO_RESTART").format({"action": InputDevice.prompt(&"attack")})
	elif _result == RESULT_DEFEAT:
		title = tr("HUD_DEFEAT")
		sub = tr("HUD_RETURNING_TO_CHECKPOINT")
	elif _player and is_instance_valid(_player) and not _player.alive:
		title = tr("HUD_DOWNED")
		sub = tr("HUD_WAIT_FOR_REVIVE")
	_banner.text = title
	_banner_sub.text = sub
	_banner.visible = title != ""
	_banner_sub.visible = sub != ""


func _build() -> void:
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)

	var bars := VBoxContainer.new()
	bars.position = Vector2(24, 20)
	bars.custom_minimum_size = Vector2(300, 0)
	root.add_child(bars)
	var health := _bar(Color(0.75, 0.15, 0.15))
	_health_bar = health[0]
	_health_label = health[1]
	bars.add_child(health[2])
	var res := _bar(Color(0.2, 0.4, 0.9))
	_resource_bar = res[0]
	_resource_label = res[1]
	bars.add_child(res[2])
	_evade_label = _label(18)
	bars.add_child(_evade_label)
	_allies = _label(16)
	bars.add_child(_allies)

	var info_box := VBoxContainer.new()
	info_box.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	info_box.position = Vector2(-260, 20)
	info_box.custom_minimum_size = Vector2(236, 0)
	root.add_child(info_box)
	_progress_label = _label(20)
	_progress_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	info_box.add_child(_progress_label)
	_hosting = _label(14)
	_hosting.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_hosting.modulate = Color(1, 1, 1, 0.6)
	info_box.add_child(_hosting)

	_hints = _label(16)
	_hints.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_hints.offset_top = -40
	_hints.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hints.modulate = Color(1, 1, 1, 0.75)
	root.add_child(_hints)

	var center := VBoxContainer.new()
	center.set_anchors_preset(Control.PRESET_CENTER)
	center.grow_horizontal = Control.GROW_DIRECTION_BOTH
	center.grow_vertical = Control.GROW_DIRECTION_BOTH
	root.add_child(center)
	_banner = _label(48)
	_banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	center.add_child(_banner)
	_banner_sub = _label(20)
	_banner_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	center.add_child(_banner_sub)

	_gamepad_lost = PanelContainer.new()
	_gamepad_lost.set_anchors_preset(Control.PRESET_CENTER)
	_gamepad_lost.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_gamepad_lost.grow_vertical = Control.GROW_DIRECTION_BOTH
	_gamepad_lost.visible = false
	var lost := Label.new()
	lost.text = "HUD_GAMEPAD_LOST"
	lost.add_theme_font_size_override("font_size", 24)
	_gamepad_lost.add_child(lost)
	root.add_child(_gamepad_lost)
	process_mode = Node.PROCESS_MODE_ALWAYS


func _bar(color: Color) -> Array:
	var holder := Control.new()
	holder.custom_minimum_size = Vector2(300, 26)
	var bar := ProgressBar.new()
	bar.set_anchors_preset(Control.PRESET_FULL_RECT)
	bar.show_percentage = false
	var fill := StyleBoxFlat.new()
	fill.bg_color = color
	bar.add_theme_stylebox_override("fill", fill)
	var bg := StyleBoxFlat.new()
	bg.bg_color = Color(0, 0, 0, 0.55)
	bar.add_theme_stylebox_override("background", bg)
	holder.add_child(bar)
	var label := _label(16)
	label.set_anchors_preset(Control.PRESET_FULL_RECT)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	holder.add_child(label)
	return [bar, label, holder]


## Rótulo cujo texto é montado por código (já traduzido com tr()).
func _label(font_size: int) -> Label:
	var label := Label.new()
	label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_constant_override("outline_size", 6)
	label.add_theme_color_override("font_outline_color", Color.BLACK)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label
