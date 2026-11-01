extends SceneTree
func _init() -> void:
	var dir := DirAccess.open("res://tmp_ruins")
	for d in dir.get_directories():
		var sub := DirAccess.open("res://tmp_ruins/" + d)
		for f in sub.get_files():
			if f.to_lower().ends_with(".dae"):
				var path := "res://tmp_ruins/%s/%s" % [d, f]
				var scn := load(path) as PackedScene
				if scn == null:
					print("FALHOU ", path); continue
				var root := scn.instantiate()
				var names := []
				var box := AABB(); var first := true
				for n in root.find_children("*", "", true, false):
					var s := String(n.name)
					if n is MeshInstance3D:
						var mi := n as MeshInstance3D
						var a: AABB = mi.get_aabb()
						names.append("%s(%d surf, %s)" % [s, mi.mesh.get_surface_count() if mi.mesh else 0, str(a.size).substr(0, 24)])
				print("OK ", f, " ", names)
				root.free()
	quit()
