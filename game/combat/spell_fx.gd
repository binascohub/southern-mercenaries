# Southern Mercenaries — GPL-3.0-or-later
class_name SpellFx
extends RefCounted
## Efeitos próprios de cada magia (só visual, em todos os PCs). Cada habilidade tem o seu em data/spell_fx.json, com um "motivo" por momento:
##   "cast" (no herói ao lançar), "proj" (o projétil e o rastro), "beam" (feixe, investida, corte), "disc" (área no chão), "warn" (aviso antes do impacto),
##   "hit" (o impacto) e as cores ("colors": [principal, clara]). Sem entrada para o momento, valem os efeitos genéricos por elemento (fx.gd).
## Os motivos são montados com poucas peças (clarão, anel, coluna, espinhos, rachaduras, raio, cúpula, símbolo no chão, partículas com formas desenhadas aqui:
## estrela, cruz, floco, gota, crescente, raio de luz, hexágono, folha). Poucas partículas por efeito (requisito de vídeo integrado).

## Motivos que existem (o teste confere data/spell_fx.json contra estas listas).
const PROJECTILES := ["comet", "dart", "spear", "arrow", "orb", "crystal", "crescent", "rock", "boulder", "pierce", "tiny_arrow"]
const GROUND := ["fire_burst", "meteor", "flame_ring", "campfire", "fire_rain", "frost_nova", "blizzard", "hail", "stone_rain", "storm_volley", "rain_heal", "spring", "mist", "whale_song", "wave_sweep",
	"tornado", "storm", "quake", "stomp", "dome", "aura_up", "aura_wind", "banner", "teleport", "vanish", "smoke", "shout", "trap", "seal", "summon", "danger", "arc_sweep", "flock", "wing_storm", "splash", "iron"]
const BEAMS := ["lightning", "chain", "sky_bolt", "fire_line", "water_jet", "earth_line", "spear", "slash", "charge", "mark", "heal", "blink", "bite", "dive"]

static var _tex_cache := {}
static var _mat_cache := {}


## Toca o efeito `kind` ("cast", "proj" não passa por aqui, "beam", "disc", "warn", "hit") da habilidade; false se ela não tem (quem chamou usa o genérico).
static func play(parent: Node, kind: String, skill_id: String, a: Vector3, b: Vector3, size: float, color: Color, duration: float) -> bool:
	var profile: Dictionary = GameData.spell_fx.get(skill_id, {})
	var spec: Dictionary = profile.get(kind, {})
	if spec.is_empty():
		return false
	var c := _colors(profile, color)
	match kind:
		"beam":
			_beam(parent, spec, a, b, size, c, duration)
		"cast":
			_cast(parent, spec, a, c)
		_:
			_ground(parent, spec, a, b, size, c, duration)
	return true


## Projétil (núcleo e rastro) da habilidade: no Projectile, na hora em que ele nasce.
static func projectile(node: Node3D, skill_id: String, direction: Vector3, radius: float, color: Color) -> bool:
	var profile: Dictionary = GameData.spell_fx.get(skill_id, {})
	var spec: Dictionary = profile.get("proj", {})
	if spec.is_empty():
		return false
	var c := _colors(profile, color)
	var yaw := atan2(direction.x, direction.z)
	var r := radius
	match String(spec.m):
		"comet":
			_core_sphere(node, c[1], r * 0.8)
			_halo(node, c[0], r * 5.5)
			_emit(node, {"amount": 36, "life": 0.55, "size": r * 2.0, "tex": "soft", "c0": c[1], "c1": c[0], "vmin": 0.1, "vmax": 0.7, "spread": 180.0, "grav": Vector3(0, 2.5, 0), "shape": "sphere", "ext": r * 0.5, "local": false})
			_emit(node, {"amount": 12, "life": 0.7, "size": r * 0.7, "tex": "star4", "c0": Color.WHITE, "c1": c[0], "vmin": 0.5, "vmax": 1.6, "spread": 180.0, "grav": Vector3(0, -1.5, 0), "local": false})
		"dart":
			_core_sphere(node, c[1], r * 0.6)
			_halo(node, c[0], r * 3.6)
			_emit(node, {"amount": 18, "life": 0.28, "size": r * 1.1, "tex": "spark", "c0": c[1], "c1": c[0], "vmin": 0.0, "vmax": 0.5, "spread": 180.0, "shape": "sphere", "ext": r * 0.3, "local": false})
		"spear":
			var core := _core_box(node, c[1], Vector3(r * 0.5, r * 0.5, r * 5.0), yaw)
			core.position.z = 0.0
			_halo(node, c[0], r * 4.0)
			_emit(node, {"amount": 26, "life": 0.4, "size": r * 1.6, "tex": "soft", "c0": c[1], "c1": c[0], "vmin": 0.1, "vmax": 0.6, "spread": 120.0, "grav": Vector3(0, 1.5, 0), "shape": "sphere", "ext": r * 0.4, "local": false})
			_emit(node, {"amount": 10, "life": 0.5, "size": r * 0.8, "tex": "star4", "c0": Color.WHITE, "c1": c[0], "vmin": 0.5, "vmax": 1.5, "spread": 180.0, "local": false})
		"arrow":
			_core_box(node, c[1], Vector3(r * 0.35, r * 0.35, r * 4.5), yaw)
			var tip := MeshInstance3D.new()
			var cone := CylinderMesh.new()
			cone.top_radius = 0.0
			cone.bottom_radius = r * 0.8
			cone.height = r * 2.0
			tip.mesh = cone
			tip.material_override = _lit_mat(c[0], true)
			tip.basis = Basis(Vector3.UP, yaw) * Basis(Vector3.RIGHT, PI / 2.0)
			tip.position = Vector3(sin(yaw), 0, cos(yaw)) * r * 2.4
			node.add_child(tip)
			_halo(node, c[0], r * 3.0)
			_emit(node, {"amount": 14, "life": 0.3, "size": r * 0.9, "tex": "spark", "c0": Color.WHITE, "c1": c[0], "vmin": 0.0, "vmax": 0.5, "spread": 180.0, "local": false})
		"orb":
			_core_sphere(node, c[1], r * 0.75)
			_halo(node, c[0], r * 4.5)
			_emit(node, {"amount": 20, "life": 0.5, "size": r * 1.0, "tex": "drop", "c0": c[1], "c1": c[0], "vmin": 0.2, "vmax": 1.0, "spread": 180.0, "grav": Vector3(0, -7.0, 0), "local": false, "shape": "sphere", "ext": r * 0.4})
		"crystal":
			var shard := _core_box(node, c[1], Vector3(r * 0.9, r * 0.9, r * 4.2), yaw)
			shard.rotation.z = PI / 4.0
			_halo(node, c[0], r * 4.0)
			_emit(node, {"amount": 22, "life": 0.6, "size": r * 1.3, "tex": "snow", "c0": Color.WHITE, "c1": c[0], "vmin": 0.2, "vmax": 0.9, "spread": 180.0, "grav": Vector3(0, -1.5, 0), "local": false, "shape": "sphere", "ext": r * 0.4})
			_emit(node, {"amount": 10, "life": 0.5, "size": r * 1.0, "mesh": "shard", "c0": c[1], "c1": c[0], "vmin": 0.3, "vmax": 1.2, "spread": 180.0, "grav": Vector3(0, -6.0, 0), "local": false, "add": false})
		"crescent":
			var moon := _flat_quad(node, "crescent", c[1], r * 7.0, 0.0)
			var spin := moon.create_tween().set_loops()
			spin.tween_property(moon, "rotation:y", TAU, 0.35).as_relative()
			_halo(node, c[0], r * 3.5)
			_emit(node, {"amount": 26, "life": 0.45, "size": r * 1.2, "tex": "soft", "c0": Color(1, 1, 1, 0.8), "c1": c[0], "vmin": 0.2, "vmax": 0.8, "spread": 180.0, "tang": 6.0, "local": false, "shape": "sphere", "ext": r * 0.8})
		"rock":
			var rock := _core_box(node, Color(0.52, 0.42, 0.3), Vector3(r * 1.5, r * 1.3, r * 1.5), 0.0, true)
			var roll := rock.create_tween().set_loops()
			roll.tween_property(rock, "rotation", Vector3(TAU, TAU * 0.7, 0.0), 0.5).as_relative()
			_emit(node, {"amount": 16, "life": 0.5, "size": r * 1.6, "tex": "soft", "c0": Color(0.6, 0.5, 0.36, 0.6), "c1": Color(0.4, 0.34, 0.26), "vmin": 0.1, "vmax": 0.6, "spread": 180.0, "local": false, "add": false})
			_emit(node, {"amount": 8, "life": 0.5, "size": r * 1.0, "mesh": "cube", "c0": Color(0.5, 0.4, 0.28), "c1": Color(0.4, 0.34, 0.24), "vmin": 0.3, "vmax": 1.2, "spread": 180.0, "grav": Vector3(0, -9.0, 0), "local": false, "add": false})
		"boulder":
			var big := _core_box(node, Color(0.46, 0.38, 0.28), Vector3(r * 1.9, r * 1.6, r * 1.9), 0.0, true)
			var second := _core_box(big, Color(0.4, 0.34, 0.25), Vector3(r * 1.3, r * 1.3, r * 1.3), 0.0, true)
			second.rotation = Vector3(0.6, 0.8, 0.3)
			var roll_b := big.create_tween().set_loops()
			roll_b.tween_property(big, "rotation", Vector3(TAU, 0.0, TAU * 0.5), 0.9).as_relative()
			_emit(node, {"amount": 22, "life": 0.7, "size": r * 2.2, "tex": "soft", "c0": Color(0.62, 0.52, 0.38, 0.55), "c1": Color(0.4, 0.34, 0.26), "vmin": 0.1, "vmax": 0.7, "spread": 180.0, "local": false, "add": false})
			_emit(node, {"amount": 12, "life": 0.6, "size": r * 1.0, "mesh": "cube", "c0": Color(0.5, 0.4, 0.28), "c1": Color(0.4, 0.34, 0.24), "vmin": 0.6, "vmax": 2.0, "spread": 180.0, "grav": Vector3(0, -10.0, 0), "local": false, "add": false})
		"pierce":
			_core_box(node, c[1], Vector3(r * 0.4, r * 0.4, r * 7.0), yaw)
			_halo(node, c[0], r * 3.2)
			_emit(node, {"amount": 10, "life": 0.35, "size": r * 3.0, "tex": "ring", "c0": c[1], "c1": c[0], "vmin": 0.0, "vmax": 0.1, "spread": 0.0, "local": false})
			_emit(node, {"amount": 16, "life": 0.3, "size": r * 0.9, "tex": "spark", "c0": Color.WHITE, "c1": c[0], "vmin": 0.1, "vmax": 0.7, "spread": 180.0, "local": false})
		"tiny_arrow":
			_core_box(node, c[1], Vector3(r * 0.3, r * 0.3, r * 3.5), yaw)
			_halo(node, c[0], r * 2.4)
			_emit(node, {"amount": 8, "life": 0.25, "size": r * 0.8, "tex": "spark", "c0": Color.WHITE, "c1": c[0], "vmin": 0.0, "vmax": 0.4, "spread": 180.0, "local": false})
		_:
			return false
	return true


# --- Fala de cada momento -------------------------------------------------------------

static func _colors(profile: Dictionary, color: Color) -> Array:
	var list: Array = profile.get("colors", [])
	if list.size() >= 2:
		return [Color(String(list[0])), Color(String(list[1]))]
	return [color, color.lightened(0.5)]


## Clarão no herói ao lançar: símbolo, anel curto e faíscas.
static func _cast(parent: Node, spec: Dictionary, at: Vector3, c: Array) -> void:
	var root := _root(parent, Vector3(at.x, 0.0, at.z), 0.5)
	_glyph(root, String(spec.get("g", "star4")), c[1], 1.7, 0.45, 0.07, 2.5)
	_ring(root, c[0], 1.0, 0.3, 0.1, 0.12)
	_emit(root, {"amount": 12, "life": 0.5, "size": 0.2, "tex": String(spec.get("t", "spark")), "c0": c[1], "c1": c[0], "vmin": 1.5, "vmax": 3.5, "spread": 40.0, "dir": Vector3.UP,
		"grav": Vector3(0, -2.0, 0), "shape": "disc", "ext": 0.5, "once": true, "burst": 0.9, "pos": Vector3(0, 0.1, 0)})


static func _ground(parent: Node, spec: Dictionary, at: Vector3, b: Vector3, s: float, c: Array, life: float) -> void:
	var root := _root(parent, Vector3(at.x, 0.0, at.z), maxf(life, 0.5))
	var lasting := life > 0.8
	var k := float(spec.get("k", 1.0))
	match String(spec.m):
		"fire_burst": _m_fire_burst(root, s * k, c)
		"meteor": _m_meteor(root, s * k, c)
		"flame_ring": _m_flame_ring(root, s * k, c, life, lasting)
		"campfire": _m_campfire(root, s * k, c, life)
		"fire_rain": _m_falling(root, s * k, c, life, {"mesh": "shard", "c0": c[1], "c1": c[0], "grav": -16.0, "ground": "fire"})
		"frost_nova": _m_frost_nova(root, s * k, c)
		"blizzard": _m_blizzard(root, s * k, c, life)
		"hail": _m_falling(root, s * k, c, life, {"mesh": "shard", "c0": Color.WHITE, "c1": c[0], "grav": -18.0, "ground": "ice"})
		"stone_rain": _m_falling(root, s * k, c, life, {"mesh": "cube", "c0": Color(0.55, 0.45, 0.3), "c1": Color(0.4, 0.34, 0.25), "grav": -14.0, "ground": "dust", "add": false})
		"storm_volley": _m_falling(root, s * k, c, life, {"mesh": "shard", "c0": c[1], "c1": c[0], "grav": -22.0, "ground": "spark", "bolts": true})
		"rain_heal": _m_rain_heal(root, s * k, c, life)
		"spring": _m_spring(root, s * k, c, life)
		"mist": _m_mist(root, s * k, c, life)
		"whale_song": _m_whale_song(root, s * k, c, life)
		"wave_sweep": _m_wave_sweep(root, s * k, c, b)
		"tornado": _m_tornado(root, s * k, c, life, b)
		"storm": _m_storm(root, s * k, c, life)
		"quake": _m_quake(root, s * k, c)
		"stomp": _m_stomp(root, s * k, c)
		"dome": _m_dome(root, s * k, c, life, String(spec.get("g", "hex")), String(spec.get("o", "")))
		"aura_up": _m_aura_up(root, s * k, c, life, String(spec.get("g", "star4")), String(spec.get("t", "spark")))
		"aura_wind": _m_aura_wind(root, s * k, c, life, String(spec.get("t", "soft")))
		"banner": _m_banner(root, s * k, c, life, String(spec.get("g", "star4")))
		"teleport": _m_teleport(root, s * k, c, String(spec.get("t", "spark")))
		"vanish": _m_vanish(root, s * k, c)
		"smoke": _m_smoke(root, s * k, c, life)
		"shout": _m_shout(root, s * k, c)
		"trap": _m_trap(root, s * k, c, life)
		"seal": _m_seal(root, s * k, c, life, String(spec.get("g", "rune")), String(spec.get("t", "spark")))
		"summon": _m_summon(root, s * k, c, String(spec.get("g", "rune")), String(spec.get("t", "leaf")))
		"danger": _m_danger(root, s * k, c, life)
		"arc_sweep": _m_arc_sweep(root, s * k, c, b)
		"flock": _m_flock(root, s * k, c, b)
		"wing_storm": _m_wing_storm(root, s * k, c, life)
		"splash": _m_splash(root, s * k, c)
		"iron": _m_iron(root, s * k, c)
		_: _flash(root, c[1], s * 2.0, 0.3, 0.4)


static func _beam(parent: Node, spec: Dictionary, a: Vector3, b: Vector3, w: float, c: Array, life: float) -> void:
	if a.distance_to(b) < 0.02:
		return
	match String(spec.m):
		"lightning": _bolt(parent, a, b, c[0], maxf(w, 0.18), maxf(life, 0.2), float(spec.get("jag", 0.5)), 9)
		"chain": _m_chain(parent, a, b, c, maxf(life, 0.25))
		"sky_bolt": _m_sky_bolt(parent, b, c, maxf(life, 0.25))
		"fire_line": _m_fire_line(parent, a, b, w, c, life)
		"water_jet": _m_water_jet(parent, a, b, w, c, maxf(life, 0.3))
		"earth_line": _m_earth_line(parent, a, b, w, c, maxf(life, 0.5))
		"spear": _m_spear_streak(parent, a, b, w, c, maxf(life, 0.25), String(spec.get("t", "spark")), bool(spec.get("zig", false)))
		"slash": _m_slash(parent, a, b, c, maxf(life, 0.4), String(spec.get("t", "spark")))
		"charge": _m_charge_dust(parent, a, b, w, c, maxf(life, 0.35), String(spec.get("t", "soft")))
		"mark": _m_mark_line(parent, a, b, c, maxf(life, 0.4))
		"heal": _m_heal_ribbon(parent, a, b, c, maxf(life, 0.5))
		"blink": _m_blink_cut(parent, a, b, c, maxf(life, 0.45), String(spec.get("t", "spark")))
		"bite": _m_bite(parent, a, b, c, maxf(life, 0.3))
		"dive": _m_dive(parent, a, b, c, maxf(life, 0.3))
		_: pass


# --- Motivos do chão ---------------------------------------------------------------------

static func _m_fire_burst(r: Node3D, s: float, c: Array) -> void:
	_flash(r, c[1], s * 2.4, 0.3, 0.5)
	_ring(r, c[0], s, 0.35)
	_ring(r, c[1], s * 0.6, 0.25)
	_emit(r, {"amount": 34, "life": 0.7, "size": s * 0.4, "tex": "soft", "c0": c[1], "c1": c[0], "vmin": 1.5, "vmax": 4.5, "spread": 180.0, "grav": Vector3(0, 3, 0), "shape": "sphere", "ext": s * 0.3, "once": true, "burst": 0.95, "pos": Vector3(0, 0.4, 0)})
	_emit(r, {"amount": 14, "life": 0.9, "size": 0.22, "tex": "star4", "c0": Color.WHITE, "c1": c[0], "vmin": 3.0, "vmax": 7.0, "spread": 70.0, "dir": Vector3.UP, "grav": Vector3(0, -6, 0), "once": true, "burst": 1.0, "pos": Vector3(0, 0.3, 0)})
	_emit(r, {"amount": 10, "life": 1.1, "size": s * 0.5, "tex": "soft", "c0": Color(0.2, 0.18, 0.17, 0.55), "c1": Color(0.1, 0.1, 0.1), "vmin": 0.6, "vmax": 1.6, "spread": 60.0, "dir": Vector3.UP, "grav": Vector3(0, 1.0, 0), "once": true, "burst": 0.9, "add": false, "pos": Vector3(0, 0.5, 0)})


static func _m_meteor(r: Node3D, s: float, c: Array) -> void:
	_flash(r, Color.WHITE, s * 3.0, 0.35, 0.6)
	_ring(r, c[1], s, 0.45)
	_ring(r, c[0], s * 0.7, 0.35)
	_cracks(r, c[0], 9, s * 0.95, 1.2)
	_column(r, c[0], s * 0.35, 6.0, 0.5)
	_emit(r, {"amount": 22, "life": 1.0, "size": 0.35, "mesh": "cube", "c0": Color(0.25, 0.18, 0.14), "c1": c[0], "vmin": 4.0, "vmax": 9.0, "spread": 55.0, "dir": Vector3.UP, "grav": Vector3(0, -14, 0), "once": true, "burst": 1.0, "add": false, "pos": Vector3(0, 0.3, 0)})
	_emit(r, {"amount": 40, "life": 0.9, "size": s * 0.35, "tex": "soft", "c0": c[1], "c1": c[0], "vmin": 2.0, "vmax": 6.0, "spread": 180.0, "grav": Vector3(0, 3, 0), "shape": "sphere", "ext": s * 0.4, "once": true, "burst": 0.95, "pos": Vector3(0, 0.5, 0)})


static func _m_flame_ring(r: Node3D, s: float, c: Array, life: float, lasting: bool) -> void:
	_glyph(r, "soft", c[0], s * 2.1, life, 0.04, 0.0, 0.3)
	_ring(r, c[0], s, 0.5)
	var p := _emit(r, {"amount": clampi(roundi(s * 10.0), 14, 44), "life": 0.8, "size": 0.7, "tex": "soft", "c0": c[1], "c1": c[0], "vmin": 0.4, "vmax": 1.4, "spread": 25.0, "dir": Vector3.UP,
		"grav": Vector3(0, 2.2, 0), "shape": "ring", "ext": s * 0.92, "inner": s * 0.55, "once": not lasting, "burst": 0.9 if not lasting else 0.0, "pos": Vector3(0, 0.1, 0)})
	_stop_later(r, p, life)


static func _m_campfire(r: Node3D, s: float, c: Array, life: float) -> void:
	_glyph(r, "soft", c[0], s * 2.0, life, 0.04, 0.0, 0.25)
	_glyph(r, "rune", c[1], s * 1.6, life, 0.05, 0.4, 0.5)
	var p := _emit(r, {"amount": 26, "life": 0.9, "size": 1.0, "tex": "soft", "c0": c[1], "c1": c[0], "vmin": 0.6, "vmax": 1.8, "spread": 18.0, "dir": Vector3.UP, "grav": Vector3(0, 2.0, 0), "shape": "disc", "ext": 0.5})
	var e := _emit(r, {"amount": 14, "life": 1.4, "size": 0.18, "tex": "star4", "c0": Color.WHITE, "c1": c[0], "vmin": 1.0, "vmax": 3.0, "spread": 40.0, "dir": Vector3.UP, "grav": Vector3(0, 0.6, 0), "shape": "disc", "ext": 0.7})
	var ring := _emit(r, {"amount": 20, "life": 1.0, "size": 0.4, "tex": "soft", "c0": c[1], "c1": c[0], "vmin": 0.2, "vmax": 0.6, "spread": 20.0, "dir": Vector3.UP, "grav": Vector3(0, 1.4, 0), "shape": "ring", "ext": s * 0.8, "inner": s * 0.7})
	_stop_later(r, p, life)
	_stop_later(r, e, life)
	_stop_later(r, ring, life)


## Chuva de coisas caindo sobre a área (flechas em chamas, granizo, pedras, flechas com raio): `o` = {mesh, c0, c1, grav, ground, add, bolts}.
static func _m_falling(r: Node3D, s: float, c: Array, life: float, o: Dictionary) -> void:
	_glyph(r, "soft", c[0], s * 2.1, life, 0.04, 0.0, 0.22)
	_ring(r, c[0], s, 0.4)
	var p := _emit(r, {"amount": clampi(roundi(s * 8.0), 16, 44), "life": 0.5, "size": 0.5, "mesh": o.mesh, "c0": o.c0, "c1": o.c1, "vmin": 0.0, "vmax": 2.0, "spread": 4.0, "dir": Vector3.DOWN,
		"grav": Vector3(0, float(o.grav), 0), "shape": "box", "ext": Vector3(s * 0.9, 0.2, s * 0.9), "pos": Vector3(0, 7.0, 0), "add": bool(o.get("add", true)), "local": true})
	var kind := String(o.ground)
	var splash := _emit(r, {"amount": 22, "life": 0.45, "size": 0.45, "tex": "star4" if kind in ["spark", "fire"] else "soft", "c0": c[1] if kind != "dust" else Color(0.6, 0.5, 0.36, 0.7), "c1": c[0],
		"vmin": 1.0, "vmax": 2.8, "spread": 60.0, "dir": Vector3.UP, "grav": Vector3(0, -6, 0), "shape": "disc", "ext": s * 0.9, "pos": Vector3(0, 0.1, 0), "add": kind != "dust"})
	_stop_later(r, p, life)
	_stop_later(r, splash, life)
	if o.get("bolts", false):
		for i in 4:
			var spot := Vector3(randf_range(-s, s) * 0.7, 0.0, randf_range(-s, s) * 0.7)
			var delay := life * (0.1 + 0.22 * i)
			r.get_tree().create_timer(delay, false).timeout.connect(_late_bolt.bind(r, spot, c))


static func _late_bolt(r: Node3D, spot: Vector3, c: Array) -> void:
	if is_instance_valid(r) and r.is_inside_tree():
		_m_sky_bolt(r, r.global_position + spot, c, 0.3)


static func _m_frost_nova(r: Node3D, s: float, c: Array) -> void:
	_flash(r, Color.WHITE, s * 2.2, 0.3, 0.4)
	_ring(r, c[1], s, 0.4)
	_ring(r, c[0], s * 0.5, 0.3)
	_glyph(r, "snow", c[1], s * 1.8, 0.7, 0.06, 1.5, 0.8)
	_spikes(r, c[1], 12, 0.35, s * 0.45, 0.8, false, s * 0.8, true)
	_emit(r, {"amount": 26, "life": 0.9, "size": s * 0.18, "tex": "snow", "c0": Color.WHITE, "c1": c[0], "vmin": 2.0, "vmax": 5.0, "spread": 60.0, "dir": Vector3.UP, "grav": Vector3(0, -2.0, 0), "shape": "disc", "ext": s * 0.3, "once": true, "burst": 0.95, "pos": Vector3(0, 0.3, 0)})


static func _m_blizzard(r: Node3D, s: float, c: Array, life: float) -> void:
	_glyph(r, "soft", c[1], s * 2.2, life, 0.04, 0.0, 0.3)
	_glyph(r, "snow", c[1], s * 1.7, life, 0.05, 0.5, 0.35)
	var p := _emit(r, {"amount": 40, "life": 1.3, "size": 0.35, "tex": "snow", "c0": Color.WHITE, "c1": c[0], "vmin": 0.4, "vmax": 1.4, "spread": 180.0, "tang": 7.0, "grav": Vector3(0, -1.2, 0), "shape": "box",
		"ext": Vector3(s * 0.9, 0.3, s * 0.9), "pos": Vector3(0, 3.0, 0)})
	var fog := _emit(r, {"amount": 12, "life": 1.6, "size": s * 0.9, "tex": "soft", "c0": Color(0.85, 0.95, 1.0, 0.25), "c1": c[0], "vmin": 0.1, "vmax": 0.4, "spread": 180.0, "shape": "disc", "ext": s * 0.7, "pos": Vector3(0, 0.6, 0)})
	_stop_later(r, p, life)
	_stop_later(r, fog, life)


static func _m_rain_heal(r: Node3D, s: float, c: Array, life: float) -> void:
	_glyph(r, "soft", c[0], s * 2.1, life, 0.04, 0.0, 0.25)
	_ring(r, c[1], s, 0.5)
	var rain := _emit(r, {"amount": 36, "life": 0.7, "size": 0.35, "tex": "drop", "c0": c[1], "c1": c[0], "vmin": 0.0, "vmax": 1.0, "spread": 3.0, "dir": Vector3.DOWN, "grav": Vector3(0, -12, 0), "shape": "box",
		"ext": Vector3(s * 0.8, 0.2, s * 0.8), "pos": Vector3(0, 5.0, 0)})
	var plus := _emit(r, {"amount": 8, "life": 1.4, "size": 0.45, "tex": "plus", "c0": Color(0.7, 1.0, 0.75, 0.95), "c1": Color(0.3, 0.9, 0.5), "vmin": 0.4, "vmax": 0.9, "spread": 10.0, "dir": Vector3.UP, "shape": "disc", "ext": s * 0.7, "pos": Vector3(0, 0.2, 0)})
	_stop_later(r, rain, life)
	_stop_later(r, plus, life)


static func _m_spring(r: Node3D, s: float, c: Array, life: float) -> void:
	_glyph(r, "soft", c[0], s * 2.0, life, 0.04, 0.0, 0.25)
	for i in 3:
		r.get_tree().create_timer(0.35 * i, false).timeout.connect(_late_ring.bind(r, c[1], s * (0.5 + 0.2 * i)))
	var jet := _emit(r, {"amount": 30, "life": 0.9, "size": 0.3, "tex": "drop", "c0": c[1], "c1": c[0], "vmin": 4.0, "vmax": 7.0, "spread": 22.0, "dir": Vector3.UP, "grav": Vector3(0, -10, 0), "shape": "disc", "ext": 0.25})
	var bub := _emit(r, {"amount": 10, "life": 1.1, "size": 0.3, "tex": "ring", "c0": Color.WHITE, "c1": c[0], "vmin": 0.4, "vmax": 1.0, "spread": 40.0, "dir": Vector3.UP, "shape": "disc", "ext": s * 0.5})
	_stop_later(r, jet, life)
	_stop_later(r, bub, life)


static func _late_ring(r: Node3D, color: Color, radius: float) -> void:
	if is_instance_valid(r) and r.is_inside_tree():
		_ring(r, color, radius, 0.5)


static func _m_mist(r: Node3D, s: float, c: Array, life: float) -> void:
	_glyph(r, "soft", Color(0.8, 0.92, 1.0), s * 2.2, life, 0.05, 0.0, 0.3)
	var fog := _emit(r, {"amount": 22, "life": 1.8, "size": s * 0.8, "tex": "soft", "c0": Color(0.9, 0.97, 1.0, 0.28), "c1": c[0], "vmin": 0.1, "vmax": 0.5, "spread": 180.0, "tang": 2.0, "shape": "ring", "ext": s * 0.7, "inner": 0.1, "pos": Vector3(0, 0.5, 0), "add": false})
	var dots := _emit(r, {"amount": 14, "life": 1.2, "size": 0.2, "tex": "drop", "c0": c[1], "c1": c[0], "vmin": 0.2, "vmax": 0.6, "spread": 180.0, "grav": Vector3(0, 0.3, 0), "shape": "ring", "ext": s * 0.8, "inner": 0.1, "pos": Vector3(0, 0.6, 0)})
	_ring(r, c[1], s, 0.6)
	_stop_later(r, fog, life)
	_stop_later(r, dots, life)


static func _m_whale_song(r: Node3D, s: float, c: Array, life: float) -> void:
	for i in 4:
		r.get_tree().create_timer(0.12 * i, false).timeout.connect(_late_ring.bind(r, c[1] if i % 2 == 0 else c[0], s * (1.0 - 0.14 * i)))
	_flash(r, c[1], s * 2.0, 0.4, 0.5)
	_glyph(r, "crescent", c[1], s * 1.6, 0.8, 0.06, 1.2, 0.8)
	_emit(r, {"amount": 30, "life": 1.0, "size": 0.35, "tex": "ring", "c0": Color.WHITE, "c1": c[0], "vmin": 1.5, "vmax": 4.0, "spread": 80.0, "dir": Vector3.UP, "grav": Vector3(0, -2.0, 0), "shape": "disc", "ext": s * 0.7, "once": true, "burst": 0.9, "pos": Vector3(0, 0.2, 0)})
	_emit(r, {"amount": 18, "life": 0.9, "size": 0.4, "tex": "drop", "c0": c[1], "c1": c[0], "vmin": 3.0, "vmax": 6.5, "spread": 25.0, "dir": Vector3.UP, "grav": Vector3(0, -11, 0), "shape": "disc", "ext": s * 0.5, "once": true, "burst": 0.95})


static func _m_wave_sweep(r: Node3D, s: float, c: Array, dir: Vector3) -> void:
	var d := Vector3(dir.x, 0, dir.z)
	d = d.normalized() if d.length() > 0.01 else Vector3.FORWARD
	var side := Vector3(-d.z, 0, d.x)
	r.global_position -= d * s
	_emit(r, {"amount": 46, "life": 0.9, "size": 0.55, "tex": "drop", "c0": Color.WHITE, "c1": c[0], "vmin": 8.0, "vmax": 11.0, "spread": 20.0, "dir": d + Vector3.UP * 0.15, "grav": Vector3(0, -6.0, 0), "shape": "box",
		"ext": side.abs() * s * 0.8 + Vector3(0.2, 0.1, 0.2), "once": true, "burst": 0.9, "pos": Vector3(0, 0.3, 0)})
	_emit(r, {"amount": 24, "life": 0.8, "size": s * 0.55, "tex": "soft", "c0": Color(c[1], 0.7), "c1": c[0], "vmin": 6.0, "vmax": 9.0, "spread": 15.0, "dir": d, "shape": "box", "ext": side.abs() * s * 0.8 + Vector3(0.2, 0.1, 0.2),
		"once": true, "burst": 0.9, "pos": Vector3(0, 0.4, 0)})
	_ring(r, c[0], s * 0.8, 0.4)


static func _m_tornado(r: Node3D, s: float, c: Array, life: float, travel: Vector3) -> void:
	var tw := r.create_tween()
	tw.tween_property(r, "global_position", r.global_position + Vector3(travel.x, 0, travel.z), maxf(life, 0.3))
	_column(r, c[1], s * 0.9, 4.5, life, 0.07)
	var fun := _emit(r, {"amount": 46, "life": 0.9, "size": 0.45, "tex": "soft", "c0": Color(1, 1, 1, 0.8), "c1": c[0], "vmin": 0.6, "vmax": 1.4, "spread": 15.0, "dir": Vector3.UP, "tang": 14.0, "shape": "ring", "ext": s * 0.8, "inner": s * 0.4,
		"grav": Vector3(0, 3.0, 0), "local": false})
	var debris := _emit(r, {"amount": 12, "life": 1.0, "size": 0.35, "tex": "leaf", "c0": Color(0.7, 0.85, 0.5), "c1": Color(0.5, 0.6, 0.3), "vmin": 1.0, "vmax": 2.0, "spread": 20.0, "dir": Vector3.UP, "tang": 16.0, "shape": "ring", "ext": s, "inner": s * 0.5, "local": false})
	_glyph(r, "soft", c[0], s * 2.0, life, 0.04, 0.0, 0.2)
	_stop_later(r, fun, life)
	_stop_later(r, debris, life)


static func _m_storm(r: Node3D, s: float, c: Array, life: float) -> void:
	_glyph(r, "soft", Color(0.35, 0.38, 0.5), s * 2.2, life, 0.04, 0.0, 0.35)
	var clouds := _emit(r, {"amount": 22, "life": 2.0, "size": s * 0.7, "tex": "soft", "c0": Color(0.22, 0.24, 0.32, 0.75), "c1": Color(0.15, 0.16, 0.22), "vmin": 0.1, "vmax": 0.5, "spread": 180.0, "tang": 1.5,
		"shape": "disc", "ext": s * 0.8, "pos": Vector3(0, 5.0, 0), "add": false})
	var rain := _emit(r, {"amount": 34, "life": 0.5, "size": 0.3, "mesh": "shard", "c0": Color(0.8, 0.9, 1.0, 0.8), "c1": c[0], "vmin": 0.0, "vmax": 1.0, "spread": 3.0, "dir": Vector3.DOWN, "grav": Vector3(0, -22, 0),
		"shape": "disc", "ext": s * 0.85, "pos": Vector3(0, 4.5, 0)})
	_stop_later(r, clouds, life)
	_stop_later(r, rain, life)
	var n := clampi(roundi(life * 1.4), 3, 9)
	for i in n:
		var spot := Vector3(randf_range(-s, s) * 0.7, 0.0, randf_range(-s, s) * 0.7)
		r.get_tree().create_timer(life * (float(i) + 0.5) / n, false).timeout.connect(_late_bolt.bind(r, spot, c))


static func _m_quake(r: Node3D, s: float, c: Array) -> void:
	_ring(r, Color(0.8, 0.68, 0.45), s, 0.4)
	_ring(r, Color(0.8, 0.68, 0.45), s * 0.6, 0.3)
	_cracks(r, Color(0.9, 0.65, 0.3), 7, s, 1.0)
	_emit(r, {"amount": 32, "life": 0.9, "size": s * 0.35, "tex": "soft", "c0": Color(0.65, 0.55, 0.4, 0.6), "c1": Color(0.45, 0.38, 0.28), "vmin": 1.0, "vmax": 3.0, "spread": 70.0, "dir": Vector3.UP, "shape": "ring", "ext": s * 0.9, "inner": s * 0.2,
		"once": true, "burst": 0.9, "add": false, "pos": Vector3(0, 0.1, 0)})
	_emit(r, {"amount": 16, "life": 0.8, "size": 0.3, "mesh": "cube", "c0": Color(0.5, 0.4, 0.28), "c1": Color(0.4, 0.34, 0.24), "vmin": 3.0, "vmax": 6.0, "spread": 40.0, "dir": Vector3.UP, "grav": Vector3(0, -13, 0), "shape": "ring", "ext": s * 0.8, "inner": 0.2,
		"once": true, "burst": 1.0, "add": false})


static func _m_stomp(r: Node3D, s: float, c: Array) -> void:
	_flash(r, c[1], s * 1.8, 0.2, 0.3)
	_ring(r, c[0], s, 0.35)
	_ring(r, c[1], s * 0.65, 0.28)
	_emit(r, {"amount": 28, "life": 0.8, "size": s * 0.4, "tex": "soft", "c0": Color(0.62, 0.52, 0.38, 0.6), "c1": Color(0.45, 0.38, 0.28), "vmin": 2.0, "vmax": 4.5, "spread": 30.0, "dir": Vector3.UP, "shape": "ring", "ext": s * 0.8, "inner": s * 0.3,
		"once": true, "burst": 0.95, "add": false, "pos": Vector3(0, 0.1, 0)})
	_emit(r, {"amount": 10, "life": 0.6, "size": 0.3, "mesh": "cube", "c0": Color(0.5, 0.4, 0.28), "c1": Color(0.4, 0.34, 0.24), "vmin": 2.5, "vmax": 5.0, "spread": 45.0, "dir": Vector3.UP, "grav": Vector3(0, -12, 0), "shape": "ring", "ext": s * 0.7, "inner": 0.2,
		"once": true, "burst": 1.0, "add": false})


static func _m_dome(r: Node3D, s: float, c: Array, life: float, glyph: String, orbit: String) -> void:
	var dome := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = s
	sphere.height = s * 2.0
	sphere.is_hemisphere = true
	dome.mesh = sphere
	var mat := _add_mat(Color(c[0], 0.22))
	dome.material_override = mat
	dome.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	r.add_child(dome)
	dome.scale = Vector3.ONE * 0.4
	var t := dome.create_tween()
	t.tween_property(dome, "scale", Vector3.ONE, 0.25).set_ease(Tween.EASE_OUT)
	t.tween_property(mat, "albedo_color:a", 0.0, maxf(life - 0.25, 0.2)).set_ease(Tween.EASE_IN)
	_glyph(r, glyph, c[1], s * 1.9, life, 0.05, 0.3, 0.55)
	_ring(r, c[0], s, 0.4)
	if orbit != "":
		_orbiters(r, orbit, c, s * 0.9, 1.0, life)
	_emit(r, {"amount": 14, "life": 1.0, "size": 0.2, "tex": "spark", "c0": c[1], "c1": c[0], "vmin": 0.3, "vmax": 0.9, "spread": 30.0, "dir": Vector3.UP, "shape": "ring", "ext": s * 0.9, "inner": s * 0.5, "once": true, "burst": 0.6})


static func _m_aura_up(r: Node3D, s: float, c: Array, life: float, glyph: String, tex: String) -> void:
	_glyph(r, glyph, c[1], s * 2.0, maxf(life, 0.5), 0.05, 1.0, 0.7)
	_ring(r, c[0], s, 0.5)
	r.get_tree().create_timer(0.3, false).timeout.connect(_late_ring.bind(r, c[1], s * 0.8))
	_column(r, c[0], s * 0.5, 3.0, 0.7, 0.18)
	var up := _emit(r, {"amount": 26, "life": 1.1, "size": 0.3, "tex": tex, "c0": Color.WHITE, "c1": c[0], "vmin": 1.0, "vmax": 2.4, "spread": 12.0, "dir": Vector3.UP, "grav": Vector3(0, 0.4, 0), "shape": "ring", "ext": s * 0.8, "inner": s * 0.3,
		"once": life <= 0.8, "burst": 0.5, "pos": Vector3(0, 0.1, 0)})
	_stop_later(r, up, life)


static func _m_aura_wind(r: Node3D, s: float, c: Array, life: float, tex: String) -> void:
	_glyph(r, "soft", c[1], s * 2.0, 0.6, 0.05, 0.0, 0.3)
	_ring(r, c[0], s, 0.5)
	var swirl := _emit(r, {"amount": 36, "life": 0.9, "size": 0.4, "tex": tex, "c0": Color(1, 1, 1, 0.85), "c1": c[0], "vmin": 0.8, "vmax": 1.8, "spread": 15.0, "dir": Vector3.UP, "tang": 16.0, "shape": "ring", "ext": s * 0.85, "inner": s * 0.45,
		"grav": Vector3(0, 1.2, 0), "once": true, "burst": 0.7})
	_emit(r, {"amount": 12, "life": 0.7, "size": 0.9, "tex": "ray", "c0": Color(1, 1, 1, 0.7), "c1": c[0], "vmin": 5.0, "vmax": 8.0, "spread": 8.0, "dir": Vector3.RIGHT, "shape": "disc", "ext": s * 0.5, "once": true, "burst": 0.9, "pos": Vector3(0, 0.7, 0)})
	_stop_later(r, swirl, life)


static func _m_banner(r: Node3D, s: float, c: Array, life: float, glyph: String) -> void:
	_glyph(r, glyph, c[1], s * 1.8, maxf(life, 0.6), 0.05, 0.5, 0.6)
	_ring(r, c[0], s, 0.5)
	_column(r, c[0], 0.5, 5.0, maxf(life, 0.8), 0.28)
	var pole := _core_box(r, c[1], Vector3(0.08, 3.0, 0.08), 0.0)
	pole.position.y = 1.5
	var flag := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2(1.3, 0.8)
	flag.mesh = quad
	var fmat := _add_mat(Color(c[0], 0.85))
	fmat.cull_mode = BaseMaterial3D.CULL_DISABLED
	flag.material_override = fmat
	flag.position = Vector3(0.7, 2.7, 0.0)
	r.add_child(flag)
	var wave := flag.create_tween().set_loops()
	wave.tween_property(flag, "rotation:y", 0.35, 0.4).set_trans(Tween.TRANS_SINE)
	wave.tween_property(flag, "rotation:y", -0.35, 0.4).set_trans(Tween.TRANS_SINE)
	var sparks := _emit(r, {"amount": 20, "life": 1.3, "size": 0.25, "tex": "star4", "c0": Color.WHITE, "c1": c[0], "vmin": 0.8, "vmax": 2.0, "spread": 20.0, "dir": Vector3.UP, "shape": "ring", "ext": s * 0.8, "inner": s * 0.2})
	_stop_later(r, sparks, life)


static func _m_teleport(r: Node3D, s: float, c: Array, tex: String) -> void:
	_flash(r, c[1], s * 2.2, 0.35, 0.8)
	_glyph(r, "rune", c[1], s * 2.2, 0.45, 0.05, -3.0, 0.8)
	_ring(r, c[0], s * 1.3, 0.35)
	r.get_tree().create_timer(0.15, false).timeout.connect(_late_ring.bind(r, c[1], s * 0.8))
	_emit(r, {"amount": 22, "life": 0.6, "size": 0.25, "tex": tex, "c0": c[1], "c1": c[0], "vmin": 2.0, "vmax": 4.5, "spread": 25.0, "dir": Vector3.UP, "grav": Vector3(0, -1.0, 0), "shape": "ring", "ext": s * 0.9, "inner": s * 0.2, "once": true, "burst": 0.9, "pos": Vector3(0, 0.1, 0)})


static func _m_vanish(r: Node3D, s: float, c: Array) -> void:
	_flash(r, Color(0.35, 0.2, 0.55), s * 2.5, 0.4, 0.8)
	_emit(r, {"amount": 22, "life": 0.9, "size": s * 0.7, "tex": "soft", "c0": Color(0.12, 0.1, 0.16, 0.8), "c1": c[0], "vmin": 0.8, "vmax": 2.2, "spread": 90.0, "dir": Vector3.UP, "shape": "sphere", "ext": s * 0.4,
		"once": true, "burst": 0.9, "add": false, "pos": Vector3(0, 0.7, 0)})
	_emit(r, {"amount": 16, "life": 0.7, "size": 0.3, "tex": "diamond", "c0": c[1], "c1": c[0], "vmin": 1.5, "vmax": 3.5, "spread": 180.0, "shape": "sphere", "ext": s * 0.3, "once": true, "burst": 1.0, "pos": Vector3(0, 0.8, 0)})
	_ring(r, c[0], s, 0.3)


static func _m_smoke(r: Node3D, s: float, c: Array, life: float) -> void:
	var cloud := _emit(r, {"amount": 30, "life": 2.0, "size": s * 0.8, "tex": "soft", "c0": Color(0.6, 0.6, 0.66, 0.7), "c1": Color(0.3, 0.3, 0.36), "vmin": 0.2, "vmax": 0.9, "spread": 180.0, "shape": "disc", "ext": s * 0.7, "pos": Vector3(0, 0.6, 0), "add": false})
	_glyph(r, "soft", Color(0.5, 0.5, 0.58), s * 2.1, life, 0.05, 0.0, 0.3)
	_flash(r, Color(0.8, 0.8, 0.9), s * 1.6, 0.25, 0.7)
	_stop_later(r, cloud, life)


static func _m_shout(r: Node3D, s: float, c: Array) -> void:
	for i in 3:
		r.get_tree().create_timer(0.1 * i, false).timeout.connect(_late_ring.bind(r, c[0] if i % 2 == 0 else c[1], s * (1.0 - 0.2 * i)))
	_flash(r, c[1], s * 1.6, 0.3, 1.2)
	_glyph(r, "ray", c[1], s * 1.2, 0.5, 0.06, 0.0, 0.7)
	_emit(r, {"amount": 20, "life": 0.6, "size": 1.1, "tex": "ray", "c0": c[1], "c1": c[0], "vmin": 5.0, "vmax": 9.0, "spread": 12.0, "dir": Vector3.RIGHT, "shape": "disc", "ext": 0.4, "once": true, "burst": 1.0, "pos": Vector3(0, 1.0, 0), "tilt": true})


static func _m_trap(r: Node3D, s: float, c: Array, life: float) -> void:
	_glyph(r, "rune", c[0], s * 2.0, life, 0.05, 0.0, 0.55)
	_spikes(r, c[1], 8, 0.14, 0.5, life, true, s * 0.7, false)
	_ring(r, c[0], s, 0.5)


static func _m_seal(r: Node3D, s: float, c: Array, life: float, glyph: String, tex: String) -> void:
	_glyph(r, glyph, c[1], s * 2.2, life, 0.05, 1.2, 0.75)
	_glyph(r, "star4", c[0], s * 1.4, life, 0.06, -2.0, 0.5)
	_ring(r, c[0], s, 0.5)
	var p := _emit(r, {"amount": 24, "life": 1.0, "size": 0.28, "tex": tex, "c0": c[1], "c1": c[0], "vmin": 0.8, "vmax": 2.0, "spread": 15.0, "dir": Vector3.UP, "tang": 5.0, "shape": "ring", "ext": s * 0.9, "inner": s * 0.4, "pos": Vector3(0, 0.1, 0)})
	_stop_later(r, p, life)


static func _m_summon(r: Node3D, s: float, c: Array, glyph: String, tex: String) -> void:
	_glyph(r, glyph, c[1], s * 2.6, 0.9, 0.05, 1.5, 0.85)
	_ring(r, c[0], s, 0.6)
	_column(r, c[1], s * 0.7, 4.0, 0.8, 0.3)
	_flash(r, c[1], s * 2.0, 0.5, 0.8)
	_emit(r, {"amount": 22, "life": 1.1, "size": 0.35, "tex": tex, "c0": c[1], "c1": c[0], "vmin": 1.2, "vmax": 2.8, "spread": 18.0, "dir": Vector3.UP, "tang": 4.0, "shape": "ring", "ext": s, "inner": s * 0.3, "once": true, "burst": 0.7, "pos": Vector3(0, 0.1, 0)})


## Aviso antes do impacto (meteoro, terremoto): círculo que pulsa e uma luz que desce.
static func _m_danger(r: Node3D, s: float, c: Array, life: float) -> void:
	var mark := _glyph(r, "rune", c[0], s * 2.2, maxf(life, 0.5), 0.06, 0.6, 0.8)
	var pulse := mark.create_tween().set_loops()
	pulse.tween_property(mark, "scale", Vector3.ONE * 1.08, 0.25)
	pulse.tween_property(mark, "scale", Vector3.ONE * 0.94, 0.25)
	_glyph(r, "soft", c[0], s * 2.0, maxf(life, 0.5), 0.04, 0.0, 0.3)
	_ring(r, c[1], s, 0.6)
	var fall := _column(r, c[1], s * 0.25, 9.0, maxf(life, 0.5), 0.0)
	fall.position.y = 14.0
	var drop := fall.create_tween()
	drop.tween_property(fall, "position:y", 0.0, maxf(life, 0.3)).set_ease(Tween.EASE_IN)


static func _m_arc_sweep(r: Node3D, s: float, c: Array, dir: Vector3) -> void:
	var d := Vector3(dir.x, 0, dir.z)
	d = d.normalized() if d.length() > 0.01 else Vector3.FORWARD
	r.global_position -= d * s * 0.9
	var arc := _flat_quad(r, "crescent", c[1], s * 2.0, 0.9)
	arc.rotation.y = atan2(d.x, d.z) - PI / 2.0
	arc.position = d * s * 0.9
	arc.scale = Vector3.ONE * 0.5
	var t := arc.create_tween().set_parallel()
	t.tween_property(arc, "scale", Vector3.ONE, 0.2).set_ease(Tween.EASE_OUT)
	t.tween_property(arc.material_override, "albedo_color:a", 0.0, 0.32)
	_emit(r, {"amount": 22, "life": 0.4, "size": 0.9, "tex": "ray", "c0": c[1], "c1": c[0], "vmin": 6.0, "vmax": 10.0, "spread": 35.0, "dir": d, "shape": "point", "once": true, "burst": 0.95, "pos": Vector3(0, 0.9, 0), "tilt": true})
	_ring(r, c[0], s * 0.5, 0.25)


static func _m_flock(r: Node3D, s: float, c: Array, dir: Vector3) -> void:
	var d := Vector3(dir.x, 0, dir.z)
	d = d.normalized() if d.length() > 0.01 else Vector3.FORWARD
	r.global_position -= d * s * 0.9
	_emit(r, {"amount": 22, "life": 0.9, "size": 0.7, "tex": "wing", "c0": Color.WHITE, "c1": c[0], "vmin": 8.0, "vmax": 13.0, "spread": 28.0, "dir": d, "shape": "point", "once": true, "burst": 0.8, "pos": Vector3(0, 1.1, 0), "tilt": true})
	_emit(r, {"amount": 24, "life": 0.8, "size": 0.25, "tex": "leaf", "c0": c[1], "c1": c[0], "vmin": 5.0, "vmax": 9.0, "spread": 30.0, "dir": d, "grav": Vector3(0, -3.0, 0), "shape": "point", "once": true, "burst": 0.9, "pos": Vector3(0, 1.0, 0)})
	_flash(r, c[1], s * 1.2, 0.3, 0.9)


static func _m_wing_storm(r: Node3D, s: float, c: Array, life: float) -> void:
	_glyph(r, "soft", c[1], s * 2.1, life, 0.04, 0.0, 0.25)
	_ring(r, c[0], s, 0.5)
	var feathers := _emit(r, {"amount": 46, "life": 1.1, "size": 0.55, "tex": "wing", "c0": Color.WHITE, "c1": c[0], "vmin": 1.0, "vmax": 2.4, "spread": 40.0, "dir": Vector3.UP, "tang": 12.0, "shape": "ring", "ext": s * 0.9, "inner": s * 0.3,
		"grav": Vector3(0, 1.0, 0), "pos": Vector3(0, 0.3, 0)})
	var spark := _emit(r, {"amount": 14, "life": 0.5, "size": 0.25, "tex": "spark", "c0": Color(1.0, 1.0, 0.7), "c1": c[0], "vmin": 0.5, "vmax": 1.5, "spread": 180.0, "shape": "disc", "ext": s * 0.8, "pos": Vector3(0, 1.5, 0)})
	_stop_later(r, feathers, life)
	_stop_later(r, spark, life)
	var n := clampi(roundi(life), 2, 6)
	for i in n:
		var spot := Vector3(randf_range(-s, s) * 0.7, 0.0, randf_range(-s, s) * 0.7)
		r.get_tree().create_timer(life * (float(i) + 0.5) / n, false).timeout.connect(_late_bolt.bind(r, spot, c))


static func _m_splash(r: Node3D, s: float, c: Array) -> void:
	_flash(r, c[1], s * 1.8, 0.25, 0.4)
	_ring(r, c[0], s, 0.35)
	_emit(r, {"amount": 22, "life": 0.7, "size": 0.35, "tex": "drop", "c0": c[1], "c1": c[0], "vmin": 3.0, "vmax": 6.0, "spread": 40.0, "dir": Vector3.UP, "grav": Vector3(0, -11, 0), "shape": "disc", "ext": s * 0.4, "once": true, "burst": 0.95})


static func _m_iron(r: Node3D, s: float, c: Array) -> void:
	_flash(r, Color.WHITE, s * 1.6, 0.25, 1.0)
	_ring(r, c[0], s, 0.45)
	_glyph(r, "hex", c[1], s * 1.8, 0.7, 0.06, 0.8, 0.8)
	_emit(r, {"amount": 16, "life": 0.7, "size": 0.35, "mesh": "shard", "c0": c[1], "c1": c[0], "vmin": 2.0, "vmax": 4.0, "spread": 60.0, "dir": Vector3.UP, "grav": Vector3(0, -8, 0), "shape": "ring", "ext": s * 0.7, "inner": s * 0.3, "once": true, "burst": 1.0, "add": false})


# --- Motivos de feixe -------------------------------------------------------------------------

static func _m_chain(parent: Node, a: Vector3, b: Vector3, c: Array, life: float) -> void:
	_bolt(parent, a, b, c[0], 0.2, life, 0.9, 11)
	_bolt(parent, a, b, c[1], 0.09, life * 0.7, 1.4, 9)
	var root := _root(parent, b, life)
	_flash(root, c[1], 1.4, 0.25, 0.0)
	_emit(root, {"amount": 10, "life": 0.4, "size": 0.25, "tex": "spark", "c0": Color.WHITE, "c1": c[0], "vmin": 1.5, "vmax": 3.5, "spread": 180.0, "once": true, "burst": 1.0})


static func _m_sky_bolt(parent: Node, at: Vector3, c: Array, life: float) -> void:
	var top := Vector3(at.x + randf_range(-0.6, 0.6), 9.0, at.z + randf_range(-0.6, 0.6))
	var low := Vector3(at.x, 0.1, at.z)
	_bolt(parent, top, low, c[0], 0.3, life, 1.2, 12)
	_bolt(parent, top, low, Color.WHITE, 0.1, life * 0.7, 0.8, 12)
	var root := _root(parent, low, life)
	_flash(root, c[1], 2.4, 0.3, 0.3)
	_ring(root, c[0], 1.2, 0.3)
	_emit(root, {"amount": 12, "life": 0.5, "size": 0.25, "tex": "spark", "c0": Color.WHITE, "c1": c[0], "vmin": 2.0, "vmax": 4.5, "spread": 70.0, "dir": Vector3.UP, "grav": Vector3(0, -8, 0), "once": true, "burst": 1.0})


static func _m_fire_line(parent: Node, a: Vector3, b: Vector3, w: float, c: Array, life: float) -> void:
	var mid := (a + b) / 2.0
	var length := a.distance_to(b)
	var root := _root(parent, Vector3(mid.x, 0.0, mid.z), maxf(life, 0.5))
	root.look_at(Vector3(b.x, 0.0, b.z), Vector3.UP)
	_flat_box(root, c[0], Vector3(w * 1.2, 0.02, length), 0.05, 0.35, life)
	var flames := _emit(root, {"amount": clampi(roundi(length * 7.0), 14, 56), "life": 0.8, "size": 1.0, "tex": "soft", "c0": c[1], "c1": c[0], "vmin": 0.4, "vmax": 1.6, "spread": 14.0, "dir": Vector3.UP,
		"grav": Vector3(0, 3.0, 0), "shape": "box", "ext": Vector3(w * 0.5, 0.1, length * 0.5), "pos": Vector3(0, 0.1, 0)})
	var sparks := _emit(root, {"amount": 12, "life": 1.2, "size": 0.2, "tex": "star4", "c0": Color.WHITE, "c1": c[0], "vmin": 1.5, "vmax": 3.5, "spread": 30.0, "dir": Vector3.UP, "shape": "box", "ext": Vector3(w * 0.5, 0.1, length * 0.5)})
	_stop_later(root, flames, life)
	_stop_later(root, sparks, life)


static func _m_water_jet(parent: Node, a: Vector3, b: Vector3, w: float, c: Array, life: float) -> void:
	var root := _root(parent, (a + b) / 2.0, life + 0.3)
	root.look_at(b, Vector3.UP if absf((b - a).normalized().y) < 0.99 else Vector3.FORWARD)
	var length := a.distance_to(b)
	_flat_box(root, c[0], Vector3(maxf(w, 0.25), 0.25, length), 0.0, 0.4, life)
	_emit(root, {"amount": 34, "life": 0.5, "size": 0.45, "tex": "drop", "c0": Color.WHITE, "c1": c[0], "vmin": 1.0, "vmax": 3.0, "spread": 50.0, "dir": Vector3.UP, "grav": Vector3(0, -8, 0), "shape": "box",
		"ext": Vector3(0.2, 0.2, length * 0.5), "once": true, "burst": 0.8})
	_emit(root, {"amount": 12, "life": 0.6, "size": 0.35, "tex": "ring", "c0": Color.WHITE, "c1": c[0], "vmin": 0.3, "vmax": 1.0, "spread": 180.0, "shape": "box", "ext": Vector3(0.2, 0.2, length * 0.5), "once": true, "burst": 0.8})


static func _m_earth_line(parent: Node, a: Vector3, b: Vector3, w: float, c: Array, life: float) -> void:
	var length := a.distance_to(b)
	var dir := (b - a)
	dir.y = 0.0
	dir = dir.normalized()
	var root := _root(parent, Vector3(a.x, 0.0, a.z), life + 0.5)
	var n := clampi(roundi(length / 1.1), 4, 16)
	for i in n:
		var pivot := Node3D.new()
		root.add_child(pivot)
		pivot.position = dir * (1.0 + length * float(i) / n) + Vector3(randf_range(-0.3, 0.3), 0, randf_range(-0.3, 0.3))
		var spike := MeshInstance3D.new()
		var cone := CylinderMesh.new()
		cone.top_radius = 0.0
		cone.bottom_radius = 0.35 + 0.15 * randf()
		cone.height = 1.3 + 0.9 * randf()
		cone.radial_segments = 6
		spike.mesh = cone
		spike.material_override = _lit_mat(Color(0.52, 0.42, 0.3), false)
		spike.position.y = cone.height / 2.0
		spike.rotation = Vector3(randf_range(-0.3, 0.3), 0, randf_range(-0.3, 0.3))
		pivot.add_child(spike)
		pivot.scale = Vector3(1, 0.01, 1)
		var t := pivot.create_tween()
		t.tween_interval(0.04 * i)
		t.tween_property(pivot, "scale", Vector3.ONE, 0.1).set_ease(Tween.EASE_OUT)
		t.tween_interval(maxf(life - 0.3, 0.2))
		t.tween_property(pivot, "scale", Vector3(1, 0.01, 1), 0.3)
	_emit(root, {"amount": 26, "life": 0.7, "size": 0.5, "tex": "soft", "c0": Color(0.62, 0.52, 0.38, 0.6), "c1": Color(0.45, 0.38, 0.28), "vmin": 0.6, "vmax": 1.8, "spread": 60.0, "dir": Vector3.UP, "shape": "box", "ext": Vector3(w * 0.5 + 0.3, 0.1, 0.1),
		"once": true, "burst": 0.9, "add": false, "pos": dir * length * 0.5})


static func _m_spear_streak(parent: Node, a: Vector3, b: Vector3, w: float, c: Array, life: float, tex: String, zig: bool) -> void:
	if zig:
		_bolt(parent, a, b, c[0], 0.22, life, 0.5, 9)
	var root := _root(parent, (a + b) / 2.0, life)
	root.look_at(b, Vector3.UP if absf((b - a).normalized().y) < 0.99 else Vector3.FORWARD)
	var length := a.distance_to(b)
	var core := _flat_box(root, c[1], Vector3(maxf(w, 0.14) * 0.5, maxf(w, 0.14) * 0.5, length), 0.0, 0.95, life)
	core.position.y = 0.0
	_flat_box(root, c[0], Vector3(maxf(w, 0.14) * 1.4, maxf(w, 0.14) * 1.0, length * 0.92), 0.0, 0.4, life)
	var tip := _root(parent, b, life)
	_flash(tip, c[1], 1.5, 0.25, 0.0)
	_ring(tip, c[0], 0.9, 0.3, 0.1)
	_emit(tip, {"amount": 12, "life": 0.45, "size": 0.25, "tex": tex, "c0": Color.WHITE, "c1": c[0], "vmin": 2.0, "vmax": 4.5, "spread": 90.0, "dir": Vector3.UP, "grav": Vector3(0, -6, 0), "once": true, "burst": 1.0})
	_emit(root, {"amount": 14, "life": 0.5, "size": 0.3, "tex": tex, "c0": c[1], "c1": c[0], "vmin": 0.3, "vmax": 1.2, "spread": 180.0, "shape": "box", "ext": Vector3(0.1, 0.1, length * 0.5), "once": true, "burst": 0.9})


static func _m_slash(parent: Node, a: Vector3, b: Vector3, c: Array, life: float, tex: String) -> void:
	var root := _root(parent, b, life)
	var base := atan2(b.x - a.x, b.z - a.z)
	for i in 2:
		var cut := _flat_quad(root, "ray", c[1], 2.8, 0.9)
		cut.rotation = Vector3(PI / 2.0, 0.0, 0.0)
		cut.rotation = Vector3(0.0, base + (0.9 if i == 0 else -0.9), 0.0)
		cut.basis = Basis(Vector3.UP, base + (0.8 if i == 0 else -0.8)) * Basis(Vector3.RIGHT, 0.0)
		cut.scale = Vector3(0.4, 1.0, 1.0)
		var t := cut.create_tween().set_parallel()
		t.tween_property(cut, "scale", Vector3(1.3, 1.0, 1.0), 0.12)
		t.tween_property(cut.material_override, "albedo_color:a", 0.0, life)
	_flash(root, c[1], 1.6, 0.2, 0.9)
	_emit(root, {"amount": 12, "life": 0.4, "size": 0.25, "tex": tex, "c0": Color.WHITE, "c1": c[0], "vmin": 2.0, "vmax": 5.0, "spread": 120.0, "dir": Vector3.UP, "grav": Vector3(0, -6, 0), "once": true, "burst": 1.0, "pos": Vector3(0, 0.9, 0)})
	var streak := _root(parent, (a + b) / 2.0, life)
	streak.look_at(b, Vector3.UP if absf((b - a).normalized().y) < 0.99 else Vector3.FORWARD)
	_flat_box(streak, c[0], Vector3(0.16, 0.16, a.distance_to(b)), 0.0, 0.6, life)


static func _m_charge_dust(parent: Node, a: Vector3, b: Vector3, w: float, c: Array, life: float, tex: String) -> void:
	var length := a.distance_to(b)
	var root := _root(parent, Vector3((a.x + b.x) / 2.0, 0.0, (a.z + b.z) / 2.0), life)
	root.look_at(Vector3(b.x, 0.0, b.z), Vector3.UP)
	_flat_box(root, c[0], Vector3(maxf(w, 0.5), 0.02, length), 0.05, 0.3, life)
	_emit(root, {"amount": clampi(roundi(length * 6.0), 12, 50), "life": 0.9, "size": 0.9, "tex": "soft", "c0": Color(0.66, 0.58, 0.45, 0.55), "c1": Color(0.45, 0.4, 0.3), "vmin": 0.3, "vmax": 1.2, "spread": 70.0, "dir": Vector3.UP,
		"shape": "box", "ext": Vector3(maxf(w, 0.5) * 0.5, 0.1, length * 0.5), "once": true, "burst": 0.85, "add": false, "pos": Vector3(0, 0.1, 0)})
	_emit(root, {"amount": clampi(roundi(length * 4.0), 10, 36), "life": 0.5, "size": 0.9, "tex": "ray", "c0": c[1], "c1": c[0], "vmin": 0.0, "vmax": 0.4, "spread": 10.0, "dir": Vector3.UP, "shape": "box", "ext": Vector3(maxf(w, 0.5) * 0.6, 0.6, length * 0.5),
		"once": true, "burst": 0.8, "pos": Vector3(0, 0.8, 0), "tilt": true})
	_emit(root, {"amount": 16, "life": 0.7, "size": 0.3, "tex": tex, "c0": c[1], "c1": c[0], "vmin": 1.0, "vmax": 2.5, "spread": 50.0, "dir": Vector3.UP, "grav": Vector3(0, -3.0, 0), "shape": "box", "ext": Vector3(w * 0.5, 0.1, length * 0.5), "once": true, "burst": 0.9})


static func _m_mark_line(parent: Node, a: Vector3, b: Vector3, c: Array, life: float) -> void:
	var root := _root(parent, Vector3(b.x, 0.0, b.z), life)
	var reticle := _glyph(root, "rune", c[0], 2.2, life, 0.9, 2.5, 0.9)
	reticle.rotation.x = 0.0
	_glyph(root, "star4", c[1], 1.2, life, 0.9, -3.0, 0.9)
	_ring(root, c[0], 1.1, 0.4, 0.9)
	var line := _root(parent, (a + b) / 2.0, life)
	line.look_at(b, Vector3.UP if absf((b - a).normalized().y) < 0.99 else Vector3.FORWARD)
	_flat_box(line, c[0], Vector3(0.05, 0.05, a.distance_to(b)), 0.0, 0.7, life)


static func _m_heal_ribbon(parent: Node, a: Vector3, b: Vector3, c: Array, life: float) -> void:
	var length := a.distance_to(b)
	var root := _root(parent, (a + b) / 2.0, life + 0.3)
	root.look_at(b, Vector3.UP if absf((b - a).normalized().y) < 0.99 else Vector3.FORWARD)
	_flat_box(root, c[0], Vector3(0.4, 0.4, length), 0.0, 0.3, life)
	_emit(root, {"amount": 14, "life": 0.9, "size": 0.5, "tex": "plus", "c0": Color(0.8, 1.0, 0.85, 0.95), "c1": c[0], "vmin": 0.3, "vmax": 0.9, "spread": 60.0, "dir": Vector3.UP, "shape": "box", "ext": Vector3(0.3, 0.2, length * 0.5), "once": true, "burst": 0.7})
	_emit(root, {"amount": 22, "life": 0.7, "size": 0.25, "tex": "spark", "c0": Color.WHITE, "c1": c[1], "vmin": 0.5, "vmax": 1.5, "spread": 180.0, "shape": "box", "ext": Vector3(0.3, 0.3, length * 0.5), "once": true, "burst": 0.7})
	var end := _root(parent, b, life + 0.3)
	_flash(end, c[1], 2.2, 0.5, 0.6)
	_column(end, c[0], 0.6, 3.0, 0.7, 0.3)
	_glyph(end, "plus", c[1], 1.6, 0.8, 0.1, 0.0, 0.9)


static func _m_blink_cut(parent: Node, a: Vector3, b: Vector3, c: Array, life: float, tex: String) -> void:
	_m_slash(parent, a, b, c, life, tex)
	var trail := _root(parent, a, life)
	_flash(trail, c[1], 1.8, 0.35, 0.9)
	_emit(trail, {"amount": 12, "life": 0.5, "size": 0.45, "tex": "diamond", "c0": c[1], "c1": c[0], "vmin": 0.6, "vmax": 1.8, "spread": 180.0, "once": true, "burst": 1.0, "pos": Vector3(0, 0.9, 0)})


static func _m_bite(parent: Node, a: Vector3, b: Vector3, c: Array, life: float) -> void:
	var root := _root(parent, Vector3(b.x, 0.0, b.z), life + 0.3)
	for i in 2:
		var pivot := Node3D.new()
		root.add_child(pivot)
		pivot.position.y = 0.6 + 1.2 * i
		var fang := MeshInstance3D.new()
		var cone := CylinderMesh.new()
		cone.top_radius = 0.0
		cone.bottom_radius = 0.28
		cone.height = 1.4
		fang.mesh = cone
		fang.material_override = _add_mat(Color(c[1], 0.9))
		fang.position = Vector3(0.0, 0.0, 0.0)
		pivot.add_child(fang)
		fang.position.y = 1.0 if i == 0 else -1.0
		fang.rotation.z = 0.0 if i == 0 else PI
		var t := fang.create_tween()
		t.tween_property(fang, "position:y", 0.2 if i == 0 else -0.2, 0.12).set_ease(Tween.EASE_IN)
		t.tween_interval(0.12)
		t.tween_property(fang, "scale", Vector3.ZERO, 0.2)
	_flash(root, c[1], 2.0, 0.3, 0.9)
	_emit(root, {"amount": 22, "life": 0.7, "size": 0.7, "tex": "soft", "c0": c[1], "c1": c[0], "vmin": 1.0, "vmax": 3.0, "spread": 120.0, "dir": Vector3.UP, "grav": Vector3(0, 2.0, 0), "once": true, "burst": 0.95, "pos": Vector3(0, 0.8, 0)})
	var line := _root(parent, (a + b) / 2.0, life)
	line.look_at(b, Vector3.UP if absf((b - a).normalized().y) < 0.99 else Vector3.FORWARD)
	_flat_box(line, c[0], Vector3(0.12, 0.12, a.distance_to(b)), 0.0, 0.5, life)


static func _m_dive(parent: Node, a: Vector3, b: Vector3, c: Array, life: float) -> void:
	var top := Vector3(b.x, 8.0, b.z)
	var mid := (top + b) / 2.0
	var root := _root(parent, mid, life + 0.3)
	root.look_at(b, Vector3.UP if absf((b - top).normalized().y) < 0.99 else Vector3.FORWARD)
	_flat_box(root, c[0], Vector3(0.5, 0.5, top.distance_to(b)), 0.0, 0.3, life)
	_emit(root, {"amount": 20, "life": 0.6, "size": 0.6, "tex": "wing", "c0": Color.WHITE, "c1": c[0], "vmin": 0.5, "vmax": 1.8, "spread": 120.0, "shape": "box", "ext": Vector3(0.3, 0.2, top.distance_to(b) * 0.5), "once": true, "burst": 0.9})
	var hit := _root(parent, Vector3(b.x, 0.0, b.z), life + 0.3)
	_flash(hit, c[1], 2.4, 0.3, 0.6)
	_ring(hit, c[0], 1.4, 0.35)
	_emit(hit, {"amount": 16, "life": 0.7, "size": 0.5, "tex": "wing", "c0": Color.WHITE, "c1": c[0], "vmin": 2.0, "vmax": 4.5, "spread": 90.0, "dir": Vector3.UP, "grav": Vector3(0, -3.0, 0), "once": true, "burst": 1.0})


# --- Peças ---------------------------------------------------------------------------------------

static func _root(parent: Node, at: Vector3, life: float) -> Node3D:
	var root := Node3D.new()
	parent.add_child(root)
	root.global_position = at
	root.get_tree().create_timer(maxf(life, 0.1) + 0.4, false).timeout.connect(root.queue_free)
	return root


static func _stop_later(root: Node, p: CPUParticles3D, life: float) -> void:
	if p and life > 0.8:
		root.get_tree().create_timer(life, false).timeout.connect(p.set_emitting.bind(false))


## Partículas por receita: amount, life, size, tex/mesh, c0, c1, vmin, vmax, spread, dir, grav, damp, tang, shape (sphere, ring, disc, box, point), ext, inner, once, burst, pos, add, local, tilt.
static func _emit(root: Node3D, s: Dictionary) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var size := float(s.get("size", 0.3))
	match String(s.get("mesh", "quad")):
		"shard":
			var box := BoxMesh.new()
			box.size = Vector3(size * 0.22, size * 1.7, size * 0.22)
			box.material = _lit_mat(Color.WHITE, bool(s.get("add", true)), true)
			p.mesh = box
			p.particle_flag_align_y = true
		"cube":
			var cube := BoxMesh.new()
			cube.size = Vector3.ONE * size * 0.6
			cube.material = _lit_mat(Color.WHITE, false, true)
			p.mesh = cube
		_:
			var quad := QuadMesh.new()
			quad.size = Vector2.ONE * size
			quad.material = _pmat(String(s.get("tex", "soft")), bool(s.get("add", true)))
			p.mesh = quad
	p.amount = int(s.get("amount", 16))
	p.lifetime = float(s.get("life", 0.6))
	p.one_shot = bool(s.get("once", false))
	p.explosiveness = float(s.get("burst", 0.0))
	p.local_coords = bool(s.get("local", true))
	p.direction = s.get("dir", Vector3.UP)
	p.spread = float(s.get("spread", 45.0))
	p.gravity = s.get("grav", Vector3.ZERO)
	p.initial_velocity_min = float(s.get("vmin", 0.5))
	p.initial_velocity_max = float(s.get("vmax", 1.5))
	p.damping_min = float(s.get("damp", 0.0))
	p.damping_max = float(s.get("damp", 0.0))
	p.tangential_accel_min = float(s.get("tang", 0.0)) * 0.6
	p.tangential_accel_max = float(s.get("tang", 0.0))
	p.scale_amount_min = 0.6
	p.scale_amount_max = 1.2
	if s.get("tilt", false):
		p.particle_flag_align_y = false
		p.angle_min = -20.0
		p.angle_max = 20.0
	var ramp := Gradient.new()
	var c0: Color = s.get("c0", Color.WHITE)
	var c1: Color = s.get("c1", Color.WHITE)
	ramp.set_color(0, c0)
	ramp.set_color(1, Color(c1.r, c1.g, c1.b, 0.0))
	ramp.add_point(0.45, Color(c1.r, c1.g, c1.b, minf(c0.a, 0.9)))
	p.color_ramp = ramp
	var ext: Variant = s.get("ext", 0.3)
	match String(s.get("shape", "point")):
		"sphere":
			p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
			p.emission_sphere_radius = float(ext)
		"ring", "disc":
			p.emission_shape = CPUParticles3D.EMISSION_SHAPE_RING
			p.emission_ring_axis = Vector3.UP
			p.emission_ring_radius = float(ext)
			p.emission_ring_inner_radius = float(s.get("inner", 0.0))
			p.emission_ring_height = 0.1
		"box":
			p.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
			p.emission_box_extents = ext if ext is Vector3 else Vector3.ONE * float(ext)
	p.position = s.get("pos", Vector3.ZERO)
	root.add_child(p)
	p.emitting = true
	return p


static func _flash(root: Node3D, color: Color, size: float, life: float, y: float) -> void:
	var m := MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2.ONE * size
	m.mesh = q
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	mat.albedo_texture = _tex("soft")
	mat.albedo_color = Color(color, 0.9)
	m.material_override = mat
	m.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	m.position.y = y
	root.add_child(m)
	m.scale = Vector3.ONE * 0.3
	var t := m.create_tween().set_parallel()
	t.tween_property(m, "scale", Vector3.ONE, life).set_ease(Tween.EASE_OUT)
	t.tween_property(mat, "albedo_color:a", 0.0, life)


static func _ring(root: Node3D, color: Color, radius: float, life: float, y := 0.06, thick := 0.1) -> MeshInstance3D:
	var ring := MeshInstance3D.new()
	var torus := TorusMesh.new()
	torus.inner_radius = 1.0 - thick
	torus.outer_radius = 1.0
	torus.rings = 32
	ring.mesh = torus
	var mat := _add_mat(Color(color.lightened(0.2), 0.9))
	ring.material_override = mat
	ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	ring.position.y = y
	ring.scale = Vector3(radius * 0.2, 0.3, radius * 0.2)
	root.add_child(ring)
	var t := ring.create_tween().set_parallel()
	t.tween_property(ring, "scale", Vector3(radius, 0.3, radius), life).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	t.tween_property(mat, "albedo_color:a", 0.0, life + 0.15).set_ease(Tween.EASE_IN)
	return ring


static func _column(root: Node3D, color: Color, radius: float, height: float, life: float, alpha := 0.35) -> MeshInstance3D:
	var col := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2(radius * 2.6, height)
	col.mesh = quad
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_FIXED_Y
	mat.albedo_texture = _tex("pillar")
	mat.albedo_color = Color(color, minf(alpha * 2.2, 0.95))
	col.material_override = mat
	col.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	col.position.y = height / 2.0
	root.add_child(col)
	col.create_tween().tween_property(mat, "albedo_color:a", 0.0, maxf(life, 0.3)).set_ease(Tween.EASE_IN)
	return col


static func _spikes(root: Node3D, color: Color, count: int, width: float, height: float, life: float, lit_up: bool, ring_radius: float, translucent: bool) -> void:
	for i in count:
		var ang := TAU * i / count
		var pivot := Node3D.new()
		root.add_child(pivot)
		pivot.position = Vector3(cos(ang), 0, sin(ang)) * ring_radius
		var spike := MeshInstance3D.new()
		var cone := CylinderMesh.new()
		cone.top_radius = 0.0
		cone.bottom_radius = width
		cone.height = height
		cone.radial_segments = 6
		spike.mesh = cone
		spike.material_override = _add_mat(Color(color, 0.7)) if (translucent or lit_up) else _lit_mat(color, false)
		spike.position.y = height / 2.0
		pivot.add_child(spike)
		pivot.rotation = Vector3(0, 0, 0)
		pivot.scale = Vector3(1, 0.01, 1)
		var t := pivot.create_tween()
		t.tween_interval(0.02 * i)
		t.tween_property(pivot, "scale", Vector3.ONE, 0.12).set_ease(Tween.EASE_OUT)
		t.tween_interval(maxf(life - 0.3, 0.2))
		t.tween_property(pivot, "scale", Vector3(1, 0.01, 1), 0.3)


static func _cracks(root: Node3D, color: Color, count: int, length: float, life: float) -> void:
	for i in count:
		var pivot := Node3D.new()
		root.add_child(pivot)
		pivot.position.y = 0.05
		pivot.rotation.y = TAU * i / maxi(count, 1) + randf() * 0.3
		var crack := MeshInstance3D.new()
		var box := BoxMesh.new()
		var l := length * (0.55 + 0.45 * randf())
		box.size = Vector3(0.09, 0.02, l)
		crack.mesh = box
		var mat := _add_mat(Color(color, 0.9))
		crack.material_override = mat
		crack.position.z = l / 2.0
		pivot.add_child(crack)
		crack.create_tween().tween_property(mat, "albedo_color:a", 0.0, maxf(life, 0.4)).set_ease(Tween.EASE_IN)


static func _bolt(parent: Node, a: Vector3, b: Vector3, color: Color, width: float, life: float, jag: float, segs: int) -> void:
	var root := Node3D.new()
	parent.add_child(root)
	root.global_position = Vector3.ZERO
	root.get_tree().create_timer(life + 0.4, false).timeout.connect(root.queue_free)
	var dir := (b - a)
	var side := dir.cross(Vector3.UP)
	side = side.normalized() if side.length() > 0.01 else Vector3.RIGHT
	var up := side.cross(dir.normalized())
	var points: Array[Vector3] = [a]
	for i in range(1, segs):
		var t := float(i) / segs
		var off := (side * randf_range(-1.0, 1.0) + up * randf_range(-1.0, 1.0)) * jag * 0.5
		points.append(a.lerp(b, t) + off)
	points.append(b)
	var mats: Array[StandardMaterial3D] = []
	for layer in 2:
		var mat := _add_mat(Color(color if layer == 0 else Color.WHITE, 0.55 if layer == 0 else 0.95))
		mats.append(mat)
		var w := width * (1.7 if layer == 0 else 0.6)
		for i in points.size() - 1:
			var p0 := points[i]
			var p1 := points[i + 1]
			var seg := MeshInstance3D.new()
			var box := BoxMesh.new()
			box.size = Vector3(w, w, p0.distance_to(p1) + w * 0.5)
			seg.mesh = box
			seg.material_override = mat
			seg.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			root.add_child(seg)
			seg.global_position = (p0 + p1) / 2.0
			if p0.distance_to(p1) > 0.01:
				seg.look_at(p1, Vector3.UP if absf((p1 - p0).normalized().y) < 0.99 else Vector3.FORWARD)
	var tween := root.create_tween().set_parallel()
	for mat in mats:
		tween.tween_property(mat, "albedo_color:a", 0.0, life).set_ease(Tween.EASE_IN)


## Símbolo achatado no chão (anel de runa, estrela, floco, hexágono, cruz): gira e some. Devolve o nó, para quem quiser animar.
static func _glyph(root: Node3D, kind: String, color: Color, size: float, life: float, y: float, spin: float, alpha := 0.8) -> MeshInstance3D:
	var quad := _flat_quad(root, kind, color, size, y)
	var mat := quad.material_override as StandardMaterial3D
	mat.albedo_color = Color(color, alpha)
	var t := quad.create_tween().set_parallel()
	if spin != 0.0:
		t.tween_property(quad, "rotation:y", spin * life, maxf(life, 0.2)).as_relative()
	t.tween_property(mat, "albedo_color:a", 0.0, maxf(life, 0.2)).set_ease(Tween.EASE_IN)
	return quad


static func _flat_quad(root: Node3D, kind: String, color: Color, size: float, y: float) -> MeshInstance3D:
	var m := MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2.ONE * size
	q.orientation = PlaneMesh.FACE_Y
	m.mesh = q
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.albedo_texture = _tex(kind)
	mat.albedo_color = Color(color, 0.9)
	m.material_override = mat
	m.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	m.position.y = y
	root.add_child(m)
	return m


static func _flat_box(root: Node3D, color: Color, size: Vector3, y: float, alpha: float, life: float) -> MeshInstance3D:
	var m := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = size
	m.mesh = box
	var mat := _add_mat(Color(color, alpha))
	m.material_override = mat
	m.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	m.position.y = y
	root.add_child(m)
	m.create_tween().tween_property(mat, "albedo_color:a", 0.0, maxf(life, 0.2)).set_ease(Tween.EASE_IN)
	return m


static func _orbiters(root: Node3D, kind: String, c: Array, radius: float, height: float, life: float) -> void:
	var pivot := Node3D.new()
	root.add_child(pivot)
	pivot.position.y = height
	for i in 5:
		var m := MeshInstance3D.new()
		var box := BoxMesh.new()
		box.size = Vector3(0.3, 0.45, 0.3) if kind == "plates" else Vector3(0.2, 0.2, 0.2)
		m.mesh = box
		m.material_override = _lit_mat(Color(0.5, 0.42, 0.3), false) if kind == "plates" else _add_mat(Color(c[1], 0.9))
		var ang := TAU * i / 5.0
		m.position = Vector3(cos(ang), 0, sin(ang)) * radius
		m.rotation.y = -ang
		pivot.add_child(m)
	var t := pivot.create_tween()
	t.tween_property(pivot, "rotation:y", TAU * maxf(life, 0.6) * 0.5, maxf(life, 0.6))
	t.parallel().tween_property(pivot, "scale", Vector3.ZERO, 0.3).set_delay(maxf(life - 0.3, 0.2))


# Pecinhas de projétil.

static func _core_sphere(node: Node3D, color: Color, radius: float) -> void:
	var core := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = radius
	sphere.height = radius * 2.0
	sphere.radial_segments = 12
	sphere.rings = 6
	core.mesh = sphere
	core.material_override = _lit_mat(color, true)
	core.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	node.add_child(core)


static func _core_box(node: Node3D, color: Color, size: Vector3, yaw: float, shaded := false) -> MeshInstance3D:
	var core := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = size
	core.mesh = box
	core.material_override = _lit_mat(color, not shaded)
	core.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	core.rotation.y = yaw
	node.add_child(core)
	return core


static func _halo(node: Node3D, color: Color, size: float) -> void:
	var halo := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2.ONE * size
	halo.mesh = quad
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	mat.albedo_texture = _tex("soft")
	mat.albedo_color = Color(color, 0.75)
	halo.material_override = mat
	halo.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	node.add_child(halo)


# --- Materiais e texturas ---------------------------------------------------------------------

static func _add_mat(color: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.albedo_color = color
	return mat


## Material de peça sólida: aceso (sem sombra) ou sombreado; `vertex` = cor vem das partículas.
static func _lit_mat(color: Color, unlit: bool, vertex := false) -> StandardMaterial3D:
	var key := "lit%s%s%s" % [color.to_html(), unlit, vertex]
	if vertex and _mat_cache.has(key):
		return _mat_cache[key]
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.vertex_color_use_as_albedo = vertex
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA if vertex else BaseMaterial3D.TRANSPARENCY_DISABLED
	if unlit:
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	else:
		mat.roughness = 0.85
	if vertex:
		_mat_cache[key] = mat
	return mat


static func _pmat(tex: String, add: bool) -> StandardMaterial3D:
	var key := "p%s%s" % [tex, add]
	if _mat_cache.has(key):
		return _mat_cache[key]
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.vertex_color_use_as_albedo = true
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD if add else BaseMaterial3D.BLEND_MODE_MIX
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	mat.billboard_keep_scale = true  # sem isso, as partículas ainda não nascidas (escala 0) aparecem inteiras na origem (preto na mistura normal)
	mat.albedo_texture = _tex(tex)
	_mat_cache[key] = mat
	return mat


static func _tex(kind: String) -> ImageTexture:
	if _tex_cache.has(kind):
		return _tex_cache[kind]
	var n := 64
	var img := Image.create_empty(n, n, false, Image.FORMAT_RGBA8)
	for y in n:
		for x in n:
			var u := (x + 0.5) / n * 2.0 - 1.0
			var v := (y + 0.5) / n * 2.0 - 1.0
			img.set_pixel(x, y, Color(1, 1, 1, clampf(_shape(kind, u, v), 0.0, 1.0)))
	var tex := ImageTexture.create_from_image(img)
	_tex_cache[kind] = tex
	return tex


## Forma (alfa) de cada símbolo, em coordenadas de -1 a 1.
static func _shape(kind: String, u: float, v: float) -> float:
	var d := sqrt(u * u + v * v)
	match kind:
		"ring":
			return 1.0 - clampf(absf(d - 0.78) / 0.14, 0.0, 1.0)
		"star4":
			var star := 1.0 - (sqrt(absf(u)) + sqrt(absf(v)))
			return maxf(star * 1.6, pow(clampf(1.0 - d, 0.0, 1.0), 2.0) * 0.8)
		"spark":
			var thin := 1.0 - (pow(absf(u), 0.35) + pow(absf(v), 0.35))
			return maxf(thin * 2.2, pow(clampf(1.0 - d * 1.3, 0.0, 1.0), 2.0))
		"plus":
			var h := (1.0 - clampf(absf(v) / 0.2, 0.0, 1.0)) * (1.0 - clampf(absf(u) / 0.9, 0.0, 1.0))
			var w := (1.0 - clampf(absf(u) / 0.2, 0.0, 1.0)) * (1.0 - clampf(absf(v) / 0.9, 0.0, 1.0))
			return maxf(h, w)
		"snow":
			var best := 0.0
			for k in 3:
				var ang := PI * k / 3.0
				var dist := absf(-sin(ang) * u + cos(ang) * v)
				var along := absf(cos(ang) * u + sin(ang) * v)
				best = maxf(best, (1.0 - clampf(dist / 0.09, 0.0, 1.0)) * (1.0 - clampf(along / 0.92, 0.0, 1.0)))
			return best
		"drop":
			var e := pow(u / 0.42, 2.0) + pow((v + 0.1) / 0.82, 2.0)
			return clampf(1.4 - e * 1.4, 0.0, 1.0)
		"crescent":
			var outer := clampf((0.92 - d) / 0.08, 0.0, 1.0)
			var inner := clampf((sqrt(pow(u - 0.38, 2.0) + v * v) - 0.78) / 0.08, 0.0, 1.0)
			return outer * inner
		"ray":
			return clampf(1.0 - (absf(u) / 0.22 + absf(v) / 0.97), 0.0, 1.0)
		"diamond":
			return clampf(1.6 - (absf(u) + absf(v)) / 0.55, 0.0, 1.0)
		"hex":
			var hx := maxf(absf(u) * 0.866 + absf(v) * 0.5, absf(v))
			return maxf(1.0 - clampf(absf(hx - 0.8) / 0.1, 0.0, 1.0), pow(clampf(1.0 - d * 1.4, 0.0, 1.0), 2.0) * 0.35)
		"rune":
			var ring := 1.0 - clampf(absf(d - 0.85) / 0.07, 0.0, 1.0)
			var ring2 := 1.0 - clampf(absf(d - 0.62) / 0.05, 0.0, 1.0)
			var star := clampf(1.0 - (sqrt(absf(u)) + sqrt(absf(v))) * 1.25, 0.0, 1.0)
			var tri := 0.0
			for k in 3:
				var ang := TAU * k / 3.0 + PI / 2.0
				var dist := absf(-sin(ang) * u + cos(ang) * v)
				var along := cos(ang) * u + sin(ang) * v
				tri = maxf(tri, (1.0 - clampf(dist / 0.045, 0.0, 1.0)) * (1.0 if along > 0.0 and along < 0.62 else 0.0))
			return maxf(maxf(ring, ring2 * 0.8), maxf(star * 0.9, tri))
		"pillar":
			return pow(clampf(1.0 - absf(u), 0.0, 1.0), 1.5) * pow(0.1 + 0.9 * (v + 1.0) / 2.0, 1.2)
		"leaf":
			var le := pow(u / 0.34, 2.0) + pow(v / 0.9, 2.0)
			return clampf(1.3 - le * 1.3, 0.0, 1.0) * (0.55 + 0.45 * clampf(1.0 - absf(u - v * 0.15) / 0.12, 0.0, 1.0))
		"wing":
			var shape := pow((u + 0.1) / 0.95, 2.0) + pow((v - u * 0.35) / 0.28, 2.0)
			return clampf(1.3 - shape * 1.3, 0.0, 1.0)
		_:
			return pow(clampf(1.0 - d, 0.0, 1.0), 1.5)
