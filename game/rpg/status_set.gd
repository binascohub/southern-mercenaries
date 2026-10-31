# Southern Mercenaries — GPL-3.0-or-later
class_name StatusSet
extends RefCounted
## Estados elementais de um alvo (02-0-elementos.md, seção 6): cada estado tem
## o tempo que falta; reaplicar renova a duração sem acumular. "Queimando"
## causa dano a cada segundo (o valor vem do golpe que aplicou).

## id -> {"time": segundos restantes, "dps": dano por segundo (só burning)}
var states := {}
var _burn_clock := 0.0


func apply(id: String, duration: float, dps := 0.0) -> void:
	var entry: Dictionary = states.get(id, {"time": 0.0, "dps": 0.0})
	entry.time = maxf(duration, 0.0)
	entry.dps = maxf(dps, 0.0) if dps > 0.0 else float(entry.dps)
	if not states.has(id) and id == "burning":
		_burn_clock = 0.0
	states[id] = entry


func has(id: String) -> bool:
	return states.has(id)


func remove(id: String) -> void:
	states.erase(id)


func clear() -> void:
	states.clear()


func dps(id: String) -> float:
	return float(states.get(id, {}).get("dps", 0.0))


## Valor guardado com o estado (o mesmo campo do dano por segundo): ex. o bônus
## de dano do Marcar Alvo.
func value(id: String) -> float:
	return dps(id)


## Passa o tempo. Retorna o dano de "queimando" deste passo (um tique por segundo).
func tick(delta: float) -> float:
	var damage := 0.0
	if states.has("burning"):
		_burn_clock += delta
		while _burn_clock >= 1.0:
			_burn_clock -= 1.0
			damage += dps("burning")
	for id: String in states.keys():
		states[id].time -= delta
		if states[id].time <= 0.0:
			states.erase(id)
	return damage


## Não se move nem ataca (congelado, derrubado, atordoado).
func can_act() -> bool:
	for id: String in states:
		if Elements.state_data(id).get("disables", false):
			return false
	return true


## Multiplicador de velocidade: as lentidões não somam, vale a maior.
func move_mult() -> float:
	var slow := 0.0
	for id: String in states:
		if Elements.state_data(id).get("root", false):
			return 0.0  # preso (Armadilha de Espinhos): não anda, mas ataca
		slow = maxf(slow, float(Elements.state_data(id).get("slow", 0.0)))
	return 1.0 - slow


func miss_chance() -> float:
	var chance := 0.0
	for id: String in states:
		chance = maxf(chance, float(Elements.state_data(id).get("miss_chance", 0.0)))
	return chance


## Bits dos estados ativos (sincronizado para o visual nos outros PCs).
func mask() -> int:
	var bits := 0
	var ids: Array = GameData.elements.states.keys()
	for id: String in states:
		var i := ids.find(id)
		if i >= 0:
			bits |= 1 << i
	return bits


static func ids_from_mask(bits: int) -> Array[String]:
	var found: Array[String] = []
	var ids: Array = GameData.elements.states.keys()
	for i in ids.size():
		if bits & (1 << i):
			found.append(ids[i])
	return found
