# Southern Mercenaries — GPL-3.0-or-later
class_name Hazards
extends Node
## Perigos no chão dos mapas (03-2-areas.md; 03-inimigos.md): poças de lodo
## tóxico (fixas da área, do cuspe do Sapo Ácido e do rastro das elites tóxicas)
## e as marcas de aviso dos golpes de monstro no chão. O servidor guarda as
## poças e tira vida de quem está dentro a cada `hazard_tick`; os visuais vão
## para a raiz da área (somem ao trocar de área).

const SLUDGE_COLOR := Color(0.35, 0.6, 0.15, 0.45)
const WARNING_COLOR := Color(0.95, 0.2, 0.1, 0.4)

## Onde ficam os discos (a raiz da área atual).
var root: Node3D
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
	for hazard: Dictionary in area.get("hazards", []):
		_disc(Vector3(hazard.position[0], 0, hazard.position[1]), float(hazard.radius), SLUDGE_COLOR, -1.0)


## Poça temporária (servidor), vista em todos os PCs.
func add(at: Vector3, radius: float, duration: float, dps: float, level: int) -> void:
	if not multiplayer.is_server():
		return
	_list.append({"position": Vector3(at.x, 0, at.z), "radius": radius, "time": duration, "dps": dps, "level": level})
	_show_sludge.rpc(at, radius, duration)


## Marca vermelha no chão: o golpe cai ali quando o tempo acabar.
func telegraph(at: Vector3, radius: float, time: float) -> void:
	if multiplayer.is_server():
		_show_warning.rpc(at, radius, time)


## Golpe no chão (cuspe, pisão): quem está dentro leva o dano; com "puddle_time", deixa poça.
func strike(at: Vector3, radius: float, damage: float, level: int, source: Node3D, extra: Dictionary) -> void:
	if not multiplayer.is_server():
		return
	var push := float(extra.get("push", 0.0))
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.alive and _inside(p.global_position, at, radius):
			p.take_damage(damage, level, source)
			if push > 0.0:
				# Vento: para longe do centro (a esquiva escapa do empurrão).
				var away := p.global_position - at
				away.y = 0.0
				if away.length() < 0.1:
					away = Vector3.BACK
				p.knock_back(away.normalized() * push, float(extra.get("push_time", 0.4)))
	if extra.get("wind", false):
		_show_gust.rpc(at, radius)
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
		if not p.alive:
			continue
		for hazard in _list:
			if _inside(p.global_position, hazard.position, hazard.radius):
				p.take_damage(hazard.dps * tick, hazard.level, null)
				break


static func _inside(point: Vector3, center: Vector3, radius: float) -> bool:
	return Vector2(point.x - center.x, point.z - center.z).length() <= radius


@rpc("authority", "call_local", "reliable")
func _show_sludge(at: Vector3, radius: float, duration: float) -> void:
	_disc(at, radius, SLUDGE_COLOR, duration)


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
func _show_warning(at: Vector3, radius: float, time: float) -> void:
	var disc := _disc(at, radius, WARNING_COLOR, time)
	if disc:
		# Cresce do centro até o tamanho do golpe: dá para ver quanto tempo falta.
		disc.scale = Vector3(0.2, 1, 0.2)
		disc.create_tween().tween_property(disc, "scale", Vector3.ONE, time)


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
	disc.position = Vector3(at.x, 0.04, at.z)
	if duration > 0.0:
		get_tree().create_timer(duration, false).timeout.connect(disc.queue_free)
	return disc
