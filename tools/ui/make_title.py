#!/usr/bin/env python3
# Southern Mercenaries — GPL-3.0-or-later
"""Gera assets/ui/title.png: o título do jogo em ouro com relevo (duas linhas em maiúsculas,
rosa dos ventos em cima e embaixo, filetes laterais). Só Pillow; Cinzel (OFL).
Uso: python3 tools/ui/make_title.py"""
import math
import random
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

FONT = "assets/fonts/Cinzel.ttf"
OUT = "assets/ui/title.png"
W, H = 2300, 1000
BOLD = 7  # espessura extra do traço (o Cinzel regular é fino para um título)


def font(size):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([900])
    except Exception:
        pass
    return f


def text_mask(text, size, center_y):
    mask = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(mask)
    f = font(size)
    box = draw.textbbox((0, 0), text, font=f, stroke_width=BOLD)
    x = (W - (box[2] - box[0])) // 2 - box[0]
    y = center_y - (box[3] - box[1]) // 2 - box[1]
    draw.text((x, y), text, font=f, fill=255, stroke_width=BOLD, stroke_fill=255)
    return mask


def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(8):
        a = i * math.pi / 4
        length = r if i % 2 == 0 else r * 0.26
        pts.append((cx + math.sin(a) * length, cy - math.cos(a) * length))
    draw.polygon(pts, fill=fill)
    d = r * 0.62  # pontas menores nas diagonais
    pts = []
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 4
        length = d if i % 2 == 0 else d * 0.22
        pts.append((cx + math.sin(a) * length, cy - math.cos(a) * length))
    draw.polygon(pts, fill=fill)
    draw.ellipse((cx - r * 0.2, cy - r * 0.2, cx + r * 0.2, cy + r * 0.2), fill=fill)


def ornament(mask, cx, cy, r, line_len):
    draw = ImageDraw.Draw(mask)
    star(draw, cx, cy, r, 255)
    for side in (-1, 1):
        x0 = cx + side * r * 1.5
        x1 = x0 + side * line_len
        draw.line((x0, cy, x1, cy), fill=255, width=7)
        draw.polygon([(x1, cy - 10), (x1 + side * 14, cy), (x1, cy + 10), (x1 - side * 14, cy)], fill=255)


def build():
    random.seed(4)
    mask = Image.new("L", (W, H), 0)
    mask = ImageChops.lighter(mask, text_mask("SOUTHERN", 300, 330))
    mask = ImageChops.lighter(mask, text_mask("MERCENARIES", 246, 640))
    ornament_mask = Image.new("L", (W, H), 0)
    ornament(ornament_mask, W // 2, 90, 84, 330)
    ornament(ornament_mask, W // 2, 905, 60, 380)
    mask = ImageChops.lighter(mask, ornament_mask)

    # Relevo: altura = máscara suavizada; luz vem do alto à esquerda.
    height = mask.filter(ImageFilter.GaussianBlur(7))
    lit = ImageChops.subtract(ImageChops.offset(height, -4, -4), ImageChops.offset(height, 4, 4), 1, 128)
    highlight = lit.point(lambda v: max(0, v - 128) * 3)
    shade = lit.point(lambda v: max(0, 128 - v) * 3)

    # Ouro: degradê vertical por faixa (claro em cima, âmbar no meio, escuro embaixo) + martelado.
    gradient = Image.linear_gradient("L").resize((W, H))
    bands = Image.new("L", (W, H))
    bands.paste(gradient.crop((0, 0, W, H // 2)).resize((W, H // 2)), (0, 0))
    bands.paste(gradient.crop((0, 0, W, H // 2)).resize((W, H // 2)).transpose(Image.FLIP_TOP_BOTTOM), (0, H // 2))
    gold = ImageOps.colorize(bands, black=(255, 236, 160), mid=(226, 166, 52), white=(120, 70, 14), midpoint=110)
    noise = Image.effect_noise((W, H), 70).filter(ImageFilter.GaussianBlur(1.2))
    grain = noise.point(lambda v: 150 + (v - 128) // 2)
    gold = ImageChops.multiply(gold, Image.merge("RGB", (grain, grain, grain)).point(lambda v: min(255, int(v * 1.5))))
    gold = ImageChops.add(gold, Image.merge("RGB", (highlight, highlight, int(1) and highlight.point(lambda v: v // 2))))
    gold = ImageChops.subtract(gold, Image.merge("RGB", (shade, shade, shade)))

    # Contorno escuro, filete de ouro fino por fora e sombra projetada.
    outline = mask.filter(ImageFilter.MaxFilter(11))
    rim = mask.filter(ImageFilter.MaxFilter(21))
    shadow = rim.filter(ImageFilter.GaussianBlur(14))
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (14, 18), shadow.point(lambda v: int(v * 0.8)))
    canvas.paste(Image.new("RGBA", (W, H), (58, 32, 8, 255)), (0, 0), rim)
    canvas.paste(Image.new("RGBA", (W, H), (20, 10, 4, 255)), (0, 0), outline)
    canvas.paste(gold.convert("RGBA"), (0, 0), mask)
    bbox = canvas.getbbox()
    canvas = canvas.crop((max(bbox[0] - 10, 0), max(bbox[1] - 10, 0), min(bbox[2] + 10, W), min(bbox[3] + 10, H)))
    canvas.save(OUT)
    print("título salvo:", OUT, canvas.size)


if __name__ == "__main__":
    build()
