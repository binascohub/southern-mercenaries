extends SceneTree
## Ícone do cajado do Mago no inventário (128 px): assets/ui/icons/staff_D.png, renderizado do Staff_D.glb (staff-d.glb enviado pelo autor do projeto,
## autor/licença a confirmar). Só o rank D tem ícone por enquanto (como a adaga do Ninja); o cajado aparece na diagonal, com fundo transparente.
##   godot --path . -s tools/assets/staff_icons.gd
var _vp: SubViewport
var _frame := 0


func _initialize() -> void:
	_vp = SubViewport.new()
	_vp.size = Vector2i(128, 128)
	_vp.transparent_bg = true
	_vp.own_world_3d = true
	_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(_vp)
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 1.95
	cam.position = Vector3(0.0, 0.8, 5.0)
	_vp.add_child(cam)
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
	var pivot := Node3D.new()
	pivot.position = Vector3(0, 0.8, 0)  # gira em torno do meio do cajado (1,6 m de altura)
	pivot.rotation_degrees = Vector3(0, 0, -40)
	_vp.add_child(pivot)
	var staff: Node3D = (load("res://assets/models/props/Staff_D.glb") as PackedScene).instantiate()
	staff.position = Vector3(0, -0.8, 0)
	pivot.add_child(staff)


func _process(_delta: float) -> bool:
	_frame += 1
	if _frame == 8:
		_vp.get_texture().get_image().save_png("res://assets/ui/icons/staff_D.png")
		quit()
	return false
