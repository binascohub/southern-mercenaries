# Southern Mercenaries — GPL-3.0-or-later
class_name Items
extends RefCounted
## Itens como dados (dicionários com IDs), iguais no save, na rede e na tela
## (05-itens-e-loot.md). Nada de texto: o nome é montado com tr() na hora.
##
## Equipamento: {kind, uid, base, material, rarity, level, affixes {id: valor}, refine}
## Empilhável:  {kind: "consumable" | "valuable", id, count}

const EQUIPMENT := "equipment"
const CONSUMABLE := "consumable"
const VALUABLE := "valuable"
const VALUABLE_STACK := 20
## Bônus de refino +0..+5 (13-balanceamento.md 2.1); o refino em si vem na Fase 6.
const REFINE_BONUS: Array[float] = [0.0, 0.05, 0.10, 0.15, 0.25, 0.35]


static func new_uid(rng: RandomNumberGenerator) -> String:
	return "%08x%08x" % [rng.randi(), rng.randi()]


static func equipment(base: String, material: String, rarity := "common", level := 1,
		affixes := {}, rng: RandomNumberGenerator = null) -> Dictionary:
	if rng == null:
		rng = RandomNumberGenerator.new()
		rng.randomize()
	return {"kind": EQUIPMENT, "uid": new_uid(rng), "base": base, "material": material,
		"rarity": rarity, "level": level, "affixes": affixes, "refine": 0}


static func stack(kind: String, id: String, count := 1) -> Dictionary:
	return {"kind": kind, "id": id, "count": count}


# --- Geração (loot) -----------------------------------------------------------------

## Equipamento aleatório de um nível, de preferência usável pela classe.
static func generate_equipment(level: int, class_id: String, rarity: String,
		rng: RandomNumberGenerator) -> Dictionary:
	var bases: Array[String] = []
	for id in GameData.item_bases:
		var classes: Array = GameData.item_bases[id].get("classes", [])
		if classes.is_empty() or class_id in classes:
			bases.append(id)
	var base: String = bases[rng.randi_range(0, bases.size() - 1)]
	var material := roll_material(level, base, rng)
	var affixes := {}
	var count_range: Array = GameData.rarities[rarity].affixes
	var count := rng.randi_range(int(count_range[0]), int(count_range[1]))
	var pool: Array = GameData.affixes.keys()
	# Embaralha com o sorteador do item (não o global): a mesma semente gera o
	# mesmo item — o estoque do Mercado Pirata é igual no servidor e no cliente.
	for i in range(pool.size() - 1, 0, -1):
		var j := rng.randi_range(0, i)
		var swap: Variant = pool[i]
		pool[i] = pool[j]
		pool[j] = swap
	for i in mini(count, pool.size()):
		var def: Dictionary = GameData.affixes[pool[i]]
		var bonus: float = def.per_level * (level - 1)
		affixes[pool[i]] = roundi(rng.randf_range(def.min + bonus, def.max + bonus))
	return equipment(base, material, rarity, level, affixes, rng)


## Tier pelo nível da área: 80% o da faixa, 15% o anterior, 5% o próximo
## (05-itens-e-loot.md, seção 7). Tier 0 (pano/madeira) só cai até o nível 2.
static func roll_material(level: int, base: String, rng: RandomNumberGenerator) -> String:
	var tier := tier_for_level(level)
	var weights: Dictionary = GameData.loot.tier_roll
	var roll := rng.randi_range(1, int(weights.same + weights.previous + weights.next))
	if roll > weights.same + weights.previous:
		tier += 1
	elif roll > weights.same:
		tier -= 1
	tier = clampi(tier, 0 if level <= 2 else 1, 5)
	return material_for_tier(tier, is_weapon(base))


static func tier_for_level(level: int) -> int:
	for id in GameData.materials:
		var m: Dictionary = GameData.materials[id]
		if m.tier > 0 and level >= m.min_level and level <= m.max_level:
			return m.tier
	return 5


static func material_for_tier(tier: int, weapon: bool) -> String:
	if tier == 0:
		return "wood" if weapon else "cloth"
	for id in GameData.materials:
		if GameData.materials[id].tier == tier:
			return id
	return "iron"


static func roll_rarity(weights: Dictionary, rng: RandomNumberGenerator) -> String:
	var total := 0
	for id in weights:
		total += int(weights[id])
	var roll := rng.randi_range(1, total)
	for id in weights:
		roll -= int(weights[id])
		if roll <= 0:
			return id
	return "common"


# --- Regras ---------------------------------------------------------------------

static func is_weapon(base: String) -> bool:
	return GameData.item_bases[base].get("weapon_material", false)


static func slot_of(item: Dictionary) -> String:
	return GameData.item_bases[item.base].slot if item.kind == EQUIPMENT else ""


static func max_stack(item: Dictionary) -> int:
	match item.kind:
		CONSUMABLE:
			return int(GameData.consumables[item.id].stack)
		VALUABLE:
			return VALUABLE_STACK
	return 1


static func required_level(item: Dictionary) -> int:
	if item.kind != EQUIPMENT:
		return 1
	var m: Dictionary = GameData.materials[item.material]
	return 1 if m.tier == 0 else int(m.min_level)


static func usable_by_class(item: Dictionary, class_id: String) -> bool:
	if item.kind != EQUIPMENT:
		return true
	var classes: Array = GameData.item_bases[item.base].get("classes", [])
	return classes.is_empty() or class_id in classes


## Dano da arma = 10 × material × (1 + raridade) × (1 + refino) (13-balanceamento.md 2.1).
static func weapon_damage(item: Dictionary) -> float:
	var base: Dictionary = GameData.item_bases[item.base]
	if not base.has("damage"):
		return 0.0
	return base.damage * GameData.materials[item.material].mult \
		* (1.0 + GameData.rarities[item.rarity].damage_bonus) * (1.0 + REFINE_BONUS[int(item.refine)])


## Armadura da peça para a classe (13-balanceamento.md 2.3).
static func armor(item: Dictionary, class_factor: float) -> float:
	var base: Dictionary = GameData.item_bases[item.base]
	if not base.has("armor"):
		return 0.0
	return base.armor * GameData.materials[item.material].mult * class_factor \
		* (1.0 + REFINE_BONUS[int(item.refine)])


## Valor base em ouro (13-balanceamento.md 5.2; valiosos em 05-itens-e-loot.md).
static func value(item: Dictionary) -> int:
	match item.kind:
		EQUIPMENT:
			return roundi(20.0 * GameData.materials[item.material].mult * (1.0 + 0.15 * item.level)
				* GameData.rarities[item.rarity].value_factor)
		VALUABLE:
			return int(GameData.valuables[item.id].value)
		CONSUMABLE:
			var c: Dictionary = GameData.consumables[item.id]
			return int(c.price_base + c.price_per_level)
	return 0


## Confere se um item recebido (save ou rede) só usa IDs e valores válidos.
static func is_valid(item: Variant) -> bool:
	if not item is Dictionary:
		return false
	match item.get("kind", ""):
		EQUIPMENT:
			return GameData.item_bases.has(item.get("base", "")) \
				and GameData.materials.has(item.get("material", "")) \
				and GameData.rarities.has(item.get("rarity", "")) \
				and int(item.get("level", 0)) in range(1, 21) \
				and int(item.get("refine", -1)) in range(0, 6) \
				and item.get("affixes", null) is Dictionary \
				and item.affixes.keys().all(func(k: Variant) -> bool: return GameData.affixes.has(k))
		CONSUMABLE:
			return GameData.consumables.has(item.get("id", "")) and int(item.get("count", 0)) >= 1
		VALUABLE:
			return GameData.valuables.has(item.get("id", "")) and int(item.get("count", 0)) >= 1
	return false


# --- Texto (só na tela, no idioma de cada jogador) -------------------------------

## Ícone do item no inventário (assets/ui/icons/<id>.png: as poções, de
## tools/assets/potion_icons.py); null sem ícone.
static func icon(item: Variant) -> Texture2D:
	if item is Dictionary and item.get("kind", "") == EQUIPMENT:
		return equipment_icon(item)
	if not item is Dictionary or not item.has("id"):
		return null
	var path := "res://assets/ui/icons/%s.png" % String(item.id)
	return load(path) as Texture2D if ResourceLoader.exists(path) else null


## Ícone de equipamento: a lança do Cavaleiro aparece como a espada do rank do material (3D Swords Pack, CC0).
static func equipment_icon(item: Dictionary) -> Texture2D:
	# Espada do Cavaleiro (3D Swords Pack, CC0) e adaga do Ninja (Iron Knife, CC0; só o rank D tem ícone).
	var prefix: String = {"lance": "sword", "daggers": "dagger"}.get(String(item.get("base", "")), "")
	if item.get("kind", "") != EQUIPMENT or prefix == "":
		return null
	var path := "res://assets/ui/icons/%s_%s.png" % [prefix, NinjaGear.rank_of(String(item.get("material", "")))]
	return load(path) as Texture2D if ResourceLoader.exists(path) else null


static func display_name(item: Dictionary) -> String:
	match item.kind:
		EQUIPMENT when item.has("legendary"):
			# Lendário: nome próprio (data/legendaries.json).
			var legendary: Dictionary = GameData.legendaries.get(item.legendary, {})
			return str(TranslationServer.translate(legendary.get("name_key", ""))) + (" +%d" % item.refine if item.refine > 0 else "")
		EQUIPMENT:
			var name := TranslationServer.translate("ITEM_NAME_PATTERN").format({
				"type": TranslationServer.translate(GameData.item_bases[item.base].name_key),
				"material": TranslationServer.translate(GameData.materials[item.material].name_key),
			})
			return name + (" +%d" % item.refine if item.refine > 0 else "")
		CONSUMABLE:
			var c: Dictionary = GameData.consumables[item.id]
			# Pergaminhos e cristais levam o material no nome.
			return str(TranslationServer.translate(c.name_key)).format({
				"material": str(TranslationServer.translate(GameData.materials.get(c.get("material", ""), {}).get("name_key", "")))})
		VALUABLE:
			return TranslationServer.translate(GameData.valuables[item.id].name_key)
	return "?"


static func color(item: Dictionary) -> Color:
	if item.kind == EQUIPMENT:
		return Color(GameData.rarities[item.rarity].color)
	return Color(0.85, 0.85, 0.75) if item.kind == CONSUMABLE else Color(0.95, 0.8, 0.35)


## Linhas da dica do item (05-itens-e-loot.md e 09-interface.md).
static func describe(item: Dictionary, class_factor := 1.0) -> PackedStringArray:
	var t := TranslationServer
	var lines := PackedStringArray([display_name(item)])
	if item.kind == EQUIPMENT:
		lines.append(t.translate(GameData.rarities[item.rarity].name_key))
		var dmg := weapon_damage(item)
		if dmg > 0.0:
			lines.append(t.translate("ITEM_STAT_DAMAGE").format({"value": "%.0f" % dmg}))
		var arm := armor(item, class_factor)
		if arm > 0.0:
			lines.append(t.translate("ITEM_STAT_ARMOR").format({"value": "%.0f" % arm}))
		for id in item.affixes:
			lines.append(t.translate(GameData.affixes[id].name_key).format({"value": item.affixes[id]}))
		if item.has("legendary"):
			lines.append(t.translate(GameData.legendaries.get(item.legendary, {}).get("lore_key", "")))
		lines.append(t.translate("ITEM_REQUIRED_LEVEL").format({"level": required_level(item)}))
	elif item.get("count", 1) > 1:
		lines.append("x%d" % item.count)
	if item.kind == CONSUMABLE:
		var c: Dictionary = GameData.consumables[item.id]
		if c.restore == "refine":
			lines.append(t.translate("ITEM_SCROLL_EFFECT"))
		elif c.restore == "none":
			lines.append(t.translate("ITEM_CRYSTAL_EFFECT"))
		elif c.restore == "return_portal":
			lines.append(t.translate("ITEM_RETURN_CHARM_EFFECT"))
		elif c.restore == "element":
			lines.append(t.translate("ITEM_ELEMENTAL_EFFECT").format({
				"element": t.translate(Elements.data(c.element).name_key)}))
		else:
			lines.append(t.translate("ITEM_RESTORES").format({"percent": roundi(c.fraction * 100)}))
	lines.append(t.translate("ITEM_VALUE").format({"gold": value(item)}))
	return lines
