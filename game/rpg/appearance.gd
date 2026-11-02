# Southern Mercenaries — GPL-3.0-or-later
class_name Appearance
extends RefCounted
## Aparência do personagem escolhida na criação (data/appearance.json): estilo e cor do cabelo,
## barba (só masculino) e tom de pele. É só visual. A ficha guarda índices (`look`), nunca
## cores; este arquivo valida a escolha e a transforma no visual do modelo (HeroModel.setup).

const FILE := "res://data/appearance.json"

static var _data: Dictionary = {}


static func data() -> Dictionary:
	if _data.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(FILE))
		_data = parsed if parsed is Dictionary else {}
	return _data


## Estilos de cabelo do sexo (malhas; "" = sem cabelo).
static func hair_styles(sex: String) -> Array:
	return data().get("hair", {}).get(sex, [""])


static func hair_color_count() -> int:
	return data().get("hair_color", []).size()


static func skin_count() -> int:
	return data().get("skin", []).size()


## A escolha como a ficha guarda: {hair: índice do estilo, hair_color, skin, beard}. Valores fora
## da lista voltam ao padrão (a ficha pode ter sido editada).
static func clean(sex: String, look: Dictionary) -> Dictionary:
	var styles := hair_styles(sex)
	return {
		"hair": clampi(int(look.get("hair", 0)), 0, styles.size() - 1),
		"hair_color": clampi(int(look.get("hair_color", 1)), 0, maxi(hair_color_count() - 1, 0)),
		"skin": clampi(int(look.get("skin", 0)), 0, maxi(skin_count() - 1, 0)),
		"beard": sex == "male" and bool(look.get("beard", false)),
	}


## O visual para HeroModel.setup. Sem escolha na ficha (personagens antigos), vale o visual
## padrão da classe (data/classes.json, "look").
static func model_look(sex: String, look: Dictionary, class_default: Dictionary) -> Dictionary:
	if look.is_empty():
		return class_default
	var chosen := clean(sex, look)
	var hair: Array = []
	var style: String = hair_styles(sex)[chosen.hair]
	if style != "":
		hair.append(style)
	if chosen.beard:
		hair.append(String(data().get("beard", "Hair_Beard")))
	var color: Array = data().hair_color[chosen.hair_color]
	return {"hair": hair, "hair_color": color, "skin": data().skin[chosen.skin]}
