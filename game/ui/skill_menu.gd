# Southern Mercenaries — GPL-3.0-or-later
class_name SkillMenu
extends CanvasLayer
## Janela de habilidades (09-interface.md, seção 4): as 10 habilidades da
## classe e do elemento em uso, nível em que liberam, rank (até 5), custo e
## recarga; "+" gasta um ponto de habilidade e 1–4 põem uma ativa num atalho.
## A descrição da habilidade em foco aparece embaixo. Os pedidos são validados
## no servidor. Funciona só com o controle e não pausa o jogo.

const ROW_NAME_WIDTH := 420

var _player: Player
var _panel: PanelContainer
var _points: Label
var _rows: VBoxContainer
var _details: Label
var _focused_key := ""
## chave -> {"label", "learn", "slots": [Button × 4]}
var _row_nodes := {}


func _ready() -> void:
	layer = 5
	_build()
	visible = false


func bind_player(player: Player) -> void:
	_player = player
	player.character_changed.connect(_on_character_changed)


## Ligado por método (não lambda): some junto com o menu quando a cena é desmontada.
func _on_character_changed(_levels: int) -> void:
	if visible:
		_refresh()

func toggle() -> void:
	if visible:
		close()
	elif _player and _player.character:
		visible = true
		Session.ui_open = true
		_rebuild_rows()
		_refresh()
		var first: Dictionary = _row_nodes.values()[0] if not _row_nodes.is_empty() else {}
		if not first.is_empty():
			first.learn.grab_focus.call_deferred()


func close() -> void:
	visible = false
	Session.ui_open = false
	var focus := _panel.get_viewport().gui_get_focus_owner()
	if focus:
		focus.release_focus()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"skills"):
		toggle()
		get_viewport().set_input_as_handled()
	elif visible and (event.is_action_pressed(&"ui_cancel") or event.is_action_pressed(&"menu")):
		close()
		get_viewport().set_input_as_handled()


func _notification(what: int) -> void:
	if what == NOTIFICATION_TRANSLATION_CHANGED and is_node_ready() and visible:
		_refresh()


# --- Conteúdo ---------------------------------------------------------------------

func _rebuild_rows() -> void:
	MenuPanel.clear(_rows)
	_row_nodes.clear()
	for key in Skills.keys(_player.character.data.class_id):
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 6)
		_rows.add_child(row)
		var label := Label.new()
		label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		label.custom_minimum_size = Vector2(ROW_NAME_WIDTH, 0)
		row.add_child(label)
		var learn := Button.new()
		learn.text = "+"
		learn.custom_minimum_size = Vector2(44, 36)
		learn.pressed.connect(func() -> void: _player.request_learn(key))
		learn.focus_entered.connect(_focus.bind(key))
		row.add_child(learn)
		var slots: Array[Button] = []
		for i in 4:
			var slot := Button.new()
			slot.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
			slot.text = str(i + 1)
			slot.toggle_mode = false
			slot.custom_minimum_size = Vector2(40, 36)
			slot.pressed.connect(func() -> void: _player.request_slot(i, key))
			slot.focus_entered.connect(_focus.bind(key))
			row.add_child(slot)
			slots.append(slot)
		_row_nodes[key] = {"label": label, "learn": learn, "slots": slots}


func _refresh() -> void:
	if _player == null or _player.character == null:
		return
	var c := _player.character
	_points.text = tr("SKILLS_POINTS").format({"points": int(c.data.get("skill_points", 0)),
		"element": tr(Elements.data(c.current_element()).name_key)})
	for key: String in _row_nodes:
		var nodes: Dictionary = _row_nodes[key]
		var skill := Skills.def(c.skill_of(key))
		var rank := c.skill_rank(key)
		var level := Skills.unlock_level(c.data.class_id, key)
		var line := tr("SKILLS_ROW").format({"name": tr(skill.get("name_key", "")), "level": level,
			"rank": rank, "max": Skills.max_rank()})
		if skill.get("kind", "") == "passive":
			line += "  " + tr("SKILLS_PASSIVE")
		var label: Label = nodes.label
		label.text = line
		label.modulate = Color.WHITE if rank > 0 else (Color(0.75, 0.75, 0.75) if level <= int(c.data.level) else Color(0.45, 0.45, 0.45))
		var learn: Button = nodes.learn
		learn.disabled = not c.can_learn(key)
		var active := Skills.is_active(c.skill_of(key)) and rank > 0
		for i in 4:
			var slot: Button = nodes.slots[i]
			slot.visible = active
			slot.modulate = Color(1.0, 0.85, 0.4) if c.data.skill_slots[i] == key else Color.WHITE
	_show_details()


func _focus(key: String) -> void:
	_focused_key = key
	_show_details()


func _show_details() -> void:
	if _focused_key == "" or _player == null or _player.character == null:
		_details.text = ""
		return
	var c := _player.character
	var skill := Skills.def(c.skill_of(_focused_key))
	var rank := maxi(c.skill_rank(_focused_key), 1)
	var lines := PackedStringArray([tr(skill.get("name_key", "")), tr(skill.get("desc_key", ""))])
	if skill.get("kind", "") == "active":
		lines.append(tr("SKILLS_COST").format({"cost": int(skill.get("cost", 0)),
			"resource": tr(c.class_data().resource_key),
			"cooldown": "%.0f" % Skills.cooldown(skill, rank)}))
	if skill.has("power") and float(skill.power) > 0.0:
		lines.append(tr("SKILLS_POWER").format({"percent": roundi(Skills.power(skill, rank) * 100.0),
			"power": tr(c.class_data().power_key), "rank": rank}))
	_details.text = "\n".join(lines)


# --- Montagem --------------------------------------------------------------------

func _build() -> void:
	_panel = PanelContainer.new()
	_panel.theme = UiTheme.paper_theme()
	_panel.set_anchors_preset(Control.PRESET_CENTER)
	_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	add_child(_panel)
	var outer := VBoxContainer.new()
	outer.add_theme_constant_override("separation", 10)
	_panel.add_child(outer)
	var title := Label.new()
	title.text = "SKILLS_TITLE"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.theme_type_variation = &"TitleLabel"
	title.add_theme_font_size_override("font_size", 26)
	outer.add_child(title)
	_points = Label.new()
	_points.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_points.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_points.add_theme_color_override("font_color", Color(0.45, 0.09, 0.07))
	outer.add_child(_points)
	_rows = VBoxContainer.new()
	_rows.add_theme_constant_override("separation", 4)
	outer.add_child(_rows)
	_details = Label.new()
	_details.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_details.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_details.custom_minimum_size = Vector2(700, 110)
	outer.add_child(_details)
	var hint := Label.new()
	hint.text = "SKILLS_HINT"
	hint.modulate = Color(1, 1, 1, 0.7)
	hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	hint.custom_minimum_size = Vector2(700, 0)
	outer.add_child(hint)
