# Southern Mercenaries — GPL-3.0-or-later
extends Control
## Menu principal. Na primeira execução mostra a escolha de idioma
## (já pré-selecionado pelo idioma do sistema). Personagem escolhido, campanha
## (Continuar / Nova campanha / Carregar campanha, 11-saves.md), hospedar ou
## entrar numa partida na LAN (busca automática + IP manual).

const ARENA_SCENE := "res://game/levels/prototype_arena.tscn"

var _main: MenuPanel
var _language: MenuPanel
var _join: JoinMenu
var _characters: CharacterMenu
var _campaigns: CampaignMenu
var _load_button: Button
var _hero: Label
var _continue_button: Button
var _characters_button: Button
var _pending_start: Callable
var _options: OptionsMenu
var _options_button: Button
var _join_button: Button
var _message: Label
var _scene: MenuScene
var _title: TextureRect
var _entries: Array[Button] = []


func _ready() -> void:
	_scene = MenuScene.new()
	_scene.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_scene)
	_build_stage()

	_main = MenuPanel.new()
	_main.theme_type_variation = &"BareMenu"
	_main.theme = null  # texto claro com contorno, direto sobre a cena (sem janela de papel)
	add_child(_main)
	# A coluna de botões cobre a que está desenhada na capa (posições em pixels da imagem).
	_main.set_anchors_preset(Control.PRESET_TOP_LEFT)
	_main.grow_horizontal = Control.GROW_DIRECTION_END
	_main.grow_vertical = Control.GROW_DIRECTION_END
	_main.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	resized.connect(_layout_buttons)
	_message = Label.new()
	_message.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_message.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_message.custom_minimum_size = Vector2(320, 0)
	_message.add_theme_color_override("font_color", Color(1.0, 0.6, 0.45))
	_main.content.add_child(_message)
	_hero = Label.new()
	_hero.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_hero.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hero.add_theme_font_override("font", load(UiTheme.BOOK_FONT) as Font)
	_hero.add_theme_font_size_override("font_size", 18)
	_hero.add_theme_color_override("font_color", UiTheme.GOLD)
	_hero.add_theme_constant_override("outline_size", 5)
	_hero.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_hero.add_theme_color_override("font_outline_color", Color(0.05, 0.03, 0.02))
	_main.content.add_child(_hero)
	_continue_button = _entry("MENU_CONTINUE", func() -> void:
		_start(NetworkManager.prepare_solo, Session.continue_or_new_campaign), true)
	_entry("MENU_NEW_CAMPAIGN", func() -> void:
		if not SaveSystem.can_create_campaign():
			_show_message(tr("CAMPAIGN_SLOTS_FULL").format({"max": SaveSystem.slot_limit("campaigns")}))
			return
		_start(NetworkManager.prepare_solo, Session.start_new_campaign))
	_load_button = _entry("MENU_LOAD_CAMPAIGN", _open_campaigns)
	_entry("MENU_HOST_LAN", func() -> void:
		_start(NetworkManager.prepare_host, Session.continue_or_new_campaign))
	_join_button = _entry("MENU_JOIN_LAN", _open_join)
	_characters_button = _entry("MENU_CHARACTERS", _open_characters)
	_options_button = _entry("MENU_OPTIONS", _open_options)
	_entry("MENU_QUIT", func() -> void: get_tree().quit())
	var version := Label.new()
	version.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	version.modulate = Color(1, 1, 1, 0.45)
	version.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	version.grow_vertical = Control.GROW_DIRECTION_BEGIN
	version.offset_left = 18
	version.offset_bottom = -12
	add_child(version)
	_refresh_texts.bind(version).call()
	Settings.changed.connect(_refresh_texts.bind(version))
	# O menu principal não fecha com "voltar".
	_main.set_process_unhandled_input(false)
	# Com um submenu aberto, o brasão e o título saem de cena (a janela fica sozinha sobre o porto).
	_main.visibility_changed.connect(_sync_stage)

	_options = OptionsMenu.new()
	add_child(_options)
	_options.closed.connect(func() -> void: _main.open(_options_button))

	_join = JoinMenu.new()
	add_child(_join)
	_join.closed.connect(func() -> void: _main.open(_join_button))
	_join.join_requested.connect(func(address: String) -> void:
		_start(NetworkManager.prepare_join.bind(address), func() -> void: Session.campaign = {}))

	_campaigns = CampaignMenu.new()
	add_child(_campaigns)
	_campaigns.closed.connect(func() -> void:
		# Pode ter apagado campanhas: atualiza Continuar / Carregar.
		_refresh_hero()
		_main.open())
	_campaigns.chosen.connect(func(c: Dictionary, host: bool) -> void:
		_start(NetworkManager.prepare_host if host else NetworkManager.prepare_solo,
			Session.use_campaign.bind(c)))

	_characters = CharacterMenu.new()
	add_child(_characters)
	_characters.closed.connect(func() -> void:
		_refresh_hero()
		_main.open(_characters_button))
	_characters.chosen.connect(func() -> void:
		if _pending_start.is_valid():
			var start := _pending_start
			_pending_start = Callable()
			start.call())

	_language = MenuPanel.new()
	add_child(_language)
	_language.add_title("LANGUAGE_CHOOSE_TITLE")
	var system_button: Button
	for code in Settings.LANGUAGES:
		var button := _language.add_button(OptionsMenu.LANGUAGE_KEYS[code], _choose_language.bind(code))
		if code == Settings.language:
			system_button = button
	_language.set_process_unhandled_input(false)

	_layout_buttons.call_deferred()
	if Settings.language_chosen:
		_main.open()
	else:
		_language.open()
		system_button.grab_focus.call_deferred()


## A cena da esquerda: o brasão pendurado por correntes e o título embaixo. Acompanha o
## tamanho da janela.
## O título é um letreiro de ouro dentro da cena 3D (MenuScene); com um submenu aberto sai de cena.
func _build_stage() -> void:
	# O título do jogo, em ouro, sobre a capa (em duas linhas).
	_title = TextureRect.new()
	_title.texture = load("res://assets/ui/title.png") as Texture2D
	_title.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_title.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT
	_title.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_title)


## A coluna de botões à esquerda, embaixo do título; acompanha o tamanho da janela.
func _layout_buttons() -> void:
	if _scene == null or _entries.is_empty() or not is_instance_valid(_main):
		return
	var unit := clampf(size.y / 720.0, 0.7, 1.6)
	# O título (imagem em ouro) ocupa o canto de cima à esquerda, com a proporção dele.
	var title_width := minf(size.x * 0.4, 640.0 * unit)
	var title_aspect := float(_title.texture.get_height()) / float(_title.texture.get_width())
	_title.size = Vector2(title_width, title_width * title_aspect)
	_title.position = Vector2(size.x * 0.03, size.y * 0.02)
	# Os botões formam uma coluna centrada no título, logo abaixo dele.
	var width := title_width * 0.66
	var height := 40.0 * unit
	_main.content.add_theme_constant_override("separation", int(round(8.0 * unit)))
	for button in _entries:
		button.custom_minimum_size = Vector2(width, height)
	_hero.custom_minimum_size = Vector2(width, 0)
	_main.size = Vector2.ZERO
	var centre_x := _title.position.x + title_width * 0.5
	_main.position = Vector2(centre_x - width * 0.5 - 24.0, _title.position.y + _title.size.y - 14.0 * unit)


func _sync_stage() -> void:
	if is_instance_valid(_title) and is_instance_valid(_main):
		_title.visible = _main.visible


## Entrada do menu: o botão padrão do jogo.
func _entry(key: String, callback: Callable, _primary := false) -> Button:
	var button := _main.add_button(key, callback)
	_entries.append(button)
	return button


## Sem personagem, abre a criação antes de começar.
func _start(prepare: Callable, campaign: Callable) -> void:
	if Session.character == null:
		_pending_start = _start.bind(prepare, campaign)
		_open_characters()
		return
	prepare.call()
	campaign.call()
	NetworkManager.last_error_key = ""
	get_tree().change_scene_to_file(ARENA_SCENE)


func _open_characters() -> void:
	_main.visible = false
	_characters.open(_characters_button)


func _refresh_hero() -> void:
	var c := Session.character
	_hero.text = tr("CHAR_ENTRY").format({"name": c.data.name,
		"class": tr(c.class_data().name_key), "level": c.data.level,
		"element": tr(Elements.data(c.data.element).name_key)}) if c else tr("CHAR_NONE")
	_continue_button.visible = not SaveSystem.list_campaigns().is_empty()
	_load_button.visible = _continue_button.visible


func _choose_language(code: String) -> void:
	Settings.set_language(code)
	_language.visible = false
	_main.open()


func _show_message(text: String) -> void:
	_message.text = text
	_message.visible = text != ""


func _open_campaigns() -> void:
	_main.visible = false
	_campaigns.open()


func _open_options() -> void:
	_main.visible = false
	_options.open()


func _open_join() -> void:
	_main.visible = false
	_join.open(_join_button)


func _refresh_texts(version: Label) -> void:
	_refresh_hero()
	version.text = tr("MENU_VERSION").format({"version": NetworkManager.version()})
	# Motivo de ter voltado ao menu (host saiu, versão diferente…).
	_message.text = tr(NetworkManager.last_error_key).format(NetworkManager.last_error_args) if NetworkManager.last_error_key != "" else ""
	_message.visible = _message.text != ""

