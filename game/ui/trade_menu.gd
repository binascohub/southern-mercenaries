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
var _yours: Label
var _theirs: Label
var _confirm: Button


func _ready() -> void:
	layer = 6
	_build()
	_hide_all()


func bind(trade: Trade, hud: Hud) -> void:
	_trade = trade
	_hud = hud
	trade.invited.connect(_on_invited)
	trade.updated.connect(_on_updated)
	trade.ended.connect(_on_ended)


func bind_player(player: Player) -> void:
	_player = player
	player.character_changed.connect(func(_levels: int) -> void:
		if _panel.visible:
			_refresh())


func is_open() -> bool:
	return _invite.visible or _panel.visible


func _unhandled_input(event: InputEvent) -> void:
	if is_open() and (event.is_action_pressed(&"ui_cancel") or event.is_action_pressed(&"menu")):
		get_viewport().set_input_as_handled()
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
	_yours.text = _offer_text("TRADE_YOUR_OFFER", you)
	_theirs.text = _offer_text("TRADE_THEIR_OFFER", them)
	_confirm.text = tr("TRADE_WAITING") if you.confirmed else tr("TRADE_CONFIRM")
	_confirm.disabled = bool(you.confirmed)


func _offer_text(title_key: String, side: Dictionary) -> String:
	var lines := PackedStringArray([tr(title_key).format({"name": side.name})])
	for item: Dictionary in side.items:
		lines.append("  " + _short(item))
	if int(side.gold) > 0:
		lines.append("  " + tr("HUD_GOLD").format({"gold": side.gold}))
	if side.items.is_empty() and int(side.gold) <= 0:
		lines.append("  —")
	lines.append(tr("TRADE_CONFIRMED") if side.confirmed else tr("TRADE_NOT_CONFIRMED"))
	return "\n".join(lines)


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
	_title.add_theme_font_size_override("font_size", 24)
	outer.add_child(_title)
	var columns := HBoxContainer.new()
	columns.add_theme_constant_override("separation", 18)
	outer.add_child(columns)

	var left := VBoxContainer.new()
	columns.add_child(left)
	var bag := GridContainer.new()
	bag.columns = BAG_COLUMNS
	left.add_child(bag)
	for i in GameData.balance.inventory_size:
		var button := Button.new()
		button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		button.custom_minimum_size = CELL
		button.clip_text = true
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		button.add_theme_font_size_override("font_size", 11)
		button.pressed.connect(_toggle.bind(i))
		bag.add_child(button)
		_bag_buttons.append(button)
	_gold_label = _text_label()
	left.add_child(_gold_label)
	_gold = HSlider.new()
	_gold.custom_minimum_size = Vector2(300, 28)
	_gold.focus_mode = Control.FOCUS_ALL
	_gold.value_changed.connect(_on_gold_changed)
	left.add_child(_gold)

	var right := VBoxContainer.new()
	right.custom_minimum_size = Vector2(260, 0)
	right.add_theme_constant_override("separation", 12)
	columns.add_child(right)
	_yours = _text_label()
	right.add_child(_yours)
	_theirs = _text_label()
	right.add_child(_theirs)
	_confirm = _button("TRADE_CONFIRM", func() -> void: _trade.confirm(_id))
	_confirm.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	right.add_child(_confirm)
	right.add_child(_button("TRADE_CANCEL", func() -> void: _trade.cancel(_id)))
	var hint := _text_label()
	hint.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_INHERIT
	hint.text = "TRADE_HINT"
	hint.modulate = Color(1, 1, 1, 0.7)
	outer.add_child(hint)


func _box() -> PanelContainer:
	var box := PanelContainer.new()
	box.set_anchors_preset(Control.PRESET_CENTER)
	box.grow_horizontal = Control.GROW_DIRECTION_BOTH
	box.grow_vertical = Control.GROW_DIRECTION_BOTH
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.09, 0.07, 0.06)  # opaco: o HUD não aparece através
	style.border_color = Color(0.45, 0.33, 0.2)
	style.set_border_width_all(2)
	style.set_content_margin_all(16)
	box.add_theme_stylebox_override("panel", style)
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
