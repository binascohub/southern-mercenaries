# Southern Mercenaries — GPL-3.0-or-later
class_name Hazards
extends Node
## Perigos no chão dos mapas (03-2-areas.md; 03-inimigos.md): poças de lodo
## tóxico (fixas da área, do cuspe do Sapo Ácido e do rastro das elites tóxicas)
## e as marcas de aviso dos golpes de monstro no chão. O servidor guarda as
## poças e tira vida de quem está dentro a cada `hazard_tick`; os visuais vão
## para a raiz da área (somem ao trocar de área).

## Cores da mancha de lodo (centro brilhante, miolo, borda escura) e das bolhas.
const SLIME_CORE := Color(0.55, 0.78, 0.2, 0.9)
const SLIME_MID := Color(0.3, 0.52, 0.12, 0.85)
const SLIME_RIM := Color(0.12, 0.22, 0.06, 0.5)
const SLIME_BUBBLE := Color(0.72, 0.9, 0.4, 0.75)
const SLIME_SEGMENTS := 40
const WARNING_COLOR := Color(0.95, 0.2, 0.1, 0.4)
## Padrões das marcas de perigo (Kenney Pattern Pack, CC0) e o shader que os desliza dentro do círculo.
const PATTERN_SHADER := preload("res://assets/shaders/pattern_decal.gdshader")
const PATTERNS := "res://assets/fx/patterns/%s.png"
## Estilo do aviso pelo tipo do golpe: [padrão, cor, deslize (x, y), repetições por metro].
const WARNING_STYLES := {
	"": ["stripes", Color(0.95, 0.18, 0.08, 0.75), Vector2(0.45, 0.0), 0.5],  # listras de perigo
	"slam": ["cracks", Color(0.95, 0.3, 0.08, 0.8), Vector2(0.0, 0.0), 0.4],  # pisão: chão rachando
	"water": ["waves", Color(0.95, 0.25, 0.15, 0.75), Vector2(0.0, 0.5), 0.45],  # jato d'água, onda
	"pull": ["chevrons", Color(0.95, 0.15, 0.3, 0.8), Vector2(0.0, -0.8), 0.5],  # arpão, bote: setas
	"net": ["net", Color(0.85, 0.2, 0.55, 0.75), Vector2(0.15, 0.15), 0.6],  # rede, tinta: lentidão
	"poison": ["bubbles", Color(0.7, 0.9, 0.15, 0.7), Vector2(0.05, 0.12), 0.55],  # cuspe que deixa poça
	"fire": ["stripes", Color(1.0, 0.45, 0.05, 0.8), Vector2(0.7, 0.0), 0.5],  # bola de fogo, canhão
}

## Onde ficam os discos (a raiz da área atual).
var root: Node3D
## Altura do chão da área atual: nas Docas o piso de tábuas fica ~13 cm acima do zero e esconderia as marcas
## no chão (avisos, poças e as áreas das habilidades em spell_fx.gd e fx.gd usam esta altura).
static var ground_y := 0.0
## Só no servidor: {position, radius, time (<0 = fixa), dps, level}.
var _list: Array[Dictionary] = []
var _tick := 0.0


## Nova área (servidor): esquece as poças e registra as fixas da área.
func reset(area: Dictionary) -> void:
	_list.clear()
	var level := int(area.get("area_level", 1))
	var dps: float = GameData.balance.get("sludge_dps", 3.0) * pow(1.12, level - 1)
	for hazard: Dictionary in area.get("hazards", []):
		_list.append({"position": Vector3(hazard.position[0], 0, hazard.position[1]),
			"radius": float(hazard.radius), "time": -1.0, "dps": dps, "level": level})


## Visuais das poças fixas (todos os PCs, ao montar a área).
func build_static(area: Dictionary) -> void:
	ground_y = 0.14 if String(area.get("style", {}).get("floor", "")).begins_with("Dock_") else 0.0
	for hazard: Dictionary in area.get("hazards", []):
		_slime(Vector3(hazard.position[0], 0, hazard.position[1]), float(hazard.radius), -1.0)


## Poça temporária (servidor), vista em todos os PCs.
func add(at: Vector3, radius: float, duration: float, dps: float, level: int) -> void:
	if not multiplayer.is_server():
		return
	_list.append({"position": Vector3(at.x, 0, at.z), "radius": radius, "time": duration, "dps": dps, "level": level})
	_show_sludge.rpc(at, radius, duration)


## Marca vermelha no chão: o golpe cai ali quando o tempo acabar.
func telegraph(at: Vector3, radius: float, time: float, style := "") -> void:
	if multiplayer.is_server():
		_show_warning.rpc(at, radius, time, style)


## Golpe no chão (cuspe, pisão): quem está dentro leva o dano; com "puddle_time", deixa poça.
func strike(at: Vector3, radius: float, damage: float, level: int, source: Node3D, extra: Dictionary) -> void:
	if not multiplayer.is_server():
		return
	var push := float(extra.get("push", 0.0))
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.alive and _inside(p.global_position, at, radius):
			# O empurrão antes do dano (o golpe sofrido deixa o herói invulnerável).
			if push > 0.0:
				# Vento: para longe do centro (a esquiva escapa do empurrão).
				var away := p.global_position - at
				away.y = 0.0
				if away.length() < 0.1:
					away = Vector3.BACK
				p.knock_back(away.normalized() * push, float(extra.get("push_time", 0.4)))
			# Arpão / âncora ("pull": metros): puxa o herói para o monstro que lançou (a esquiva escapa).
			var pull := float(extra.get("pull", 0.0))
			if pull > 0.0 and source and is_instance_valid(source):
				var to := source.global_position - p.global_position
				to.y = 0.0
				if to.length() > 1.6:
					p.knock_back(to.normalized() * minf(pull, to.length() - 1.4), float(extra.get("push_time", 0.35)))
			p.take_damage(damage, level, source)
			# Rede, piche, grito ("slow": [quanto, segundos]): o herói anda e ataca mais devagar por um tempo.
			var slow: Array = extra.get("slow", [])
			if slow.size() == 2:
				p.add_buff("slow", float(slow[0]), float(slow[1]))
	if extra.get("wind", false):
		_show_gust.rpc(at, radius)
	if extra.has("boom"):
		_show_boom.rpc(at, radius, Color(extra.boom[0], extra.boom[1], extra.boom[2]))
	if float(extra.get("puddle_time", 0.0)) > 0.0:
		add(at, radius, float(extra.puddle_time), float(extra.get("puddle_dps", 3.0)) * pow(1.12, level - 1), level)


## Quantos perigos o servidor acompanha agora (testes).
func count() -> int:
	return _list.size()


func _physics_process(delta: float) -> void:
	if not multiplayer.is_server() or _list.is_empty():
		return
	for hazard in _list.duplicate():
		if hazard.time >= 0.0:
			hazard.time -= delta
			if hazard.time <= 0.0:
				_list.erase(hazard)
	_tick -= delta
	if _tick > 0.0:
		return
	var tick: float = GameData.balance.get("hazard_tick", 0.5)
	_tick = tick
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if not p.alive or p.is_airborne():
			continue  # no ar, passa por cima das poças
		for hazard in _list:
			if _inside(p.global_position, hazard.position, hazard.radius):
				p.take_damage(hazard.dps * tick, hazard.level, null)
				break


static func _inside(point: Vector3, center: Vector3, radius: float) -> bool:
	return Vector2(point.x - center.x, point.z - center.z).length() <= radius


@rpc("authority", "call_local", "reliable")
func _show_sludge(at: Vector3, radius: float, duration: float) -> void:
	_slime(at, radius, duration)


## Estouro no chão (bala de canhão, barril de pólvora): clarão e fumaça na cor dada.
@rpc("authority", "call_local", "reliable")
func _show_boom(at: Vector3, radius: float, color: Color) -> void:
	if root == null or not is_instance_valid(root):
		return
	Fx.burst(root, Vector3(at.x, 0.4, at.z), radius, color, "fire", 0.6)
	Sfx.play("explosion", at)


## Rajada de vento (asas da Rainha): anéis claros que se abrem e somem, e
## riscos de vento correndo para fora.
@rpc("authority", "call_local", "reliable")
func _show_gust(at: Vector3, radius: float) -> void:
	if root == null or not is_instance_valid(root):
		return
	var gust := Node3D.new()
	root.add_child(gust)
	gust.position = Vector3(at.x, 0.6, at.z)
	for i in 3:
		var ring := MeshInstance3D.new()
		var torus := TorusMesh.new()
		torus.inner_radius = 0.85
		torus.outer_radius = 1.0
		ring.mesh = torus
		var material := StandardMaterial3D.new()
		material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		material.albedo_color = Color(0.85, 0.95, 1.0, 0.55)
		ring.material_override = material
		ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		ring.position.y = 0.3 * i
		ring.scale = Vector3.ONE * 0.5
		gust.add_child(ring)
		var tween := ring.create_tween().set_parallel()
		tween.tween_property(ring, "scale", Vector3(radius, 1.0, radius), 0.45 + 0.12 * i).set_delay(0.08 * i)
		tween.tween_property(material, "albedo_color:a", 0.0, 0.45 + 0.12 * i).set_delay(0.08 * i)
	for i in 14:
		var streak := MeshInstance3D.new()
		var box := BoxMesh.new()
		box.size = Vector3(0.06, 0.06, 1.2)
		streak.mesh = box
		var material := StandardMaterial3D.new()
		material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		material.albedo_color = Color(0.9, 0.97, 1.0, 0.7)
		streak.material_override = material
		streak.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var angle := TAU * i / 14.0 + randf() * 0.2
		var dir := Vector3(sin(angle), 0, cos(angle))
		streak.rotation.y = angle
		streak.position = dir * 1.0 + Vector3.UP * randf_range(-0.3, 0.6)
		gust.add_child(streak)
		var tween := streak.create_tween().set_parallel()
		tween.tween_property(streak, "position", dir * radius + Vector3.UP * streak.position.y, 0.5)
		tween.tween_property(material, "albedo_color:a", 0.0, 0.5)
	get_tree().create_timer(1.0, false).timeout.connect(gust.queue_free)


@rpc("authority", "call_local", "reliable")
func _show_warning(at: Vector3, radius: float, time: float, style := "") -> void:
	if style == "rune":
		_rune_ring(at, radius, time)
		return
	var look: Array = WARNING_STYLES.get(style, WARNING_STYLES[""])
	var decal := pattern_decal(root, Vector3(at.x, 0.05 + ground_y, at.z), radius, String(look[0]), look[1], look[2], float(look[3]), time)
	if decal:
		# O padrão enche o círculo do centro até a borda (a borda já aparece): dá para ver quanto tempo falta.
		var mat := decal.material_override as ShaderMaterial
		mat.set_shader_parameter("fill", 0.15)
		decal.create_tween().tween_method(func(v: float) -> void: mat.set_shader_parameter("fill", v), 0.15, 1.0, maxf(time, 0.05))


## Selo Rúnico (golpe "rune_ring"): o anel de runas douradas (assets/models/fx/rune_ring.glb, "Dark Magician Ring", Anthony Yanez,
## CC BY 4.0) aparece no alto, desce girando até o chão enquanto o golpe não cai e some girando depressa; uma luz dourada o acompanha.
const RUNE_RING := "res://assets/models/fx/rune_ring.glb"


func _rune_ring(at: Vector3, radius: float, time: float) -> void:
	if root == null or not is_instance_valid(root) or not ResourceLoader.exists(RUNE_RING):
		pattern_decal(root, Vector3(at.x, 0.05 + ground_y, at.z), radius, "stripes", Color(0.95, 0.75, 0.25, 0.75), Vector2(0.4, 0.0), 0.5, time)
		return
	var holder := Node3D.new()
	root.add_child(holder)
	holder.position = Vector3(at.x, ground_y + 2.6, at.z)
	var ring := (load(RUNE_RING) as PackedScene).instantiate() as Node3D
	ring.scale = Vector3.ONE * radius * 2.0
	for mesh in ring.find_children("*", "MeshInstance3D", true, false):
		(mesh as MeshInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	holder.add_child(ring)
	var glow := OmniLight3D.new()
	glow.light_color = Color(1.0, 0.8, 0.35)
	glow.omni_range = radius * 1.8
	glow.light_energy = 1.2
	glow.position.y = 0.4
	holder.add_child(glow)
	# A área onde o selo cai, fraca no chão, para dar tempo de sair.
	pattern_decal(root, Vector3(at.x, 0.05 + ground_y, at.z), radius, "stripes", Color(0.95, 0.75, 0.25, 0.45), Vector2(0.3, 0.0), 0.5, time)
	var t := holder.create_tween().set_parallel()
	t.tween_property(holder, "position:y", ground_y + 0.08, maxf(time, 0.1)).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_QUAD)
	t.tween_property(ring, "rotation:y", TAU * 1.5, maxf(time, 0.1)).as_relative()
	var out := holder.create_tween()
	out.tween_interval(maxf(time, 0.1))
	out.tween_property(ring, "rotation:y", TAU, 0.35).as_relative()
	out.parallel().tween_property(ring, "scale", ring.scale * 1.25, 0.35)
	out.parallel().tween_property(glow, "light_energy", 0.0, 0.35)
	out.tween_callback(holder.queue_free)


## Marca no chão com um padrão deslizando (aviso, poça, faixa): quadrado deitado com o shader de padrão.
## `per_meter` = quantas vezes o padrão se repete por metro; `band` = faixa sem recorte redondo (o tamanho vem de `size`).
static func pattern_decal(parent: Node3D, at: Vector3, radius: float, pattern: String, color: Color, scroll: Vector2, per_meter: float, duration: float,
		band := false, size := Vector2.ZERO) -> MeshInstance3D:
	if parent == null or not is_instance_valid(parent):
		return null
	var decal := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.orientation = PlaneMesh.FACE_Y
	quad.size = size if band else Vector2.ONE * radius * 2.0
	decal.mesh = quad
	var mat := ShaderMaterial.new()
	mat.shader = PATTERN_SHADER
	mat.set_shader_parameter("pattern", load(PATTERNS % pattern))
	mat.set_shader_parameter("color", color)
	mat.set_shader_parameter("scroll", scroll)
	mat.set_shader_parameter("tiles", quad.size * per_meter)
	mat.set_shader_parameter("band", band)
	mat.set_shader_parameter("rim", 0.18 if band else clampf(0.25 / maxf(radius, 0.5), 0.04, 0.2))
	decal.material_override = mat
	decal.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(decal)
	decal.position = at
	if duration > 0.0:
		decal.get_tree().create_timer(duration, false).timeout.connect(decal.queue_free)
	return decal


## Mancha de lodo mucoso: contorno irregular (sempre dentro do raio do dano), centro
## brilhante, borda escura e translúcida e algumas bolhas. Cada mancha tem a sua
## forma (sorteada pela posição, igual em todos os PCs) e "respira" devagar.
func _slime(at: Vector3, radius: float, duration: float) -> Node3D:
	if root == null or not is_instance_valid(root):
		return null
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(Vector2i(roundi(at.x * 10.0), roundi(at.z * 10.0)))
	var phase := [rng.randf() * TAU, rng.randf() * TAU, rng.randf() * TAU]
	var amount := [rng.randf_range(0.08, 0.14), rng.randf_range(0.04, 0.09), rng.randf_range(0.02, 0.05)]
	var tool := SurfaceTool.new()
	tool.begin(Mesh.PRIMITIVE_TRIANGLES)
	tool.set_normal(Vector3.UP)
	# Aneis: centro, miolo e borda; o contorno ondula com o ângulo.
	var ring_scale := [0.0, 0.62, 1.0]
	var ring_color := [SLIME_CORE, SLIME_MID, SLIME_RIM]
	var rings: Array[PackedVector3Array] = []
	for r in 3:
		var ring := PackedVector3Array()
		for i in SLIME_SEGMENTS:
			var angle := TAU * i / SLIME_SEGMENTS
			var wobble := 1.0 - 0.12 + float(amount[0]) * sin(3.0 * angle + float(phase[0])) \
				+ float(amount[1]) * sin(5.0 * angle + float(phase[1])) + float(amount[2]) * sin(9.0 * angle + float(phase[2]))
			var reach := radius * float(ring_scale[r]) * clampf(wobble, 0.6, 1.0)
			ring.append(Vector3(cos(angle) * reach, 0, sin(angle) * reach))
		rings.append(ring)
	for i in SLIME_SEGMENTS:
		var j := (i + 1) % SLIME_SEGMENTS
		# Centro -> miolo.
		tool.set_color(ring_color[0])
		tool.add_vertex(Vector3.ZERO)
		tool.set_color(ring_color[1])
		tool.add_vertex(rings[1][j])
		tool.add_vertex(rings[1][i])
		# Miolo -> borda (dois triângulos por fatia).
		tool.set_color(ring_color[1])
		tool.add_vertex(rings[1][i])
		tool.add_vertex(rings[1][j])
		tool.set_color(ring_color[2])
		tool.add_vertex(rings[2][j])
		tool.set_color(ring_color[1])
		tool.add_vertex(rings[1][i])
		tool.set_color(ring_color[2])
		tool.add_vertex(rings[2][j])
		tool.add_vertex(rings[2][i])
	var holder := Node3D.new()
	var stain := MeshInstance3D.new()
	stain.mesh = tool.commit()
	var material := StandardMaterial3D.new()
	material.vertex_color_use_as_albedo = true
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.roughness = 0.12
	material.metallic_specular = 0.9
	material.emission_enabled = true
	material.emission = Color(0.18, 0.32, 0.05)
	material.emission_energy_multiplier = 0.5
	stain.material_override = material
	stain.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	holder.add_child(stain)
	# Bolhas brilhantes dentro da mancha.
	var bubble_material := StandardMaterial3D.new()
	bubble_material.albedo_color = SLIME_BUBBLE
	bubble_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	bubble_material.roughness = 0.05
	bubble_material.metallic_specular = 1.0
	bubble_material.emission_enabled = true
	bubble_material.emission = Color(0.3, 0.5, 0.1)
	bubble_material.emission_energy_multiplier = 0.4
	var bubble_count := clampi(roundi(radius * 2.2), 3, 9)
	for i in bubble_count:
		var bubble := MeshInstance3D.new()
		var sphere := SphereMesh.new()
		var size := radius * rng.randf_range(0.05, 0.13)
		sphere.radius = size
		sphere.height = size * 1.4
		sphere.radial_segments = 10
		sphere.rings = 6
		bubble.mesh = sphere
		bubble.material_override = bubble_material
		bubble.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var angle := rng.randf() * TAU
		var reach := radius * sqrt(rng.randf()) * 0.6
		bubble.position = Vector3(cos(angle) * reach, size * 0.3, sin(angle) * reach)
		holder.add_child(bubble)
	root.add_child(holder)
	holder.position = Vector3(at.x, 0.04 + ground_y, at.z)
	holder.rotation.y = rng.randf() * TAU
	# Respira devagar (a borda parece escorrer).
	var breathe := holder.create_tween().set_loops()
	breathe.tween_property(stain, "scale", Vector3(1.03, 1.0, 1.03), 1.6 + rng.randf()).set_trans(Tween.TRANS_SINE)
	breathe.tween_property(stain, "scale", Vector3(0.97, 1.0, 0.97), 1.6 + rng.randf()).set_trans(Tween.TRANS_SINE)
	if duration > 0.0:
		var fade := holder.create_tween()
		fade.tween_interval(maxf(duration - 0.6, 0.0))
		fade.tween_property(material, "albedo_color:a", 0.0, 0.6)
		fade.parallel().tween_property(bubble_material, "albedo_color:a", 0.0, 0.6)
		get_tree().create_timer(duration, false).timeout.connect(holder.queue_free)
	return holder


func _disc(at: Vector3, radius: float, color: Color, duration: float) -> MeshInstance3D:
	if root == null or not is_instance_valid(root):
		return null
	var disc := MeshInstance3D.new()
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius
	mesh.bottom_radius = radius
	mesh.height = 0.03
	mesh.radial_segments = 24
	disc.mesh = mesh
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.albedo_color = color
	disc.material_override = material
	disc.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	root.add_child(disc)
	disc.position = Vector3(at.x, 0.04 + ground_y, at.z)
	if duration > 0.0:
		get_tree().create_timer(duration, false).timeout.connect(disc.queue_free)
	return disc
