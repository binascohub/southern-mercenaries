#!/bin/sh
# Golens da Floresta (Fire/Ice/Stone Golem, umask007, CC BY 3.0 / CC BY-SA 3.0; texturas base de yughues/Nobiax, CC0): o golem.blend tem uma
# malha só e as três texturas assadas; cada variante troca a textura (fireBaked = a textura da variante) e vira assets/models/monsters/golem_<x>.glb
# (2,3 m de largura, de frente para +Z; idle, walk, attack, hit (flinch) e die).
# uso: tools/assets/build_golems.sh <golem.blend>   (a partir da raiz do projeto)
set -e
for v in fire:fire_diffuse ice:iceDiffuse stone:stoneBaked; do
    blender -b -P tools/assets/build_monsters.py -- "$1" "assets/models/monsters/golem_${v%%:*}.glb" stone 2.3 \
        "idle=idle,walk=walk,attack=attack,die=die,flinch=hit" "fireBaked=${v##*:}" UVMap
done
