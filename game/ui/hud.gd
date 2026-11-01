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
## Fase 6: área, missão ativa (diário) e aviso de interagir.
var _area_name := ""
var _quest_id := ""
var _quest_label: Label
var _prompt: Label
var _training_label: Label
var _result := 0
## Área de teste: a vitória pede "ataque para recomeçar"; nos mapas, o título
## da vitória (victory_key) aparece e some sozinho.
var _replayable := true
var _victory_key := "HUD_VICTORY"
var _victory_shown := false
var _connecting := false
var _local_alive := true
var _xp_bar: ProgressBar
var _xp_label: Label
var _gold_label: Label
var _element_label: Label
## Barra de habilidades (09-interface.md, seção 3): 4 atalhos com tecla, nome,
## recarga e cinza quando falta mana.
var _skill_slots: Array[Label] = []
var _potions: Label
var _toasts: VBoxContainer
var _saving: Label
## Minimapa com névoa (09-interface.md, seção 3); `map` amplia.
var minimap: Minimap
## Barra do chefe (09-interface.md): nome, fase e vida, no alto, enquanto ele luta.
var _boss_box: VBoxContainer
var _boss_name: Label
var _boss_bar: ProgressBar
## Balão da dica do tutorial (14-tutorial.md, seção 4): até 2 linhas, sem pausar.
var _tip: PanelContainer
## Aviso ao entrar numa área de mapa: os monstros dela e o elemento de cada um.
var _foes: PanelContainer
var _foes_list: VBoxContainer
var _foes_tween: Tween
var _tip_label: Label
var _tip_id := ""
const TOAST_TIME := 3.0


func _ready() -> void:
	_build()
	# Métodos (e não funções anônimas) nos sinais globais, que seguem disparando depois que
	# o HUD é liberado (trocar de cena); as conexões se desfazem sozinhas com o nó.
	InputDevice.device_changed.connect(_on_device_changed)
	Controls.bindings_changed.connect(_refresh_texts)
	Settings.changed.connect(_refresh_texts)
	SaveSystem.saving.connect(_on_saving)
	TipManager.tip_shown.connect(_on_tip_shown)
	TipManager.tip_hidden.connect(_on_tip_hidden)
	_refresh_texts()


func _on_device_changed(_pad: bool) -> void:
	_refresh_texts()


func _on_saving(active: bool) -> void:
	if not active:
		return
	_saving.visible = true
	_saving.modulate.a = 1.0
	var tween := create_tween()
	tween.tween_interval(0.8)
	tween.tween_property(_saving, "modulate:a", 0.0, 0.4)
	tween.tween_callback(_hide_saving)


func _hide_saving() -> void:
	_saving.visible = false


func _on_tip_hidden() -> void:
	_tip_id = ""
	_tip.visible = false


func _on_tip_shown(id: String, text: String) -> void:
	_tip_id = id
	_tip_label.text = text
	_tip.visible = true
	_tip.modulate.a = 0.0
	_tip.create_tween().tween_property(_tip, "modulate:a", 1.0, 0.25)


## Monstros da área que o grupo acabou de entrar ({nome, elemento}); some sozinho.
func show_area_foes(foes: Array) -> void:
	for child in _foes_list.get_children():
		child.queue_free()
	if foes.is_empty():
		_foes.visible = false
		return
	var title := _label(18)
	title.text = tr("HUD_AREA_FOES")
	title.add_theme_color_override("font_color", UiTheme.INK)
	title.add_theme_constant_override("outline_size", 0)
	_foes_list.add_child(title)
	for foe: Dictionary in foes:
		var line := _label(16)
		line.add_theme_constant_override("outline_size", 0)
		var element: String = foe.get("element", "")
		if element != "":
			line.text = "%s — %s" % [tr(foe.name_key), tr("ELEMENT_" + element.to_upper())]
			line.add_theme_color_override("font_color", Elements.color(element).darkened(0.35))
		else:
			line.text = tr(foe.name_key)
			line.add_theme_color_override("font_color", UiTheme.INK)
		_foes_list.add_child(line)
	_foes.visible = true
	_foes.modulate.a = 0.0
	if _foes_tween:
		_foes_tween.kill()
	_foes_tween = _foes.create_tween()
	_foes_tween.tween_property(_foes, "modulate:a", 1.0, 0.3)
	_foes_tween.tween_interval(8.0)
	_foes_tween.tween_property(_foes, "modulate:a", 0.0, 0.8)
	_foes_tween.tween_callback(func() -> void: _foes.visible = false)


## Monstros listados agora no aviso da área (testes).
func area_foes_shown() -> int:
	return maxi(_foes_list.get_child_count() - 1, 0) if _foes.visible else 0


## Chefe acordado (null esconde a barra).
func set_boss(boss: Enemy) -> void:
	_boss_box.visible = boss != null
	if boss == null:
		return
	var phase_keys: Array = boss.data.get("phase_keys", [])
	var title := tr(boss.data.get("name_key", ""))
	if boss.phase > 0 and boss.phase <= phase_keys.size():
		title += "  —  " + tr(phase_keys[boss.phase - 1])
	_boss_name.text = title
	_boss_bar.max_value = boss.max_health
	_boss_bar.value = boss.health


func boss_visible() -> bool:
	return _boss_box.visible


func tip_text() -> String:
	return _tip_label.text if _tip.visible else ""


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


func set_area(area_name: String) -> void:
	_area_name = area_name
	_refresh_texts()


func set_quest(quest_id: String) -> void:
	_quest_id = quest_id
	_refresh_texts()


## "[G] Taverna": objeto ao alcance para interagir ("" esconde).
func set_interact_prompt(target: String) -> void:
	_prompt.visible = target != ""
	if target != "":
		_prompt.text = tr("HUD_INTERACT").format({"action": InputDevice.prompt(&"interact"), "target": target})


## Painel de treino ({} esconde): mostrado só dentro do pátio.
func set_training(stats: Dictionary) -> void:
	_training_label.visible = not stats.is_empty()
	if stats.is_empty():
		return
	_training_label.text = tr("HUD_TRAINING").format({
		"total": roundi(float(stats.get("total", 0.0))),
		"dps": "%.1f" % Town.training_dps(stats),
		"biggest": roundi(float(stats.get("biggest", 0.0))),
		"crits": int(stats.get("crits", 0)),
		"hits": int(stats.get("hits", 0)),
	})


func set_progress(cleared: int, total: int) -> void:
	_progress = [cleared, total]
	_refresh_texts()


func set_replayable(replayable: bool, victory_key: String) -> void:
	_replayable = replayable
	_victory_key = victory_key


func show_result(result: int) -> void:
	var newly_won := result == RESULT_VICTORY and _result != RESULT_VICTORY
	_result = result
	_victory_shown = newly_won or (result == RESULT_VICTORY and _replayable)
	if newly_won and not _replayable:
		get_tree().create_timer(6.0, false).timeout.connect(func() -> void:
			_victory_shown = false
			_refresh_texts())
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


func _update_skill_bar() -> void:
	var c := _player.character
	for i in _skill_slots.size():
		var label := _skill_slots[i]
		var prompt := InputDevice.prompt(StringName("skill_%d" % (i + 1)))
		var key: String = c.data.skill_slots[i] if c else ""
		if key == "":
			label.text = "%s\n—" % prompt
			label.modulate = Color(1, 1, 1, 0.45)
			continue
		var skill := Skills.def(c.skill_of(key))
		var cd := _player.skill_cooldown_left(key)
		var text := "%s\n%s" % [prompt, tr(skill.get("name_key", ""))]
		if cd > 0.0:
			text += "\n%.0fs" % ceilf(cd)
		label.text = text
		var ready := cd <= 0.0 and _player.resource >= float(skill.get("cost", 0.0))
		label.modulate = Color.WHITE if ready else Color(0.55, 0.55, 0.55)


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
	_update_skill_bar()
	if _player.shield > 0.0:
		_health_label.text = "%d / %d  (+%d)" % [ceili(_player.health), roundi(_player.max_health), ceili(_player.shield)]
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
	if _tip_id != "":
		_tip_label.text = TipManager.text(_tip_id)  # o botão segue o dispositivo
	# Na cidade (sem encontros) mostra só o nome da área.
	_progress_label.text = tr("HUD_ENCOUNTERS").format({"cleared": _progress[0], "total": _progress[1]}) \
		if _progress[1] > 0 else _area_name
	if _quest_id != "":
		var quest: Dictionary = GameData.quests.get(_quest_id, {})
		var target: String = quest.get("target_element", "")
		_quest_label.text = tr("HUD_QUEST").format({"quest": tr(quest.get("name_key", "")),
			"weak": tr(Elements.data(Elements.weakness_of(target)).get("name_key", "")) if target != "" else ""})
	_quest_label.visible = _quest_id != ""
	var title := ""
	var sub := ""
	if _connecting:
		title = tr("NET_CONNECTING")
	elif _result == RESULT_VICTORY and _victory_shown:
		title = tr(_victory_key)
		sub = tr("HUD_PRESS_TO_RESTART").format({"action": InputDevice.prompt(&"attack")}) if _replayable \
			else tr("HUD_VICTORY_TREASURE")
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
	# Cresce para a esquerda: nomes longos (área, missão) não saem da tela.
	# Fica embaixo do minimapa (09-interface.md, seção 3).
	info_box.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	info_box.offset_left = -260
	info_box.offset_right = -24
	info_box.offset_top = 16 + Minimap.SMALL.y + 8
	info_box.custom_minimum_size = Vector2(236, 0)
	root.add_child(info_box)
	_progress_label = _label(20)
	_progress_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	info_box.add_child(_progress_label)
	_quest_label = _label(16)
	_quest_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_quest_label.add_theme_color_override("font_color", Color(1.0, 0.85, 0.45))
	_quest_label.visible = false
	info_box.add_child(_quest_label)
	_prompt = _label(20)
	_prompt.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	_prompt.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_prompt.offset_top = -190
	_prompt.offset_bottom = -160
	_prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_prompt.visible = false
	root.add_child(_prompt)
	# Painel de treino (pátio): dano total, DPS, maior golpe, críticos.
	_training_label = _label(18)
	_training_label.set_anchors_preset(Control.PRESET_CENTER_TOP)
	_training_label.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_training_label.offset_top = 24
	_training_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_training_label.add_theme_color_override("font_color", Color(0.85, 0.95, 1.0))
	_training_label.visible = false
	root.add_child(_training_label)
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

	var skill_bar := HBoxContainer.new()
	skill_bar.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	skill_bar.grow_horizontal = Control.GROW_DIRECTION_BOTH
	skill_bar.grow_vertical = Control.GROW_DIRECTION_BEGIN
	skill_bar.offset_bottom = -76
	skill_bar.add_theme_constant_override("separation", 8)
	skill_bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(skill_bar)
	for i in 4:
		var box := PanelContainer.new()
		box.theme_type_variation = &"HudPanel"
		box.custom_minimum_size = Vector2(112, 64)
		skill_bar.add_child(box)
		var slot_label := _label(14)
		slot_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		slot_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		slot_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		box.add_child(slot_label)
		_skill_slots.append(slot_label)

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
	_xp_bar.add_theme_stylebox_override("fill", UiTheme.bar_fill(Color(0.85, 0.7, 0.25)))
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

	minimap = Minimap.new()
	root.add_child(minimap)

	_boss_box = VBoxContainer.new()
	_boss_box.set_anchors_preset(Control.PRESET_CENTER_TOP)
	_boss_box.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_boss_box.offset_top = 16
	_boss_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_boss_name = _label(20)
	_boss_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_boss_name.add_theme_color_override("font_color", Color(1.0, 0.55, 0.45))
	_boss_box.add_child(_boss_name)
	_boss_bar = ProgressBar.new()
	_boss_bar.custom_minimum_size = Vector2(440, 18)
	_boss_bar.show_percentage = false
	_boss_bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_boss_bar.add_theme_stylebox_override("fill", UiTheme.bar_fill(Color(0.7, 0.1, 0.08)))
	_boss_box.add_child(_boss_bar)
	_boss_box.visible = false
	root.add_child(_boss_box)

	_foes = PanelContainer.new()
	_foes.set_anchors_preset(Control.PRESET_CENTER_LEFT)
	_foes.grow_vertical = Control.GROW_DIRECTION_BOTH
	_foes.offset_left = 24
	_foes.offset_right = 24
	_foes.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_foes.theme_type_variation = &"ParchmentPanel"
	_foes_list = VBoxContainer.new()
	_foes_list.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_foes.add_child(_foes_list)
	_foes.visible = false
	root.add_child(_foes)

	_tip = PanelContainer.new()
	_tip.set_anchors_preset(Control.PRESET_CENTER_RIGHT)
	_tip.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	_tip.grow_vertical = Control.GROW_DIRECTION_BOTH
	_tip.offset_right = -24
	_tip.offset_top = 60
	_tip.offset_bottom = 60
	_tip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_tip.theme_type_variation = &"ParchmentPanel"
	_tip_label = _label(17)
	# Tinta no pergaminho, sem o contorno dos textos do HUD.
	_tip_label.add_theme_color_override("font_color", UiTheme.INK)
	_tip_label.add_theme_constant_override("outline_size", 0)
	_tip_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_tip_label.custom_minimum_size = Vector2(320, 0)
	_tip.add_child(_tip_label)
	_tip.visible = false
	root.add_child(_tip)

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
	bar.add_theme_stylebox_override("fill", UiTheme.bar_fill(color))
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
