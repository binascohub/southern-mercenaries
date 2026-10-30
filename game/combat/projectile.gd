# Southern Mercenaries — GPL-3.0-or-later
class_name Projectile
extends Area3D
## Projétil reto dos jogadores. Atravessa `pierce` inimigos; some ao bater
## em parede ou ao atingir o alcance.

var direction := Vector3.FORWARD
var speed := 20.0
var max_range := 10.0
var radius := 0.25
var damage := 10.0
var pierce := 0
var color := Color.WHITE

var _travelled := 0.0
var _hit: Array[Node] = []


func _ready() -> void:
	collision_layer = 8
	collision_mask = 1 | 4
	monitorable = false
	var shape := CollisionShape3D.new()
	var sphere := SphereShape3D.new()
	sphere.radius = radius
	shape.shape = sphere
	add_child(shape)

	var mesh := MeshInstance3D.new()
	var sphere_mesh := SphereMesh.new()
	sphere_mesh.radius = radius
	sphere_mesh.height = radius * 2.0
	sphere_mesh.radial_segments = 12
	sphere_mesh.rings = 6
	mesh.mesh = sphere_mesh
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = color
	mesh.material_override = material
	mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mesh)

	body_entered.connect(_on_body_entered)


func _physics_process(delta: float) -> void:
	var step := speed * delta
	global_position += direction * step
	_travelled += step
	if _travelled >= max_range:
		queue_free()


func _on_body_entered(body: Node) -> void:
	if body in _hit:
		return
	if body.is_in_group(&"enemies"):
		_hit.append(body)
		if multiplayer.is_server():
			body.take_damage(damage)
		pierce -= 1
		if pierce < 0:
			queue_free()
	else:
		queue_free()
