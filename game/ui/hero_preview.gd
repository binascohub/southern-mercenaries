# Southern Mercenaries — GPL-3.0-or-later
class_name HeroPreview
extends SubViewportContainer
## Prévia 3D do herói na criação de personagem: o mesmo modelo do jogo, girando devagar,
## que se refaz a cada mudança de sexo, cabelo, barba ou pele.

var _viewport: SubViewport
var _holder: Node3D
var _model: HeroModel


func _init() -> void:
	custom_minimum_size = Vector2(220, 300)
	stretch = true
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_viewport = SubViewport.new()
	_viewport.own_world_3d = true
	_viewport.transparent_bg = true
	_viewport.msaa_3d = Viewport.MSAA_2X
	add_child(_viewport)
	_holder = Node3D.new()
	_viewport.add_child(_holder)
	var camera := Camera3D.new()
	camera.fov = 30.0
	_viewport.add_child(camera)
	camera.look_at_from_position(Vector3(0, 1.0, 4.3), Vector3(0, 0.95, 0))
	var key := DirectionalLight3D.new()
	key.light_energy = 1.1
	key.rotation_degrees = Vector3(-35, -25, 0)
	_viewport.add_child(key)
	var env := Environment.new()
	env.background_mode = Environment.BG_CLEAR_COLOR
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.9, 0.8, 0.7)
	env.ambient_light_energy = 0.7
	var world_env := WorldEnvironment.new()
	world_env.environment = env
	_viewport.add_child(world_env)


func _process(delta: float) -> void:
	if _holder and visible:
		_holder.rotation.y += delta * 0.5


## Mostra o herói do sexo dado com a aparência (formato da ficha, ver Appearance) e, se `gear_rank`
## (D a S) vier, com o equipamento dessa classificação.
func show_hero(sex: String, look: Dictionary, gear_rank := "", class_id := "ninja", element := "fire", hooded := false) -> void:
	if _model:
		_holder.remove_child(_model)
		_model.queue_free()
	_model = HeroModel.new()
	_holder.add_child(_model)
	_model.setup(sex, Appearance.model_look(sex, look, {}), class_id)
	_model.set_suit_element(element)
	_model.set_hooded(hooded)  # Ninja: com ou sem capuz e máscara (a caixa da criação); sem, o rosto e o cabelo aparecem
	_model.set_outfit({})
	if gear_rank != "":
		# Prévia do equipamento da classe no rank escolhido (todas as peças do mesmo rank).
		HeroGear.apply(_model, class_id, {"body": gear_rank, "head": gear_rank, "hands": gear_rank, "feet": gear_rank})
