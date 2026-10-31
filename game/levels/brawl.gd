# Southern Mercenaries — GPL-3.0-or-later
class_name Brawl
extends Node3D
## Briga de rua em Tortuga: dois brigões frente a frente trocando socos. Quem
## ataca dá um jab ou um direto; o outro acusa o golpe (na cabeça ou no peito)
## e recua meio passo; depois os papéis se invertem. Só cenário: cada PC anima
## o seu, sem rede (a rodinha em volta vem de "crowd" na área).

const GAP := 1.0
const EXCHANGE := 1.1

var fighters: Array[HeroModel] = []
var _timer := 0.6
var _attacker := 0
var _hit_in := -1.0
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.seed = hash(position)


func _process(delta: float) -> void:
	if fighters.size() < 2:
		return
	if _hit_in > 0.0:
		_hit_in -= delta
		if _hit_in <= 0.0:
			var defender := fighters[1 - _attacker]
			defender.play_action("hit_head" if _rng.randf() < 0.5 else "hit")
			# O golpe empurra meio passo para trás (e o outro avança).
			var push := 0.25 if _attacker == 0 else -0.25
			for f in fighters:
				f.get_parent().position.x += push
	_timer -= delta
	if _timer > 0.0:
		return
	_timer = EXCHANGE + _rng.randf_range(-0.2, 0.4)
	# Às vezes o mesmo bate de novo; quase sempre trocam.
	if _rng.randf() < 0.7:
		_attacker = 1 - _attacker
	fighters[_attacker].play_action("punch_jab" if _rng.randf() < 0.5 else "punch_cross")
	_hit_in = 0.3
	# Não deixa a briga andar para longe do lugar.
	var drift: float = fighters[0].get_parent().position.x + GAP / 2.0
	if absf(drift) > 0.6:
		for f in fighters:
			f.get_parent().position.x -= drift * 0.5
