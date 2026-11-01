#!/bin/sh
# Porco e cavalo da Fazenda (Farm Animals, Quaternius, CC0): Pig.blend e Horse.blend viram
# assets/models/characters/pig.glb (1,2 m) e farm_horse.glb (2,2 m), de frente para +Z, com idle e walk.
# uso: tools/assets/build_farm_animals.sh <pasta Blends do pacote extraído>   (a partir da raiz do projeto)
set -e
blender -b -P tools/assets/build_monsters.py -- "$1/Pig.blend" assets/models/characters/pig.glb Pig 1.2 "Idle=idle,Walk=walk" ""
blender -b -P tools/assets/build_monsters.py -- "$1/Horse.blend" assets/models/characters/farm_horse.glb Horse 2.2 "Idle=idle,Walk=walk" ""
