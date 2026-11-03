# Southern Mercenaries — GPL-3.0-or-later
class_name TradeMenu
extends CanvasLayer
## Janela de troca entre jogadores (05-itens-e-loot.md, seção 8): convite
## (aceitar / recusar) e a troca em si — a sua bolsa à esquerda (aperte um item
## para pôr ou tirar da oferta), o ouro oferecido, a oferta do outro e o estado
## das confirmações. Tudo funciona só com o controle. Não pausa o jogo.

const BAG_COLUMNS := 8
const CELL := Vector2(92, 48)

var _trade: Trade
var _hud: Hud
var _player: Player
var _id := 0
var _state := {}

var _invite: PanelContainer
var _invite_text: Label
var _accept: Button
var _panel: PanelContainer
var _title: Label
var _bag_buttons: Array[Button] = []
var _gold: HSlider
var _gold_label: Label
var _yours: VBoxContainer
var _theirs: VBoxContainer
var _bag_title: Label
var _popup: PanelContainer
var _popup_icon: TextureRect
var _popup_text: Label
var _confirm: Button


func _ready() -> void:
	layer = 6
	_build()
	_build_popup()
	_hide_all()


func bind(trade: Trade, hud: Hud) -> void:
	_trade = trade
	_hud = hud
	trade.invited.connect(_on_invited)
	trade.updated.connect(_on_updated)
	trade.ended.connect(_on_ended)


func bind_player(player: Player) -> void:
	_player = player
	player.character_changed.connect(_on_character_changed)


## Ligado por método (não lambda): some junto com o menu quando a cena é desmontada.
func _on_character_changed(_levels: int) -> void:
	if _panel.visible:
		_refresh()

func is_open() -> bool:
	return _invite.visible or _panel.visible


func _unhandled_input(event: InputEvent) -> void:
	if is_open() and (event.is_action_pressed(&"ui_cancel") or event.is_action_pressed(&"menu")):
		get_viewport().set_input_as_handled()
		if _popup.visible:
			_popup.visible = false
			return
		if _panel.visible:
			_trade.cancel(_id)
		else:
			_trade.answer(_id, false)
			_hide_all()


func _notification(what: int) -> void:
	if what == NOTIFICATION_TRANSLATION_CHANGED and is_node_ready() and _panel.visible:
		_refresh()


# --- Eventos ---------------------------------------------------------------------

func _on_invited(trade_id: int, from_name: String) -> void:
	_id = trade_id
	_invite_text.text = tr("TRADE_INVITED").format({"name": from_name})
	_invite.visible = true
	Session.ui_open = true
	_accept.grab_focus.call_deferred()


func _on_updated(state: Dictionary) -> void:
	var opening := not _panel.visible
	_state = state
	_id = int(state.id)
	_invite.visible = false
	_panel.visible = true
	Session.ui_open = true
	_refresh()
	if opening:
		_bag_buttons[0].grab_focus.call_deferred()


func _on_ended(reason_key: String) -> void:
	_hide_all()
	if _hud:
		_hud.toast(tr(reason_key))


func _hide_all() -> void:
	var was_open := _invite.visible or _panel.visible
	_invite.visible = false
	_panel.visible = false
	_popup.visible = false
	_state = {}
	if was_open:
		Session.ui_open = false
		var focus := _panel.get_viewport().gui_get_focus_owner()
		if focus:
			focus.release_focus()


# --- Oferta ----------------------------------------------------------------------

func _toggle(index: int) -> void:
	if _state.is_empty() or _player == null or _player.character == null:
		return
	var bag: Array = _player.character.data.inventory
	if index >= bag.size() or bag[index] == null:
		return
	var indices: Array = _state.you.indices.duplicate()
	if index in indices:
		indices.erase(index)
	else:
		indices.append(index)
	_trade.set_offer(_id, indices, int(_gold.value))


func _on_gold_changed(value: float) -> void:
	if not _state.is_empty() and int(value) != int(_state.you.gold):
		_trade.set_offer(_id, _state.you.indices, int(value))


func _refresh() -> void:
	if _state.is_empty() or _player == null or _player.character == null:
		return
	var you: Dictionary = _state.you
	var them: Dictionary = _state.them
	var bag: Array = _player.character.data.inventory
	_title.text = tr("TRADE_TITLE").format({"name": them.name})
	_bag_title.text = tr("TRADE_BAG")
	for i in _bag_buttons.size():
		var item: Variant = bag[i] if i < bag.size() else null
		var button := _bag_buttons[i]
		var offered: bool = i in you.indices
		button.text = ("» " if offered else "") + (_short(item) if item else "")
		button.add_theme_color_override("font_color", Items.color(item) if item else Color.WHITE)
		button.modulate = Color(1.0, 0.85, 0.4) if offered else Color.WHITE
	var gold := int(_player.character.data.gold)
	_gold.max_value = gold
	_gold.step = maxi(1, gold / 100)
	_gold.set_value_no_signal(int(you.gold))
	_gold_label.text = tr("TRADE_GOLD").format({"gold": int(you.gold), "total": gold})
	_fill_offer(_yours, "TRADE_YOUR_OFFER", you, true)
	_fill_offer(_theirs, "TRADE_THEIR_OFFER", them, false)
	_confirm.text = tr("TRADE_WAITING") if you.confirmed else tr("TRADE_CONFIRM")
	_confirm.disabled = bool(you.confirmed)


## Monta o quadro de uma oferta: título, um botão por item (botão direito = detalhes; na sua, apertar tira da oferta),
## ouro e estado da confirmação.
func _fill_offer(box: VBoxContainer, title_key: String, side: Dictionary, yours: bool) -> void:
	for child in box.get_children():
		box.remove_child(child)
		child.queue_free()
	var title := _text_label()
	title.theme_type_variation = &"TitleLabel"
	title.text = tr(title_key).format({"name": side.name})
	box.add_child(title)
	var bag: Array = _player.character.data.inventory if yours else []
	for n in side.items.size():
		var item: Dictionary = side.items[n]
		var button := Button.new()
		button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		button.text = _short(item)
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.add_theme_color_override("font_color", Items.color(item))
		button.gui_input.connect(_on_item_input.bind(item))
		if yours and n < side.indices.size():
			button.pressed.connect(_toggle.bind(int(side.indices[n])))
		else:
			button.pressed.connect(_show_popup.bind(item))
		box.add_child(button)
	if int(side.gold) > 0:
		var gold := _text_label()
		gold.text = tr("HUD_GOLD").format({"gold": side.gold})
		box.add_child(gold)
	if side.items.is_empty() and int(side.gold) <= 0:
		var empty := _text_label()
		empty.text = "—"
		box.add_child(empty)
	var state := _text_label()
	state.text = tr("TRADE_CONFIRMED") if side.confirmed else tr("TRADE_NOT_CONFIRMED")
	state.modulate = Color(0.45, 0.85, 0.45) if side.confirmed else Color(1, 1, 1, 0.65)
	box.add_child(state)


func _on_item_input(event: InputEvent, item: Dictionary) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_RIGHT:
		_show_popup(item)
		get_viewport().set_input_as_handled()


func _on_bag_input(event: InputEvent, index: int) -> void:
	if not (event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_RIGHT):
		return
	var bag: Array = _player.character.data.inventory
	if index < bag.size() and bag[index] != null:
		_show_popup(bag[index])
	get_viewport().set_input_as_handled()


## Detalhe do item (imagem e descrição), igual ao da bolsa.
func _show_popup(item: Dictionary) -> void:
	var icon := Items.icon(item)
	_popup_icon.texture = icon
	_popup_icon.visible = icon != null
	var factor: float = _player.character.class_data().armor_factor if _player and _player.character else 1.0
	_popup_text.text = "\n".join(Items.describe(item, factor))
	_popup_text.add_theme_color_override("font_color", Color(0.18, 0.12, 0.07))
	_popup.visible = true


func _short(item: Dictionary) -> String:
	var name := Items.display_name(item)
	if name.length() > 20:
		name = name.substr(0, 19) + "…"
	if item.kind != Items.EQUIPMENT and int(item.get("count", 1)) > 1:
		name += " x%d" % item.count
	return name


# --- Montagem --------------------------------------------------------------------

func _build() -> void:
	_invite = _box()
	var invite_box := VBoxContainer.new()
	invite_box.add_theme_constant_override("separation", 10)
	_invite.add_child(invite_box)
	_invite_text = _text_label()
	_invite_text.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	invite_box.add_child(_invite_text)
	_accept = _button("TRADE_ACCEPT", func() -> void: _trade.answer(_id, true))
	invite_box.add_child(_accept)
	invite_box.add_child(_button("TRADE_DECLINE", func() -> void:
		_trade.answer(_id, false)
		_hide_all()))

	_panel = _box()
	var outer := VBoxContainer.new()
	outer.add_theme_constant_override("separation", 10)
	_panel.add_child(outer)
	_title = _text_label()
	_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_title.theme_type_variation = &"TitleLabel"
	_title.add_theme_font_size_override("font_size", 24)
	outer.add_child(_title)
	var columns := HBoxContainer.new()
	columns.add_theme_constant_override("separation", 18)
	outer.add_child(columns)

	var left := _section(Color(0.35, 0.28, 0.18, 0.35))
	columns.add_child(left.panel)
	_bag_title = _text_label()
	var bag_title := _bag_title
	bag_title.theme_type_variation = &"TitleLabel"
	left.box.add_child(bag_title)
	var bag := GridContainer.new()
	bag.columns = BAG_COLUMNS
	left.box.add_child(bag)
	for i in GameData.balance.inventory_size:
		var button := Button.new()
		button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		button.custom_minimum_size = CELL
		button.clip_text = true
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		button.add_theme_font_size_override("font_size", 11)
		button.pressed.connect(_toggle.bind(i))
		button.gui_input.connect(_on_bag_input.bind(i))
		bag.add_child(button)
		_bag_buttons.append(button)
	_gold_label = _text_label()
	left.box.add_child(_gold_label)
	_gold = HSlider.new()
	_gold.custom_minimum_size = Vector2(300, 28)
	_gold.focus_mode = Control.FOCUS_ALL
	_gold.value_changed.connect(_on_gold_changed)
	left.box.add_child(_gold)

	var mine := _section(Color(0.25, 0.5, 0.3, 0.3))
	mine.panel.custom_minimum_size = Vector2(230, 0)
	columns.add_child(mine.panel)
	_yours = mine.box
	var other := _section(Color(0.25, 0.4, 0.6, 0.3))
	other.panel.custom_minimum_size = Vector2(230, 0)
	columns.add_child(other.panel)
	_theirs = other.box
	var actions := VBoxContainer.new()
	actions.add_theme_constant_override("separation", 12)
	columns.add_child(actions)
	_confirm = _button("TRADE_CONFIRM", func() -> void: _trade.confirm(_id))
	_confirm.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	actions.add_child(_confirm)
	actions.add_child(_button("TRADE_CANCEL", func() -> void: _trade.cancel(_id)))
	var hint := _text_label()
	hint.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_INHERIT
	hint.text = "TRADE_HINT"
	hint.modulate = Color(1, 1, 1, 0.7)
	outer.add_child(hint)


func _box() -> PanelContainer:
	var box := PanelContainer.new()
	box.theme = UiTheme.paper_theme()
	box.set_anchors_preset(Control.PRESET_CENTER)
	box.grow_horizontal = Control.GROW_DIRECTION_BOTH
	box.grow_vertical = Control.GROW_DIRECTION_BOTH
	add_child(box)
	return box


func _button(key: String, callback: Callable) -> Button:
	var button := Button.new()
	button.text = key
	button.custom_minimum_size = Vector2(260, 44)
	button.pressed.connect(callback)
	return button


func _text_label() -> Label:
	var label := Label.new()
	label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return label


## Quadro com fundo tingido (bolsa, oferta sua, oferta do outro): {panel, box}.
func _section(tint: Color) -> Dictionary:
	var panel := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = tint
	style.border_color = tint.lightened(0.4)
	style.set_border_width_all(2)
	style.set_corner_radius_all(4)
	style.set_content_margin_all(10)
	panel.add_theme_stylebox_override("panel", style)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 6)
	panel.add_child(box)
	return {"panel": panel, "box": box}


func _build_popup() -> void:
	_popup = PanelContainer.new()
	_popup.theme = UiTheme.paper_theme()
	_popup.set_anchors_preset(Control.PRESET_CENTER)
	_popup.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_popup.grow_vertical = Control.GROW_DIRECTION_BOTH
	_popup.custom_minimum_size = Vector2(420, 0)
	_popup.visible = false
	add_child(_popup)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 12)
	_popup.add_child(box)
	_popup_icon = TextureRect.new()
	_popup_icon.custom_minimum_size = Vector2(160, 160)
	_popup_icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_popup_icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_popup_icon.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	box.add_child(_popup_icon)
	_popup_text = _text_label()
	_popup_text.custom_minimum_size = Vector2(380, 0)
	box.add_child(_popup_text)
	var close_button := Button.new()
	close_button.text = "INV_POPUP_CLOSE"
	close_button.custom_minimum_size = Vector2(200, 40)
	close_button.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	close_button.pressed.connect(func() -> void: _popup.visible = false)
	box.add_child(close_button)
