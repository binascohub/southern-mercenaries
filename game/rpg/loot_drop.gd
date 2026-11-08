# Southern Mercenaries — GPL-3.0-or-later
class_name LootDrop
extends Node3D
## Item ou ouro no chão. Existe só no PC do dono: cada jogador vê e pega só o
## seu loot (07-rede.md, seção 7). O servidor guarda o registro e valida a coleta.

var loot_id := 0
var item: Dictionary = {}
var gold := 0

const COIN_MODEL := "res://assets/models/props/Coin_Gold.glb"
## Frasco de cada poção no chão (assets/models/props, tools/assets/build_potions.py): vida vermelho, recurso azul, elementais na cor do elemento.
const POTION_MODELS := {"potion_health": "Potion_Red", "potion_resource": "Potion_Blue", "elemental_potion_water": "Potion_Aqua",
	"elemental_potion_fire": "Potion_Orange", "elemental_potion_air": "Potion_Yellow", "elemental_potion_earth": "Potion_Green"}
const POTION_HEIGHT := 0.5
## Equipamento no chão: o mesmo modelo que o herói usa (ou o do ícone), pelo rank do material
## (pano/ferro = D, aço = C...; NinjaGear.rank_of). "%s" = rank; tamanho = maior lado em metros.
const GEAR_MODELS := {"lance": ["Sword_%s", 0.75], "daggers": ["Dagger_%s", 0.5], "book": ["Book_%s", 0.4],
	"staff": ["Staff_D", 0.8], "bow": ["Bow_Vulture", 0.75], "amulet": ["Necklace", 0.35]}
## Cristais de refino (Fantasy Crystals) na cor do material.
const CRYSTAL_SIZE := 0.35
## Carne de cervo: o mesmo modelo do ícone do inventário (tools/assets/build_venison_icon.py).
const STACK_MODELS := {"venison": ["Raw_Meat", 0.45]}
## Sem modelo 3D (capuz, túnica, luvas, botas, anel, peitoral, barda, pergaminhos...): o ícone do inventário em pé.
const ICON_HEIGHT := 0.55

var _time := 0.0
var _mesh: Node3D
var _top := 0.0  # altura do topo do modelo, acima de _mesh


static func create(id: int, at: Vector3, drop_item: Dictionary, drop_gold: int) -> LootDrop:
	var drop := LootDrop.new()
	drop.loot_id = id
	drop.item = drop_item
	drop.gold = drop_gold
	drop.position = at
	return drop


func _ready() -> void:
	add_to_group(&"loot")
	var color := Items.color(item) if not item.is_empty() else Color(1.0, 0.82, 0.25)
	_mesh = Node3D.new()
	var relic: String = GameData.valuables.get(item.get("id", ""), {}).get("model", "") if item.get("kind", "") == Items.VALUABLE else ""
	if relic != "" and Kit.has(relic):
		# Relíquia de missão (coração, crânio): o modelo girando no chão.
		var relic_node := Kit.piece(relic)
		_mesh.add_child(relic_node)
		var relic_anim := relic_node.find_child("AnimationPlayer", true, false) as AnimationPlayer
		if relic_anim and not relic_anim.get_animation_list().is_empty():
			relic_anim.get_animation(relic_anim.get_animation_list()[0]).loop_mode = Animation.LOOP_LINEAR
			relic_anim.play(relic_anim.get_animation_list()[0])  # o fantasma "respira" no chão
	elif POTION_MODELS.has(item.get("id", "")) and Kit.has(POTION_MODELS[item.id]):
		# Poção: o frasco em pé girando no chão, com ~0,5 m de altura.
		var bottle := Kit.piece(POTION_MODELS[item.id])
		var box := _bounds(bottle)
		if box.size.y > 0.001:
			bottle.scale = Vector3.ONE * (POTION_HEIGHT / box.size.y)
			bottle.position.y = -box.position.y * bottle.scale.y
		_mesh.add_child(bottle)
	elif gold > 0:
		# Moeda antiga em pé, girando (Old coin, yd, CC0).
		var coin: Node3D = load(COIN_MODEL).instantiate()
		coin.rotation.x = deg_to_rad(90.0)
		coin.position.y = 0.0
		_mesh.add_child(coin)
	elif _item_visual():
		pass  # modelo do item ou o ícone do inventário (abaixo)
	else:
		var material := StandardMaterial3D.new()
		material.albedo_color = color
		material.emission_enabled = true
		material.emission = color
		material.emission_energy_multiplier = 0.8
		var bag := MeshInstance3D.new()
		var box := BoxMesh.new()
		box.size = Vector3(0.35, 0.3, 0.35)
		bag.mesh = box
		bag.material_override = material
		_mesh.add_child(bag)
	_mesh.position.y = 0.3
	add_child(_mesh)

	# Etiqueta na cor da raridade (09-interface.md, "Itens no chão").
	var label := Label3D.new()
	label.text = TranslationServer.translate("LOOT_GOLD").format({"amount": gold}) if gold > 0 \
		else Items.display_name(item)
	label.modulate = color
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = true
	label.font_size = 40
	label.outline_size = 8
	label.position.y = maxf(0.9, _top + 0.45)  # acima do modelo mais alto (espada, cajado)
	label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	add_child(label)


## Modelo 3D do item no chão (equipamento, cristal, carne) ou, sem modelo, o ícone do inventário em pé.
## Põe o visual em _mesh e devolve false quando não há nenhum dos dois (fica a caixa colorida).
func _item_visual() -> bool:
	if item.is_empty() or gold > 0:
		return false
	var spec := visual_spec(item)
	if spec.is_empty():
		return false
	if spec.has("piece"):
		var node := Kit.piece(spec.piece)
		if spec.has("tint"):
			_tint(node, spec.tint)
		var box := _bounds(node)
		var longest := maxf(box.size.x, maxf(box.size.y, box.size.z))
		if longest > 0.001:
			node.scale = Vector3.ONE * (float(spec.size) / longest)
			# Centrado no eixo de giro, com a base no chão do visual.
			var centre := box.get_center() * node.scale.x
			node.position = Vector3(-centre.x, -box.position.y * node.scale.y, -centre.z)
			_top = box.size.y * node.scale.y
		_mesh.add_child(node)
		return true
	var sprite := Sprite3D.new()
	sprite.texture = spec.icon
	sprite.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	sprite.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	sprite.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	sprite.pixel_size = ICON_HEIGHT / maxf(1.0, float(spec.icon.get_height()))
	sprite.position.y = ICON_HEIGHT / 2.0
	sprite.name = "Icon"
	_mesh.add_child(sprite)
	_top = ICON_HEIGHT
	return true


## Qual visual o item usa no chão: {piece, size, tint?} (modelo do Kit) ou {icon} (ícone do inventário); {} = nenhum.
static func visual_spec(drop_item: Dictionary) -> Dictionary:
	var kind: String = drop_item.get("kind", "")
	if kind == Items.EQUIPMENT:
		var base := String(drop_item.get("base", ""))
		var material := String(drop_item.get("material", ""))
		var rank := NinjaGear.rank_of(material)
		var tint := Color(GameData.materials.get(material, {}).get("color", "#ffffff"))
		if base == "helm" and Kit.has(ClassGear.HELMETS.get(rank, "")):
			# Elmo do Cavaleiro: a mesma peça e cor que ele veste (class_gear.gd).
			return {"piece": ClassGear.HELMETS[rank], "size": 0.4, "tint": ClassGear.HELMET_TINT[rank]}
		if GEAR_MODELS.has(base):
			var piece := String(GEAR_MODELS[base][0])
			piece = piece % rank if "%s" in piece else piece
			if Kit.has(piece):
				var spec := {"piece": piece, "size": GEAR_MODELS[base][1]}
				# Peças de rank único (cajado, arco, colar) ganham a cor do material acima de D, como nos ícones.
				if not "%s" in String(GEAR_MODELS[base][0]) and rank != "D":
					spec.tint = tint
				return spec
	elif kind == Items.CONSUMABLE:
		var id := String(drop_item.get("id", ""))
		if STACK_MODELS.has(id) and Kit.has(STACK_MODELS[id][0]):
			return {"piece": STACK_MODELS[id][0], "size": STACK_MODELS[id][1]}
		var def: Dictionary = GameData.consumables.get(id, {})
		if id.begins_with("crystal_") and Kit.has("Crystal_Gem"):
			return {"piece": "Crystal_Gem", "size": CRYSTAL_SIZE, "tint": Color(GameData.materials.get(def.get("material", ""), {}).get("color", "#ffffff"))}
	var icon := Items.icon(drop_item)
	return {"icon": icon} if icon else {}


## Multiplica a cor de todas as malhas do modelo (cópias dos materiais, o arquivo original fica igual).
static func _tint(node: Node3D, tint: Color) -> void:
	for found in node.find_children("*", "MeshInstance3D", true, false):
		var mi := found as MeshInstance3D
		if mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var source := mi.get_active_material(i) as BaseMaterial3D
			if source:
				var copy := source.duplicate() as BaseMaterial3D
				copy.albedo_color = source.albedo_color * tint
				mi.set_surface_override_material(i, copy)


## Caixa que as malhas do modelo ocupam (antes de entrar na cena), nas coordenadas do próprio modelo.
static func _bounds(node: Node3D) -> AABB:
	var total := AABB()
	var first := true
	for found in node.find_children("*", "MeshInstance3D", true, false):
		var mi := found as MeshInstance3D
		var box := mi.transform * mi.get_aabb()
		var parent := mi.get_parent()
		while parent != null and parent != node:
			if parent is Node3D:
				box = (parent as Node3D).transform * box
			parent = parent.get_parent()
		total = box if first else total.merge(box)
		first = false
	return total


func _process(delta: float) -> void:
	_time += delta
	_mesh.rotation.y = _time * 1.5
	_mesh.position.y = 0.3 + sin(_time * 3.0) * 0.05
