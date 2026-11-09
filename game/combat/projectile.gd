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
var crit_mult := 1.5
## Habilidades: o golpe completo (Elements.resolve_hit) e a explosão em área.
var hit := {}
var explode := 0.0
## Flecha do Arqueiro: o elemento do golpe escolhe o modelo (ARROWS); vazio = orbe.
var arrow := ""
## Habilidade de quem atirou (efeito visual próprio, SpellFx; "" = o genérico por elemento).
var fx := ""
## O ataque do Invocador: em vez do orbe, uma ave (o Falcão) voa até o alvo (`bird_scale` cresce no ataque forte).
var bird := false
var bird_scale := 0.5

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
	projectile.crit_mult = spawn.get("crit_mult", 1.5)
	projectile.hit = spawn.get("hit", {})
	projectile.explode = spawn.get("explode", 0.0)
	projectile.arrow = String(spawn.get("arrow", ""))
	projectile.fx = String(spawn.get("fx", ""))
	projectile.bird = bool(spawn.get("bird", false))
	projectile.bird_scale = float(spawn.get("bird_scale", 0.5))
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

	# Núcleo brilhante e rastro de partículas do elemento (fx.gd).
	var look := element if element != "" else Fx.element_for(color)
	if bird and Kit.has("Falcon"):
		_add_bird(look)
	elif ARROWS.has(arrow) and Kit.has(ARROWS[arrow]):
		_add_arrow(look)
	elif fx == "" or not SpellFx.projectile(self, fx, direction, radius, color):
		Fx.orb(self, color, look, radius)
		Fx.trail(self, color, look, radius)

	body_entered.connect(_on_body_entered)


## Flechas por elemento ("Arrows", Akshat, CC BY 4.0; tools/assets/build_element_arrows.py): 0,8 m, ponta para +Z.
const ARROWS := {"fire": "Arrow_Fire", "water": "Arrow_Water", "air": "Arrow_Air", "earth": "Arrow_Earth"}


## Flecha do Arqueiro, de ponta para o alvo, com o rastro do elemento.
func _add_arrow(look: String) -> void:
	var holder := Node3D.new()
	add_child(holder)
	holder.rotation.y = atan2(direction.x, direction.z)
	holder.add_child(Kit.piece(ARROWS[arrow]))
	Fx.trail(self, color, look, radius * 0.6)


## Falcão em voo (modelo do jogo, com a animação de bater asas), de frente para o alvo, com o rastro do elemento.
func _add_bird(look: String) -> void:
	var holder := Node3D.new()
	add_child(holder)
	holder.rotation.y = atan2(direction.x, direction.z)
	var falcon := Kit.piece("Falcon")
	falcon.scale = Vector3.ONE * bird_scale
	holder.add_child(falcon)
	var wings := falcon.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if wings and not wings.get_animation_list().is_empty():
		var clip: StringName = &"Fly_Loop" if wings.has_animation(&"Fly_Loop") else wings.get_animation_list()[0]
		wings.get_animation(clip).loop_mode = Animation.LOOP_LINEAR
		wings.play(clip)
	if bird_scale > 0.55:
		# Ataque forte: o mesmo rastro, só que mais forte (maior, mais denso e mais longo); a cor não muda.
		var trail := Fx.trail(self, color, look, radius * 1.8)
		trail.amount = 56
		trail.lifetime = 0.6
	else:
		Fx.trail(self, color, look, radius * 0.6)


func _physics_process(delta: float) -> void:
	var step := speed * delta
	global_position += direction * step
	_travelled += step
	if _travelled >= max_range:
		if multiplayer.is_server():
			_ignite(global_position)
			queue_free()
		else:
			visible = false


func _on_body_entered(body: Node) -> void:
	if body in _hit:
		return
	if body.is_in_group(&"enemies"):
		_hit.append(body)
		var full := hit if not hit.is_empty() else \
			{"damage": damage, "element": element, "state": state, "crit_chance": crit_chance, "crit_mult": crit_mult}
		if explode > 0.0:
			# Bola de Fogo: explode e acerta todos em volta (inclusive o alvo).
			get_tree().call_group(&"arena", &"skill_burst", body.global_position, explode, full, fx)
			queue_free()
			return
		body.take_hit(full)
		pierce -= 1
		if pierce < 0:
			_ignite(body.global_position)
			queue_free()
	else:
		if explode > 0.0:
			get_tree().call_group(&"arena", &"skill_burst", global_position, explode, hit, fx)
		_ignite(global_position)
		queue_free()


## Flecha do Leque de fogo (hit.ground): deixa uma poça de fogo onde acerta ou cai. Só no servidor.
func _ignite(at: Vector3) -> void:
	if multiplayer.is_server() and hit.has("ground"):
		get_tree().call_group(&"arena", &"skill_ground", at, hit)
