# Southern Mercenaries — GPL-3.0-or-later
class_name Brawl
extends Node3D
## Briga de rua em Tortuga: dois brigões frente a frente trocando socos e chutes. Quem
## ataca dá um jab, um direto ou um chute; o outro acusa o golpe (na cabeça ou no peito) e
## recua meio passo; depois os papéis se invertem. Depois de alguns golpes um deles cambaleia
## e a briga faz uma pausa e recomeça; ninguém cai no chão.
## Só cenário: cada PC anima o seu, sem rede (a rodinha em volta vem de "crowd" na área).

const GAP := 1.0
const EXCHANGE := 1.1
## Chance de o golpe ser um chute.
const KICK_CHANCE := 0.4
## Golpes sofridos até cambalear e a briga parar (sorteado nesta faixa a cada rodada).
const HITS_TO_FALL := Vector2i(3, 5)
## Pausa (s) depois do golpe decisivo, antes de a briga recomeçar.
const BREATHER := 3.0

enum State { FIGHT, BREATHER }

var fighters: Array[HeroModel] = []
## Papel de cada brigão.
var roles: Array[String] = []
var _timer := 0.6
var _attacker := 0
var _hit_in := -1.0
var _kick_hit := false
var _state := State.FIGHT
var _taken := [0, 0]
var _falls_at := 4
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.seed = hash(position)
	_falls_at = _rng.randi_range(HITS_TO_FALL.x, HITS_TO_FALL.y)


func _process(delta: float) -> void:
	if fighters.size() < 2:
		return
	match _state:
		State.FIGHT:
			_fight(delta)
		State.BREATHER:
			_timer -= delta
			if _timer <= 0.0:
				fighters[0].set_pose("idle")
				fighters[1].set_pose("idle")
				_recenter()
				_taken = [0, 0]
				_falls_at = _rng.randi_range(HITS_TO_FALL.x, HITS_TO_FALL.y)
				_state = State.FIGHT
				_timer = 0.4


func _fight(delta: float) -> void:
	if _hit_in > 0.0:
		_hit_in -= delta
		if _hit_in <= 0.0:
			_land_hit()
			if _state != State.FIGHT:
				return
	_timer -= delta
	if _timer > 0.0:
		return
	_timer = EXCHANGE + _rng.randf_range(-0.2, 0.4)
	# Às vezes o mesmo bate de novo; quase sempre trocam.
	if _rng.randf() < 0.7:
		_attacker = 1 - _attacker
	_kick_hit = _rng.randf() < KICK_CHANCE
	if _kick_hit:
		fighters[_attacker].play_action("kick")
	else:
		fighters[_attacker].play_action("punch_jab" if _rng.randf() < 0.5 else "punch_cross")
	_hit_in = 0.4 if _kick_hit else 0.3
	# Não deixa a briga andar para longe do lugar.
	var drift: float = fighters[0].get_parent().position.x + GAP / 2.0
	if absf(drift) > 0.6:
		for f in fighters:
			f.get_parent().position.x -= drift * 0.5


func _land_hit() -> void:
	var defender_index := 1 - _attacker
	var defender := fighters[defender_index]
	_taken[defender_index] += 1
	if _taken[defender_index] >= _falls_at:
		# Cambaleia (sem cair); o vencedor espera de braços cruzados e a briga recomeça.
		_state = State.BREATHER
		_timer = BREATHER
		defender.play_action("hit_head")
		fighters[_attacker].set_pose("fold_arms")
		return
	defender.play_action("hit" if _kick_hit or _rng.randf() < 0.5 else "hit_head")
	# O golpe empurra meio passo para trás (e o outro avança).
	var push := 0.25 if _attacker == 0 else -0.25
	for f in fighters:
		f.get_parent().position.x += push


## Volta os dois para as posições de partida, frente a frente.
func _recenter() -> void:
	for i in fighters.size():
		fighters[i].get_parent().position.x = (i - 0.5) * GAP
