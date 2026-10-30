# Southern Mercenaries — GPL-3.0-or-later
class_name Hud
extends CanvasLayer
## HUD mínimo da Fase 1: vida, recurso, esquiva, onda e dicas de botões que
## acompanham o dispositivo em uso. Todo texto vem de chaves de tradução.

var _player: Player
var _health_bar: ProgressBar
var _health_label: Label
var _resource_bar: ProgressBar
var _resource_label: Label
var _evade_label: Label
var _wave_label: Label
var _enemies_label: Label
var _hints: Label
var _banner: Label
var _banner_sub: Label
var _gamepad_lost: PanelContainer
var _wave := [0, 0, 0]
var _banner_kind := ""


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


func set_wave(current: int, total: int, enemies: int) -> void:
	_wave = [current, total, enemies]
	_refresh_texts()


func show_victory() -> void:
	_banner_kind = "victory"
	_refresh_texts()


func show_defeat() -> void:
	_banner_kind = "defeat"
	_refresh_texts()


func show_gamepad_lost(value: bool) -> void:
	_gamepad_lost.visible = value


func is_gamepad_lost_visible() -> bool:
	return _gamepad_lost.visible


func _process(_delta: float) -> void:
	if _player == null:
		return
	var cd := _player.evade_cooldown_left()
	_evade_label.text = tr("HUD_EVADE_READY") if cd <= 0.0 \
		else tr("HUD_EVADE_COOLDOWN").format({"seconds": "%.1f" % cd})


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
	_wave_label.text = tr("HUD_WAVE").format({"current": _wave[0], "total": _wave[1]})
	_enemies_label.text = tr("HUD_ENEMIES_LEFT").format({"count": _wave[2]})
	_hints.text = tr("HUD_HINTS").format({
		"attack": InputDevice.prompt(&"attack"),
		"evade": InputDevice.prompt(&"evade"),
		"menu": InputDevice.prompt(&"menu"),
	})
	_banner.visible = _banner_kind != ""
	_banner_sub.visible = _banner.visible
	if _banner_kind == "victory":
		_banner.text = tr("HUD_VICTORY")
	elif _banner_kind == "defeat":
		_banner.text = tr("HUD_DEFEAT")
	_banner_sub.text = tr("HUD_PRESS_TO_RESTART").format({"action": InputDevice.prompt(&"attack")})


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

	var wave_box := VBoxContainer.new()
	wave_box.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	wave_box.position = Vector2(-260, 20)
	wave_box.custom_minimum_size = Vector2(236, 0)
	root.add_child(wave_box)
	_wave_label = _label(22)
	_wave_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	wave_box.add_child(_wave_label)
	_enemies_label = _label(18)
	_enemies_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	wave_box.add_child(_enemies_label)

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
