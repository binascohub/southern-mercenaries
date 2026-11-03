"""Texturas de água feitas do zero (sem pacote de terceiros), sem emenda (repetem em qualquer direção), para o shader assets/shaders/water.gdshader:
  assets/textures/water/water_normal.png   mapa de normais de ondas suaves (soma de senoides de números inteiros de ondas, por isso fecha nas bordas)
  assets/textures/water/water_caustic.png  linhas de cáustica (diagrama de Voronoi sem emenda): R = linhas brilhantes, G = ruído suave para a espuma
uso: python3 tools/assets/build_water_textures.py   (a partir da raiz do projeto)"""
import math, random
from PIL import Image
N = 256
rng = random.Random("water")
# --- normais: altura = soma de senoides com direções e fases sorteadas
waves = []
for _ in range(14):
    kx, ky = rng.randint(-6, 6), rng.randint(-6, 6)
    if kx == 0 and ky == 0:
        continue
    waves.append((kx, ky, rng.uniform(0, math.tau), rng.uniform(0.5, 1.0) / math.hypot(kx, ky)))
def height(x, y):
    return sum(a * math.sin(math.tau * (kx * x + ky * y) / N + ph) for kx, ky, ph, a in waves)
img = Image.new("RGB", (N, N))
px = img.load()
for y in range(N):
    for x in range(N):
        dx = height(x + 1, y) - height(x - 1, y)
        dy = height(x, y + 1) - height(x, y - 1)
        nx, ny, nz = -dx * 2.2, -dy * 2.2, 1.0
        l = math.sqrt(nx * nx + ny * ny + nz * nz)
        px[x, y] = (int((nx / l * 0.5 + 0.5) * 255), int((ny / l * 0.5 + 0.5) * 255), int((nz / l * 0.5 + 0.5) * 255))
img.save("assets/textures/water/water_normal.png")
# --- cáusticas: Voronoi periódico (G: ruído de ondas)
G = 12
pts = [[(rng.random(), rng.random()) for _ in range(G)] for _ in range(G)]
cell = N / G
cau = Image.new("RGB", (N, N))
cp = cau.load()
for y in range(N):
    for x in range(N):
        gx, gy = int(x // cell), int(y // cell)
        d = []
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                cx, cy = (gx + ox) % G, (gy + oy) % G
                fx, fy = pts[cy][cx]
                qx, qy = (gx + ox + fx) * cell, (gy + oy + fy) * cell
                d.append(math.hypot(x - qx, y - qy))
        d.sort()
        edge = d[1] - d[0]
        line = max(0.0, 1.0 - edge / (cell * 0.22))
        soft = 0.5 + 0.5 * math.sin(math.tau * (2 * x + 3 * y) / N + 1.3) * math.cos(math.tau * (3 * x - y) / N)
        cp[x, y] = (int(line * line * 255), int(soft * 255), 0)
cau.save("assets/textures/water/water_caustic.png")
print("OK texturas de água", N)
