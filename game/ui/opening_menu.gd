# Southern Mercenaries — GPL-3.0-or-later
class_name OpeningMenu
extends CanvasLayer
## Abertura na Taverna (06-mundo-e-historia.md, seção 5; 14-tutorial.md, seção 2):
## as histórias dos heróis, uma fala por vez, com quem fala em cima (a narração
## fica sem nome). Cada PC lê no seu ritmo; nada pausa o jogo. "Pular abertura"
## fecha na hora (as missões continuam com o velho bêbado). Só com o controle.

var _lines: Array = []
var _line := 0
var _panel: PanelContainer
var _speaker: Label
var _text: Label
var _next: Button
var _skip: Button


func _ready() -> void:
	layer = 6
	_build()
	visible = false


func bind(town: Town) -> void:
	town.opening_started.connect(open)


func open(players: Array) -> void:
	_lines = Opening.lines(players)
	if _lines.is_empty():
		return
	_line = 0
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


func current_key() -> String:
	return String(_lines[_line].key) if visible and _line < _lines.size() else ""


func _show_line() -> void:
	var line: Dictionary = _lines[_line]
	var args := {}
	for k: String in line.args:
		args[k] = line.args[k]
	_speaker.text = line.speaker
	_speaker.visible = line.speaker != ""
	_text.text = tr(line.key).format(args)
	# Narração em cinza claro; as falas dos heróis em branco.
	_text.add_theme_color_override("font_color", Color(0.78, 0.74, 0.68) if line.speaker == "" else Color.WHITE)
	var last := _line >= _lines.size() - 1
	_next.text = tr("DLG_CLOSE") if last else tr("DLG_NEXT")
	_skip.visible = not last
	_next.grab_focus.call_deferred()


func _advance() -> void:
	if _line >= _lines.size() - 1:
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
	var title := Label.new()
	title.text = "OPENING_TITLE"
	title.add_theme_font_size_override("font_size", 16)
	title.modulate = Color(1, 1, 1, 0.6)
	box.add_child(title)
	_speaker = Label.new()
	_speaker.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_speaker.add_theme_font_size_override("font_size", 22)
	_speaker.add_theme_color_override("font_color", Color(0.9, 0.8, 0.5))
	box.add_child(_speaker)
	_text = Label.new()
	_text.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text.custom_minimum_size = Vector2(760, 90)
	box.add_child(_text)
	var buttons := HBoxContainer.new()
	buttons.alignment = BoxContainer.ALIGNMENT_END
	buttons.add_theme_constant_override("separation", 10)
	box.add_child(buttons)
	_skip = _button(buttons, close)
	_skip.text = "OPENING_SKIP"
	_skip.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_INHERIT
	_next = _button(buttons, _advance)


func _button(parent: Node, callback: Callable) -> Button:
	var button := Button.new()
	button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	button.custom_minimum_size = Vector2(170, 40)
	button.pressed.connect(callback)
	parent.add_child(button)
	return button
