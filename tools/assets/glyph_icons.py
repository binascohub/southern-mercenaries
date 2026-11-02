"""Ícones de inventário (128 px) feitos das silhuetas do game-icons.net (CC BY 3.0: lorc, delapouite): pergaminhos de refino, valiosos e as peças de
equipamento sem modelo 3D (capuz, túnica, luvas, botas, anel, boné, colete, máscara, elmo, peitoral, barda; cajado e adaga dos ranks C a S).
Cada silhueta ganha contorno escuro, degradê de cor (a do material/rank ou a do item) e um brilho em cima, para casar com os ícones pintados dos outros.
1) baixar os .svg de https://github.com/game-icons/icons (pasta/autor/nome.svg) para uma pasta; 2) glyph_masks.gd gera as máscaras;
uso: python3 -I tools/assets/glyph_icons.py <pasta das máscaras> <pasta de saída (assets/ui/icons)>"""
import sys, os
from PIL import Image, ImageFilter, ImageChops, ImageDraw

masks, out = sys.argv[1:3]
OUTLINE = (26, 18, 8)
MATERIAL = {"iron": "#7d8085", "steel": "#b8bfc6", "copper": "#c06a3c", "silver": "#eef2f5", "gold": "#e3b23c"}
RANK = {"D": "#9a7b55", "C": "#b8bfc6", "B": "#c06a3c", "A": "#eef2f5", "S": "#e3b23c"}


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def glyph(name, color, glow=None):
    m = Image.open(os.path.join(masks, name + ".png")).convert("RGBA").split()[3]
    box = m.getbbox()
    m = m.crop(box)
    k = 104 / max(m.size)
    m = m.resize((max(1, round(m.width * k)), max(1, round(m.height * k))), Image.LANCZOS)
    a = Image.new("L", (128, 128), 0)
    a.paste(m, ((128 - m.width) // 2, (128 - m.height) // 2))
    outline = a.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(0.6))
    base = rgb(color)
    fill = Image.new("RGBA", (128, 128))
    px = fill.load()
    for y in range(128):
        t = y / 127
        f = 1.25 - 0.55 * t  # mais claro em cima, mais escuro embaixo
        c = tuple(max(0, min(255, int(v * f))) for v in base)
        for x in range(128):
            px[x, y] = c + (255,)
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    if glow:  # abençoado: aura dourada atrás
        g = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        d = ImageDraw.Draw(g)
        d.ellipse((6, 6, 122, 122), fill=rgb(glow) + (120,))
        img = Image.alpha_composite(img, g.filter(ImageFilter.GaussianBlur(10)))
    img.paste(Image.new("RGBA", (128, 128), OUTLINE + (255,)), (0, 0), outline)
    img.paste(fill, (0, 0), a)
    edge = ImageChops.subtract(a, a.filter(ImageFilter.MinFilter(3)))  # fio claro na borda de cima
    hl = Image.new("RGBA", (128, 128), (255, 255, 255, 70))
    img.paste(hl, (0, 0), ImageChops.multiply(edge, a))
    return img


def save(img, fname):
    path = os.path.join(out, fname + ".png")
    img.save(path)
    print("icone", fname)


VALUABLES = {
    "old_coins": ("coins", "#d9a93a"), "war_coins": ("coins-pile", "#c9a24a"), "silver_goblet": ("jeweled-chalice", "#dfe5ea"),
    "rough_gem": ("gems", "#4fb8c9"), "war_medal": ("medal", "#c8933a"), "royal_seal_ring": ("ring", "#e3b23c"),
    "crown_jewel": ("crown", "#e8c04a"), "cursed_skull": ("daemon-skull", "#9a62c4"), "bone_dagger": ("bone-knife", "#e8dfc8"),
    "key_spades": ("skeleton-key", "#9aa3ab"), "key_hearts": ("heart-key", "#d4504c"), "adams_rib": ("ribcage", "#e8dfc8"),
}
for item, (g, c) in VALUABLES.items():
    save(glyph(g, c), item)
for mat, c in MATERIAL.items():
    for blessed in (False, True):
        for kind, g in (("weapon", "scroll-unfurled"), ("armor", "tied-scroll")):
            save(glyph(g, c, "#ffe08a" if blessed else None), "%sscroll_refine_%s_%s" % ("blessed_" if blessed else "", kind, mat))
GEAR = {"hood": "hood", "tunic": "robe", "gloves": "gloves", "boots": "boots", "ring": "ring", "hunter_cap": "robin-hood-hat",
        "leather_vest": "leather-vest", "ninja_mask": "ninja-mask", "helm": "visored-helm", "plate": "breastplate", "barding": "horse-head"}
for prefix, g in GEAR.items():
    for rank, c in RANK.items():
        save(glyph(g, c), "%s_%s" % (prefix, rank))
for prefix, g in (("staff", "wizard-staff"), ("dagger", "plain-dagger")):
    for rank, c in RANK.items():
        if not os.path.exists(os.path.join(out, "%s_%s.png" % (prefix, rank))):  # o rank D já tem ícone 3D
            save(glyph(g, c), "%s_%s" % (prefix, rank))
