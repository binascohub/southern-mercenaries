#!/bin/sh
# Cervos da Floresta (CDmir e TinyWorlds, CC0): o macho (Old Deer Male, deer1.blend) e a fêmea (Deer Female, doe.blend)
# viram assets/models/monsters/deer_buck.glb e deer_doe.glb (1,6 m de comprimento, de frente para +Z; idle, walk e die).
# uso: tools/assets/build_deer.sh <deer1.blend> <doe.blend>   (a partir da raiz do projeto)
set -e
blender -b -P tools/assets/build_monsters.py -- "$1" assets/models/monsters/deer_buck.glb Body,Head,Horns,Eyes 1.6 \
    "Idle.000=idle,Run=walk,Die.000=die" "Head=head,Body=body,Antlers=deer-antlers.png" UVMap
blender -b -P tools/assets/build_monsters.py -- "$2" assets/models/monsters/deer_doe.glb Body,Head,Eyes 1.6 \
    "Idle.000=idle,Run=walk,Die.000=die" "head=doe-head,body=doe-body" UVMap
