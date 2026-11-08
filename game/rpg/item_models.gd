# Southern Mercenaries — GPL-3.0-or-later
class_name ItemModels
extends RefCounted
## Modelos 3D procedurais das peças de equipamento que não têm modelo próprio (capuz, túnica,
## luvas, botas, anel, boné, colete, máscara, peitoral, barda) e dos pergaminhos de refino, na cor
## do material (pano, ferro, aço...). Usados no item caído no chão (loot_drop.gd) e para renderizar
## os ícones do inventário por material (tools/assets/gear_icons.gd), para os dois serem iguais.
## Não usa GameData: as cores ficam aqui, iguais às de data/materials.json.

## Cor principal, de acabamento (couro, costura) e quanto é metal, por material.
const PALETTE := {
	"cloth": {"main": Color("c9bb9b"), "trim": Color("6b4a2b"), "metal": 0.0, "rough": 0.9},
	"wood": {"main": Color("9a7b55"), "trim": Color("5a3a20"), "metal": 0.0, "rough": 0.85},
	"iron": {"main": Color("6f7378"), "trim": Color("4a3424"), "metal": 0.45, "rough": 0.55},
	"steel": {"main": Color("d3dae2"), "trim": Color("3b2a1f"), "metal": 0.5, "rough": 0.3},
	"copper": {"main": Color("c06a3c"), "trim": Color("4a2418"), "metal": 0.85, "rough": 0.35},
	"silver": {"main": Color("eef2f5"), "trim": Color("2a3550"), "metal": 0.9, "rough": 0.25},
	"gold": {"main": Color("e3b23c"), "trim": Color("5a1e1e"), "metal": 0.95, "rough": 0.25},
}
## Peças de couro: no tier de pano são de couro marrom, não de tecido.
const LEATHER := ["hunter_cap", "leather_vest", "gloves", "boots"]
const LEATHER_COLOR := Color("8a5a34")
const DARK := Color(0.08, 0.06, 0.05)
const BASES := ["hood", "tunic", "gloves", "boots", "ring", "hunter_cap", "leather_vest", "ninja_mask", "plate", "barding"]


static func has_gear(base: String) -> bool:
	return base in BASES


## Peça de equipamento (base de data/item_bases.json) no material dado; null se a base não tem modelo aqui.
static func gear(base: String, material: String) -> Node3D:
	if not has_gear(base):
		return null
	var p: Dictionary = PALETTE.get(material, PALETTE.iron)
	var main := _mat(p.main, p.metal, p.rough)
	if base in LEATHER and material in ["cloth", "wood"]:
		main = _mat(LEATHER_COLOR, 0.0, 0.75)
	var trim := _mat(p.trim, 0.0, 0.8)
	var dark := _mat(DARK, 0.0, 1.0)
	var root := Node3D.new()
	root.name = base
	match base:
		"hood":
			_part(root, _sphere(0.14), main, Vector3(0, 0.17, 0), Vector3.ZERO, Vector3(1.0, 1.25, 1.1))
			_part(root, _sphere(0.11), dark, Vector3(0, 0.15, 0.1), Vector3.ZERO, Vector3(0.85, 1.25, 0.5))
			_part(root, _cyl(0.0, 0.06, 0.16), main, Vector3(0, 0.3, -0.1), Vector3(-60, 0, 0))
			_part(root, _cyl(0.13, 0.2, 0.09), main, Vector3(0, 0.03, 0))
			_part(root, _cyl(0.205, 0.205, 0.02), trim, Vector3(0, -0.01, 0))
		"hunter_cap":
			_part(root, _sphere(0.13, true), main, Vector3(0, 0.03, 0), Vector3.ZERO, Vector3(1.0, 1.25, 1.12))
			_part(root, _cyl(0.16, 0.16, 0.015), main, Vector3(0, 0.03, 0.02), Vector3.ZERO, Vector3(1.0, 1.0, 1.15))
			_part(root, _cyl(0.132, 0.132, 0.03), trim, Vector3(0, 0.05, 0), Vector3.ZERO, Vector3(1.0, 1.0, 1.12))
			_part(root, _capsule(0.022, 0.26), _mat(Color("b03a2e"), 0.0, 0.7), Vector3(0.11, 0.14, -0.03), Vector3(0, 0, -50), Vector3(1, 1, 0.3))
		"ninja_mask":
			_part(root, _sphere(0.12), main, Vector3(0, 0.15, 0), Vector3.ZERO, Vector3(1.0, 1.2, 0.95))
			_part(root, _box(Vector3(0.18, 0.035, 0.06)), dark, Vector3(0, 0.18, 0.09))
			_part(root, _cyl(0.114, 0.114, 0.035), trim, Vector3(0, 0.215, 0), Vector3.ZERO, Vector3(1, 1, 0.96))
			_part(root, _box(Vector3(0.04, 0.14, 0.012)), trim, Vector3(-0.03, 0.14, -0.13), Vector3(20, 0, 15))
			_part(root, _box(Vector3(0.04, 0.14, 0.012)), trim, Vector3(0.03, 0.14, -0.13), Vector3(20, 0, -15))
		"tunic":
			_part(root, _cyl(0.15, 0.22, 0.5), main, Vector3(0, 0.25, 0), Vector3.ZERO, Vector3(1, 1, 0.55))
			for side in [-1.0, 1.0]:
				# Mangas caídas para fora, um pouco abertas.
				_part(root, _cyl(0.05, 0.068, 0.26), main, Vector3(0.2 * side, 0.36, 0), Vector3(0, 0, 28 * side))
				_part(root, _cyl(0.07, 0.07, 0.025), trim, Vector3(0.258 * side, 0.245, 0), Vector3(0, 0, 28 * side))
			_part(root, _cyl(0.06, 0.06, 0.012), dark, Vector3(0, 0.497, 0.01), Vector3.ZERO, Vector3(1, 1, 0.7))
			_part(root, _torus(0.055, 0.075), trim, Vector3(0, 0.495, 0.01), Vector3.ZERO, Vector3(1, 1, 0.7))
			_part(root, _cyl(0.177, 0.18, 0.045), trim, Vector3(0, 0.2, 0), Vector3.ZERO, Vector3(1, 1, 0.57))
			_part(root, _cyl(0.222, 0.222, 0.025), trim, Vector3(0, 0.01, 0), Vector3.ZERO, Vector3(1, 1, 0.56))
		"leather_vest":
			_part(root, _cyl(0.16, 0.18, 0.38), main, Vector3(0, 0.19, 0), Vector3.ZERO, Vector3(1, 1, 0.58))
			for side in [-1.0, 1.0]:
				_part(root, _box(Vector3(0.05, 0.03, 0.2)), main, Vector3(0.1 * side, 0.385, 0))
			_part(root, _box(Vector3(0.012, 0.3, 0.012)), dark, Vector3(0, 0.2, 0.1))
			for i in 4:
				_part(root, _box(Vector3(0.06, 0.01, 0.01)), trim, Vector3(0, 0.08 + i * 0.07, 0.102))
			_part(root, _cyl(0.172, 0.176, 0.04), trim, Vector3(0, 0.07, 0), Vector3.ZERO, Vector3(1, 1, 0.6))
			_part(root, _box(Vector3(0.04, 0.035, 0.012)), _mat(Color("c9a23c"), 0.9, 0.3), Vector3(0, 0.07, 0.105))
		"plate":
			_part(root, _cyl(0.17, 0.19, 0.4), main, Vector3(0, 0.22, 0), Vector3.ZERO, Vector3(1, 1, 0.62))
			_part(root, _box(Vector3(0.02, 0.36, 0.02)), main, Vector3(0, 0.22, 0.115))
			for side in [-1.0, 1.0]:
				_part(root, _sphere(0.1, true), main, Vector3(0.2 * side, 0.38, 0), Vector3(0, 0, -30 * side), Vector3(1, 0.8, 1))
				_part(root, _cyl(0.1, 0.1, 0.012), trim, Vector3(0.2 * side, 0.38, 0), Vector3(0, 0, -30 * side))
			_part(root, _torus(0.06, 0.09), main, Vector3(0, 0.43, 0), Vector3.ZERO, Vector3(1, 1.4, 0.75))
			for i in 2:
				_part(root, _cyl(0.195 + i * 0.012, 0.2 + i * 0.012, 0.06), main, Vector3(0, -0.01 - i * 0.055, 0), Vector3.ZERO, Vector3(1, 1, 0.64))
			_part(root, _cyl(0.193, 0.193, 0.02), trim, Vector3(0, 0.03, 0), Vector3.ZERO, Vector3(1, 1, 0.64))
		"gloves":
			for side in [-1.0, 1.0]:
				var glove := Node3D.new()
				glove.position = Vector3(0.075 * side, 0, 0)
				glove.rotation_degrees = Vector3(0, -15 * side, 8 * side)
				root.add_child(glove)
				_part(glove, _cyl(0.05, 0.042, 0.08), trim if base in LEATHER and material in ["cloth", "wood"] else main, Vector3(0, 0.04, 0))
				_part(glove, _box(Vector3(0.085, 0.1, 0.035)), main, Vector3(0, 0.13, 0))
				for f in 4:
					_part(glove, _capsule(0.011, 0.075), main, Vector3((f - 1.5) * 0.021, 0.21, 0))
				_part(glove, _capsule(0.012, 0.06), main, Vector3(-0.05 * side, 0.15, 0.01), Vector3(0, 0, 40 * side))
				_part(glove, _cyl(0.052, 0.052, 0.015), trim, Vector3(0, 0.085, 0))
		"boots":
			for side in [-1.0, 1.0]:
				var boot := Node3D.new()
				boot.position = Vector3(0.065 * side, 0, 0)
				boot.rotation_degrees = Vector3(0, -10 * side, 0)
				root.add_child(boot)
				_part(boot, _cyl(0.048, 0.052, 0.2), main, Vector3(0, 0.15, -0.02))
				_part(boot, _box(Vector3(0.09, 0.06, 0.15)), main, Vector3(0, 0.04, 0.03))
				_part(boot, _sphere(0.046), main, Vector3(0, 0.04, 0.1), Vector3.ZERO, Vector3(1, 0.7, 1.1))
				_part(boot, _box(Vector3(0.095, 0.018, 0.2)), dark, Vector3(0, 0.005, 0.04))
				_part(boot, _torus(0.046, 0.06), trim, Vector3(0, 0.25, -0.02))
		"ring":
			_part(root, _torus(0.028, 0.038), main, Vector3(0, 0.038, 0), Vector3(90, 0, 0))
			_part(root, _cyl(0.014, 0.012, 0.012), main, Vector3(0, 0.078, 0))
			var gem := _mat(Color("3c8fd8"), 0.2, 0.1)
			gem.emission_enabled = true
			gem.emission = Color("3c8fd8")
			gem.emission_energy_multiplier = 0.4
			_part(root, _sphere(0.014), gem, Vector3(0, 0.09, 0))
		"barding":
			# Manta (caparazão) com as abas caídas dos lados, a sela por cima e os estribos.
			_part(root, _box(Vector3(0.46, 0.02, 0.24)), main, Vector3(0, 0.3, 0))
			for side in [-1.0, 1.0]:
				_part(root, _box(Vector3(0.46, 0.24, 0.018)), main, Vector3(0, 0.19, 0.13 * side), Vector3(-12 * side, 0, 0))
				_part(root, _box(Vector3(0.465, 0.025, 0.022)), trim, Vector3(0, 0.075, 0.155 * side), Vector3(-12 * side, 0, 0))
				_part(root, _box(Vector3(0.012, 0.16, 0.012)), dark, Vector3(0, 0.22, 0.16 * side))
				_part(root, _torus(0.022, 0.032), _mat(Color("8a8f96"), 0.6, 0.4), Vector3(0, 0.12, 0.165 * side), Vector3(90, 0, 0))
			_part(root, _box(Vector3(0.24, 0.05, 0.17)), trim, Vector3(0, 0.335, 0))
			_part(root, _cyl(0.025, 0.035, 0.07), trim, Vector3(0.11, 0.38, 0))
			_part(root, _box(Vector3(0.035, 0.08, 0.17)), trim, Vector3(-0.12, 0.37, 0), Vector3(0, 0, 15))
	return root


## Pergaminho de refino enrolado: papel, pontas de madeira e fita na cor do material; o abençoado brilha.
static func scroll(material: String, blessed: bool) -> Node3D:
	var p: Dictionary = PALETTE.get(material, PALETTE.iron)
	var root := Node3D.new()
	root.name = "scroll"
	var paper := _mat(Color("e8dcb8"), 0.0, 0.9)
	if blessed:
		paper.emission_enabled = true
		paper.emission = Color(1.0, 0.85, 0.4)
		paper.emission_energy_multiplier = 0.35
	_part(root, _cyl(0.04, 0.04, 0.3), paper, Vector3(0, 0.05, 0), Vector3(0, 0, 90))
	for side in [-1.0, 1.0]:
		_part(root, _cyl(0.014, 0.014, 0.05), _mat(Color("5a3a20"), 0.0, 0.8), Vector3(0.17 * side, 0.05, 0), Vector3(0, 0, 90))
		_part(root, _sphere(0.02), _mat(Color("5a3a20"), 0.0, 0.8), Vector3(0.2 * side, 0.05, 0))
	_part(root, _cyl(0.043, 0.043, 0.04), _mat(p.main, p.metal, p.rough), Vector3(0, 0.05, 0), Vector3(0, 0, 90))
	_part(root, _cyl(0.022, 0.022, 0.012), _mat(Color("9b1c1c"), 0.0, 0.6), Vector3(0, 0.05, 0.045), Vector3(90, 0, 0))
	return root


# --- Peças --------------------------------------------------------------------------

static func _part(parent: Node3D, mesh: Mesh, material: Material, at: Vector3, rot := Vector3.ZERO, scale := Vector3.ONE) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = material
	mi.position = at
	mi.rotation_degrees = rot
	mi.scale = scale
	parent.add_child(mi)
	return mi


static func _mat(color: Color, metal: float, rough: float) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.metallic = metal
	m.roughness = rough
	return m


static func _sphere(radius: float, hemisphere := false) -> SphereMesh:
	var m := SphereMesh.new()
	m.radius = radius
	m.height = radius if hemisphere else radius * 2.0
	m.is_hemisphere = hemisphere
	m.radial_segments = 20
	m.rings = 10
	return m


static func _cyl(top: float, bottom: float, height: float) -> CylinderMesh:
	var m := CylinderMesh.new()
	m.top_radius = top
	m.bottom_radius = bottom
	m.height = height
	m.radial_segments = 20
	m.rings = 1
	return m


static func _capsule(radius: float, height: float) -> CapsuleMesh:
	var m := CapsuleMesh.new()
	m.radius = radius
	m.height = height
	m.radial_segments = 10
	m.rings = 4
	return m


static func _box(size: Vector3) -> BoxMesh:
	var m := BoxMesh.new()
	m.size = size
	return m


static func _torus(inner: float, outer: float) -> TorusMesh:
	var m := TorusMesh.new()
	m.inner_radius = inner
	m.outer_radius = outer
	m.rings = 20
	m.ring_segments = 8
	return m
