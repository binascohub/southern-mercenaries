# Southern Mercenaries — GPL-3.0-or-later
class_name CampaignMenu
extends MenuPanel
## Carregar campanha (11-saves.md, seções 3 e 5): lista as campanhas deste PC,
## da mais recente para a mais antiga, com data, tempo de jogo, área e heróis.
## Só o host continua uma campanha; a opção "hospedar na LAN" abre a mesma
## campanha para os amigos entrarem.

## `host` = abrir na LAN em vez de jogar sozinho.
signal chosen(campaign: Dictionary, host: bool)

var _list: VBoxContainer
var _host: CheckButton
var _empty: Label


func _ready() -> void:
	add_title("CAMPAIGN_LOAD_TITLE")
	_host = CheckButton.new()
	_host.text = "CAMPAIGN_HOST_LAN"
	content.add_child(_host)
	_empty = Label.new()
	_empty.text = "CAMPAIGN_NONE"
	_empty.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	content.add_child(_empty)
	_list = VBoxContainer.new()
	_list.add_theme_constant_override("separation", 6)
	content.add_child(_list)
	add_button("MENU_BACK", close)


func _on_open() -> void:
	for child in _list.get_children():
		child.queue_free()
	var campaigns := SaveSystem.list_campaigns()
	_empty.visible = campaigns.is_empty()
	for c in campaigns:
		var button := Button.new()
		button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		button.custom_minimum_size = Vector2(420, 56)
		button.text = describe(c)
		button.pressed.connect(func() -> void:
			visible = false
			chosen.emit(c, _host.button_pressed))
		_list.add_child(button)


## Uma linha por campanha: área, data, tempo de jogo e heróis.
static func describe(c: Dictionary) -> String:
	var area: Dictionary = GameData.arenas.get(c.get("area", ""), {})
	var names: Array = c.get("hero_names", {}).values()
	var summary := str(TranslationServer.translate("CAMPAIGN_ENTRY")).format({
		"area": str(TranslationServer.translate(area.get("name_key", ""))),
		"date": str(c.get("updated", c.get("created", ""))).replace("T", " ").left(16),
		"time": SaveSystem.format_played(float(c.get("played_seconds", 0))),
	})
	if not names.is_empty():
		summary += "\n" + ", ".join(PackedStringArray(names))
	return summary
