# Southern Mercenaries — GPL-3.0-or-later
class_name Brawl
extends Node3D
## Briga de rua em Tortuga: dois brigões frente a frente trocando socos e chutes. Quem
## ataca dá um jab, um direto ou um chute; o outro acusa o golpe (na cabeça ou no peito) e
## recua meio passo; depois os papéis se invertem. Depois de alguns golpes um deles cai: o
## bêbado fica uns 30 s no chão (os outros, uns 8 s) e levanta devagar; aí a briga recomeça.
## Só cenário: cada PC anima o seu, sem rede (a rodinha em volta vem de "crowd" na área).

const GAP := 1.0
const EXCHANGE := 1.1
## Chance de o golpe ser um chute.
const KICK_CHANCE := 0.4
## Golpes sofridos até cair (sorteado nesta faixa a cada rodada).
const HITS_TO_FALL := Vector2i(3, 5)
## Tempo caído no chão (s), por papel; o resto usa "default".
const DOWN_TIME := {"drunk": 30.0, "default": 8.0}
## Pausa (s) depois de levantar, antes de a briga recomeçar.
const BREATHER := 1.5
## Velocidade de levantar (1 = a queda ao contrário, em tempo normal): devagar.
const GET_UP_SPEED := 0.3

enum State { FIGHT, DOWN, RISING, BREATHER }

var fighters: Array[HeroModel] = []
## Papel de cada brigão (define quanto tempo fica no chão).
var roles: Array[String] = []
var _timer := 0.6
var _attacker := 0
var _hit_in := -1.0
var _kick_hit := false
var _state := State.FIGHT
var _loser := 0
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
		State.DOWN:
			_timer -= delta
			if _timer <= 0.0:
				_state = State.RISING
				_timer = fighters[_loser].get_up(GET_UP_SPEED)
		State.RISING:
			_timer -= delta
			if _timer <= 0.0:
				_state = State.BREATHER
				_timer = BREATHER
				fighters[1 - _loser].set_pose("idle")
		State.BREATHER:
			_timer -= delta
			if _timer <= 0.0:
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
		# Cai e fica no chão; o vencedor espera de braços cruzados.
		_state = State.DOWN
		_loser = defender_index
		var role := roles[defender_index] if defender_index < roles.size() else "default"
		_timer = float(DOWN_TIME.get(role, DOWN_TIME.default)) + _rng.randf_range(-2.0, 2.0)
		defender.lie_down()
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
