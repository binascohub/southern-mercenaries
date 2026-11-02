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
## HeroModel ou NpcModel (os dois têm set_pose).
var model: Node3D
## Mercador ambulante: a posição sai do relógio (igual em todos os PCs, pois a loja é decidida no
## servidor), sem sorteio: anda de um ponto ao outro e para SYNC_PAUSE s em cada ponta.
var synced := false
## Objeto de interação (prop da área) que acompanha este NPC: a posição dele é atualizada a cada quadro.
var tracked := {}
const SYNC_PAUSE := 3.0

var _forward := true
var _was_moving := true
var _pause := 0.0
var _time := 0.0


func _process(delta: float) -> void:
	if synced:
		_process_synced()
		return
	if model == null:
		return
	_time += delta
	if _pause > 0.0:
		_pause -= delta
		if _pause <= 0.0:
			model.call("set_pose", "walk")
		return
	var target := to if _forward else from
	var offset := target - position
	offset.y = 0.0
	if offset.length() < 0.2:
		_forward = not _forward
		_pause = randf_range(1.5, 4.0)
		model.call("set_pose", "idle" if sway == 0.0 else "talk")
		return
	var dir := offset.normalized()
	var side := Vector3(-dir.z, 0, dir.x) * sin(_time * 2.3) * sway
	position += (dir * speed + side) * delta
	rotation.y = atan2(dir.x + side.x * 0.5, dir.z + side.z * 0.5)


func _process_synced() -> void:
	var span := to - from
	span.y = 0.0
	var leg := span.length() / speed
	if leg <= 0.0:
		return
	var t := fposmod(Time.get_unix_time_from_system(), 2.0 * (leg + SYNC_PAUSE))
	var forward := t < leg + SYNC_PAUSE
	var u := t if forward else t - (leg + SYNC_PAUSE)
	var a := from if forward else to
	var b := to if forward else from
	var moving := u < leg
	position = a.lerp(b, clampf(u / leg, 0.0, 1.0))
	if moving:
		var dir := (b - a).normalized()
		rotation.y = atan2(dir.x, dir.z)
	if moving != _was_moving:
		_was_moving = moving
		if model:
			model.call("set_pose", "walk" if moving else "talk")
	if not tracked.is_empty():
		tracked.position[0] = position.x
		tracked.position[1] = position.z
