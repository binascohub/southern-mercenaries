# Southern Mercenaries — GPL-3.0-or-later
class_name Projectile
extends Area3D
## Projétil reto dos jogadores. Atravessa `pierce` inimigos; some ao bater
## em parede ou ao atingir o alcance.
##
## Leva o elemento de quem atirou e, no ataque forte, o estado básico dele
## (02-0-elementos.md, seção 5.3); o alvo resolve fraqueza, combos e crítico.
##
## Rede: o movimento é determinístico, então todos os PCs só o simulam a partir
## dos dados do spawn. Acerto e dano são decididos só no servidor, que remove
## o projétil (e o spawner o remove dos outros PCs).

var direction := Vector3.FORWARD
var speed := 20.0
var max_range := 10.0
var radius := 0.25
var damage := 10.0
var pierce := 0
var color := Color.WHITE
var element := ""
## Estado aplicado ao acertar ("" no ataque básico).
var state := ""
var crit_chance := 0.05
## Habilidades: o golpe completo (Elements.resolve_hit) e a explosão em área.
var hit := {}
var explode := 0.0

var _travelled := 0.0
var _hit: Array[Node] = []


static func create(spawn: Dictionary) -> Projectile:
	var projectile := Projectile.new()
	projectile.position = spawn.position
	projectile.direction = spawn.direction
	projectile.speed = spawn.speed
	projectile.max_range = spawn.range
	projectile.radius = spawn.radius
	projectile.pierce = spawn.pierce
	projectile.damage = spawn.damage
	projectile.color = spawn.color
	projectile.element = spawn.get("element", "")
	projectile.state = spawn.get("state", "")
	projectile.crit_chance = spawn.get("crit_chance", 0.05)
	projectile.hit = spawn.get("hit", {})
	projectile.explode = spawn.get("explode", 0.0)
	return projectile


func _ready() -> void:
	collision_layer = 8
	collision_mask = 1 | 4
	monitorable = false
	monitoring = multiplayer.is_server()
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
		if multiplayer.is_server():
			queue_free()
		else:
			visible = false


func _on_body_entered(body: Node) -> void:
	if body in _hit:
		return
	if body.is_in_group(&"enemies"):
		_hit.append(body)
		var full := hit if not hit.is_empty() else \
			{"damage": damage, "element": element, "state": state, "crit_chance": crit_chance}
		if explode > 0.0:
			# Bola de Fogo: explode e acerta todos em volta (inclusive o alvo).
			get_tree().call_group(&"arena", &"skill_burst", body.global_position, explode, full)
			queue_free()
			return
		body.take_hit(full)
		pierce -= 1
		if pierce < 0:
			queue_free()
	else:
		if explode > 0.0:
			get_tree().call_group(&"arena", &"skill_burst", global_position, explode, hit)
		queue_free()
