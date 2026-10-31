# Southern Mercenaries — GPL-3.0-or-later
class_name StashMenu
extends CanvasLayer
## Baú da Rua Principal (04-tortuga-e-missoes.md, seção 2): à esquerda a bolsa
## (apertar guarda no baú), à direita o baú (apertar tira para a bolsa). O baú é
## do jogador, compartilhado entre os personagens deste PC; a passagem entre
## bolsa e baú é feita pelo servidor (Town). Funciona só com o controle.

var _town: Town
var _player: Player
var _panel: PanelContainer
var _bag_list: VBoxContainer
var _stash_list: VBoxContainer


func _ready() -> void:
	layer = 6
	_build()
	visible = false


func bind(town: Town) -> void:
	_town = town
	town.stash_opened.connect(func() -> void:
		if not visible:
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
	MenuPanel.clear(_bag_list)
	MenuPanel.clear(_stash_list)
	var bag: Array = _player.character.data.inventory
	for i in bag.size():
		if bag[i] != null:
			_bag_list.add_child(_row(bag[i], func() -> void: _town.request_deposit(i)))
	var stash := SaveSystem.load_stash()
	for i in stash.size():
		if stash[i] != null:
			_stash_list.add_child(_row(stash[i], func() -> void: _town.request_withdraw(i)))
	_focus_first.call_deferred()


## Escolhe o botão na hora de focar (a lista pode ter sido refeita no meio do quadro).
func _focus_first() -> void:
	if not visible:
		return
	for list in [_bag_list, _stash_list]:
		for child in list.get_children():
			if child.is_inside_tree() and not child.is_queued_for_deletion():
				(child as Control).grab_focus()
				return


func _row(item: Dictionary, callback: Callable) -> Button:
	var button := Button.new()
	button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	button.custom_minimum_size = Vector2(360, 34)
	button.text = Items.display_name(item) + (" x%d" % item.count if item.has("count") and int(item.count) > 1 else "")
	if item.kind == Items.EQUIPMENT:
		button.add_theme_color_override("font_color", Items.color(item))
	button.pressed.connect(callback)
	return button


func _build() -> void:
	_panel = PanelContainer.new()
	_panel.set_anchors_preset(Control.PRESET_CENTER)
	_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	add_child(_panel)
	var outer := VBoxContainer.new()
	_panel.add_child(outer)
	var title := Label.new()
	title.text = "STASH_TITLE"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.theme_type_variation = &"TitleLabel"
	title.add_theme_font_size_override("font_size", 24)
	outer.add_child(title)
	var columns := HBoxContainer.new()
	columns.add_theme_constant_override("separation", 16)
	outer.add_child(columns)
	for side in [["STASH_BAG", true], ["STASH_CHEST", false]]:
		var col := VBoxContainer.new()
		columns.add_child(col)
		var head := Label.new()
		head.text = side[0]
		col.add_child(head)
		var scroll := ScrollContainer.new()
		scroll.custom_minimum_size = Vector2(380, 380)
		scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		col.add_child(scroll)
		var list := VBoxContainer.new()
		list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		scroll.add_child(list)
		if side[1]:
			_bag_list = list
		else:
			_stash_list = list
	var hint := Label.new()
	hint.text = "STASH_HINT"
	hint.modulate = Color(1, 1, 1, 0.7)
	outer.add_child(hint)
