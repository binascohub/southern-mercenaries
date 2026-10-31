# Southern Mercenaries — GPL-3.0-or-later
class_name BestiaryMenu
extends MenuPanel
## Bestiário do Bardo (03-1-bestiario.md): as criaturas cuja história o grupo já
## ouviu, com a lenda, o elemento, a fraqueza e a pista. Escolher uma mostra o
## texto completo embaixo.

var _town: Town
var _list: VBoxContainer
var _details: Label
var _empty: Label


func _ready() -> void:
	add_title("BESTIARY_TITLE")
	_empty = Label.new()
	_empty.text = "BESTIARY_NONE"
	content.add_child(_empty)
	_list = VBoxContainer.new()
	content.add_child(_list)
	_details = Label.new()
	_details.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_details.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_details.custom_minimum_size = Vector2(620, 120)
	content.add_child(_details)
	add_button("MENU_BACK", close)


func bind(town: Town) -> void:
	_town = town
	town.bestiary_opened.connect(func() -> void:
		Session.ui_open = true
		open())
	closed.connect(func() -> void: Session.ui_open = false)


func _on_open() -> void:
	clear(_list)
	_details.text = ""
	_empty.visible = _town.bestiary.is_empty()
	for id: String in _town.bestiary:
		var entry: Dictionary = GameData.bestiary.get(id, {})
		var button := Button.new()
		button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		button.custom_minimum_size = Vector2(420, 40)
		button.text = tr("BESTIARY_ENTRY").format({"name": tr(entry.name_key),
			"element": tr(Elements.data(entry.element).name_key),
			"weak": tr(Elements.data(Elements.weakness_of(entry.element)).name_key)})
		button.add_theme_color_override("font_color", Elements.color(entry.element))
		button.focus_entered.connect(func() -> void:
			_details.text = "%s\n\n\"%s\"" % [tr(entry.legend_key), tr(entry.hint_key)])
		_list.add_child(button)
