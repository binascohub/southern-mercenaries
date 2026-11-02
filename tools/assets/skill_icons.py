"""Ícones das habilidades (128 px, assets/ui/icons/skills/<id>.png) feitos das silhuetas do game-icons.net (CC BY 3.0: lorc, delapouite, skoll e outros; github.com/game-icons/icons):
um quadrado de cantos arredondados com degradê na cor do elemento da habilidade (Fogo laranja, Água azul, Ar roxo, Terra verde; as da classe, dourado/aço) e a silhueta clara por cima,
com contorno escuro e um brilho. Uma silhueta por habilidade (SKILLS abaixo); a que faltar cai no ícone padrão do tipo (FALLBACK). Os ícones aparecem na barra de atalhos, no menu de habilidades e no dock.
1) baixar os .svg usados (nomes em SKILLS) de https://github.com/game-icons/icons para uma pasta; 2) SVGDIR=<pasta> MASKDIR=<pasta de máscaras> godot --headless --path . --script tools/assets/glyph_masks.gd;
3) python3 -I tools/assets/skill_icons.py <pasta das máscaras> <pasta de saída (assets/ui/icons/skills)>"""
import sys, os, json
from PIL import Image, ImageFilter, ImageChops, ImageDraw

masks, out = sys.argv[1:3]
os.makedirs(out, exist_ok=True)
ELEMENT = {"fire": ("#e8742a", "#5a1d08"), "water": ("#3f8fe6", "#0f2e5c"), "air": ("#a98bf0", "#2f2160"), "earth": ("#7fae45", "#25380f"), "": ("#d7b25a", "#4a3410")}
SKILLS = {
    # Mago
    "sharp_mind": "brain", "teleport": "teleport", "mana_shield": "magic-shield", "elemental_mastery": "spell-book",
    "fire_bolt": "fire-spell-cast", "fireball": "fireball", "flame_blessing": "flame-spin", "fire_lance": "flame-claws", "fire_wall": "fire-ring", "meteor": "meteor-impact",
    "water_bolt": "water-drop", "frost_nova": "snowflake-2", "healing_rain": "raining", "ice_lance": "ice-spear", "tidal_wave": "wave-crest", "blizzard": "snowflake-1",
    "wind_blade": "whirlwind", "chain_lightning": "lightning-arc", "tailwind": "feather", "lightning_bolt": "lightning-tree", "tornado": "tornado", "storm": "lightning-storm",
    "stone_bolt": "rock", "earth_spikes": "earth-spit", "stone_skin": "cracked-shield", "boulder": "stone-block", "quake": "quake-stomp", "earthquake": "earth-crack",
    # Arqueiro
    "precise_shot": "bullseye", "back_leap": "sprint", "eagle_eye": "eye-target", "spike_trap": "mantrap", "arrow_fan": "arrow-cluster", "piercing_arrow": "plain-arrow", "mark_target": "target-arrows",
    "hunters_campfire": "campfire", "flaming_arrow": "flaming-arrow", "fire_rain": "arrow-flights",
    "spring_arrow": "water-drop", "frost_arrow": "ice-bolt", "hail_storm": "snowflake-1",
    "hunters_wind": "whirlwind", "thunder_arrow": "lightning-arc", "storm_volley": "split-arrows",
    "bulwark_arrow": "shield", "boulder_arrow": "arrowhead", "stone_rain": "stone-block",
    # Ninja
    "twin_slash": "crossed-swords", "shadow_step": "dodge", "backstab": "backstab", "smoke_bomb": "smoke-bomb", "iron_body": "armor-upgrade", "evasion": "sprint", "blink_strike": "daggers",
    "fire_seal": "fire-ring", "flame_strike": "flame-claws", "flame_thousand_cuts": "shuriken", "mist_seal": "waves", "ice_fang": "ice-bolt", "rain_thousand_cuts": "ninja-star",
    "wind_seal": "whirlwind", "lightning_flash": "lightning-shield", "storm_thousand_cuts": "lightning-branches", "stone_seal": "stone-wall", "stone_fang": "spikeball", "quake_thousand_cuts": "spiked-wall",
    # Invocador
    "call_companion": "paw-print", "flock": "arrow-wings", "bond": "heart-wings", "scatter_escape": "feathered-wing", "guardian_bear": "gorilla", "stampede": "charging-bull", "animal_rescue": "healing-shield",
    "den_warmth": "fox-head", "salamander_bite": "claw-slashes", "fire_stampede": "horseshoe",
    "otter_spring": "fountain", "narwhal_charge": "whale-tail", "whale_song": "sperm-whale",
    "falcon_wings": "eagle-emblem", "eagle_dive": "eagle-head", "wing_storm": "raven",
    "turtle_shell": "turtle", "rhino_charge": "rhinoceros-horn", "mammoth_stomp": "mammoth",
    # Cavaleiro
    "lance_thrust": "spear-hook", "charge": "horse-head", "heavy_armor": "armor-upgrade", "challenge": "knight-banner", "trample": "boot-stomp", "lance_sweep": "broadsword", "unstoppable": "shield-bash",
    "fire_banner": "tattered-banner", "blazing_lance": "flame-claws", "inferno_charge": "flame-tunnel",
    "tide_banner": "vertical-banner", "frost_lance": "ice-spear", "tidal_charge": "wave-crest",
    "gale_banner": "pirate-flag", "thunder_lance": "lightning-saber", "storm_charge": "lightning-helix",
    "stone_banner": "knight-banner", "earthbreaker_lance": "spears", "avalanche_charge": "earth-crack",
}
FALLBACK = {"projectile": "arrow-cluster", "area": "whirlwind", "melee": "crossed-swords", "buff": "heart-plus", "shield": "shield", "summon": "paw-print"}


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def icon(glyph_name, element):
    light, dark = (rgb(c) for c in ELEMENT[element])
    plate = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    px = plate.load()
    for y in range(128):
        t = y / 127
        c = tuple(int(dark[i] * (0.55 + 0.9 * t) * 0.9 + light[i] * 0.15 * (1 - t)) for i in range(3))
        for x in range(128):
            px[x, y] = tuple(min(255, v) for v in c) + (255,)
    corner = Image.new("L", (128, 128), 0)
    ImageDraw.Draw(corner).rounded_rectangle((3, 3, 124, 124), radius=22, fill=255)
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    img.paste(plate, (0, 0), corner)
    border = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    ImageDraw.Draw(border).rounded_rectangle((3, 3, 124, 124), radius=22, outline=light + (255,), width=4)
    img = Image.alpha_composite(img, border)
    m = Image.open(os.path.join(masks, glyph_name + ".png")).convert("RGBA").split()[3]
    m = m.crop(m.getbbox())
    k = 84 / max(m.size)
    m = m.resize((max(1, round(m.width * k)), max(1, round(m.height * k))), Image.LANCZOS)
    a = Image.new("L", (128, 128), 0)
    a.paste(m, ((128 - m.width) // 2, (128 - m.height) // 2))
    outline = a.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(0.6))
    fill = Image.new("RGBA", (128, 128))
    fp = fill.load()
    top = tuple(min(255, int(v * 0.35 + 255 * 0.65)) for v in light)
    for y in range(128):
        t = y / 127
        c = tuple(int(top[i] * (1.0 - 0.28 * t)) for i in range(3))
        for x in range(128):
            fp[x, y] = c + (255,)
    img.paste(Image.new("RGBA", (128, 128), (14, 8, 4, 255)), (0, 0), outline)
    img.paste(fill, (0, 0), a)
    return img


def main():
    skills = json.load(open("data/skills.json", encoding="utf-8"))
    element_of = {}
    for cls in skills["classes"].values():
        for el, ids in cls["element"].items():
            for sid in ids:
                element_of[sid] = el
    missing = []
    for sid, d in skills["skills"].items():
        name = SKILLS.get(sid) or FALLBACK.get(d.get("effect", ""), "paw-print")
        if not os.path.exists(os.path.join(masks, name + ".png")):
            missing.append((sid, name))
            name = "paw-print"
        icon(name, element_of.get(sid, "")).save(os.path.join(out, sid + ".png"))
    print("ícones:", len(skills["skills"]), "sem silhueta:", missing)


main()
