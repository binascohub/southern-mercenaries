"""Ícones das marcas do minimapa e do Viajante do Tempo (assets/ui/map_icons/*.png), feitos com Board Game Icons da Kenney (CC0).
As silhuetas brancas da Kenney viram medalhões na identidade do jogo (docs/09-interface.md, seção 7): disco de couro escuro, aro na cor
da marca com filete de latão e o símbolo na mesma cor, com contorno escuro.
uso: python3 tools/ui/make_map_icons.py <pasta "PNG/Double (128px)" do kenney_board-game-icons.zip>   (a partir da raiz do projeto)"""
import os, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter

SRC = sys.argv[1]
OUT = "assets/ui/map_icons"
SIZE = 64            # o minimapa desenha a 14-22 px; 64 deixa nítido também nos botões
LEATHER = (28, 21, 17, 255)     # #1C1511
BRASS = (140, 110, 51, 255)     # #8C6E33
INK = (10, 8, 6, 255)

ICONS = {  # nome: (ícone da Kenney, cor)
    "exit": ("structure_gate", (110, 205, 240)),
    "quest": ("flag_triangle", (247, 217, 133)),       # brilho do ouro #F7D985
    "questgiver": ("notepad_write", (255, 150, 40)),
    "altar": ("book_open", (195, 120, 255)),
    "teleporter": ("hourglass", (225, 200, 255)),
    "miniboss": ("skull", (235, 50, 40)),
    "locked": ("lock_closed", (212, 171, 74)),          # ouro #D4AB4A
}

os.makedirs(OUT, exist_ok=True)
S = SIZE * 4  # desenha grande e reduz (bordas macias)
for name, (src, color) in ICONS.items():
    rgb = tuple(color) + (255,)
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = S * 0.03
    d.ellipse([pad, pad, S - pad, S - pad], fill=INK)                                   # contorno escuro
    d.ellipse([pad + S * 0.035, pad + S * 0.035, S - pad - S * 0.035, S - pad - S * 0.035], fill=rgb)        # aro na cor da marca
    d.ellipse([pad + S * 0.085, pad + S * 0.085, S - pad - S * 0.085, S - pad - S * 0.085], fill=BRASS)      # filete de latão
    d.ellipse([pad + S * 0.105, pad + S * 0.105, S - pad - S * 0.105, S - pad - S * 0.105], fill=LEATHER)    # couro
    glyph = Image.open(os.path.join(SRC, src + ".png")).convert("RGBA")
    g = int(S * 0.56)
    glyph = glyph.resize((g, g), Image.LANCZOS)
    alpha = glyph.getchannel("A")
    outline = alpha.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MaxFilter(9))
    at = ((S - g) // 2, (S - g) // 2)
    img.paste(Image.new("RGBA", (g, g), INK), at, outline)
    shade = Image.new("RGBA", (g, g), tuple(int(c * 0.62) for c in color) + (255,))
    lit = Image.new("RGBA", (g, g), rgb)
    grad = Image.linear_gradient("L").resize((g, g))                                  # luz de cima, sombra embaixo (pintado, não chapado)
    body = Image.composite(shade, lit, grad)
    img.paste(body, at, ImageChops.multiply(alpha, Image.new("L", (g, g), 255)))
    img.resize((SIZE, SIZE), Image.LANCZOS).save(os.path.join(OUT, name + ".png"))
print("OK", len(ICONS), "ícones em", OUT)
