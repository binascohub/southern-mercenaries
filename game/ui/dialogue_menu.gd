# Southern Mercenaries — GPL-3.0-or-later
class_name DialogueMenu
extends CanvasLayer
## Conversa com um NPC (04-tortuga-e-missoes.md, seção 3): uma fala por vez
## (Continuar), e no fim aceitar/recusar a missão oferecida ou usar o serviço
## (descansar na taverna). As falas vêm de data/npcs.json (chaves de tradução).
## Não pausa o jogo; funciona só com o controle.

var _town: Town
var _npc_id := ""
var _dialogue: Dictionary = {}
var _line := 0
var _panel: PanelContainer
var _name: Label
var _text: Label
var _next: Button
var _accept: Button
var _decline: Button
var _service: Button


func _ready() -> void:
	layer = 6
	_build()
	visible = false


func bind(town: Town) -> void:
	_town = town
	town.dialogue_opened.connect(open)
	town.visitor_opened.connect(open_visitor)


## Visitante da taverna: falas montadas (história gerada) e a missão secundária.
func open_visitor(visitor_name: String, lines: Array, visitor_index: int) -> void:
	_npc_id = ""
	_dialogue = {"lines": lines, "offer": "side", "visitor": visitor_index}
	_line = 0
	_name.text = visitor_name
	visible = true
	Session.ui_open = true
	_show_line()


func open(npc_id: String, index: int) -> void:
	var npc: Dictionary = GameData.npcs.get(npc_id, {})
	var dialogues: Array = npc.get("dialogues", [])
	if index < 0 or index >= dialogues.size():
		return
	_npc_id = npc_id
	_dialogue = dialogues[index]
	_line = 0
	_name.text = tr(npc.get("name_key", ""))
	visible = true
	Session.ui_open = true
	_show_line()


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


func _show_line() -> void:
	var lines: Array = _dialogue.get("lines", [])
	_text.text = _line_text(lines[_line]) if _line < lines.size() else ""
	var last := _line >= lines.size() - 1
	var offer: String = _dialogue.get("offer", "")
	var service: String = _dialogue.get("service", "")
	_next.visible = not last
	_accept.visible = last and offer != ""
	_decline.visible = last and offer != ""
	_service.visible = last and service != ""
	if service != "":
		var price := Session.character.respec_price() if Session.character else 0
		_service.text = tr("DLG_SERVICE_" + service.to_upper()).format({"price": price})
	_next.text = tr("DLG_NEXT")
	# No fim de uma conversa sem escolha, "Continuar" fecha.
	if last and offer == "" and service == "":
		_next.visible = true
		_next.text = tr("DLG_CLOSE")
	var target: Button = _accept if _accept.visible else (_service if _service.visible else _next)
	target.grab_focus.call_deferred()


## Fala simples (chave) ou montada ([chave, args]); args que são chaves saem traduzidos.
func _line_text(line: Variant) -> String:
	if line is Array:
		var args := {}
		for k in line[1]:
			args[k] = tr(line[1][k]) if line[1][k] is String else line[1][k]
		return tr(line[0]).format(args)
	return tr(line)


func _advance() -> void:
	if _line >= _dialogue.get("lines", []).size() - 1:
		close()
		return
	_line += 1
	_show_line()


func _build() -> void:
	_panel = PanelContainer.new()
	_panel.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_panel.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_panel.offset_bottom = -120
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.09, 0.07, 0.06)
	style.border_color = Color(0.45, 0.33, 0.2)
	style.set_border_width_all(2)
	style.set_content_margin_all(16)
	_panel.add_theme_stylebox_override("panel", style)
	add_child(_panel)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 10)
	_panel.add_child(box)
	_name = Label.new()
	_name.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_name.add_theme_font_size_override("font_size", 22)
	_name.add_theme_color_override("font_color", Color(0.9, 0.8, 0.5))
	box.add_child(_name)
	_text = Label.new()
	_text.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text.custom_minimum_size = Vector2(760, 90)
	box.add_child(_text)
	var buttons := HBoxContainer.new()
	buttons.alignment = BoxContainer.ALIGNMENT_END
	buttons.add_theme_constant_override("separation", 10)
	box.add_child(buttons)
	_service = _button(buttons, func() -> void:
		_town.request_service(_npc_id, String(_dialogue.get("service", "")))
		close())
	_accept = _button(buttons, func() -> void:
		if _dialogue.has("visitor"):
			_town.request_accept_side(int(_dialogue.visitor))
		else:
			_town.request_accept(String(_dialogue.get("offer", "")))
		close())
	_accept.text = "DLG_ACCEPT"
	_accept.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_INHERIT
	_decline = _button(buttons, close)
	_decline.text = "DLG_DECLINE"
	_decline.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_INHERIT
	_next = _button(buttons, _advance)


func _button(parent: Node, callback: Callable) -> Button:
	var button := Button.new()
	button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	button.custom_minimum_size = Vector2(170, 40)
	button.pressed.connect(callback)
	parent.add_child(button)
	return button
