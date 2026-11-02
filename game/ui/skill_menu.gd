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
## Linhas das poções (também vão para os quadrados): token -> {"icon", "slots"}.
var _potion_rows: Dictionary = {}
var _details: Label
var _focused_key := ""
## chave -> {"label", "learn", "slots": [Button × 4]}
var _row_nodes := {}
## Os 4 atalhos repetidos aqui, por cima da janela (a barra da tela fica escondida atrás dela): soltar uma habilidade neles a põe no atalho.
var _dock: VBoxContainer
var _dock_labels: Array[Label] = []
var _dock_icons: Array[TextureRect] = []


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
		_dock.visible = true
		var first: Dictionary = _row_nodes.values()[0] if not _row_nodes.is_empty() else {}
		if not first.is_empty():
			first.learn.grab_focus.call_deferred()


func close() -> void:
	if _dock:
		_dock.visible = false
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
		var icon := TextureRect.new()
		icon.custom_minimum_size = Vector2(34, 34)
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(icon)
		var label := Label.new()
		label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		label.custom_minimum_size = Vector2(ROW_NAME_WIDTH - 40, 0)
		label.mouse_filter = Control.MOUSE_FILTER_STOP  # para receber o arrastar (a habilidade aprendida e ativa vai para um atalho)
		label.set_drag_forwarding(_drag_skill.bind(key, label), Callable(), Callable())
		row.add_child(label)
		var learn := Button.new()
		learn.text = "+"
		learn.custom_minimum_size = Vector2(44, 36)
		learn.pressed.connect(func() -> void: _player.request_learn(key))
		learn.focus_entered.connect(_focus.bind(key))
		row.add_child(learn)
		var slots: Array[Button] = []
		for i in PlayerInput.SKILL_SLOTS:
			var slot := Button.new()
			slot.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
			slot.text = str(i + 2)  # a tecla (o 1 é o ataque básico)
			slot.toggle_mode = false
			slot.custom_minimum_size = Vector2(30, 36)
			slot.pressed.connect(func() -> void: _player.request_slot(i, key))
			slot.focus_entered.connect(_focus.bind(key))
			row.add_child(slot)
			slots.append(slot)
		_row_nodes[key] = {"label": label, "learn": learn, "slots": slots, "icon": icon}
	# As poções: cada uma também pode ocupar um dos 8 quadrados (arrastar ou clicar no número), no lugar de uma habilidade.
	_potion_rows.clear()
	for token: String in CharacterData.POTION_SLOTS:
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 6)
		_rows.add_child(row)
		var icon := TextureRect.new()
		icon.custom_minimum_size = Vector2(34, 34)
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(icon)
		var label := Label.new()
		label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		label.custom_minimum_size = Vector2(ROW_NAME_WIDTH - 40 + 44, 0)  # a largura da linha de habilidade sem o botão "+"
		label.mouse_filter = Control.MOUSE_FILTER_STOP
		label.set_drag_forwarding(_drag_skill.bind(token, label), Callable(), Callable())
		row.add_child(label)
		var slots: Array[Button] = []
		for i in PlayerInput.SKILL_SLOTS:
			var slot := Button.new()
			slot.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
			slot.text = str(i + 2)
			slot.toggle_mode = false
			slot.custom_minimum_size = Vector2(30, 36)
			slot.pressed.connect(func() -> void: _player.request_slot(i, token))
			row.add_child(slot)
			slots.append(slot)
		_potion_rows[token] = {"label": label, "icon": icon, "slots": slots}


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
		var icon_path := "res://assets/ui/icons/skills/%s.png" % c.skill_of(key)
		(nodes.icon as TextureRect).texture = load(icon_path) as Texture2D if ResourceLoader.exists(icon_path) else null
		label.text = line
		label.modulate = Color.WHITE if rank > 0 else (Color(0.75, 0.75, 0.75) if level <= int(c.data.level) else Color(0.45, 0.45, 0.45))
		var learn: Button = nodes.learn
		learn.disabled = not c.can_learn(key)
		var active := Skills.is_active(c.skill_of(key)) and rank > 0
		for i in PlayerInput.SKILL_SLOTS:
			var slot: Button = nodes.slots[i]
			slot.visible = active
			slot.modulate = Color(1.0, 0.85, 0.4) if c.data.skill_slots[i] == key else Color.WHITE
	for token: String in _potion_rows:
		var nodes: Dictionary = _potion_rows[token]
		(nodes.label as Label).text = _potion_name(token)
		var path := "res://assets/ui/icons/%s.png" % _potion_icon_id(token)
		(nodes.icon as TextureRect).texture = load(path) as Texture2D if ResourceLoader.exists(path) else null
		for i in PlayerInput.SKILL_SLOTS:
			(nodes.slots[i] as Button).modulate = Color(1.0, 0.85, 0.4) if c.data.skill_slots[i] == token else Color.WHITE
	_refresh_dock()
	_show_details()


## Nome e ícone de uma poção que vai num quadrado (a elemental é a do elemento do herói).
func _potion_name(token: String) -> String:
	match token:
		"potion_health":
			return tr("ITEM_POTION_HEALTH")
		"potion_resource":
			return tr("ITEM_POTION_RESOURCE")
	return tr("ITEM_POTION_ELEMENTAL_" + String(_player.element).to_upper())


func _potion_icon_id(token: String) -> String:
	return token if token != "potion_elemental" else "elemental_potion_" + String(_player.element)


## Arrastar uma habilidade ativa e aprendida: o que vai na mão é o nome dela, e o destino é um dos 4 atalhos do dock.
func _drag_skill(_at: Vector2, key: String, source: Control) -> Variant:
	var c := _player.character if _player else null
	var is_potion := key in CharacterData.POTION_SLOTS
	if c == null or (not is_potion and (c.skill_rank(key) <= 0 or not Skills.is_active(c.skill_of(key)))):
		return null
	var preview := Label.new()
	preview.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	preview.text = _potion_name(key) if is_potion else tr(Skills.def(c.skill_of(key)).get("name_key", ""))
	preview.add_theme_font_size_override("font_size", 18)
	preview.add_theme_color_override("font_color", Color(1.0, 0.9, 0.5))
	preview.add_theme_color_override("font_outline_color", Color.BLACK)
	preview.add_theme_constant_override("outline_size", 6)
	source.set_drag_preview(preview)
	return {"skill_key": key}


func _can_drop_skill(_at: Vector2, data: Variant, _index: int) -> bool:
	return data is Dictionary and data.has("skill_key")


func _drop_skill(_at: Vector2, data: Variant, index: int) -> void:
	if _player and data is Dictionary and data.has("skill_key"):
		_player.request_slot(index, String(data.skill_key))


func _build_dock() -> void:
	_dock = VBoxContainer.new()  # coluna à direita da janela (a janela ocupa o meio da tela e cobriria uma barra embaixo)
	_dock.set_anchors_preset(Control.PRESET_CENTER_RIGHT)
	_dock.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	_dock.grow_vertical = Control.GROW_DIRECTION_BOTH
	_dock.offset_right = -20
	_dock.offset_top = 40
	_dock.offset_bottom = 40
	_dock.add_theme_constant_override("separation", 6)
	add_child(_dock)
	for i in PlayerInput.SKILL_SLOTS:
		var box := PanelContainer.new()
		box.theme = UiTheme.paper_theme()
		box.custom_minimum_size = Vector2(220, 54)
		box.set_drag_forwarding(Callable(), _can_drop_skill.bind(i), _drop_skill.bind(i))
		_dock.add_child(box)
		var line := HBoxContainer.new()
		line.add_theme_constant_override("separation", 8)
		line.mouse_filter = Control.MOUSE_FILTER_IGNORE
		box.add_child(line)
		var dock_icon := TextureRect.new()
		dock_icon.custom_minimum_size = Vector2(40, 40)
		dock_icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		dock_icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		dock_icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		line.add_child(dock_icon)
		_dock_icons.append(dock_icon)
		var label := Label.new()
		label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		label.custom_minimum_size = Vector2(120, 0)
		label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		line.add_child(label)
		_dock_labels.append(label)


func _refresh_dock() -> void:
	var c := _player.character if _player else null
	for i in _dock_labels.size():
		var key: String = c.data.skill_slots[i] if c else ""
		var prompt := _both_keys(StringName("skill_%d" % (i + 1)))
		var is_potion := key in CharacterData.POTION_SLOTS
		var shown_name := _potion_name(key) if is_potion else (tr(Skills.def(c.skill_of(key)).get("name_key", "")) if key != "" else "")
		_dock_labels[i].text = "%s\n—" % prompt if key == "" else "%s\n%s" % [prompt, shown_name]
		var dock_path := "res://assets/ui/icons/%s.png" % _potion_icon_id(key) if is_potion else "res://assets/ui/icons/skills/%s.png" % (c.skill_of(key) if key != "" else "")
		_dock_icons[i].texture = load(dock_path) as Texture2D if key != "" and ResourceLoader.exists(dock_path) else null


## A tecla e o botão do controle de uma ação ("2 · A"); sem botão no controle, só a tecla.
func _both_keys(action: StringName) -> String:
	var keyboard := Controls.binding_label(action, Controls.KB)
	var pad := Controls.binding_label(action, Controls.PAD)
	return keyboard if pad == "—" else "%s · %s" % [keyboard, pad]


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
	_build_dock()
	_dock.visible = false
