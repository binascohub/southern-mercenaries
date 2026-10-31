# Southern Mercenaries — GPL-3.0-or-later
class_name ForgeMenu
extends CanvasLayer
## Forja do Ferreiro de Tortuga (05-1-refino.md): refinar os equipamentos
## (equipados e da bolsa) com pergaminho normal ou abençoado — +4 e +5 pedem
## confirmação porque podem quebrar —, cristalizar um item da bolsa e fazer
## pergaminhos com 10 cristais + ouro. A loja vende os pergaminhos de Ferro e Aço.
## O sorteio é no servidor (Town). Funciona só com o controle.

var _town: Town
var _player: Player
var _panel: PanelContainer
var _items: VBoxContainer
var _craft: VBoxContainer
var _info: Label


func _ready() -> void:
	layer = 6
	_build()
	visible = false


func bind(town: Town) -> void:
	_town = town
	town.forge_opened.connect(func() -> void:
		visible = true
		Session.ui_open = true
		_refresh())


func bind_player(player: Player) -> void:
	_player = player
	player.character_changed.connect(func(_levels: int) -> void:
		if visible:
			_refresh())


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


func _refresh() -> void:
	if _player == null or _player.character == null:
		return
	var c := _player.character
	MenuPanel.clear(_items)
	var refs: Array[String] = []
	for slot in CharacterData.SLOTS:
		if c.data.equipment.get(slot) != null:
			refs.append("eq:" + slot)
	for i in c.data.inventory.size():
		var item: Variant = c.data.inventory[i]
		if item != null and item.kind == Items.EQUIPMENT:
			refs.append("bag:%d" % i)
	for ref in refs:
		var item: Dictionary = Town.item_at(c, ref)
		if Refine.scroll_for(item, false) == "":
			continue
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 6)
		_items.add_child(row)
		var label := Label.new()
		label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		label.custom_minimum_size = Vector2(300, 0)
		label.text = Items.display_name(item) + ("  " + tr("FORGE_EQUIPPED") if ref.begins_with("eq:") else "")
		label.add_theme_color_override("font_color", Items.color(item))
		row.add_child(label)
		if int(item.refine) < int(GameData.refine.max):
			var percent := roundi(Refine.chance(item) * 100.0)
			var normal := c.count_of(Refine.scroll_for(item, false))
			var blessed := c.count_of(Refine.scroll_for(item, true))
			row.add_child(_refine_button(ref, false, percent, normal, int(item.refine) + 1 >= 4))
			row.add_child(_refine_button(ref, true, percent, blessed, false))
		if ref.begins_with("bag:"):
			var crush := _button(tr("FORGE_CRYSTALLIZE").format({"count": Refine.crystals_for(item)}),
				func() -> void: _town.request_crystallize(int(ref.get_slice(":", 1))))
			row.add_child(crush)
	MenuPanel.clear(_craft)
	for material in ["iron", "steel", "copper", "silver", "gold"]:
		var crystals := c.count_of("crystal_" + material)
		if crystals <= 0:
			continue
		for target in ["weapon", "armor"]:
			var scroll := "scroll_refine_%s_%s" % [target, material]
			var button := _button(tr("FORGE_CRAFT").format({"scroll": Items.display_name(Items.stack(Items.CONSUMABLE, scroll)),
				"count": GameData.refine.craft_crystals, "gold": Refine.craft_gold(scroll), "have": crystals}),
				func() -> void: _town.request_craft(scroll))
			button.disabled = crystals < int(GameData.refine.craft_crystals) or int(c.data.gold) < Refine.craft_gold(scroll)
			_craft.add_child(button)
	_info.text = tr("FORGE_INFO")
	_focus_first.call_deferred()


## Refinar: com risco (+4/+5 com pergaminho normal), o primeiro aperto pede confirmação.
func _refine_button(ref: String, blessed: bool, percent: int, scrolls: int, risky: bool) -> Button:
	var key := "FORGE_REFINE_BLESSED" if blessed else "FORGE_REFINE"
	var text := tr(key).format({"percent": percent, "count": scrolls})
	var button := _button(text, func() -> void: pass)
	button.disabled = scrolls <= 0
	button.pressed.connect(func() -> void:
		if risky and button.text == text:
			button.text = tr("FORGE_CONFIRM_RISK").format({"percent": percent})
			return
		_town.request_refine(ref, blessed))
	button.focus_exited.connect(func() -> void: button.text = text)
	return button


func _button(text: String, callback: Callable) -> Button:
	var button := Button.new()
	button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	button.text = text
	button.pressed.connect(callback)
	return button


func _focus_first() -> void:
	if not visible:
		return
	for row in _items.get_children() + _craft.get_children():
		for child in ([row] if row is Button else row.get_children()):
			if child is Button and not child.disabled and child.is_inside_tree() and not child.is_queued_for_deletion():
				child.grab_focus()
				return


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
	var title := Label.new()
	title.text = "FORGE_TITLE"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 24)
	outer.add_child(title)
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(900, 330)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	outer.add_child(scroll)
	_items = VBoxContainer.new()
	_items.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_items)
	_craft = VBoxContainer.new()
	outer.add_child(_craft)
	_info = Label.new()
	_info.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_info.custom_minimum_size = Vector2(900, 0)
	_info.modulate = Color(1, 1, 1, 0.7)
	outer.add_child(_info)
	var shop := Button.new()
	shop.text = "FORGE_SHOP"
	shop.pressed.connect(func() -> void:
		close()
		_town.shop_opened.emit("blacksmith"))
	outer.add_child(shop)
