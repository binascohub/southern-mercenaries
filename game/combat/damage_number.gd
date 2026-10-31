# Southern Mercenaries — GPL-3.0-or-later
class_name DamageNumber
extends Label3D
## Número de dano que sobe e some. Na fraqueza do monstro sai maior e na cor
## do elemento; quando ele resiste, cinza e menor (02-0-elementos.md, seção 3).
## Crítico ganha "!"; um combo mostra o nome dele acima do número.

const LIFETIME := 0.7


static func spawn(parent: Node, at: Vector3, amount: float, effect := "normal", element := "",
		crit := false, combo := "") -> void:
	var label := DamageNumber.new()
	label.text = str(roundi(amount)) + ("!" if crit else "")
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = true
	label.font_size = 72
	label.outline_size = 10
	label.modulate = Color(1.0, 0.9, 0.5)
	match effect:
		"weak":
			label.font_size = 104
			label.modulate = Elements.color(element).lightened(0.15)
		"resist":
			label.font_size = 52
			label.modulate = Color(0.6, 0.6, 0.6)
		"dot":
			label.font_size = 56
			label.modulate = Elements.state_color("burning")
	if crit:
		label.font_size = int(label.font_size * 1.2)
	label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	parent.add_child(label)
	label.global_position = at
	if combo != "":
		var name_label := Label3D.new()
		name_label.text = TranslationServer.translate(GameData.elements.combos[combo].name_key)
		name_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		name_label.no_depth_test = true
		name_label.font_size = 64
		name_label.outline_size = 10
		name_label.modulate = Color(1.0, 0.95, 0.8)
		name_label.position = Vector3.UP * 0.6
		label.add_child(name_label)
	var tween := label.create_tween()
	tween.set_parallel()
	tween.tween_property(label, "global_position", at + Vector3.UP * 1.2, LIFETIME)
	tween.tween_property(label, "modulate:a", 0.0, LIFETIME).set_delay(LIFETIME * 0.4)
	tween.chain().tween_callback(label.queue_free)
