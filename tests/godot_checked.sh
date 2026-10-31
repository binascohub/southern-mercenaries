#!/usr/bin/env bash
# Southern Mercenaries — GPL-3.0-or-later
# Roda um comando do Godot e falha também se o motor registrar erro de script
# (um erro no meio de um teste nem sempre muda o código de saída).
# No GitHub Actions, o resumo (OK/FALHOU) e os erros viram anotações.
# Uso: tests/godot_checked.sh godot --headless --path . res://tests/rpg_tests.tscn
set -o pipefail
log="$(mktemp)"
"$@" 2>&1 | tee "$log"
status=$?
if grep -qE "SCRIPT ERROR|^ERROR:" "$log"; then
  if [ -n "${GITHUB_ACTIONS:-}" ]; then
    grep -E -A3 "SCRIPT ERROR|^ERROR:" "$log" | head -20 | sed "s/^/::error title=godot::/"
  fi
  echo "FALHOU: erros do motor"
  exit 1
fi
if [ -n "${GITHUB_ACTIONS:-}" ]; then
  grep -hE "^(OK|FALHOU)|^  ✗" "$log" | head -20 | sed "s/^/::notice title=godot::/"
fi
exit $status
