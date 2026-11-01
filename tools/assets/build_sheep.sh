#!/bin/sh
# Ovelha da Fazenda (Sheep rigged, textured and animated, p0ss, CC-BY-SA 3.0): a "Sheep 2" do sheepies.blend vira
# assets/models/characters/sheep.glb (1,2 m de comprimento, de frente para +Z; idle, walk e eat).
# uso: tools/assets/build_sheep.sh <sheepies.blend>   (a partir da raiz do projeto)
set -e
blender -b -P tools/assets/build_monsters.py -- "$1" assets/models/characters/sheep.glb "Sheep 2" 1.2 \
    "idle=idle,walking=walk,eating=eat" "Material.001=untitled"
