# Southern Mercenaries — GPL-3.0-or-later
class_name InventoryMenu
extends CanvasLayer
## Inventário, equipamento e atributos (09-interface.md, seção 4): slots do
## herói, bolsa de 40 espaços, atributos com pontos livres e a dica do item em
## foco comparada com o equipado. Toda a janela funciona só com o controle.
## Os pedidos (equipar, usar, gastar ponto) são validados no servidor.
## Não pausa o jogo (no co-op o herói fica vulnerável, 07-rede.md).
## No co-op, "Trocar" chama o aliado mais perto para uma troca (TradeMenu).

## Pediu para trocar com o aliado mais perto.
signal trade_requested
## Abrir a janela de habilidades (no controle não há tecla própria).
signal skills_requested
## Abrir o diário de missões.
signal journal_requested

const BAG_COLUMNS := 8
## Cabe em 1280 px: atributos 230 + slots 2 × 130 + bolsa 8 × 68 (+ espaços).
const CELL := Vector2(68, 56)
const SLOT_SIZE := Vector2(130, 56)

var _player: Player
var _panel: PanelContainer
var _stats: Label
var _attr_buttons := {}
var _slot_buttons := {}
var _bag_buttons: Array[Button] = []
var _details: Label
var _hint: Label
var _trade_button: Button
var _focused := {}  # {"bag": index} ou {"slot": nome}


func _ready() -> void:
	layer = 5
	_build()
	visible = false


func bind_player(player: Player) -> void:
	_player = player
	player.character_changed.connect(func(_levels: int) -> void:
		if visible:
			_refresh())


func toggle() -> void:
	if visible:
		close()
	elif _player and _player.character:
		visible = true
		Session.ui_open = true
		_refresh()
		_bag_buttons[0].grab_focus.call_deferred()


func close() -> void:
	visible = false
	Session.ui_open = false
	var focus := _panel.get_viewport().gui_get_focus_owner()
	if focus:
		focus.release_focus()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"inventory"):
		toggle()
		get_viewport().set_input_as_handled()
	elif visible and (event.is_action_pressed(&"ui_cancel") or event.is_action_pressed(&"menu")):
		close()
		get_viewport().set_input_as_handled()


func _notification(what: int) -> void:
	if what == NOTIFICATION_TRANSLATION_CHANGED and is_node_ready() and visible:
		_refresh()


# --- Conteúdo -----------------------------------------------------------------

func _refresh() -> void:
	var c := _player.character
	var d := c.data
	var cls := c.class_data()
	_stats.text = "\n".join(PackedStringArray([
		"%s — %s" % [d.name, tr(cls.name_key)],
		tr("INV_LEVEL").format({"level": d.level}),
		tr("HUD_LEVEL_XP").format({"level": d.level, "xp": d.xp, "next": CharacterData.xp_to_next(int(d.level))}),
		tr("INV_HEALTH").format({"value": roundi(c.max_health())}),
		tr("INV_RESOURCE").format({"name": tr(cls.resource_key), "value": roundi(c.max_resource())}),
		tr("INV_POWER").format({"name": tr(cls.power_key), "value": "%.1f" % c.power()}),
		tr("INV_ARMOR").format({"value": "%.1f" % c.armor()}),
		tr("HUD_GOLD").format({"gold": d.gold}),
		tr("INV_FREE_POINTS").format({"points": int(d.free_points)}),
	]))
	for attr in CharacterData.ATTRIBUTES:
		var button: Button = _attr_buttons[attr]
		button.text = tr("ATTR_" + attr.to_upper()).format({"value": c.attribute(attr)})
		button.disabled = int(d.free_points) <= 0
	for slot in CharacterData.SLOTS:
		var item: Variant = d.equipment.get(slot)
		var button: Button = _slot_buttons[slot]
		button.text = "%s\n%s" % [tr("SLOT_" + slot.to_upper()), _short(item) if item else "—"]
		button.add_theme_color_override("font_color", Items.color(item) if item else Color(0.6, 0.6, 0.6))
		# Barda: só o Cavaleiro tem cavalo.
		button.visible = slot != "barding" or cls.has("mount")
	for i in _bag_buttons.size():
		var item: Variant = d.inventory[i] if i < d.inventory.size() else null
		var button := _bag_buttons[i]
		button.text = _short(item) if item else ""
		# Poções com ícone: o frasco em cima, só a quantidade embaixo.
		var icon := Items.icon(item)
		button.icon = icon
		if icon:
			button.text = "x%d" % int(item.count) if int(item.get("count", 1)) > 1 else ""
		button.add_theme_color_override("font_color", Items.color(item) if item else Color.WHITE)
		button.add_theme_color_override("font_focus_color", Items.color(item) if item else Color.WHITE)
	_hint.text = tr("INV_HINT").format({"close": InputDevice.prompt(&"inventory")})
	_trade_button.visible = NetworkManager.is_online()
	_show_details()


func _short(item: Dictionary) -> String:
	var name := Items.display_name(item)
	if name.length() > 24:
		name = name.substr(0, 23) + "…"
	if item.kind != Items.EQUIPMENT and int(item.count) > 1:
		name += " x%d" % item.count
	return name


func _show_details() -> void:
	if _player == null or _player.character == null:
		return
	var c := _player.character
	var factor: float = c.class_data().armor_factor
	var item: Variant = null
	if _focused.has("bag"):
		item = c.data.inventory[_focused.bag]
	elif _focused.has("slot"):
		item = c.data.equipment.get(_focused.slot)
	if item == null:
		_details.text = ""
		return
	var lines := Items.describe(item, factor)
	if item.kind == Items.EQUIPMENT and _focused.has("bag"):
		if not c.can_equip(item):
			lines.append(tr("INV_CANNOT_EQUIP"))
		var slot := Items.slot_of(item)
		var current: Variant = c.data.equipment.get("ring_1" if slot == "ring" else slot)
		if current != null:
			lines.append("")
			lines.append(tr("INV_EQUIPPED_NOW"))
			lines.append_array(Items.describe(current, factor))
	_details.text = "\n".join(lines)


# --- Montagem --------------------------------------------------------------------

func _build() -> void:
	_panel = PanelContainer.new()
	_panel.set_anchors_preset(Control.PRESET_CENTER)
	_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	add_child(_panel)

	var outer := VBoxContainer.new()
	outer.add_theme_constant_override("separation", 10)
	_panel.add_child(outer)
	var title := Label.new()
	title.text = "INV_TITLE"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.theme_type_variation = &"TitleLabel"
	title.add_theme_font_size_override("font_size", 26)
	outer.add_child(title)

	var columns := HBoxContainer.new()
	columns.add_theme_constant_override("separation", 18)
	outer.add_child(columns)

	# Atributos.
	var left := VBoxContainer.new()
	left.custom_minimum_size = Vector2(230, 0)
	columns.add_child(left)
	_stats = _text_label()
	left.add_child(_stats)
	for attr in CharacterData.ATTRIBUTES:
		var button := Button.new()
		button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		button.pressed.connect(func() -> void: _player.request_spend_point(attr))
		left.add_child(button)
		_attr_buttons[attr] = button

	# Equipamento.
	var slots := GridContainer.new()
	slots.columns = 2
	columns.add_child(slots)
	for slot in CharacterData.SLOTS:
		var button := Button.new()
		button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		button.custom_minimum_size = SLOT_SIZE
		button.clip_text = true
		button.pressed.connect(func() -> void: _player.request_unequip(slot))
		button.focus_entered.connect(func() -> void:
			_focused = {"slot": slot}
			_show_details())
		slots.add_child(button)
		_slot_buttons[slot] = button

	# Bolsa.
	var bag := GridContainer.new()
	bag.columns = BAG_COLUMNS
	columns.add_child(bag)
	for i in GameData.balance.inventory_size:
		var button := Button.new()
		button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		button.custom_minimum_size = CELL
		button.clip_text = true
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		button.expand_icon = true
		button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
		button.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		button.add_theme_font_size_override("font_size", 11)
		button.pressed.connect(func() -> void: _player.request_use(i))
		button.focus_entered.connect(func() -> void:
			_focused = {"bag": i}
			_show_details())
		bag.add_child(button)
		_bag_buttons.append(button)

	_details = _text_label()
	_details.custom_minimum_size = Vector2(0, 150)
	outer.add_child(_details)
	_hint = _text_label()
	_hint.modulate = Color(1, 1, 1, 0.7)
	outer.add_child(_hint)
	# Ações lado a lado, para a janela continuar cabendo em 720 px de altura.
	var actions := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_CENTER
	actions.add_theme_constant_override("separation", 12)
	outer.add_child(actions)
	_trade_button = Button.new()
	_trade_button.text = "INV_TRADE"
	_trade_button.custom_minimum_size = Vector2(260, 40)
	_trade_button.pressed.connect(func() -> void:
		close()
		trade_requested.emit())
	actions.add_child(_trade_button)
	var skills_button := Button.new()
	skills_button.text = "INV_SKILLS"
	skills_button.custom_minimum_size = Vector2(260, 40)
	skills_button.pressed.connect(func() -> void:
		close()
		skills_requested.emit())
	actions.add_child(skills_button)
	var journal_button := Button.new()
	journal_button.text = "INV_JOURNAL"
	journal_button.custom_minimum_size = Vector2(200, 40)
	journal_button.pressed.connect(func() -> void:
		close()
		journal_requested.emit())
	actions.add_child(journal_button)


func _text_label() -> Label:
	var label := Label.new()
	label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return label
