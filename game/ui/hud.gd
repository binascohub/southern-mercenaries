# Southern Mercenaries — GPL-3.0-or-later
class_name Hud
extends CanvasLayer
## HUD (09-interface.md, seção 3): vida, recurso, esquiva, poções, XP e nível,
## ouro, encontros vencidos, aliados, avisos curtos e "salvando…", com dicas de
## botões que acompanham o dispositivo em uso. Todo texto vem de chaves de tradução.

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
var _xp_bar: ProgressBar
var _xp_label: Label
var _gold_label: Label
var _element_label: Label
var _potions: Label
var _toasts: VBoxContainer
var _saving: Label
const TOAST_TIME := 3.0


func _ready() -> void:
	_build()
	InputDevice.device_changed.connect(func(_pad: bool) -> void: _refresh_texts())
	Controls.bindings_changed.connect(_refresh_texts)
	Settings.changed.connect(_refresh_texts)
	SaveSystem.saving.connect(func(active: bool) -> void:
		if active:
			_saving.visible = true
			_saving.modulate.a = 1.0
			var tween := create_tween()
			tween.tween_interval(0.8)
			tween.tween_property(_saving, "modulate:a", 0.0, 0.4)
			tween.tween_callback(func() -> void: _saving.visible = false))
	_refresh_texts()


func bind_player(player: Player) -> void:
	_player = player
	player.health_changed.connect(_on_health)
	player.resource_changed.connect(_on_resource)
	_on_health(player.health, player.max_health)
	_on_resource(player.resource, player.max_resource)
	_resource_bar.tooltip_text = player.data.resource_key
	player.character_changed.connect(_on_character)
	if player.character:
		_on_character(0)


## Aviso curto no topo (subiu de nível, bolsa cheia…), some sozinho.
func toast(text: String) -> void:
	var label := _label(22)
	label.text = text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_toasts.add_child(label)
	var tween := label.create_tween()
	tween.tween_interval(TOAST_TIME)
	tween.tween_property(label, "modulate:a", 0.0, 0.5)
	tween.tween_callback(label.queue_free)


func _on_character(levels: int) -> void:
	if levels > 0:
		toast(tr("TOAST_LEVEL_UP").format({"level": _player.level}))
	_refresh_character()


func _refresh_character() -> void:
	if _player == null or _player.character == null:
		return
	var c := _player.character
	var needed := CharacterData.xp_to_next(int(c.data.level))
	_xp_bar.max_value = needed
	_xp_bar.value = int(c.data.xp)
	_xp_label.text = tr("HUD_LEVEL_XP").format({"level": c.data.level, "xp": c.data.xp, "next": needed})
	_gold_label.text = tr("HUD_GOLD").format({"gold": c.data.gold})
	# Elemento em uso; com Poção Elemental ativa, avisa que é temporário.
	var element := c.current_element()
	_element_label.text = tr("HUD_ELEMENT").format({"element": tr(Elements.data(element).name_key)}) \
		+ (" " + tr("HUD_ELEMENT_POTION") if c.data.get("element_potion", "") != "" else "")
	_element_label.add_theme_color_override("font_color", Elements.color(element))


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
	if _player.character:
		var c := _player.character
		var cooldown := ""
		if _player.potion_cooldown > 0.0:
			cooldown = "  (%.0fs)" % ceilf(_player.potion_cooldown)
		_potions.text = tr("HUD_POTIONS").format({
			"health_key": InputDevice.prompt(&"potion_health"), "health": c.count_of("potion_health"),
			"resource_key": InputDevice.prompt(&"potion_mana"), "resource": c.count_of("potion_resource"),
		}) + cooldown
		var elemental := 0
		for id in Elements.ALL:
			elemental += c.count_of("elemental_potion_" + id)
		if elemental > 0:
			_potions.text += "   " + tr("HUD_POTION_ELEMENTAL").format({
				"key": InputDevice.prompt(&"potion_elemental"), "count": elemental})


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
	_refresh_character()
	_saving.text = tr("HUD_SAVING")
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

	_potions = _label(18)
	bars.add_child(_potions)
	_gold_label = _label(18)
	_gold_label.add_theme_color_override("font_color", Color(1.0, 0.85, 0.35))
	bars.add_child(_gold_label)
	_element_label = _label(18)
	bars.add_child(_element_label)

	# Faixa de XP na base da tela.
	var xp_box := VBoxContainer.new()
	xp_box.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	xp_box.offset_top = -30
	xp_box.offset_left = 24
	xp_box.offset_right = -24
	xp_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(xp_box)
	_xp_bar = ProgressBar.new()
	_xp_bar.show_percentage = false
	_xp_bar.custom_minimum_size = Vector2(0, 8)
	var xp_fill := StyleBoxFlat.new()
	xp_fill.bg_color = Color(0.85, 0.7, 0.25)
	_xp_bar.add_theme_stylebox_override("fill", xp_fill)
	var xp_bg := StyleBoxFlat.new()
	xp_bg.bg_color = Color(0, 0, 0, 0.55)
	_xp_bar.add_theme_stylebox_override("background", xp_bg)
	xp_box.add_child(_xp_bar)
	_xp_label = _label(14)
	_xp_label.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	_xp_label.position = Vector2(24, -52)
	root.add_child(_xp_label)

	_toasts = VBoxContainer.new()
	_toasts.set_anchors_preset(Control.PRESET_CENTER_TOP)
	_toasts.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_toasts.position.y = 90
	_toasts.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(_toasts)

	_saving = _label(16)
	_saving.text = tr("HUD_SAVING")
	_saving.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	_saving.position = Vector2(-140, -60)
	_saving.visible = false
	root.add_child(_saving)

	_hints = _label(16)
	_hints.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_hints.offset_top = -64
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
