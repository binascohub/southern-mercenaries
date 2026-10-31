# Southern Mercenaries — GPL-3.0-or-later
class_name LootDrop
extends Node3D
## Item ou ouro no chão. Existe só no PC do dono: cada jogador vê e pega só o
## seu loot (07-rede.md, seção 7). O servidor guarda o registro e valida a coleta.

var loot_id := 0
var item: Dictionary = {}
var gold := 0

var _time := 0.0
var _mesh: MeshInstance3D


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
	_mesh = MeshInstance3D.new()
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.emission_enabled = true
	material.emission = color
	material.emission_energy_multiplier = 0.8
	if gold > 0:
		var coin := CylinderMesh.new()
		coin.top_radius = 0.18
		coin.bottom_radius = 0.18
		coin.height = 0.06
		_mesh.mesh = coin
	else:
		var bag := BoxMesh.new()
		bag.size = Vector3(0.35, 0.3, 0.35)
		_mesh.mesh = bag
	_mesh.material_override = material
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


func _process(delta: float) -> void:
	_time += delta
	_mesh.rotation.y = _time * 1.5
	_mesh.position.y = 0.3 + sin(_time * 3.0) * 0.05
