# Southern Mercenaries — GPL-3.0-or-later
class_name PortalMenu
extends MenuPanel
## Viajante do Tempo (antes o Macumbeiro; 04-tortuga-e-missoes.md, seção 5.1): teleporte entre Tortuga, Capital e Fazenda (todas
## na lista; as outras ficam travadas até concluir as missões de aldeia dos mapas da cidade atual) e, abaixo, os checkpoints
## já alcançados nos mapas, com o preço por jogador; escolher um leva o grupo todo (cada um paga com o próprio ouro nos checkpoints).

var _town: Town
var _list: VBoxContainer
var _hubs: VBoxContainer
var _empty: Label


func _ready() -> void:
	add_title("PORTALS_TITLE")
	_hubs = VBoxContainer.new()
	content.add_child(_hubs)
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
	clear(_hubs)
	var here: String = _town._arena().area_id
	var left := Town.hub_pending(here, _town.quests)
	for hub: String in Town.HUB_MAPS:
		var city := tr(GameData.arenas.get(hub, {}).get("name_key", ""))
		var hub_button := Button.new()
		hub_button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		hub_button.custom_minimum_size = Vector2(420, 44)
		if hub == here:
			hub_button.text = tr("PORTALS_HERE").format({"city": city})
			hub_button.disabled = true
		elif left > 0:
			hub_button.text = tr("PORTALS_LOCKED").format({"city": city, "here": tr(GameData.arenas.get(here, {}).get("name_key", "")), "n": left})
			hub_button.disabled = true
		else:
			hub_button.text = tr("PORTALS_GO").format({"city": city})
			hub_button.pressed.connect(func() -> void:
				_town.request_hub_travel(hub)
				close())
		_hubs.add_child(hub_button)
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
