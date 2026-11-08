extends Node

func _ready() -> void:
	await get_tree().process_frame
	var root := get_tree().root
	var gd: Node = root.get_node("GameData")
	var items: Array = []
	for base in gd.item_bases:
		if base.begins_with("_"):
			continue
		for material in ["cloth", "wood", "iron", "steel"]:
			if material in ["cloth", "wood"] and Items.material_for_tier(0, Items.is_weapon(base)) != material:
				continue
			items.append(Items.equipment(base, material))
	for id in gd.consumables:
		if id.ends_with("_iron") or id.ends_with("_steel") or id == "venison":
			items.append(Items.stack(Items.CONSUMABLE, id))
	var bad := 0
	for it in items:
		var drop := LootDrop.create(1, Vector3.ZERO, it, 0)
		root.add_child(drop)
		var mesh: Node3D = drop._mesh
		var child := mesh.get_child(0)
		var what := "BOX"
		if child is Sprite3D:
			what = "icon %s" % (child as Sprite3D).texture.resource_path.get_file()
		elif not child is MeshInstance3D:
			what = "model %s top=%.2f" % [child.scene_file_path.get_file() if child.scene_file_path else String(child.name), drop._top]
		else:
			bad += 1
		print("%-45s -> %s" % [Items.display_name(it) + " [" + str(it.get("base", it.get("id"))) + "/" + str(it.get("material", "")) + "]", what])
		drop.free()
	print("PLACEHOLDERS: ", bad)
	get_tree().quit()
