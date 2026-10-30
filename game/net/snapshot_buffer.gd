# Southern Mercenaries — GPL-3.0-or-later
class_name SnapshotBuffer
extends RefCounted
## Interpolação nos clientes (07-rede.md, seção 5): guarda as posições que
## chegam do servidor (~20 Hz) e devolve a posição de `delay` segundos atrás,
## para o movimento dos outros ficar liso mesmo com poucos pacotes.

const MAX_SNAPSHOTS := 32

var delay := 0.1
var _times: PackedFloat64Array = []
var _values: Array[Vector3] = []


static func now() -> float:
	return Time.get_ticks_usec() / 1_000_000.0


func push(value: Vector3, time := now()) -> void:
	_times.append(time)
	_values.append(value)
	if _times.size() > MAX_SNAPSHOTS:
		_times.remove_at(0)
		_values.remove_at(0)


func sample(time := now()) -> Vector3:
	if _values.is_empty():
		return Vector3.ZERO
	var t := time - delay
	if t <= _times[0]:
		return _values[0]
	for i in range(_times.size() - 1, 0, -1):
		if _times[i - 1] <= t:
			if t >= _times[i]:
				return _values[i]
			var w := (t - _times[i - 1]) / (_times[i] - _times[i - 1])
			return _values[i - 1].lerp(_values[i], w)
	return _values[-1]
