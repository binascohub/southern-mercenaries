# Southern Mercenaries — GPL-3.0-or-later
class_name JournalMenu
extends MenuPanel
## Diário de missões (04-tortuga-e-missoes.md, seção 3): a missão principal e as
## secundárias aceitas, com o elemento do alvo e a fraqueza (e o progresso das
## caçadas); embaixo, as concluídas. Abre pelo inventário. "Dicas" troca para
## a ajuda: as dicas do tutorial já vistas (14-tutorial.md, seção 4); "Histórias"
## revê a abertura na Taverna.

var _town: Town
var _text: Label
var _tips_button: Button
var _showing_tips := false


func _ready() -> void:
	add_title("JOURNAL_TITLE")
	_text = Label.new()
	_text.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text.custom_minimum_size = Vector2(620, 0)
	content.add_child(_text)
	_tips_button = add_button("JOURNAL_TIPS", func() -> void:
		_showing_tips = not _showing_tips
		_on_open())
	add_button("JOURNAL_STORIES", _replay_opening)
	add_button("MENU_BACK", close)


func bind(town: Town) -> void:
	_town = town
	closed.connect(func() -> void: Session.ui_open = false)


func show_journal() -> void:
	Session.ui_open = true
	open()


func _on_open() -> void:
	_tips_button.text = tr("JOURNAL_QUESTS") if _showing_tips else tr("JOURNAL_TIPS")
	if _showing_tips:
		var lines := PackedStringArray()
		for id in TipManager.seen_tips():
			lines.append("• " + TipManager.text(id))
		_text.text = tr("JOURNAL_TIPS_SEEN") + "\n" + ("\n".join(lines) if not lines.is_empty() else tr("JOURNAL_NONE"))
		return
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
	if not _town.relics.is_empty():
		var relics := PackedStringArray()
		for id: String in _town.relics:
			var relic: Dictionary = GameData.relics.get(id, {})
			relics.append("%s — %s" % [tr(relic.get("name_key", "")), tr(relic.get("desc_key", ""))])
		text += "\n\n" + tr("JOURNAL_RELICS") + "\n" + "\n".join(relics)
	_text.text = text


## Histórias dos heróis de novo (a abertura com o herói deste PC).
func _replay_opening() -> void:
	var c := Session.character
	if c == null:
		return
	close()
	_town.opening_started.emit([{"name": c.data.name, "class_id": c.data.class_id, "sex": c.data.sex}])


func _target_element(quest: Dictionary) -> String:
	return String(quest.get("target_element", ""))


## "(Terra → fraco a Fogo)".
func _weak(element: String) -> String:
	if element == "":
		return ""
	return tr("JOURNAL_WEAK").format({"element": tr(Elements.data(element).name_key),
		"weak": tr(Elements.data(Elements.weakness_of(element)).name_key)})
