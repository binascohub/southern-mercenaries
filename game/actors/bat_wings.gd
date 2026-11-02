# Southern Mercenaries — GPL-3.0-or-later
class_name BatWings
extends Node
## Batida de asas do morcego (bat.glb). A animação "fly" do arquivo não mexe nas asas (só 4 trilhas de 1 quadro, nenhuma nos ossos W_01.*),
## então as asas batem por código: o osso-raiz de cada asa (W_01.L e W_01.R) gira em volta do eixo do corpo (Z) e arrasta o resto da asa.
## Também vira o modelo: no arquivo a cabeça aponta para -Z, e o jogo anda para +Z (sem isso o morcego voava de ré).

const FLAP_HZ := 2.4
const AMPLITUDE := 0.75

var _skeleton: Skeleton3D
var _roots: Array[Dictionary] = []  # {bone, rest (pose local), parent_global (repouso), sign}
var _time := randf() * TAU


## Liga a batida às asas de `model` (a cena do bat.glb) e vira o modelo para a frente do jogo. `speed` multiplica a frequência.
static func attach(model: Node3D, speed := 1.0) -> BatWings:
	model.rotation.y = PI
	var wings := BatWings.new()
	wings.name = "BatWings"
	wings._skeleton = model.find_child("Skeleton3D", true, false) as Skeleton3D
	wings._time *= speed
	model.add_child(wings)
	wings._collect()
	return wings


func _collect() -> void:
	if _skeleton == null:
		set_process(false)
		return
	for side in [["W_01.L", -1.0], ["W_01.R", 1.0]]:
		var bone := _skeleton.find_bone(side[0])
		if bone < 0:
			continue
		var parent := _skeleton.get_bone_parent(bone)
		_roots.append({"bone": bone, "rest": _skeleton.get_bone_rest(bone).basis,
			"parent_global": _skeleton.get_bone_global_rest(parent).basis if parent >= 0 else Basis.IDENTITY, "sign": side[1]})
	set_process(not _roots.is_empty())


func _process(delta: float) -> void:
	_time += delta * FLAP_HZ * TAU
	var flap := sin(_time)
	for root: Dictionary in _roots:
		var swing := Basis(Vector3.BACK, float(root.sign) * -AMPLITUDE * flap)  # as duas sobem juntas (o lado esquerdo está em -X)
		var parent_basis: Basis = root.parent_global
		var local: Basis = parent_basis.inverse() * swing * parent_basis * (root.rest as Basis)
		_skeleton.set_bone_pose_rotation(int(root.bone), local.get_rotation_quaternion())
