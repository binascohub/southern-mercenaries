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

var _time := 0.0
var _mesh: Node3D


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
	label.position.y = 0.9
	label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	add_child(label)


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
