# Southern Mercenaries — GPL-3.0-or-later
class_name MenuPanel
extends PanelContainer
## Base dos menus: painel centralizado, navegável só com o controle, que
## fecha com ui_cancel e devolve o foco para quem o abriu.

signal closed

var content: VBoxContainer
var _return_focus: Control


func _init() -> void:
	set_anchors_preset(Control.PRESET_CENTER)
	grow_horizontal = Control.GROW_DIRECTION_BOTH
	grow_vertical = Control.GROW_DIRECTION_BOTH
	process_mode = Node.PROCESS_MODE_ALWAYS
	theme = UiTheme.paper_theme()
	var margin := MarginContainer.new()
	for side in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 24)
	add_child(margin)
	content = VBoxContainer.new()
	content.add_theme_constant_override("separation", 10)
	margin.add_child(content)
	visible = false


func open(return_focus: Control = null) -> void:
	_return_focus = return_focus
	visible = true
	_on_open()
	focus_first.call_deferred()


func close() -> void:
	visible = false
	closed.emit()
	if is_instance_valid(_return_focus):
		_return_focus.grab_focus()


func focus_first() -> void:
	for child in _focusables(content):
		child.grab_focus()
		return


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
		close()


## Para subclasses: atualizar conteúdo ao abrir.
func _on_open() -> void:
	pass


func add_title(key: String) -> Label:
	var label := Label.new()
	label.text = key
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.theme_type_variation = &"TitleLabel"
	content.add_child(label)
	content.add_child(OrnamentDivider.new())
	return label


func add_button(key: String, callback: Callable) -> Button:
	var button := Button.new()
	button.text = key
	button.custom_minimum_size = Vector2(320, 44)
	button.pressed.connect(callback)
	content.add_child(button)
	return button


## Botão "Apagar" (saves): o primeiro aperto pede confirmação, o segundo apaga
## e reabre o menu com a lista atualizada.
func delete_button(on_delete: Callable) -> Button:
	var button := Button.new()
	button.text = "SAVE_DELETE"
	button.custom_minimum_size = Vector2(120, 44)
	button.pressed.connect(func() -> void:
		if button.text != "SAVE_DELETE_CONFIRM":
			button.text = "SAVE_DELETE_CONFIRM"
			return
		on_delete.call()
		_reopen.call_deferred())
	button.focus_exited.connect(func() -> void: button.text = "SAVE_DELETE")
	return button


## Tira os filhos já (para o foco não cair num nó que vai sumir).
static func clear(node: Node) -> void:
	for child in node.get_children():
		node.remove_child(child)
		child.queue_free()


func _reopen() -> void:
	_on_open()
	focus_first()


static func _focusables(node: Node) -> Array[Control]:
	var found: Array[Control] = []
	for child in node.get_children():
		if child is Control and child.visible and child.focus_mode == Control.FOCUS_ALL:
			found.append(child)
		found.append_array(_focusables(child))
	return found
