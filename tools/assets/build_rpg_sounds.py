#!/usr/bin/env python3
"""Converte o "RPG Sound Pack" (artisticdude, CC0, opengameart.org/content/rpg-sound-pack) em OGG curtos em assets/audio/sfx/.
Uso: python3 tools/assets/build_rpg_sounds.py <pasta "RPG Sound Pack">
Nomes com sufixo _1.._N são variantes: Sfx.play sorteia uma delas."""
import subprocess, sys
from pathlib import Path

pack = Path(sys.argv[1])
out = Path(__file__).resolve().parents[2] / "assets/audio/sfx"
MAX_MONSTER = 1.4

SFX = {  # nome: (arquivos, duração máxima, ganho dB)
	"swing": (["battle/swing", "battle/swing2"], 0.5, 0),
	"swing_heavy": (["battle/swing3"], 0.5, 2),
	"coin": (["inventory/coin", "inventory/coin2", "inventory/coin3"], 1.0, 0),
	"drink": (["inventory/bubble", "inventory/bubble2", "inventory/bubble3"], 1.0, 0),
	"pickup": (["inventory/cloth", "inventory/beads"], 0.8, 0),
	"equip": (["inventory/armor-light", "inventory/chainmail1", "inventory/chainmail2", "inventory/cloth-heavy"], 1.0, 0),
	"block": (["inventory/metal-small1", "inventory/metal-small2", "inventory/metal-small3", "inventory/metal-ringing"], 0.9, 0),
	"ui_click": (["interface/interface1", "interface/interface2", "interface/interface3"], 0.6, -4),
	"ui_open": (["interface/interface4", "interface/interface5"], 0.6, -4),
	"door": (["world/door"], 1.2, 0),
	"bottle": (["inventory/bottle"], 0.8, 0),
	"wood": (["inventory/wood-small"], 0.6, 0),
	"burp": (["misc/burp"], 1.2, 0),
	"unsheathe": (["battle/sword-unsheathe", "battle/sword-unsheathe2", "battle/sword-unsheathe3"], 1.0, 0),
	"spell_magic": (["battle/magic1"], 1.0, 0),
	"spell_long": (["battle/spell"], 1.6, -1),
}
MONSTERS = {  # família: arquivos
	"slime": [f"NPC/slime/slime{i}" for i in (1, 2, 3, 4)],
	"beetle": ["NPC/beetle/bite-small", "NPC/beetle/bite-small2", "NPC/beetle/bite-small3"],
	"shade": [f"NPC/shade/shade{i}" for i in (1, 2, 3, 4)],
	"ogre": [f"NPC/ogre/ogre{i}" for i in (1, 2, 3)],
	"giant": [f"NPC/giant/giant{i}" for i in (1, 2, 3)],
	"beast": [f"NPC/gutteral beast/mnstr{i}" for i in (1, 2, 3, 4)],
	"wolfman": ["NPC/misc/wolfman"],
}


def convert(src: Path, dst: Path, dur: float, gain: float) -> None:
	fade = min(0.12, dur / 4)
	filt = f"atrim=0:{dur},afade=t=out:st={max(0.0, dur - fade)}:d={fade},volume={gain}dB"
	subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", "44100", "-af", filt,
		"-c:a", "libvorbis", "-q:a", "4", str(dst)], check=True)


for name, (files, dur, gain) in SFX.items():
	for i, f in enumerate(files, 1):
		convert(pack / (f + ".wav"), out / (f"{name}_{i}.ogg" if len(files) > 1 else f"{name}.ogg"), dur, gain)
for fam, files in MONSTERS.items():
	for i, f in enumerate(files, 1):
		convert(pack / (f + ".wav"), out / f"m_{fam}_{i}.ogg", MAX_MONSTER, 0)
print("ok")
