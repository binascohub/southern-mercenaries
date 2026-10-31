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


func _ready() -> void:
	add_title("CHAR_TITLE")
	_list = VBoxContainer.new()
	content.add_child(_list)

	_create = VBoxContainer.new()
	content.add_child(_create)
	var create_title := Label.new()
	create_title.text = "CHAR_NEW"
	create_title.add_theme_color_override("font_color", Color(0.9, 0.8, 0.5))
	_create.add_child(create_title)
	_class = OptionButton.new()
	for id in GameData.classes:
		_class_ids.append(id)
		_class.add_item(GameData.classes[id].name_key)
	_create.add_child(_class)
	_element = OptionButton.new()
	for id in Elements.ALL:
		_element.add_item(Elements.data(id).name_key)
	_create.add_child(_element)
	_sex = OptionButton.new()
	_sex.add_item("CHAR_SEX_MALE")
	_sex.add_item("CHAR_SEX_FEMALE")
	_sex.item_selected.connect(func(_i: int) -> void: _suggest_name())
	_create.add_child(_sex)
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
		Elements.ALL[_element.selected])
	SaveSystem.save_character(c)
	Session.select_character(c)
	close()
	chosen.emit()
