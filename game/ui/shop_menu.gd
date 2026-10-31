# Southern Mercenaries — GPL-3.0-or-later
class_name ShopMenu
extends CanvasLayer
## Janela de loja (04-tortuga-e-missoes.md, seção 2): à esquerda o que a loja
## vende (com preço e cinza quando falta ouro ou já foi vendido), à direita a
## bolsa do herói com o preço que a loja paga (25% do valor; valiosos só com os
## piratas, pelo preço do dia). Abre ao interagir com a banca, sem trocar de cena.
## Os pedidos vão para o servidor (Town). Funciona só com o controle.

var _town: Town
var _player: Player
var _shop_id := ""
var _panel: PanelContainer
var _title: Label
var _gold: Label
var _buy_list: VBoxContainer
var _sell_list: VBoxContainer
var _details: Label


func _ready() -> void:
	layer = 6
	_build()
	visible = false


func bind(town: Town) -> void:
	_town = town
	town.shop_opened.connect(open)
	town.state_changed.connect(func() -> void:
		if visible:
			_refresh())


func bind_player(player: Player) -> void:
	_player = player
	player.character_changed.connect(func(_levels: int) -> void:
		if visible:
			_refresh())


func open(shop_id: String) -> void:
	_shop_id = shop_id
	visible = true
	Session.ui_open = true
	_refresh()
	_focus_first.call_deferred()


func close() -> void:
	visible = false
	Session.ui_open = false
	var focus := _panel.get_viewport().gui_get_focus_owner()
	if focus:
		focus.release_focus()


func _unhandled_input(event: InputEvent) -> void:
	if visible and (event.is_action_pressed(&"ui_cancel") or event.is_action_pressed(&"menu")):
		get_viewport().set_input_as_handled()
		close()


func _focus_first() -> void:
	for list in [_buy_list, _sell_list]:
		for child in list.get_children():
			if child is Button and not child.disabled:
				child.grab_focus()
				return


func _refresh() -> void:
	if _player == null or _player.character == null or _shop_id == "":
		return
	var c := _player.character
	var level := int(c.data.level)
	var shop := Shops.shop(_shop_id)
	_title.text = tr(shop.get("name_key", ""))
	var captain := Shops.captain_key(_town.ship) if shop.has("rarity_weights") else ""
	if captain != "":
		_title.text += " — " + tr(captain)
	_gold.text = tr("HUD_GOLD").format({"gold": c.data.gold})
	var focused := _panel.get_viewport().gui_get_focus_owner()
	var focus_index := -1
	if focused and focused.get_parent() in [_buy_list, _sell_list]:
		focus_index = focused.get_index() + (1000 if focused.get_parent() == _sell_list else 0)
	MenuPanel.clear(_buy_list)
	var stock := Shops.stock(_shop_id, c, _town.ship)
	for i in stock.size():
		var item: Dictionary = stock[i]
		var price := Shops.buy_price(_shop_id, item, level)
		var sold := Shops.sold_out(_shop_id, i, item, c, _town.ship)
		var button := _row(Items.display_name(item), tr("SHOP_PRICE").format({"price": price}) if not sold else tr("SHOP_SOLD"),
			Items.color(item) if item.kind == Items.EQUIPMENT else Color.WHITE)
		button.disabled = sold or int(c.data.gold) < price
		button.pressed.connect(func() -> void: _town.request_buy(_shop_id, i))
		button.focus_entered.connect(_describe.bind(item))
		_buy_list.add_child(button)
	MenuPanel.clear(_sell_list)
	for i in c.data.inventory.size():
		var item: Variant = c.data.inventory[i]
		if item == null:
			continue
		var price := Shops.sell_price(_shop_id, item, level, _town.ship)
		var label := Items.display_name(item) + (" x%d" % item.count if item.has("count") and int(item.count) > 1 else "")
		var button := _row(label, tr("SHOP_PRICE").format({"price": price}) if price >= 0 else tr("SHOP_NOT_BUYING"),
			Items.color(item) if item.kind == Items.EQUIPMENT else Color.WHITE)
		button.disabled = price < 0
		button.pressed.connect(func() -> void: _town.request_sell(_shop_id, i))
		button.focus_entered.connect(_describe.bind(item))
		_sell_list.add_child(button)
	# Depois de comprar/vender o foco fica no mesmo lugar da lista.
	if focus_index >= 0:
		_focus_at.call_deferred(_sell_list if focus_index >= 1000 else _buy_list, focus_index % 1000)


## Foca o botão da posição (escolhido na hora: a lista pode ter mudado de novo).
func _focus_at(list: VBoxContainer, index: int) -> void:
	if not visible or list.get_child_count() == 0:
		return
	var child := list.get_child(mini(index, list.get_child_count() - 1)) as Control
	if child and child.is_inside_tree() and not child.is_queued_for_deletion():
		child.grab_focus()


func _row(text: String, price: String, color: Color) -> Button:
	var button := Button.new()
	button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	button.custom_minimum_size = Vector2(400, 34)
	button.text = "%s   —   %s" % [text, price]
	button.add_theme_color_override("font_color", color)
	return button


func _describe(item: Dictionary) -> void:
	var factor: float = _player.character.class_data().armor_factor if _player and _player.character else 1.0
	_details.text = "\n".join(Items.describe(item, factor))


func _build() -> void:
	_panel = PanelContainer.new()
	_panel.set_anchors_preset(Control.PRESET_CENTER)
	_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.09, 0.07, 0.06)
	style.border_color = Color(0.45, 0.33, 0.2)
	style.set_border_width_all(2)
	style.set_content_margin_all(16)
	_panel.add_theme_stylebox_override("panel", style)
	add_child(_panel)
	var outer := VBoxContainer.new()
	outer.add_theme_constant_override("separation", 8)
	_panel.add_child(outer)
	_title = Label.new()
	_title.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_title.add_theme_font_size_override("font_size", 24)
	outer.add_child(_title)
	_gold = Label.new()
	_gold.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_gold.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_gold.add_theme_color_override("font_color", Color(1.0, 0.85, 0.35))
	outer.add_child(_gold)
	var columns := HBoxContainer.new()
	columns.add_theme_constant_override("separation", 16)
	outer.add_child(columns)
	for side in [["SHOP_BUY", true], ["SHOP_SELL", false]]:
		var col := VBoxContainer.new()
		columns.add_child(col)
		var head := Label.new()
		head.text = side[0]
		col.add_child(head)
		var scroll := ScrollContainer.new()
		scroll.custom_minimum_size = Vector2(420, 360)
		scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		col.add_child(scroll)
		var list := VBoxContainer.new()
		list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		scroll.add_child(list)
		if side[1]:
			_buy_list = list
		else:
			_sell_list = list
	_details = Label.new()
	_details.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_details.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_details.custom_minimum_size = Vector2(840, 100)
	outer.add_child(_details)
	var hint := Label.new()
	hint.text = "SHOP_HINT"
	hint.modulate = Color(1, 1, 1, 0.7)
	outer.add_child(hint)
