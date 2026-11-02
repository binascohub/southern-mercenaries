extends SceneTree
## Ícones do arco do Arqueiro no inventário (128 px): assets/ui/icons/bow_D.png ... bow_S.png, renderizados do Bow_Vulture.glb
## (Vulture Bow, Mophs / genderfreak, CC-BY 4.0) na cor do material de cada rank (D madeira natural, C aço, B cobre, A prata, S ouro).
##   godot --path . -s tools/assets/bow_icons.gd
const TINTS := {"D": Color(1, 1, 1), "C": Color("b8bfc6"), "B": Color("c06a3c"), "A": Color("eef2f5"), "S": Color("e3b23c")}
var _vp: SubViewport
var _frame := 0
var _ranks: Array = TINTS.keys()
var _index := 0


func _initialize() -> void:
	_vp = SubViewport.new()
	_vp.size = Vector2i(128, 128)
	_vp.transparent_bg = true
	_vp.own_world_3d = true
	_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(_vp)
	var cam := Camera3D.new()
	_vp.add_child(cam)
	cam.fov = 35.0
	cam.look_at_from_position(Vector3(0.0, 0.62, 2.4), Vector3(0, 0.6, 0), Vector3.UP)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-30, 35, 0)
	_vp.add_child(light)
	var env := Environment.new()
	env.background_mode = Environment.BG_CLEAR_COLOR
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.85, 0.85, 0.85)
	var world := WorldEnvironment.new()
	world.environment = env
	_vp.add_child(world)
	_show(_ranks[0])


func _show(rank: String) -> void:
	var old := _vp.get_node_or_null("bow")
	if old:
		old.free()
	var bow: Node3D = (load("res://assets/models/props/Bow_Vulture.glb") as PackedScene).instantiate()
	bow.name = "bow"
	bow.rotation_degrees = Vector3(0, 90, 18)  # o arco de lado, levemente inclinado
	for node in bow.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		for i in mesh.get_surface_override_material_count():
			var source := mesh.get_active_material(i) as StandardMaterial3D
			if source:
				var copy := source.duplicate() as StandardMaterial3D
				copy.albedo_color = Color.WHITE.lerp(TINTS[rank], 0.6) if rank != "D" else Color.WHITE
				mesh.set_surface_override_material(i, copy)
	_vp.add_child(bow)


func _process(_delta: float) -> bool:
	_frame += 1
	if _frame % 6 == 0:
		var rank: String = _ranks[_index]
		_vp.get_texture().get_image().save_png("res://assets/ui/icons/bow_%s.png" % rank)
		_index += 1
		if _index >= _ranks.size():
			quit()
		else:
			_show(_ranks[_index])
	return false
