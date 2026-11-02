#!/bin/sh
# Galo da Fazenda (Rooster (animated), CDmir e TinyWorlds, CC0): rooster.blend vira assets/models/characters/rooster.glb
# (0,5 m de comprimento, de frente para +Z; idle, walk e eat).
# uso: tools/assets/build_rooster.sh <rooster.blend>   (a partir da raiz do projeto)
set -e
blender -b -P tools/assets/build_monsters.py -- "$1" assets/models/characters/rooster.glb Rooster,Eyes 0.5 \
    "Idle1=idle,Walking=walk,Pecking.002=eat" "Body=UV,Head=UV,Comb=UV,Spatule=UV"
