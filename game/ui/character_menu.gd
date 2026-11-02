# Southern Mercenaries — GPL-3.0-or-later
class_name CharacterMenu
extends MenuPanel
## Escolher um personagem salvo ou criar um novo (11-saves.md; 02-personagens.md:
## classe, sexo e nome). Por enquanto só o Mago é jogável; as outras classes
## entram na Fase 5. O nome é livre e não é traduzido. Até 12 personagens
## por PC (11-saves.md, seção 3); "Apagar" libera um espaço.

signal chosen

var _list: VBoxContainer
var _create: VBoxContainer
var _name: LineEdit
var _sex: OptionButton
var _class: OptionButton
var _class_ids: Array[String] = []
## Elemento de origem (02-0-elementos.md, seção 1): escolhido na criação, não muda.
var _element: OptionButton
var _create_button: Button
var _full: Label
var _hair: OptionButton
var _hair_color: OptionButton
var _skin: OptionButton
var _beard: CheckBox
var _preview: HeroPreview
var _gear: OptionButton


func _ready() -> void:
	add_title("CHAR_TITLE")
	_list = VBoxContainer.new()
	content.add_child(_list)

	_create = VBoxContainer.new()
	content.add_child(_create)
	var create_title := Label.new()
	create_title.text = "CHAR_NEW"
	create_title.add_theme_color_override("font_color", Color(0.45, 0.09, 0.07))
	_create.add_child(create_title)
	_class = OptionButton.new()
	for id in GameData.classes:
		_class_ids.append(id)
		_class.add_item(GameData.classes[id].name_key)
	var body := HBoxContainer.new()
	body.add_theme_constant_override("separation", 14)
	_create.add_child(body)
	_preview = HeroPreview.new()
	body.add_child(_preview)
	var fields := VBoxContainer.new()
	fields.add_theme_constant_override("separation", 6)
	body.add_child(fields)
	_class.item_selected.connect(func(_i: int) -> void:
		if _class_ids[_class.selected] in ["ninja", "knight", "summoner"]:
			_sex.select(0)  # o Ninja tem corpo, rosto e capuz próprios: sem escolha de sexo, rosto nem cabelo
			_refresh_hair_options()
		_suggest_name()
		_on_look_changed())
	fields.add_child(_class)
	_element = OptionButton.new()
	for id in Elements.ALL:
		_element.add_item(Elements.data(id).name_key)
	_element.item_selected.connect(_on_look_changed)
	fields.add_child(_element)
	_sex = OptionButton.new()
	_sex.add_item("CHAR_SEX_MALE")
	_sex.add_item("CHAR_SEX_FEMALE")
	_sex.item_selected.connect(_on_sex_changed)
	fields.add_child(_sex)
	_hair = OptionButton.new()
	_hair.item_selected.connect(_on_look_changed)
	fields.add_child(_hair)
	_hair_color = OptionButton.new()
	for i in Appearance.hair_color_count():
		_hair_color.add_item("CHAR_HAIR_COLOR_%d" % i)
	_hair_color.select(1)
	_hair_color.item_selected.connect(_on_look_changed)
	fields.add_child(_hair_color)
	_beard = CheckBox.new()
	_beard.text = "CHAR_BEARD"
	_beard.toggled.connect(_on_look_changed)
	fields.add_child(_beard)
	_skin = OptionButton.new()
	for i in Appearance.skin_count():
		_skin.add_item("CHAR_SKIN_%d" % i)
	_skin.item_selected.connect(_on_look_changed)
	fields.add_child(_skin)
	# Prévia do equipamento por classificação (D a S).
	_gear = OptionButton.new()
	_gear.add_item("CHAR_GEAR_NONE")
	for rank in HeroGear.RANKS:
		_gear.add_item("CHAR_GEAR_" + rank)
	_gear.item_selected.connect(_on_look_changed)
	fields.add_child(_gear)
	_refresh_hair_options()
	_name = LineEdit.new()
	_name.max_length = CharacterData.NAME_MAX
	_name.custom_minimum_size = Vector2(320, 40)
	_create.add_child(_name)
	_create_button = Button.new()
	_create_button.text = "CHAR_CREATE"
	_create_button.custom_minimum_size = Vector2(320, 44)
	_create_button.pressed.connect(_create_character)
	_create.add_child(_create_button)
	_full = Label.new()
	_full.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_full.custom_minimum_size = Vector2(320, 0)
	_full.add_theme_color_override("font_color", Color(1.0, 0.6, 0.45))
	_create.add_child(_full)

	add_button("MENU_BACK", close)


func _on_open() -> void:
	clear(_list)
	var characters := SaveSystem.list_characters()
	for summary in characters:
		var row := HBoxContainer.new()
		_list.add_child(row)
		var button := Button.new()
		button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		button.custom_minimum_size = Vector2(320, 44)
		button.text = tr("CHAR_ENTRY").format({"name": summary.name,
			"class": tr(GameData.get_class_data(summary.class_id).name_key), "level": summary.level,
			"element": tr(Elements.data(summary.element).name_key)})
		button.pressed.connect(_choose.bind(summary.id))
		row.add_child(button)
		row.add_child(delete_button(func() -> void:
			SaveSystem.delete_character(summary.id)
			Session.forget_character(summary.id)))
	var full := characters.size() >= SaveSystem.slot_limit("characters")
	_create_button.disabled = full
	_full.text = tr("CHAR_SLOTS_FULL").format({"max": SaveSystem.slot_limit("characters")}) if full else ""
	_full.visible = full
	_suggest_name()


## Troca de sexo: refaz a lista de cabelos (cada sexo tem os seus), esconde a barba e o nome padrão.
func _on_sex_changed(_index: int) -> void:
	_refresh_hair_options()
	_suggest_name()


func _refresh_hair_options() -> void:
	var sex := CharacterData.SEXES[_sex.selected]
	var chosen := _hair.selected
	_hair.clear()
	for style: String in Appearance.hair_styles(sex):
		_hair.add_item("CHAR_HAIR_" + (style if style != "" else "NONE"))
	_hair.select(clampi(chosen, 0, _hair.item_count - 1))
	_beard.visible = sex == "male"
	if sex != "male":
		_beard.button_pressed = false
	_on_look_changed()


func _on_look_changed(_value: Variant = null) -> void:
	var class_id := _class_ids[_class.selected]
	if class_id in ["ninja", "knight", "summoner"] and _sex.selected != 0:
		_sex.select(0)  # Ninja e Cavaleiro: corpo próprio, sempre masculino
	var sex := CharacterData.SEXES[_sex.selected]
	var has_gear := HeroGear.has_gear(class_id, sex)
	var witch := class_id in ["ninja", "mage", "knight", "archer", "summoner"]  # a Maga e a Arqueira têm corpo, rosto e cabelo do modelo delas: sem escolha de cabelo, pele nem rank
	_gear.visible = has_gear and not witch  # no Ninja: sem peça aparece o Camponês; com qualquer rank, a roupa ninja (o rank não muda a cor)
	var rank: String = HeroGear.RANKS[_gear.selected - 1] if has_gear and _gear.selected > 0 else ""
	if witch:
		rank = "D"  # a prévia mostra a Maga vestida (qualquer rank: o rank não muda a roupa)
	for field: Control in [_hair, _hair_color, _skin]:
		field.visible = class_id != "ninja" and not witch
	_sex.visible = class_id not in ["ninja", "knight", "summoner"]
	_beard.visible = class_id != "ninja" and not witch and sex == "male"
	_preview.show_hero(sex, _current_look(), rank, class_id, Elements.ALL[_element.selected])


## A escolha de aparência como a ficha guarda (índices).
func _current_look() -> Dictionary:
	return {"hair": _hair.selected, "hair_color": _hair_color.selected, "skin": _skin.selected,
		"beard": _beard.button_pressed}


func _suggest_name() -> void:
	var cls := GameData.get_class_data(_class_ids[_class.selected])
	var sex := CharacterData.SEXES[_sex.selected]
	_name.text = tr(cls.hero_name_keys[sex])


func _choose(id: String) -> void:
	var c := SaveSystem.load_character(id)
	if c:
		Session.select_character(c)
		close()
		chosen.emit()


func _create_character() -> void:
	if not SaveSystem.can_create_character():
		return
	var c := CharacterData.create(_class_ids[_class.selected], CharacterData.SEXES[_sex.selected], _name.text,
		Elements.ALL[_element.selected], _current_look())
	SaveSystem.save_character(c)
	Session.select_character(c)
	close()
	chosen.emit()
