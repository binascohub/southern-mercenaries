#!/bin/sh
# Réptil da Floresta (Rigged Textured Reptile, thecubber, CC BY / CC BY-SA): cria as animações nos controles do rig e exporta
# assets/models/monsters/reptile.glb (de frente para +Z; idle, walk, attack, hit e die).
# uso: tools/assets/build_reptile.sh <raptile_rig_fin.blend>   (a partir da raiz do projeto)
set -e
TMP=$(mktemp -d)
blender -b -P tools/assets/build_reptile_anims.py -- "$1" "$TMP/anims.blend"
blender -b -P tools/assets/build_monsters.py -- "$TMP/anims.blend" assets/models/monsters/reptile.glb lizardman 1.2 \
    "idle=idle,walk=walk,attack=attack,hit=hit,die=die" "mat=diff2k+color.tga.jpg" UVTex
rm -r "$TMP"
