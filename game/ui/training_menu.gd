# Southern Mercenaries — GPL-3.0-or-later
class_name TrainingMenu
extends MenuPanel
## Quadro do pátio de treino (04-tortuga-e-missoes.md, seção 5.2): zerar o
## painel, reiniciar os bonecos e ligar/desligar "recursos e recargas livres".
## O painel em si (dano, DPS, maior golpe, críticos) fica no HUD dentro do pátio.

var _arena: Node


func _ready() -> void:
	add_title("TRAINING_TITLE")
	var info := Label.new()
	info.text = "TRAINING_INFO"
	info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	info.custom_minimum_size = Vector2(420, 0)
	content.add_child(info)
	add_button("TRAINING_RESET_STATS", func() -> void: _arena.request_training("reset_stats"))
	add_button("TRAINING_RESET_DUMMIES", func() -> void: _arena.request_training("reset_dummies"))
	add_button("TRAINING_TOGGLE_FREE", func() -> void: _arena.request_training("toggle_free"))
	add_button("MENU_BACK", close)


func bind(arena: Node, town: Town) -> void:
	_arena = arena
	town.training_opened.connect(func() -> void:
		Session.ui_open = true
		open())
	closed.connect(func() -> void: Session.ui_open = false)
