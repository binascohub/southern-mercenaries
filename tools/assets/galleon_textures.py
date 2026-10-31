"""Texturas do galeão: tábuas do casco, pano carmesim das velas com o emblema
(caveira sobre ossos cruzados) e a bandeira pirata."""
import sys, random, math
from PIL import Image, ImageDraw, ImageFilter
out = sys.argv[1]
random.seed(7)

# Tábuas escuras do casco: faixas horizontais com veios e juntas.
W, H = 512, 512
img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)
plank = 32
for row in range(H // plank):
    base = random.randint(26, 40)
    for y in range(row * plank, (row + 1) * plank):
        for x in range(W):
            n = base + int(6 * math.sin(x * 0.05 + row * 1.7) + random.randint(-3, 3))
            img.putpixel((x, y), (n + 8, int(n * 0.72), int(n * 0.5)))
    d.line([(0, row * plank), (W, row * plank)], fill=(10, 7, 5), width=2)
    off = (row * 137) % W
    for x in range(off % 160, W, 160):
        d.line([(x, row * plank), (x, (row + 1) * plank)], fill=(12, 8, 6), width=2)
img.save(f"{out}/hull_planks.png")

def skull(draw, cx, cy, s, fill, hole):
    """Caveira com dois ossos cruzados atrás."""
    for a in (35, -35):
        r = math.radians(a)
        dx, dy = math.cos(r) * s * 1.25, math.sin(r) * s * 1.25
        draw.line([(cx - dx, cy + s * 0.55 - dy), (cx + dx, cy + s * 0.55 + dy)], fill=fill, width=int(s * 0.22))
        for ex, ey in ((cx - dx, cy + s * 0.55 - dy), (cx + dx, cy + s * 0.55 + dy)):
            for k in (-1, 1):
                draw.ellipse([ex - s * 0.17 + k * s * 0.1 * math.sin(r), ey - s * 0.17 - k * s * 0.1 * math.cos(r),
                              ex + s * 0.17 + k * s * 0.1 * math.sin(r), ey + s * 0.17 - k * s * 0.1 * math.cos(r)], fill=fill)
    draw.ellipse([cx - s * 0.62, cy - s * 0.7, cx + s * 0.62, cy + s * 0.45], fill=fill)
    draw.rounded_rectangle([cx - s * 0.36, cy + s * 0.2, cx + s * 0.36, cy + s * 0.7], radius=s * 0.1, fill=fill)
    for ex in (-0.25, 0.25):
        draw.ellipse([cx + ex * s - s * 0.17, cy - s * 0.25, cx + ex * s + s * 0.17, cy + s * 0.07], fill=hole)
    draw.polygon([(cx, cy + s * 0.12), (cx - s * 0.08, cy + s * 0.3), (cx + s * 0.08, cy + s * 0.3)], fill=hole)
    for tx in (-0.2, 0, 0.2):
        draw.line([(cx + tx * s, cy + s * 0.48), (cx + tx * s, cy + s * 0.68)], fill=hole, width=max(2, int(s * 0.04)))

# Pano carmesim: costuras verticais, manchas, emblema em vermelho-escuro com borda dourada.
S = 512
sail = Image.new("RGB", (S, S), (140, 22, 26))
d = ImageDraw.Draw(sail)
for y in range(S):
    for x in range(S):
        n = random.randint(-10, 10)
        shade = int(12 * math.sin(y * 0.02)) + n
        sail.putpixel((x, y), (max(0, 140 + shade), max(0, 22 + shade // 3), max(0, 26 + shade // 3)))
for x in range(0, S, 64):
    d.line([(x, 0), (x, S)], fill=(95, 12, 16), width=3)
d.rectangle([0, 0, S - 1, S - 1], outline=(70, 8, 10), width=10)
skull(d, S / 2 + 3, S / 2 + 3, 120, (180, 130, 40), (180, 130, 40))
skull(d, S / 2, S / 2, 120, (70, 6, 10), (140, 22, 26))
sail = sail.filter(ImageFilter.SMOOTH)
sail.save(f"{out}/sail_crimson.png")

# Bandeira pirata: preta, caveira e ossos brancos.
flag = Image.new("RGB", (256, 160), (14, 12, 12))
d = ImageDraw.Draw(flag)
skull(d, 128, 74, 52, (232, 228, 214), (14, 12, 12))
flag.save(f"{out}/jolly_roger.png")
print("ok")
