# Southern Mercenaries — GPL-3.0-or-later
class_name CharacterMenu
extends MenuPanel
## Escolher um personagem salvo ou criar um novo (11-saves.md; 02-personagens.md:
## classe, sexo e nome). Por enquanto só o Mago é jogável; as outras classes
## entram na Fase 5. O nome é livre e não é traduzido.

signal chosen

var _list: VBoxContainer
var _create: VBoxContainer
var _name: LineEdit
var _sex: OptionButton
var _class: OptionButton
var _class_ids: Array[String] = []


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
	_sex = OptionButton.new()
	_sex.add_item("CHAR_SEX_MALE")
	_sex.add_item("CHAR_SEX_FEMALE")
	_sex.item_selected.connect(func(_i: int) -> void: _suggest_name())
	_create.add_child(_sex)
	_name = LineEdit.new()
	_name.max_length = CharacterData.NAME_MAX
	_name.custom_minimum_size = Vector2(320, 40)
	_create.add_child(_name)
	var create_button := Button.new()
	create_button.text = "CHAR_CREATE"
	create_button.custom_minimum_size = Vector2(320, 44)
	create_button.pressed.connect(_create_character)
	_create.add_child(create_button)

	add_button("MENU_BACK", close)


func _on_open() -> void:
	for child in _list.get_children():
		child.queue_free()
	for summary in SaveSystem.list_characters():
		var button := Button.new()
		button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		button.custom_minimum_size = Vector2(320, 44)
		button.text = tr("CHAR_ENTRY").format({"name": summary.name,
			"class": tr(GameData.get_class_data(summary.class_id).name_key), "level": summary.level})
		button.pressed.connect(_choose.bind(summary.id))
		_list.add_child(button)
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
	var c := CharacterData.create(_class_ids[_class.selected], CharacterData.SEXES[_sex.selected], _name.text)
	SaveSystem.save_character(c)
	Session.select_character(c)
	close()
	chosen.emit()
