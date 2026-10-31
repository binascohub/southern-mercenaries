# Southern Mercenaries — GPL-3.0-or-later
extends Node
## O que o jogador escolheu no menu: o personagem dele e, se for hospedar ou
## jogar sozinho, a campanha (11-saves.md). O servidor recebe o personagem de
## cada cliente na entrada (07-rede.md, seção 3).

## Personagem deste PC (cópia local; durante a partida o servidor manda as mudanças).
var character: CharacterData
## Campanha que este PC hospeda (solo ou host). Vazia para clientes.
var campaign: Dictionary = {}
## Uma janela de jogo (inventário) está aberta: o herói não ataca.
var ui_open := false


func _ready() -> void:
	var last: String = Settings.last_character
	if last != "":
		character = SaveSystem.load_character(last)


func select_character(c: CharacterData) -> void:
	character = c
	Settings.set_value("last_character", c.data.id)


## Personagem para entrar numa partida (cria um padrão se o jogador não tiver).
func ensure_character() -> CharacterData:
	if character == null:
		var cls := GameData.get_class_data("mage")
		var c := CharacterData.create("mage", "male", TranslationServer.translate(cls.hero_name_keys.male))
		SaveSystem.save_character(c)
		select_character(c)
	return character


func continue_or_new_campaign() -> void:
	var campaigns := SaveSystem.list_campaigns()
	campaign = campaigns[0] if not campaigns.is_empty() else SaveSystem.new_campaign()


func start_new_campaign() -> void:
	campaign = SaveSystem.new_campaign()
	SaveSystem.save_campaign(campaign)
