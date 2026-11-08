# Southern Mercenaries — GPL-3.0-or-later
class_name UiTheme
extends RefCounted
## Tema medieval da interface (09-interface.md, seção 7), num único Theme
## aplicado à janela principal: molduras de couro escuro com filete e cantoneiras de
## ouro (a identidade do brasão: ouro, noite azul-marinho e lacre vermelho); botões de
## couro com aro de latão que acende em ouro no foco; pergaminho com tinta escura nas conversas e dicas;
## barras como tubos de vidro. Fontes: Cinzel (títulos, maiúsculas entalhadas)
## e Alegreya (texto legível, com acentos), SIL OFL 1.1 (CREDITS.md).
##
## As texturas são geradas aqui (ruído de veios, rebites, manchas) como 9-patch
## pequenos: poucas texturas, reaproveitadas em todas as janelas. Quando houver
## molduras pintadas, basta trocar as texturas sem mexer nas telas.

const INK := Color(0.2, 0.13, 0.08)
const CREAM := Color(0.93, 0.87, 0.74)
const GOLD := Color(0.92, 0.76, 0.4)
const IRON := Color(0.36, 0.36, 0.38)
const LEATHER := Color(0.11, 0.085, 0.07)
const PARCHMENT := Color(0.85, 0.76, 0.58)

const FRAME := 14
## A sombra interna fica na borda do 9-patch (o centro é liso, sem emendas).
const SHADOW := 4
const BODY_FONT := "res://assets/fonts/Alegreya.ttf"
const TITLE_FONT := "res://assets/fonts/Cinzel.ttf"
## Título do jogo (gótica de pirata) e texto dos menus (tipografia de livro antigo).
const GAME_FONT := "res://assets/fonts/PirataOne.ttf"
const BOOK_FONT := "res://assets/fonts/IMFellEnglish.ttf"
const PAPER_MARGIN := 30
const WAX := Color(0.55, 0.11, 0.09)
const BRASS := Color(0.55, 0.43, 0.2)
## Molduras da Kenney (Fantasy UI Borders, CC0; assets/ui/borders): brancas, tingidas aqui e desenhadas por dentro da
## borda do papel (o 9-patch repete as linhas retas, então elas seguem a janela de qualquer tamanho).
const WINDOW_BORDER := "res://assets/ui/borders/window_border.png"
const BOX_BORDER := "res://assets/ui/borders/box_border.png"
## Tamanho dos cantos da moldura (pixels da imagem de 48) e o recuo dela a partir da beira do papel.
const BORDER_CORNER := 16
const BORDER_INSET := 11
## Cor da moldura sobre o papel: latão escuro (ouro claro some no pergaminho).
const FRAME_INK := Color(0.42, 0.28, 0.09)

static var _theme: Theme


## Vale para todos os controles, inclusive os que estão em CanvasLayers (que
## não herdam o tema da janela): mescla no tema padrão do Godot.
static func apply() -> void:
	var theme := get_theme()
	var default := ThemeDB.get_default_theme()
	default.merge_with(theme)
	if theme.default_font:
		default.default_font = theme.default_font
		ThemeDB.fallback_font = theme.default_font
	default.default_font_size = theme.default_font_size
	ThemeDB.fallback_font_size = theme.default_font_size


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
	theme.default_font_size = 17

	# Janelas: pergaminho com moldura dupla de latão (Kenney Fantasy UI Borders) por dentro da borda queimada.
	var window := _tiled_box(_framed(_paper_image(PARCHMENT), WINDOW_BORDER, FRAME_INK), PAPER_MARGIN, 32)  # o conteúdo começa depois da moldura
	for type in ["PanelContainer", "Panel", "PopupPanel", "PopupMenu"]:
		theme.set_stylebox("panel", type, window)
	# Pergaminho: conversas, abertura, dicas, diário.
	theme.set_type_variation("ParchmentPanel", "PanelContainer")
	theme.set_stylebox("panel", "ParchmentPanel", _tiled_box(_framed(_paper_image(PARCHMENT.lightened(0.04)), BOX_BORDER, FRAME_INK), PAPER_MARGIN, 32))
	theme.set_type_variation("ParchmentLabel", "Label")
	theme.set_color("font_color", "ParchmentLabel", INK)
	theme.set_constant("outline_size", "ParchmentLabel", 0)
	# HUD: painéis pequenos e discretos nas bordas.
	theme.set_type_variation("HudPanel", "PanelContainer")
	theme.set_stylebox("panel", "HudPanel", _texture_box(_frame_image(Color(0.08, 0.06, 0.05), 0.82, 6), 6 + SHADOW, 6))
	# Pergaminho compacto, sem moldura: caixas pequenas (atalhos da janela de habilidades, dicas e avisos do HUD).
	theme.set_type_variation("CompactPaper", "PanelContainer")
	theme.set_stylebox("panel", "CompactPaper", _tiled_box(_paper_image(PARCHMENT), PAPER_MARGIN, 12))
	theme.set_stylebox("panel", "TooltipPanel", _tiled_box(_paper_image(PARCHMENT), PAPER_MARGIN, 14))
	theme.set_color("font_color", "TooltipLabel", INK)

	# Textos.
	theme.set_color("font_color", "Label", CREAM)
	theme.set_type_variation("TitleLabel", "Label")
	if title:
		theme.set_font("font", "TitleLabel", title)
	if _font(GAME_FONT):
		theme.set_font("font", "TitleLabel", _font(GAME_FONT))
	theme.set_font_size("font_size", "TitleLabel", 40)
	theme.set_color("font_color", "TitleLabel", GOLD)
	theme.set_color("font_outline_color", "TitleLabel", Color(0.08, 0.05, 0.03))
	theme.set_constant("outline_size", "TitleLabel", 6)

	# Botões: couro escuro com aro de latão, que acende em ouro no foco.
	theme.set_font_size("font_size", "Button", 17)
	theme.set_stylebox("normal", "Button", _button_box(Color(0.13, 0.1, 0.08), BRASS.darkened(0.15)))
	theme.set_stylebox("hover", "Button", _button_box(Color(0.2, 0.15, 0.1), GOLD))
	theme.set_stylebox("pressed", "Button", _button_box(Color(0.08, 0.06, 0.05), GOLD.darkened(0.2)))
	theme.set_stylebox("disabled", "Button", _button_box(Color(0.1, 0.085, 0.075), Color(0.3, 0.27, 0.22)))
	theme.set_stylebox("hover_pressed", "Button", _button_box(Color(0.12, 0.09, 0.07), GOLD.darkened(0.2)))
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

	# Campos de seleção: o mesmo couro dos botões.
	for state in ["normal", "hover", "pressed", "disabled"]:
		theme.set_stylebox(state, "OptionButton", theme.get_stylebox(state, "Button"))
	theme.set_stylebox("focus", "OptionButton", focus)
	for color_name in ["font_color", "font_hover_color", "font_focus_color", "font_pressed_color", "font_disabled_color", "font_outline_color"]:
		theme.set_color(color_name, "OptionButton", theme.get_color(color_name, "Button"))
	theme.set_constant("outline_size", "OptionButton", 3)

	_add_menu_styles(theme)

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
	grab.bg_color = BRASS.darkened(0.2)
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


## Estilos do menu principal: o título gótico, as entradas de livro-razão (texto sobre
## a noite, com uma barra de ouro no lado quando em foco) e o lacre de cera da entrada
## principal. O painel "BareMenu" não desenha moldura: o menu fica solto sobre o fundo.
static func _add_menu_styles(theme: Theme) -> void:
	var fell := _font(BOOK_FONT)
	var pirata := _font(GAME_FONT)
	theme.set_type_variation("GameTitle", "Label")
	if pirata:
		theme.set_font("font", "GameTitle", pirata)
	theme.set_font_size("font_size", "GameTitle", 76)
	theme.set_color("font_color", "GameTitle", Color(0.96, 0.82, 0.46))
	theme.set_color("font_outline_color", "GameTitle", Color(0.05, 0.03, 0.02))
	theme.set_constant("outline_size", "GameTitle", 9)
	theme.set_color("font_shadow_color", "GameTitle", Color(0, 0, 0, 0.7))
	theme.set_constant("shadow_offset_x", "GameTitle", 3)
	theme.set_constant("shadow_offset_y", "GameTitle", 5)
	theme.set_type_variation("BareMenu", "PanelContainer")
	theme.set_stylebox("panel", "BareMenu", StyleBoxEmpty.new())

	theme.set_type_variation("MenuEntry", "Button")
	if fell:
		theme.set_font("font", "MenuEntry", fell)
	theme.set_font_size("font_size", "MenuEntry", 25)
	theme.set_constant("outline_size", "MenuEntry", 4)
	theme.set_color("font_outline_color", "MenuEntry", Color(0.03, 0.02, 0.02, 0.9))
	theme.set_color("font_color", "MenuEntry", Color(0.86, 0.8, 0.66))
	theme.set_color("font_hover_color", "MenuEntry", Color(1.0, 0.9, 0.6))
	theme.set_color("font_focus_color", "MenuEntry", Color(1.0, 0.9, 0.6))
	theme.set_color("font_pressed_color", "MenuEntry", GOLD)
	var idle := _entry_box(Color(0, 0, 0, 0), Color(0, 0, 0, 0))
	var lit := _entry_box(Color(0.78, 0.62, 0.26, 0.14), GOLD)
	var pressed := _entry_box(Color(0.78, 0.62, 0.26, 0.26), GOLD)
	theme.set_stylebox("normal", "MenuEntry", idle)
	theme.set_stylebox("hover", "MenuEntry", lit)
	theme.set_stylebox("focus", "MenuEntry", lit)
	theme.set_stylebox("pressed", "MenuEntry", pressed)
	theme.set_stylebox("hover_pressed", "MenuEntry", pressed)
	theme.set_stylebox("disabled", "MenuEntry", idle)
	theme.set_color("font_disabled_color", "MenuEntry", Color(0.5, 0.46, 0.4, 0.6))

	theme.set_type_variation("SealEntry", "Button")
	if fell:
		theme.set_font("font", "SealEntry", fell)
	theme.set_font_size("font_size", "SealEntry", 31)
	theme.set_constant("outline_size", "SealEntry", 5)
	theme.set_color("font_outline_color", "SealEntry", Color(0.12, 0.02, 0.02))
	theme.set_color("font_color", "SealEntry", Color(0.99, 0.93, 0.8))
	theme.set_color("font_hover_color", "SealEntry", Color(1, 1, 0.9))
	theme.set_color("font_focus_color", "SealEntry", Color(1, 1, 0.9))
	theme.set_stylebox("normal", "SealEntry", _seal_box(Color(0.5, 0.08, 0.06)))
	theme.set_stylebox("hover", "SealEntry", _seal_box(Color(0.7, 0.13, 0.09)))
	theme.set_stylebox("focus", "SealEntry", _seal_box(Color(0.7, 0.13, 0.09)))
	theme.set_stylebox("pressed", "SealEntry", _seal_box(Color(0.36, 0.05, 0.04)))
	theme.set_stylebox("hover_pressed", "SealEntry", _seal_box(Color(0.36, 0.05, 0.04)))


## Botão comum: couro escuro texturizado, com pesponto e aro de latão (ouro quando aceso).
static func _button_box(fill: Color, rim: Color) -> StyleBox:
	var box := _tiled_box(_leather_image(fill, rim), 8, 6)
	box.content_margin_left = 12
	box.content_margin_right = 12
	box.content_margin_top = 6
	box.content_margin_bottom = 6
	return box


## Entrada do livro-razão: uma barra de ouro à esquerda só quando acesa.
static func _entry_box(fill: Color, bar: Color) -> StyleBoxFlat:
	var box := StyleBoxFlat.new()
	box.bg_color = fill
	box.border_color = bar
	box.border_width_left = 4
	box.set_corner_radius_all(2)
	box.content_margin_left = 22
	box.content_margin_right = 12
	box.content_margin_top = 7
	box.content_margin_bottom = 7
	return box


## Lacre de cera: vermelho-sangue com aro de ouro e sombra funda.
static func _seal_box(color: Color) -> StyleBoxFlat:
	var box := StyleBoxFlat.new()
	box.bg_color = color
	box.border_color = Color(0.86, 0.68, 0.3)
	box.set_border_width_all(3)
	box.set_corner_radius_all(12)
	box.shadow_color = Color(0, 0, 0, 0.6)
	box.shadow_size = 10
	box.shadow_offset = Vector2(0, 4)
	box.content_margin_left = 24
	box.content_margin_right = 16
	box.content_margin_top = 11
	box.content_margin_bottom = 11
	return box


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
	# Esticar (não repetir): sem emendas visíveis nas texturas geradas.
	box.axis_stretch_horizontal = StyleBoxTexture.AXIS_STRETCH_MODE_STRETCH
	box.axis_stretch_vertical = StyleBoxTexture.AXIS_STRETCH_MODE_STRETCH
	return box


static func _noise(seed_: int, frequency: float) -> FastNoiseLite:
	var noise := FastNoiseLite.new()
	noise.seed = seed_
	noise.frequency = frequency
	return noise


## Moldura das janelas: couro escuro com um filete de ouro (o do brasão), uma segunda
## linha fina de latão por dentro e cantoneiras de ouro com um losango. Sem madeira.
static func _frame_image(fill: Color, fill_alpha: float, frame := FRAME) -> Image:
	var size := frame * 4
	var image := Image.create(size, size, false, Image.FORMAT_RGBA8)
	var grain := _noise(7, 0.08)
	var gold := Color(0.83, 0.67, 0.29)
	var gold_dark := Color(0.45, 0.33, 0.12)
	var gold_light := Color(0.97, 0.85, 0.52)
	var band_start := 1
	var band := maxi(2, frame / 5)  # largura do filete de ouro
	for y in size:
		for x in size:
			var edge := mini(mini(x, y), mini(size - 1 - x, size - 1 - y))
			var color: Color
			if edge < frame:
				# Couro da borda, com leve ruído, e o filete de ouro com brilho no centro.
				var v := grain.get_noise_2d(x * 0.9, y * 0.9)
				color = Color(0.1, 0.08, 0.07).lightened(0.08 * v) if v > 0 else Color(0.1, 0.08, 0.07).darkened(-0.2 * v)
				if edge >= band_start and edge < band_start + band:
					var t := float(edge - band_start) / maxf(band - 1, 1)
					color = gold_dark.lerp(gold_light, 1.0 - absf(t - 0.35) * 1.8) if t < 0.7 else gold_dark
				elif edge == band_start + band:
					color = Color(0.03, 0.025, 0.02)
				elif edge == frame - 2 and frame >= 12:
					color = gold_dark.lerp(gold, 0.5)  # fio de latão interno
			else:
				color = fill
				color.a = fill_alpha
				# Sombra interna junto à moldura, com um fio de latão logo dentro dela.
				if edge < frame + SHADOW:
					color = color.darkened(0.35 * (1.0 - float(edge - frame) / SHADOW))
			image.set_pixel(x, y, color)
	# Cantoneiras de ouro: placa quadrada com um losango em relevo.
	for corner in [Vector2i(0, 0), Vector2i(size - frame, 0), Vector2i(0, size - frame), Vector2i(size - frame, size - frame)]:
		var middle := (frame - 1) * 0.5
		for y in frame:
			for x in frame:
				var c := gold_dark
				var d := absf(x - middle) + absf(y - middle)
				if x >= 1 and y >= 1 and x < frame - 1 and y < frame - 1:
					c = gold.lerp(gold_dark, 0.35)
				if d < frame * 0.36:
					c = gold_light if (x + y) % 2 == 0 else gold
				if d < frame * 0.14:
					c = Color(0.5, 0.08, 0.06)
				if x < 1 or y < 1 or x >= frame - 1 or y >= frame - 1:
					c = Color(0.03, 0.025, 0.02)
				image.set_pixel(corner.x + x, corner.y + y, c)
	return image


## Papel antigo: fibras, manchas de umidade, pintas de ferrugem, bordas rasgadas e queimadas.
## Os ruídos se repetem a cada PAPER_PERIOD pixels, para o centro e as bordas poderem ser
## ladrilhados (a caixa estica por repetição, sem emenda).
const PAPER_PERIOD := 64

static func _paper_image(tint: Color) -> Image:
	var period := PAPER_PERIOD
	var margin := PAPER_MARGIN
	var size := period + margin * 2
	var image := Image.create(size, size, false, Image.FORMAT_RGBA8)
	var blotch := _noise(5, 0.03).get_seamless_image(period, period)
	var fiber := _noise(11, 0.45).get_seamless_image(period, period)
	var rag := _noise(23, 0.14).get_seamless_image(period, period)
	var fox := _noise(31, 0.2).get_seamless_image(period, period)
	var rust := Color(0.45, 0.26, 0.1)
	var burnt := Color(0.2, 0.1, 0.04)
	for y in size:
		for x in size:
			var u := posmod(x - margin, period)
			var v := posmod(y - margin, period)
			var edge := mini(mini(x, y), mini(size - 1 - x, size - 1 - y))
			var cut := 2.0 + 8.0 * rag.get_pixel(u, v).r
			var color := tint.darkened(0.28 * blotch.get_pixel(u, v).r)
			color = color * (0.9 + 0.2 * fiber.get_pixel(u, v).r)
			var spot := fox.get_pixel(u, v).r
			if spot > 0.72:
				color = color.lerp(rust, 0.45 * (spot - 0.72) / 0.28)
			var burn := clampf(1.0 - (edge - cut) / 12.0, 0.0, 1.0)
			color = color.lerp(burnt, 0.85 * burn * burn)
			color.a = clampf((edge - cut) / 1.5, 0.0, 1.0)
			image.set_pixel(x, y, color)
	return image


## Desenha a moldura `border` (9-patch de 48 px, tingida de `tint`) sobre a imagem, recuada BORDER_INSET da beira:
## os cantos vão inteiros e as bordas retas são esticadas (são linhas lisas).
static func _framed(image: Image, border: String, tint: Color) -> Image:
	if not ResourceLoader.exists(border):
		return image
	var src := (load(border) as Texture2D).get_image()
	src.decompress()
	src.convert(Image.FORMAT_RGBA8)
	var m := BORDER_CORNER
	var sw := src.get_width()
	var sh := src.get_height()
	var w := image.get_width() - BORDER_INSET * 2
	var h := image.get_height() - BORDER_INSET * 2
	var frame := Image.create(w, h, false, Image.FORMAT_RGBA8)
	# [origem na moldura, tamanho na origem, destino, tamanho no destino]
	var parts := [
		[Vector2i(0, 0), Vector2i(m, m), Vector2i(0, 0), Vector2i(m, m)],
		[Vector2i(sw - m, 0), Vector2i(m, m), Vector2i(w - m, 0), Vector2i(m, m)],
		[Vector2i(0, sh - m), Vector2i(m, m), Vector2i(0, h - m), Vector2i(m, m)],
		[Vector2i(sw - m, sh - m), Vector2i(m, m), Vector2i(w - m, h - m), Vector2i(m, m)],
		[Vector2i(m, 0), Vector2i(sw - 2 * m, m), Vector2i(m, 0), Vector2i(w - 2 * m, m)],
		[Vector2i(m, sh - m), Vector2i(sw - 2 * m, m), Vector2i(m, h - m), Vector2i(w - 2 * m, m)],
		[Vector2i(0, m), Vector2i(m, sh - 2 * m), Vector2i(0, m), Vector2i(m, h - 2 * m)],
		[Vector2i(sw - m, m), Vector2i(m, sh - 2 * m), Vector2i(w - m, m), Vector2i(m, h - 2 * m)],
	]
	for part: Array in parts:
		var piece := src.get_region(Rect2i(part[0], part[1]))
		piece.resize(part[3].x, part[3].y, Image.INTERPOLATE_NEAREST)
		frame.blit_rect(piece, Rect2i(Vector2i.ZERO, part[3]), part[2])
	var out := image.duplicate() as Image
	for y in h:
		for x in w:
			var a := frame.get_pixel(x, y).a
			if a <= 0.0:
				continue
			var at := Vector2i(x + BORDER_INSET, y + BORDER_INSET)
			var under := out.get_pixelv(at)
			var c := under.lerp(tint, a)
			c.a = maxf(under.a, a)
			out.set_pixelv(at, c)
	return out


## Couro: grão, pesponto e aro de metal; as pontas são arredondadas.
static func _leather_image(fill: Color, rim: Color) -> Image:
	var period := 24
	var margin := 8
	var size := period + margin * 2
	var image := Image.create(size, size, false, Image.FORMAT_RGBA8)
	var grain := _noise(3, 0.5).get_seamless_image(period, period)
	var blotch := _noise(8, 0.08).get_seamless_image(period, period)
	for y in size:
		for x in size:
			var u := posmod(x - margin, period)
			var v := posmod(y - margin, period)
			var edge := mini(mini(x, y), mini(size - 1 - x, size - 1 - y))
			var color := fill * (0.78 + 0.3 * grain.get_pixel(u, v).r + 0.18 * blotch.get_pixel(u, v).r)
			color.a = 1.0
			if edge == 0:
				color = Color(0.03, 0.02, 0.02)
			elif edge <= 2:
				color = rim.lerp(rim.lightened(0.35), 0.5 if edge == 1 else 0.0)
			elif edge == 3:
				color = Color(0.04, 0.03, 0.02)
			elif edge == 5 and (x + y) % 5 < 3:
				color = color.lightened(0.25)  # o pesponto
			# Cantos arredondados.
			var corner_x := mini(x, size - 1 - x)
			var corner_y := mini(y, size - 1 - y)
			if corner_x < 3 and corner_y < 3 and corner_x + corner_y < 2:
				color.a = 0.0
			image.set_pixel(x, y, color)
	return image


## Caixa que repete o miolo e as bordas (em vez de esticar a textura).
static func _tiled_box(image: Image, margin: int, content: int) -> StyleBoxTexture:
	var box := _texture_box(image, margin, content)
	box.axis_stretch_horizontal = StyleBoxTexture.AXIS_STRETCH_MODE_TILE_FIT
	box.axis_stretch_vertical = StyleBoxTexture.AXIS_STRETCH_MODE_TILE_FIT
	return box


## Tema das janelas de papel: a tinta escura no lugar do creme (o resto herda do tema do jogo).
static func paper_theme() -> Theme:
	var theme := Theme.new()
	for type in ["Label", "CheckBox", "CheckButton", "RichTextLabel"]:
		theme.set_color("font_color", type, INK)
	theme.set_color("default_color", "RichTextLabel", INK)
	theme.set_constant("outline_size", "Label", 0)
	theme.set_type_variation("TitleLabel", "Label")
	theme.set_color("font_color", "TitleLabel", Color(0.45, 0.09, 0.07))
	theme.set_color("font_outline_color", "TitleLabel", Color(0.9, 0.8, 0.6, 0.6))
	theme.set_constant("outline_size", "TitleLabel", 2)
	return theme
