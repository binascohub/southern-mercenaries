extends Node
func _ready() -> void:
	var hero := HeroModel.new()
	add_child(hero)
	hero.setup("female", {"hair": ["Hair_Long"], "hair_color": [0.5, 0.25, 0.1]}, "summoner")
	await get_tree().process_frame
	await get_tree().process_frame
	var sk: Skeleton3D = hero.skeleton
	for b in ["pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "Head", "head", "clavicle_l", "upperarm_l"]:
		var i := sk.find_bone(b)
		if i >= 0:
			var t: Transform3D = sk.global_transform * sk.get_bone_global_pose(i)
			print("BONE ", b, " ", t.origin, " zaxis ", t.basis.z, " yaxis ", t.basis.y)
	print("HEROSCALE ", hero.global_transform.basis.get_scale(), " skel ", sk.global_transform.basis.get_scale())
	get_tree().quit()
