# Southern Mercenaries — GPL-3.0-or-later
class_name PortalMenu
extends MenuPanel
## Viajante do Tempo (antes o Macumbeiro; 04-tortuga-e-missoes.md, seção 5.1): teleporte entre Tortuga, Capital e Fazenda (todas
## na lista; voltar a uma cidade anterior é livre, a próxima fica travada até concluir os mapas da cidade atual) e, abaixo, os checkpoints já alcançados nos mapas
## (menos os que um portão da cidade alcança de graça), com o preço por jogador; escolher um leva o grupo todo (cada um paga com o próprio ouro nos checkpoints).

## Medalhões dos botões das cidades (assets/ui/map_icons, Board Game Icons da Kenney): ampulheta do Viajante e cadeado da cidade travada.
const ICON_TRAVEL := preload("res://assets/ui/map_icons/teleporter.png")
const ICON_LOCKED := preload("res://assets/ui/map_icons/locked.png")

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
	for hub: String in Town.HUB_MAPS:
		var left := Town.hub_locked(here, hub, _town.quests)
		var city := tr(GameData.arenas.get(hub, {}).get("name_key", ""))
		var hub_button := Button.new()
		hub_button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		hub_button.custom_minimum_size = Vector2(420, 44)
		hub_button.add_theme_constant_override("icon_max_width", 28)
		if hub == here:
			hub_button.text = tr("PORTALS_HERE").format({"city": city})
			hub_button.disabled = true
		elif left > 0:
			hub_button.text = tr("PORTALS_LOCKED").format({"city": city, "here": tr(GameData.arenas.get(here, {}).get("name_key", "")), "n": left})
			hub_button.disabled = true
			hub_button.icon = ICON_LOCKED
		else:
			hub_button.text = tr("PORTALS_GO").format({"city": city})
			hub_button.icon = ICON_TRAVEL
			hub_button.pressed.connect(func() -> void:
				_town.request_hub_travel(hub)
				close())
		_hubs.add_child(hub_button)
	clear(_list)
	# Pontos onde um portão desta cidade já leva de graça (o início dos mapas dela) não entram na lista paga.
	var free: Array[String] = []
	for prop: Dictionary in _town._arena().arena.get("props", []):
		if prop.get("kind", "") == "exit" and prop.has("to"):
			free.append("%s:%s" % [prop.to, prop.get("entry", "start")])
	var paid := _town.reached.filter(func(key: String) -> bool: return key not in free)
	_empty.visible = paid.is_empty()
	for key: String in paid:
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
