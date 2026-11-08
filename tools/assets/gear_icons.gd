extends SceneTree
## Ícones de inventário por material (128 px, fundo transparente): assets/ui/icons/<base>_<material>.png, renderizados
## dos mesmos modelos que aparecem no chão (game/rpg/item_models.gd: capuz, túnica, luvas, botas, anel, boné, colete,
## máscara, peitoral e barda em pano, ferro e aço) e, para o aço, da adaga (Dagger_C) e do cajado (Staff_D na cor do aço).
## Items.equipment_icon usa <base>_<material>.png antes do ícone por rank.
##   godot --path . -s tools/assets/gear_icons.gd   (precisa de janela: o modo --headless não renderiza)

const MATERIALS := ["cloth", "iron", "steel"]
## Prefixo do ícone de cada base (o mesmo de Items.equipment_icon).
const PREFIX := {"daggers": "dagger", "staff": "staff"}
var _vp: SubViewport
var _cam: Camera3D
var _jobs: Array = []
var _index := 0
var _frame := 0


func _initialize() -> void:
	for base in ItemModels.BASES:
		for material in MATERIALS:
			_jobs.append([base, material])
	_jobs.append(["daggers", "steel"])
	_jobs.append(["staff", "steel"])
	_vp = SubViewport.new()
	_vp.size = Vector2i(128, 128)
	_vp.transparent_bg = true
	_vp.own_world_3d = true
	_vp.msaa_3d = Viewport.MSAA_4X
	_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(_vp)
	_cam = Camera3D.new()
	_cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	_vp.add_child(_cam)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-40, 30, 0)
	light.light_energy = 1.3
	_vp.add_child(light)
	var env := Environment.new()
	env.background_mode = Environment.BG_CLEAR_COLOR
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.75, 0.75, 0.78)
	env.ambient_light_energy = 0.9
	env.background_color = Color(0.6, 0.6, 0.62, 0.0)  # o metal reflete um cinza, não o preto
	env.reflected_light_source = Environment.REFLECTION_SOURCE_BG
	var world := WorldEnvironment.new()
	world.environment = env
	_vp.add_child(world)
	_show()


func _model(base: String, material: String) -> Node3D:
	if base == "daggers":
		var dagger := Kit.piece("Dagger_C")
		dagger.rotation_degrees = Vector3(0, 0, -45)  # na diagonal, como os outros ícones de arma
		return _wrap(dagger)
	if base == "staff":
		var staff := Kit.piece("Staff_D")
		_tint(staff, ItemModels.PALETTE[material].main)
		staff.rotation_degrees = Vector3(0, 0, -45)
		return _wrap(staff)
	return ItemModels.gear(base, material)


func _wrap(node: Node3D) -> Node3D:
	var holder := Node3D.new()
	holder.add_child(node)
	return holder


func _show() -> void:
	var old := _vp.get_node_or_null("Item")
	if old:
		old.free()
	var job: Array = _jobs[_index]
	var node := _model(job[0], job[1])
	node.name = "Item"
	var box := _bounds(node)
	node.position = -box.get_center()
	_vp.add_child(node)
	# Vista de 3/4 (de frente, um pouco de cima e de lado), enquadrando a peça inteira.
	var radius := box.size.length() / 2.0
	var dir := Vector3(0.45, 0.45, 1.0).normalized()
	if job[0] in ["daggers", "staff"]:
		dir = Vector3(0, 0.15, 1.0).normalized()
	_cam.size = maxf(box.size.x, box.size.y) * 1.1 if job[0] in ["daggers", "staff"] else radius * 1.75
	_cam.look_at_from_position(dir * radius * 4.0, Vector3.ZERO, Vector3.UP)


func _process(_delta: float) -> bool:
	_frame += 1
	if _frame % 8 == 0:
		var job: Array = _jobs[_index]
		var path := "res://assets/ui/icons/%s_%s.png" % [PREFIX.get(job[0], job[0]), job[1]]
		_vp.get_texture().get_image().save_png(path)
		print("OK ", path)
		_index += 1
		if _index >= _jobs.size():
			quit()
		else:
			_show()
	return false


## Cópias de LootDrop._tint/_bounds (LootDrop usa o GameData, que não existe no modo -s).
func _tint(node: Node3D, tint: Color) -> void:
	for found in node.find_children("*", "MeshInstance3D", true, false):
		var mi := found as MeshInstance3D
		for i in mi.mesh.get_surface_count():
			var source := mi.get_active_material(i) as BaseMaterial3D
			if source:
				var copy := source.duplicate() as BaseMaterial3D
				copy.albedo_color = source.albedo_color * tint
				mi.set_surface_override_material(i, copy)


func _bounds(node: Node3D) -> AABB:
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
