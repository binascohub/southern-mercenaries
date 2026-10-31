# Southern Mercenaries — GPL-3.0-or-later
class_name Wanderer
extends Node3D
## Gente andando pela rua de Tortuga (04-tortuga-e-missoes.md, seção 1): vai e
## volta entre dois pontos, parando um pouco em cada ponta; o bêbado cambaleia
## (anda devagar e balança). Só cenário: cada PC anima o seu, sem rede.

var from := Vector3.ZERO
var to := Vector3.ZERO
var speed := 1.2
## 0 = anda reto; mais = cambaleia de lado.
var sway := 0.0
var model: HeroModel

var _forward := true
var _pause := 0.0
var _time := 0.0


func _process(delta: float) -> void:
	if model == null:
		return
	_time += delta
	if _pause > 0.0:
		_pause -= delta
		if _pause <= 0.0:
			model.set_pose("walk")
		return
	var target := to if _forward else from
	var offset := target - position
	offset.y = 0.0
	if offset.length() < 0.2:
		_forward = not _forward
		_pause = randf_range(1.5, 4.0)
		model.set_pose("idle" if sway == 0.0 else "talk")
		return
	var dir := offset.normalized()
	var side := Vector3(-dir.z, 0, dir.x) * sin(_time * 2.3) * sway
	position += (dir * speed + side) * delta
	rotation.y = atan2(dir.x + side.x * 0.5, dir.z + side.z * 0.5)
