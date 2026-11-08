# Southern Mercenaries — GPL-3.0-or-later
class_name Fx
extends RefCounted
## Efeitos visuais das magias e golpes (só visual, em todos os PCs): partículas
## por elemento (02-0-elementos.md) — Fogo: chamas e brasas subindo; Água: gotas
## que caem e respingam; Ar: redemoinho claro girando; Terra: pedrinhas e poeira
## caindo; sem elemento: faíscas brancas. Usado pelos projéteis (núcleo
## brilhante e rastro), pelas explosões e áreas no chão (anel que se abre e
## partículas) e pelos feixes. Partículas de CPU: funcionam no renderizador de
## compatibilidade.

static var _soft: GradientTexture2D
static var _materials := {}


## Elemento pela cor (as chamadas antigas só passam a cor do elemento).
static func element_for(color: Color) -> String:
	var best := ""
	var best_d := 0.12
	for id: String in ["fire", "water", "air", "earth"]:
		var c := Elements.color(id)
		var d := Vector3(c.r - color.r, c.g - color.g, c.b - color.b).length()
		if d < best_d:
			best = id
			best_d = d
	return best


## Rastro do projétil (preso a ele, partículas no mundo).
static func trail(parent: Node3D, color: Color, element: String, radius: float) -> CPUParticles3D:
	var p := _particles(element, color, maxf(radius, 0.15))
	p.amount = 24
	p.lifetime = 0.35 if element != "fire" else 0.45
	p.local_coords = false
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	p.emission_sphere_radius = radius * 0.6
	p.initial_velocity_min = 0.2
	p.initial_velocity_max = 0.8
	parent.add_child(p)
	return p


## Núcleo brilhante do projétil: esfera acesa e um halo suave em volta.
static func orb(parent: Node3D, color: Color, element: String, radius: float) -> void:
	var core := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = radius * 0.7
	sphere.height = radius * 1.4
	sphere.radial_segments = 12
	sphere.rings = 6
	core.mesh = sphere
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = color.lightened(0.45)
	core.material_override = material
	core.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(core)
	var halo := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2.ONE * radius * 4.0
	halo.mesh = quad
	halo.material_override = _glow_material(color)
	halo.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(halo)
	if element == "earth":
		# Pedra rolando: núcleo marrom, sem halo forte.
		material.albedo_color = color.darkened(0.35)
		halo.scale = Vector3.ONE * 0.6


## Explosão ou área no chão: anel que se abre, disco que esmaece e partículas.
## Áreas longas (fumaça, chão em chamas) soltam partículas o tempo todo.
## Morte de chefe final: o chão estoura onde ele caiu ("Bomb Crack_Ground_00 (Free)", paulyang, CC BY 4.0; tools/assets/build_boss_crack.py):
## o entulho de concreto salta até ~4 m e cai espalhado em ~6 m em volta, fica um pouco e afunda. `scale` acompanha o tamanho do chefe.
const BOSS_CRACK := "res://assets/fx/boss_crack.glb"
const BOSS_CRACK_HOLD := 4.0


static func boss_crack(parent: Node, at: Vector3, scale := 1.0) -> void:
	if not ResourceLoader.exists(BOSS_CRACK):
		return
	var node := (load(BOSS_CRACK) as PackedScene).instantiate() as Node3D
	parent.add_child(node)
	node.global_position = Vector3(at.x, Hazards.ground_y, at.z)
	node.rotation.y = randf() * TAU
	node.scale = Vector3.ONE * scale
	var player := node.find_child("AnimationPlayer", true, false) as AnimationPlayer
	var length := 3.3
	if player and player.has_animation("burst"):
		player.play("burst")
		length = player.get_animation("burst").length
	var tween := node.create_tween()
	tween.tween_interval(length + BOSS_CRACK_HOLD)
	tween.tween_property(node, "position:y", node.position.y - 0.6 * scale, 1.5)
	tween.tween_callback(node.queue_free)


static func burst(parent: Node, at: Vector3, radius: float, color: Color, element: String, duration: float) -> void:
	var root := Node3D.new()
	parent.add_child(root)
	root.global_position = Vector3(at.x, 0.05 + Hazards.ground_y, at.z)
	var lasting := duration > 0.8
	# Disco suave no chão.
	var disc := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2.ONE * radius * 2.2
	quad.orientation = PlaneMesh.FACE_Y
	disc.mesh = quad
	var disc_material := _glow_material(color).duplicate() as StandardMaterial3D
	disc_material.billboard_mode = BaseMaterial3D.BILLBOARD_DISABLED
	# Fraco e na cor do elemento (aditivo: forte demais vira névoa cinza).
	disc_material.albedo_color = Color(color.r * 0.8, color.g * 0.8, color.b * 0.8, 0.22 if lasting else 0.4)
	disc.material_override = disc_material
	disc.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	root.add_child(disc)
	# Anel que se abre até a borda.
	var ring := MeshInstance3D.new()
	var torus := TorusMesh.new()
	torus.inner_radius = 0.9
	torus.outer_radius = 1.0
	torus.rings = 32
	ring.mesh = torus
	var ring_material := StandardMaterial3D.new()
	ring_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	ring_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	ring_material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	ring_material.albedo_color = Color(color.lightened(0.3), 0.9)
	ring.material_override = ring_material
	ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	ring.scale = Vector3(radius * 0.25, 0.3, radius * 0.25)
	root.add_child(ring)
	var open_time := clampf(duration * 0.6, 0.2, 0.45)
	var tween := root.create_tween().set_parallel()
	tween.tween_property(ring, "scale", Vector3(radius, 0.3, radius), open_time).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	tween.tween_property(ring_material, "albedo_color:a", 0.0, open_time + 0.15).set_ease(Tween.EASE_IN)
	tween.tween_property(disc_material, "albedo_color:a", 0.0, maxf(duration, 0.3)).set_ease(Tween.EASE_IN)
	# Partículas do elemento.
	var p := _particles(element, color, clampf(radius * 0.18, 0.15, 0.45))
	p.amount = clampi(roundi(radius * 14.0), 12, 64)
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_RING
	p.emission_ring_axis = Vector3.UP
	p.emission_ring_radius = radius * 0.85
	p.emission_ring_inner_radius = radius * 0.1
	p.emission_ring_height = 0.1
	if lasting:
		p.lifetime = 0.8
	else:
		p.one_shot = true
		p.explosiveness = 0.9
		p.lifetime = 0.7
	root.add_child(p)
	var life := maxf(duration, 0.3)
	if lasting:
		# Ligado ao método da partícula (não a uma função anônima): se ela for liberada antes
		# (o dono do efeito saiu de cena), a ligação some junto, sem erro.
		root.get_tree().create_timer(life, false).timeout.connect(p.set_emitting.bind(false))
	root.get_tree().create_timer(life + 1.0, false).timeout.connect(root.queue_free)


## Feixe de `a` a `b` (raio, corrente, investida): faixa brilhante e partículas
## ao longo dela.
static func beam(parent: Node, a: Vector3, b: Vector3, width: float, color: Color, element: String, duration: float) -> void:
	var length := a.distance_to(b)
	if length < 0.01:
		return
	var root := Node3D.new()
	parent.add_child(root)
	root.global_position = (a + b) / 2.0
	root.look_at(b, Vector3.UP if absf((b - a).normalized().y) < 0.99 else Vector3.FORWARD)
	var core := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(width * 0.35, width * 0.35, length)
	core.mesh = box
	var core_material := StandardMaterial3D.new()
	core_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	core_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	core_material.albedo_color = Color(color.lightened(0.6), 0.95)
	core.material_override = core_material
	core.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	root.add_child(core)
	var glow := MeshInstance3D.new()
	var glow_box := BoxMesh.new()
	glow_box.size = Vector3(width, width * 0.6, length)
	glow.mesh = glow_box
	var glow_material := StandardMaterial3D.new()
	glow_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	glow_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	glow_material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	glow_material.albedo_color = Color(color, 0.45)
	glow.material_override = glow_material
	glow.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	root.add_child(glow)
	var p := _particles(element, color, clampf(width * 0.6, 0.1, 0.35))
	p.amount = clampi(roundi(length * 6.0), 8, 48)
	p.one_shot = true
	p.explosiveness = 0.8
	p.lifetime = 0.5
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	p.emission_box_extents = Vector3(width * 0.3, width * 0.2, length / 2.0)
	root.add_child(p)
	var life := maxf(duration, 0.1)
	var tween := root.create_tween().set_parallel()
	tween.tween_property(core_material, "albedo_color:a", 0.0, life).set_ease(Tween.EASE_IN)
	tween.tween_property(glow_material, "albedo_color:a", 0.0, life).set_ease(Tween.EASE_IN)
	tween.tween_property(core, "scale", Vector3(0.3, 0.3, 1.0), life)
	root.get_tree().create_timer(life + 0.6, false).timeout.connect(root.queue_free)


# --- Partículas -----------------------------------------------------------------

static func _particles(element: String, color: Color, size: float) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	p.mesh = _particle_mesh(element, size)
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	p.direction = Vector3.UP
	p.spread = 60.0
	var ramp := Gradient.new()
	match element:
		"fire":
			p.gravity = Vector3(0, 3.0, 0)
			p.initial_velocity_min = 0.8
			p.initial_velocity_max = 2.2
			p.damping_min = 1.0
			p.damping_max = 2.0
			p.scale_amount_min = 0.6
			p.scale_amount_max = 1.2
			ramp.set_color(0, Color(1.0, 0.95, 0.6, 1.0))
			ramp.set_color(1, Color(0.6, 0.08, 0.02, 0.0))
			ramp.add_point(0.35, Color(1.0, 0.5, 0.1, 0.9))
		"water":
			p.gravity = Vector3(0, -9.0, 0)
			p.initial_velocity_min = 2.0
			p.initial_velocity_max = 4.0
			p.spread = 35.0
			p.scale_amount_min = 0.5
			p.scale_amount_max = 1.0
			ramp.set_color(0, Color(0.8, 0.95, 1.0, 0.95))
			ramp.set_color(1, Color(0.2, 0.5, 1.0, 0.0))
		"air":
			p.gravity = Vector3(0, 0.6, 0)
			p.initial_velocity_min = 0.5
			p.initial_velocity_max = 1.5
			p.tangential_accel_min = 6.0
			p.tangential_accel_max = 10.0
			p.spread = 90.0
			p.scale_amount_min = 0.7
			p.scale_amount_max = 1.4
			ramp.set_color(0, Color(1.0, 1.0, 1.0, 0.8))
			ramp.set_color(1, Color(color.r, color.g, color.b, 0.0))
		"earth":
			p.gravity = Vector3(0, -12.0, 0)
			p.initial_velocity_min = 2.5
			p.initial_velocity_max = 4.5
			p.spread = 40.0
			p.angular_velocity_min = -360.0
			p.angular_velocity_max = 360.0
			p.scale_amount_min = 0.5
			p.scale_amount_max = 1.1
			ramp.set_color(0, Color(0.55, 0.42, 0.26, 1.0))
			ramp.set_color(1, Color(0.35, 0.3, 0.2, 0.0))
			ramp.add_point(0.7, Color(0.45, 0.38, 0.25, 0.9))
		_:
			p.gravity = Vector3(0, -2.0, 0)
			p.initial_velocity_min = 1.0
			p.initial_velocity_max = 3.0
			p.spread = 180.0
			p.scale_amount_min = 0.4
			p.scale_amount_max = 0.8
			ramp.set_color(0, Color(1, 1, 1, 1))
			ramp.set_color(1, Color(color.r, color.g, color.b, 0.0))
	p.color_ramp = ramp
	return p


## Pedrinhas de terra são cubos; o resto, quadrados suaves virados para a câmera.
static func _particle_mesh(element: String, size: float) -> Mesh:
	if element == "earth":
		var box := BoxMesh.new()
		box.size = Vector3.ONE * size * 0.5
		box.material = _particle_material(false)
		return box
	var quad := QuadMesh.new()
	quad.size = Vector2.ONE * size * (1.6 if element == "fire" else 1.0)  # a chama do sprite ocupa menos do quadrado
	quad.material = _particle_material(true, element)
	return quad


## Sprite por elemento (Kenney Particle Pack): chama no Fogo, redemoinho no Ar, brilho suave na Água, estrela sem elemento.
const ELEMENT_SPRITES := {"fire": "flame_05", "air": "twirl_02", "water": "circle_05", "": "star_06"}


static func _particle_material(soft: bool, element := "") -> StandardMaterial3D:
	var key := ("soft" + element) if soft else "solid"
	if _materials.has(key):
		return _materials[key]
	var material := StandardMaterial3D.new()
	material.vertex_color_use_as_albedo = true
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	if soft:
		material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
		material.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
		var sprite := "res://assets/fx/particles/%s.png" % String(ELEMENT_SPRITES.get(element, "circle_05"))
		material.albedo_texture = load(sprite) if ResourceLoader.exists(sprite) else _soft_texture()
	else:
		material.roughness = 0.9
	_materials[key] = material
	return material


## Halo/disco suave na cor dada (aditivo, virado para a câmera).
static func _glow_material(color: Color) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	material.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	material.albedo_texture = _soft_texture()
	material.albedo_color = Color(color, 0.8)
	return material


static func _soft_texture() -> GradientTexture2D:
	if _soft == null:
		var gradient := Gradient.new()
		gradient.set_color(0, Color(1, 1, 1, 1))
		gradient.set_color(1, Color(1, 1, 1, 0))
		gradient.add_point(0.4, Color(1, 1, 1, 0.55))
		_soft = GradientTexture2D.new()
		_soft.gradient = gradient
		_soft.fill = GradientTexture2D.FILL_RADIAL
		_soft.fill_from = Vector2(0.5, 0.5)
		_soft.fill_to = Vector2(1.0, 0.5)
		_soft.width = 64
		_soft.height = 64
	return _soft
