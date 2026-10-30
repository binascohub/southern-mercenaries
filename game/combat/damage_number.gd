# Southern Mercenaries — GPL-3.0-or-later
class_name DamageNumber
extends Label3D
## Número de dano que sobe e some.

const LIFETIME := 0.7


static func spawn(parent: Node, at: Vector3, amount: float) -> void:
	var label := DamageNumber.new()
	label.text = str(roundi(amount))
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = true
	label.font_size = 72
	label.outline_size = 10
	label.modulate = Color(1.0, 0.9, 0.5)
	label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	parent.add_child(label)
	label.global_position = at
	var tween := label.create_tween()
	tween.set_parallel()
	tween.tween_property(label, "global_position", at + Vector3.UP * 1.2, LIFETIME)
	tween.tween_property(label, "modulate:a", 0.0, LIFETIME).set_delay(LIFETIME * 0.4)
	tween.chain().tween_callback(label.queue_free)
