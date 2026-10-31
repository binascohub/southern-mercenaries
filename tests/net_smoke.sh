#!/usr/bin/env bash
# Southern Mercenaries — GPL-3.0-or-later
# Testes de rede em tempo real, com processos separados via UDP local:
#   1. host + cliente jogam a arena juntos até a vitória;
#   2. o host recusa um cliente com versão diferente;
#   3. um cliente cai (processo morto) e outro do mesmo PC reentra a tempo e
#      assume o mesmo herói (07-rede.md, seção 9).
# Uso: tests/net_smoke.sh [godot] [pasta_de_logs]
set -u
GODOT="${1:-godot}"
LOGS="${2:-$(mktemp -d)}"
cd "$(dirname "$0")/.."
run() { "$GODOT" --headless --path . res://tests/smoke_arena.tscn -- "$@"; }
# Em segundo plano sem subshell, para o PID ser o do próprio Godot.
start() { local log="$1"; shift; "$GODOT" --headless --path . res://tests/smoke_arena.tscn -- "$@" > "$log" 2>&1 & }
show() {
  grep -hE "^(OK|FALHOU)|SCRIPT ERROR|ERROR:" "$1" | sed "s/^/$2: /"
  # No GitHub Actions as falhas também viram anotações, legíveis sem baixar o log.
  if [ -n "${GITHUB_ACTIONS:-}" ]; then
    grep -hE -A3 "^FALHOU|SCRIPT ERROR|^ERROR:" "$1" | head -20 | sed "s/^/::error title=net_smoke ($2)::/"
  fi
}
FAIL=0

start "$LOGS/host.log" host 2
HOST_PID=$!
sleep 2
run join 127.0.0.1 > "$LOGS/client.log" 2>&1 || FAIL=1
wait $HOST_PID || FAIL=1
show "$LOGS/host.log" "host  "
show "$LOGS/client.log" "client"

start "$LOGS/host2.log" host 2
HOST_PID=$!
sleep 2
run join 127.0.0.1 0.0.0-outra > "$LOGS/version.log" 2>&1 || FAIL=1
kill $HOST_PID 2>/dev/null
wait $HOST_PID 2>/dev/null
sleep 1
show "$LOGS/version.log" "versão"

start "$LOGS/host3.log" host 2 resume
HOST_PID=$!
sleep 2
start "$LOGS/dropped.log" join 127.0.0.1
DROP_PID=$!
sleep 6
kill -9 $DROP_PID 2>/dev/null
sleep 1
run join 127.0.0.1 > "$LOGS/rejoin.log" 2>&1 || FAIL=1
wait $HOST_PID || FAIL=1
show "$LOGS/host3.log" "queda "
show "$LOGS/rejoin.log" "volta "

# Nenhum erro do motor em nenhum processo (o cliente morto de propósito fica de fora).
for log in host client host2 version host3 rejoin; do
  if grep -qE "SCRIPT ERROR|^ERROR:" "$LOGS/$log.log"; then
    echo "FALHOU: erros em $log.log"
    FAIL=1
  fi
done

exit $FAIL
