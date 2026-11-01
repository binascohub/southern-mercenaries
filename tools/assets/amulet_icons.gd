extends SceneTree
## Ícones do amuleto no inventário (128 px): assets/ui/icons/amulet_D.png ... amulet_S.png, renderizados do Necklace.glb
## (Necklace, Paul Wortmann, CC0) na cor do material de cada rank (D madeira natural, C aço, B cobre, A prata, S ouro).
##   godot --path . -s tools/assets/amulet_icons.gd
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
	cam.fov = 38.0
	cam.look_at_from_position(Vector3(0.1, 0.0, 0.34), Vector3(0.1, 0.0, 0), Vector3.UP)  # enquadra a gema e um trecho do cordão
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
	var old := _vp.get_node_or_null("amulet")
	if old:
		old.free()
	var neck: Node3D = (load("res://assets/models/props/Necklace.glb") as PackedScene).instantiate()
	neck.name = "amulet"
	neck.rotation_degrees = Vector3(-62, 0, 12)  # deitado, visto de cima em perspectiva (o colar é um cordão em anel com a gema na ponta)
	for node in neck.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		for i in mesh.get_surface_override_material_count():
			var source := mesh.get_active_material(i) as StandardMaterial3D
			if source:
				var copy := source.duplicate() as StandardMaterial3D
				copy.albedo_color = Color.WHITE.lerp(TINTS[rank], 0.6) if rank != "D" else Color.WHITE
				mesh.set_surface_override_material(i, copy)
	_vp.add_child(neck)


func _process(_delta: float) -> bool:
	_frame += 1
	if _frame % 6 == 0:
		var rank: String = _ranks[_index]
		_vp.get_texture().get_image().save_png("res://assets/ui/icons/amulet_%s.png" % rank)
		_index += 1
		if _index >= _ranks.size():
			quit()
		else:
			_show(_ranks[_index])
	return false
