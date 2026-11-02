# Southern Mercenaries — GPL-3.0-or-later
class_name Flyer
extends Node3D
## Bicho voando em círculos de enfeite (morcegos do esgoto): gira em volta de um ponto, com o raio e a altura
## variando de leve. Só cenário: cada PC anima o seu, sem rede e sem colisão.

var center := Vector3.ZERO
var radius := 2.0
var speed := 2.5
var height := 2.6
## Meio sentido de giro (1 ou -1) e fase inicial (rad).
var direction := 1.0
var phase := 0.0

var _t := 0.0


func _process(delta: float) -> void:
	_t += delta
	phase += direction * speed / radius * delta
	var r := radius * (1.0 + 0.2 * sin(_t * 0.7))
	position = center + Vector3(cos(phase) * r, height + sin(_t * 1.9) * 0.25, sin(phase) * r)
	var tangent := Vector3(-sin(phase), 0.0, cos(phase)) * direction
	rotation.y = atan2(tangent.x, tangent.z)
	rotation.z = -0.3 * direction  # inclina para dentro da curva
