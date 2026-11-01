# Southern Mercenaries — GPL-3.0-or-later
class_name HeroGear
extends RefCounted
## Ponto de entrada dos conjuntos de roupa e armadura por rank (D a S): decide se a classe e o sexo
## têm visual por rank e veste o modelo (NinjaGear para o Ninja, ClassGear para as outras classes).
## O rank de cada peça vem do material dela (05-itens-e-loot.md).

const RANKS: Array[String] = ["D", "C", "B", "A", "S"]
const SLOTS: Array[String] = ["body", "head", "hands", "feet"]


static func has_gear(class_id: String, sex: String) -> bool:
	if class_id == "ninja":
		return NinjaGear.has_gear(class_id, sex)
	return ClassGear.has_gear(class_id)


static func rank_of(material: String) -> String:
	return NinjaGear.rank_of(material)


static func apply(model: HeroModel, class_id: String, ranks: Dictionary) -> void:
	if class_id == "ninja":
		NinjaGear.apply(model, ranks)
	else:
		ClassGear.apply(model, class_id, ranks)
