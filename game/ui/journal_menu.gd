# Southern Mercenaries — GPL-3.0-or-later
class_name JournalMenu
extends MenuPanel
## Diário de missões (04-tortuga-e-missoes.md, seção 3): a missão principal e as
## secundárias aceitas, com o elemento do alvo e a fraqueza (e o progresso das
## caçadas); embaixo, as concluídas. Abre pelo inventário.

var _town: Town
var _text: Label


func _ready() -> void:
	add_title("JOURNAL_TITLE")
	_text = Label.new()
	_text.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text.custom_minimum_size = Vector2(620, 0)
	content.add_child(_text)
	add_button("MENU_BACK", close)


func bind(town: Town) -> void:
	_town = town
	closed.connect(func() -> void: Session.ui_open = false)


func show_journal() -> void:
	Session.ui_open = true
	open()


func _on_open() -> void:
	var active := PackedStringArray()
	var done := PackedStringArray()
	for id: String in _town.quests:
		var quest: Dictionary = GameData.quests.get(id, {})
		var line := tr(quest.get("name_key", "")) + "  " + _weak(_target_element(quest))
		if _town.quests[id] == "active":
			active.append(line)
		else:
			done.append(line)
	for quest: Dictionary in _town.side_quests.values():
		var entry: Dictionary = GameData.bestiary.get(quest.target, {})
		var line := SideQuests.title(quest) + "  " + _weak(entry.get("element", ""))
		if quest.status == "active":
			active.append(line)
		elif quest.status == "done":
			done.append(line)
	var text := tr("JOURNAL_ACTIVE") + "\n" + ("\n".join(active) if not active.is_empty() else tr("JOURNAL_NONE"))
	if not done.is_empty():
		text += "\n\n" + tr("JOURNAL_DONE") + "\n" + "\n".join(done)
	_text.text = text


func _target_element(quest: Dictionary) -> String:
	return String(quest.get("target_element", ""))


## "(Terra → fraco a Fogo)".
func _weak(element: String) -> String:
	if element == "":
		return ""
	return tr("JOURNAL_WEAK").format({"element": tr(Elements.data(element).name_key),
		"weak": tr(Elements.data(Elements.weakness_of(element)).name_key)})
