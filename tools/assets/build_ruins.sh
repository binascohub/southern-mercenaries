#!/usr/bin/env bash
# Converte as peças do "3D Fantasy Ruins Pack" (Ron Kapaun / 3 Tier Digital Studios, CC0) em .glb para assets/models/maps/
# (Ruin_*), com o conversor de Collada tools/assets/dae_to_glb.py (o Blender 5 e o Godot 4.7 não leem esses .dae).
# uso: tools/assets/build_ruins.sh <pasta game/art/shapes/Ruins do pacote extraído> [saída]   (saída padrão: assets/models/maps)
set -euo pipefail
src="${1:?pasta Ruins do pacote}"
out="${2:-assets/models/maps}"
here="$(cd "$(dirname "$0")" && pwd)"
export RUIN_PARTS_DIR="$here/ruin_parts"   # caixas das partes de cada peça (usadas por build_maps.py para as colisões)
conv() {  # <pasta/arquivo.dae> <nome> <tamanho: h=altura | w=largura>
  blender -b -P "$here/dae_to_glb.py" -- "$src/$1" "$out/$2.glb" "$3" 2>&1 | grep -E '^(OK|Error|Traceback)' || true
}
conv RomanTypeCol_01/RomanTypeCol_01.dae Ruin_Column h=3.6
conv RuinPillar_01/RuinPillar_01.dae Ruin_Pillar h=2.8
conv PillarSegment_01/PillarSegment_01.DAE Ruin_PillarStub h=1.5
conv RuinArch_01/RuinArch_01.dae Ruin_Arch w=7.2
conv RuinWallSegment_01/RuinWallSegment_01.dae Ruin_Wall w=6.0
conv RuinWallSegment_02/RuinWallSegment_02.dae Ruin_WallStub h=1.8
conv RomanRail_01/RomanRail_01.dae Ruin_Rail w=5.0
conv FoundationRuin_01/foundationRuin_01.dae Ruin_Foundation w=6.0
conv SpeakingStones_01/SpeakingStones_01.dae Ruin_Stones w=8.5
conv TempleRuin_01/TempleRuin_01.DAE Ruin_Temple1 w=11.0
conv TempleRuin_02/TempleRuin_02.DAE Ruin_Temple2 w=11.0
