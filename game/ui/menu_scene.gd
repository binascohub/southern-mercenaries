# Southern Mercenaries — GPL-3.0-or-later
class_name MenuScene
extends Control
## Fundo do menu principal: a capa do jogo (assets/ui/menu_cover.jpg, sem texto), preenchendo a
## janela sem distorcer, com um véu escuro à esquerda para o título e os botões lerem bem.
## É uma imagem, não uma cena montada em código.

const COVER := "res://assets/ui/menu_cover.jpg"


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var cover := TextureRect.new()
	if ResourceLoader.exists(COVER):
		cover.texture = load(COVER) as Texture2D
	cover.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	cover.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	cover.set_anchors_preset(Control.PRESET_FULL_RECT)
	cover.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(cover)
	var gradient := Gradient.new()
	gradient.set_color(0, Color(0.03, 0.02, 0.04, 0.7))
	gradient.set_color(1, Color(0.03, 0.02, 0.04, 0.0))
	var texture := GradientTexture2D.new()
	texture.gradient = gradient
	texture.fill_from = Vector2(0, 0)
	texture.fill_to = Vector2(1, 0)
	var veil := TextureRect.new()
	veil.texture = texture
	veil.stretch_mode = TextureRect.STRETCH_SCALE
	veil.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	veil.mouse_filter = Control.MOUSE_FILTER_IGNORE
	veil.anchor_right = 0.42
	veil.anchor_bottom = 1.0
	add_child(veil)
