# Southern Mercenaries — GPL-3.0-or-later
class_name PortalMenu
extends MenuPanel
## Portais do Macumbeiro (04-tortuga-e-missoes.md, seção 5.1): lista os
## checkpoints já alcançados nos mapas, com o preço por jogador; escolher um
## leva o grupo todo (cada um paga com o próprio ouro).

var _town: Town
var _list: VBoxContainer
var _empty: Label


func _ready() -> void:
	add_title("PORTALS_TITLE")
	_empty = Label.new()
	_empty.text = "PORTALS_NONE"
	content.add_child(_empty)
	_list = VBoxContainer.new()
	content.add_child(_list)
	add_button("MENU_BACK", close)


func bind(town: Town) -> void:
	_town = town
	town.portals_opened.connect(func() -> void:
		Session.ui_open = true
		open())
	closed.connect(func() -> void: Session.ui_open = false)


func _on_open() -> void:
	clear(_list)
	_empty.visible = _town.reached.is_empty()
	for key: String in _town.reached:
		var area: Dictionary = GameData.arenas.get(key.get_slice(":", 0), {})
		var button := Button.new()
		button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		button.custom_minimum_size = Vector2(420, 44)
		button.text = tr("PORTALS_ENTRY").format({"area": tr(area.get("name_key", "")),
			"checkpoint": key.get_slice(":", 1), "price": Town.portal_price(key)})
		button.pressed.connect(func() -> void:
			_town.request_portal(key)
			close())
		_list.add_child(button)
