# Southern Mercenaries — GPL-3.0-or-later
class_name UiTheme
extends RefCounted
## Tema medieval da interface (09-interface.md, seção 7), num único Theme
## aplicado à janela principal: molduras de madeira escura com cantoneiras de
## ferro e fundo de couro; botões de tábua entalhada que clareiam no foco e
## afundam ao apertar; pergaminho com tinta escura nas conversas e dicas;
## barras como tubos de vidro. Fontes: Cinzel (títulos, maiúsculas entalhadas)
## e Alegreya (texto legível, com acentos), SIL OFL 1.1 (CREDITS.md).
##
## As texturas são geradas aqui (ruído de veios, rebites, manchas) como 9-patch
## pequenos: poucas texturas, reaproveitadas em todas as janelas. Quando houver
## molduras pintadas, basta trocar as texturas sem mexer nas telas.

const INK := Color(0.2, 0.13, 0.08)
const CREAM := Color(0.93, 0.87, 0.74)
const GOLD := Color(0.92, 0.76, 0.4)
const WOOD := Color(0.27, 0.17, 0.1)
const IRON := Color(0.36, 0.36, 0.38)
const LEATHER := Color(0.11, 0.085, 0.07)
const PARCHMENT := Color(0.85, 0.76, 0.58)

const FRAME := 18
const BODY_FONT := "res://assets/fonts/Alegreya.ttf"
const TITLE_FONT := "res://assets/fonts/Cinzel.ttf"

static var _theme: Theme


## O tema (criado uma vez).
static func get_theme() -> Theme:
	if _theme == null:
		_theme = build()
	return _theme


static func build() -> Theme:
	var theme := Theme.new()
	var body := _font(BODY_FONT)
	var title := _font(TITLE_FONT)
	if body:
		theme.default_font = body
	theme.default_font_size = 18

	# Janelas: madeira com cantoneiras de ferro, fundo de couro.
	var window := _texture_box(_frame_image(LEATHER, 0.97), FRAME, 22)
	for type in ["PanelContainer", "Panel", "PopupPanel", "PopupMenu"]:
		theme.set_stylebox("panel", type, window)
	# Pergaminho: conversas, abertura, dicas, diário.
	theme.set_type_variation("ParchmentPanel", "PanelContainer")
	theme.set_stylebox("panel", "ParchmentPanel", _texture_box(_parchment_image(), 14, 18))
	theme.set_type_variation("ParchmentLabel", "Label")
	theme.set_color("font_color", "ParchmentLabel", INK)
	theme.set_constant("outline_size", "ParchmentLabel", 0)
	# HUD: painéis pequenos e discretos nas bordas.
	theme.set_type_variation("HudPanel", "PanelContainer")
	theme.set_stylebox("panel", "HudPanel", _texture_box(_frame_image(Color(0.08, 0.06, 0.05), 0.82, 8), 8, 6))
	theme.set_stylebox("panel", "TooltipPanel", _texture_box(_parchment_image(), 14, 10))
	theme.set_color("font_color", "TooltipLabel", INK)

	# Textos.
	theme.set_color("font_color", "Label", CREAM)
	theme.set_type_variation("TitleLabel", "Label")
	if title:
		theme.set_font("font", "TitleLabel", title)
	theme.set_font_size("font_size", "TitleLabel", 30)
	theme.set_color("font_color", "TitleLabel", GOLD)
	theme.set_color("font_outline_color", "TitleLabel", Color(0.08, 0.05, 0.03))
	theme.set_constant("outline_size", "TitleLabel", 6)

	# Botões: tábuas entalhadas.
	theme.set_stylebox("normal", "Button", _texture_box(_plank_image(1.0, false, false), 8, 10))
	theme.set_stylebox("hover", "Button", _texture_box(_plank_image(1.2, true, false), 8, 10))
	theme.set_stylebox("pressed", "Button", _texture_box(_plank_image(0.8, true, true), 8, 10))
	theme.set_stylebox("disabled", "Button", _texture_box(_plank_image(0.55, false, false), 8, 10))
	theme.set_stylebox("hover_pressed", "Button", _texture_box(_plank_image(0.9, true, true), 8, 10))
	var focus := StyleBoxFlat.new()
	focus.draw_center = false
	focus.border_color = GOLD
	focus.set_border_width_all(2)
	focus.set_corner_radius_all(3)
	focus.set_expand_margin_all(2)
	theme.set_stylebox("focus", "Button", focus)
	theme.set_color("font_color", "Button", CREAM)
	theme.set_color("font_hover_color", "Button", Color(1.0, 0.94, 0.8))
	theme.set_color("font_focus_color", "Button", Color(1.0, 0.92, 0.7))
	theme.set_color("font_pressed_color", "Button", GOLD)
	theme.set_color("font_disabled_color", "Button", Color(0.6, 0.55, 0.48, 0.7))
	theme.set_color("font_outline_color", "Button", Color(0.06, 0.04, 0.02))
	theme.set_constant("outline_size", "Button", 3)

	# Campos de texto e listas: couro afundado com borda de ferro.
	var inset := StyleBoxFlat.new()
	inset.bg_color = Color(0.06, 0.05, 0.04, 0.9)
	inset.border_color = IRON.darkened(0.2)
	inset.set_border_width_all(2)
	inset.set_corner_radius_all(3)
	inset.set_content_margin_all(6)
	for type in ["LineEdit", "ItemList", "TextEdit"]:
		theme.set_stylebox("normal", type, inset)
	theme.set_stylebox("focus", "LineEdit", focus)
	theme.set_color("font_color", "LineEdit", CREAM)

	# Barras: tubos de vidro com aro de metal (o líquido é a cor de cada barra).
	theme.set_stylebox("background", "ProgressBar", bar_background())
	theme.set_stylebox("fill", "ProgressBar", bar_fill(Color(0.75, 0.15, 0.1)))
	# Deslizantes e rolagem.
	var slider := StyleBoxFlat.new()
	slider.bg_color = Color(0.08, 0.06, 0.05)
	slider.border_color = IRON
	slider.set_border_width_all(1)
	slider.set_corner_radius_all(3)
	slider.content_margin_top = 4
	slider.content_margin_bottom = 4
	theme.set_stylebox("slider", "HSlider", slider)
	var grabber := StyleBoxFlat.new()
	grabber.bg_color = GOLD.darkened(0.3)
	grabber.set_corner_radius_all(3)
	theme.set_stylebox("grabber_area", "HSlider", grabber)
	theme.set_stylebox("grabber_area_highlight", "HSlider", grabber)
	var scroll := StyleBoxFlat.new()
	scroll.bg_color = Color(0.05, 0.04, 0.03, 0.6)
	scroll.set_corner_radius_all(4)
	var grab := StyleBoxFlat.new()
	grab.bg_color = WOOD.lightened(0.15)
	grab.set_corner_radius_all(4)
	for type in ["VScrollBar", "HScrollBar"]:
		theme.set_stylebox("scroll", type, scroll)
		theme.set_stylebox("grabber", type, grab)
		theme.set_stylebox("grabber_highlight", type, grab)
		theme.set_stylebox("grabber_pressed", type, grab)
	# Divisores de ferro forjado.
	var line := StyleBoxLine.new()
	line.color = IRON
	line.thickness = 2
	theme.set_stylebox("separator", "HSeparator", line)
	return theme


## Fundo das barras: vidro escuro com aro de metal.
static func bar_background() -> StyleBox:
	var bg := StyleBoxFlat.new()
	bg.bg_color = Color(0.04, 0.03, 0.03, 0.8)
	bg.border_color = Color(0.55, 0.5, 0.42)
	bg.set_border_width_all(2)
	bg.set_corner_radius_all(7)
	return bg


## Líquido da barra: a cor dada com brilho em cima e sombra embaixo (vidro).
static func bar_fill(color: Color) -> StyleBox:
	var image := Image.create(4, 16, false, Image.FORMAT_RGBA8)
	for y in 16:
		var t := y / 15.0
		var shade := color.lightened(0.45 * (1.0 - t / 0.3)) if t < 0.3 else color.darkened(0.35 * (t - 0.3) / 0.7)
		for x in 4:
			image.set_pixel(x, y, shade)
	var box := StyleBoxTexture.new()
	box.texture = ImageTexture.create_from_image(image)
	box.set_texture_margin_all(1)
	box.set_expand_margin_all(-2)
	return box


static func _font(path: String) -> Font:
	if not ResourceLoader.exists(path):
		return null
	return load(path) as Font


static func _texture_box(image: Image, margin: int, content: int) -> StyleBoxTexture:
	var box := StyleBoxTexture.new()
	box.texture = ImageTexture.create_from_image(image)
	box.set_texture_margin_all(margin)
	box.set_content_margin_all(content)
	box.axis_stretch_horizontal = StyleBoxTexture.AXIS_STRETCH_MODE_TILE_FIT
	box.axis_stretch_vertical = StyleBoxTexture.AXIS_STRETCH_MODE_TILE_FIT
	return box


static func _noise(seed_: int, frequency: float) -> FastNoiseLite:
	var noise := FastNoiseLite.new()
	noise.seed = seed_
	noise.frequency = frequency
	return noise


## Moldura: madeira com veios, bisel, cantoneiras de ferro com rebites e o fundo.
static func _frame_image(fill: Color, fill_alpha: float, frame := FRAME) -> Image:
	var size := frame * 4
	var image := Image.create(size, size, false, Image.FORMAT_RGBA8)
	var grain := _noise(7, 0.08)
	var spots := _noise(11, 0.3)
	for y in size:
		for x in size:
			var edge := mini(mini(x, y), mini(size - 1 - x, size - 1 - y))
			var color: Color
			if edge < frame:
				# Veios correm ao longo de cada lado.
				var along := x if (y < frame or y >= size - frame) else y
				var across := y if (y < frame or y >= size - frame) else x
				var v := grain.get_noise_2d(along * 0.35, across * 3.0)
				color = WOOD.lightened(0.12 * v) if v > 0 else WOOD.darkened(-0.25 * v)
				if edge < 2 or edge >= frame - 2:
					color = color.darkened(0.45)  # bisel escuro por fora e por dentro
				elif edge == 2:
					color = color.lightened(0.15)
			else:
				var s := spots.get_noise_2d(x, y)
				color = fill.lightened(0.05 * s) if s > 0 else fill.darkened(-0.1 * s)
				color.a = fill_alpha
				# Sombra interna junto à moldura.
				if edge < frame + 4:
					color = color.darkened(0.35 * (1.0 - (edge - frame) / 4.0))
			image.set_pixel(x, y, color)
	# Cantoneiras de ferro com dois rebites.
	for corner in [Vector2i(0, 0), Vector2i(size - frame, 0), Vector2i(0, size - frame), Vector2i(size - frame, size - frame)]:
		for y in frame:
			for x in frame:
				var n := spots.get_noise_2d(corner.x + x, corner.y + y)
				var c := IRON.lightened(0.1 * n) if n > 0 else IRON.darkened(-0.2 * n)
				if x < 1 or y < 1 or x >= frame - 1 or y >= frame - 1:
					c = c.darkened(0.5)
				image.set_pixel(corner.x + x, corner.y + y, c)
		for rivet in [Vector2i(frame / 3, frame / 3), Vector2i(frame * 2 / 3, frame * 2 / 3)]:
			for dy in range(-2, 3):
				for dx in range(-2, 3):
					var d := Vector2(dx, dy).length()
					if d <= 2.2:
						var c := Color(0.7, 0.7, 0.72) if (dx < 0 and dy < 0) else (Color(0.15, 0.15, 0.16) if d > 1.5 else Color(0.5, 0.5, 0.52))
						image.set_pixel(corner.x + rivet.x + dx, corner.y + rivet.y + dy, c)
	return image


## Tábua de botão: madeira mais clara, bisel (afundado quando apertado), pregos.
static func _plank_image(brightness: float, rim: bool, sunken: bool) -> Image:
	var w := 64
	var h := 32
	var image := Image.create(w, h, false, Image.FORMAT_RGBA8)
	var grain := _noise(23, 0.09)
	var base := Color(0.36, 0.24, 0.14) * brightness
	base.a = 1.0
	for y in h:
		for x in w:
			var v := grain.get_noise_2d(x * 0.4, y * 2.5)
			var color := base.lightened(0.12 * v) if v > 0 else base.darkened(-0.25 * v)
			var top := y < 2
			var bottom := y >= h - 2
			if (top and not sunken) or (bottom and sunken):
				color = color.lightened(0.25)
			elif (bottom and not sunken) or (top and sunken):
				color = color.darkened(0.45)
			if x < 1 or x >= w - 1 or y < 1 or y >= h - 1:
				color = IRON.lightened(0.2) if rim else color.darkened(0.6)
			image.set_pixel(x, y, color)
	for nail in [Vector2i(4, h / 2), Vector2i(w - 5, h / 2)]:
		for dy in range(-1, 2):
			for dx in range(-1, 2):
				image.set_pixel(nail.x + dx, nail.y + dy, Color(0.55, 0.55, 0.57) if dx + dy < 0 else Color(0.2, 0.2, 0.22))
	return image


## Pergaminho: manchas suaves e bordas queimadas.
static func _parchment_image() -> Image:
	var size := 64
	var image := Image.create(size, size, false, Image.FORMAT_RGBA8)
	var blotch := _noise(5, 0.06)
	var fiber := _noise(9, 0.5)
	for y in size:
		for x in size:
			var edge := mini(mini(x, y), mini(size - 1 - x, size - 1 - y))
			var color := PARCHMENT.darkened(0.12 * (blotch.get_noise_2d(x, y) + 1.0) / 2.0)
			color = color.darkened(0.05 * fiber.get_noise_2d(x, y))
			if edge < 6:
				color = color.darkened(0.55 * (1.0 - edge / 6.0))
			color.a = 0.97 if edge > 0 else 0.0
			image.set_pixel(x, y, color)
	return image
