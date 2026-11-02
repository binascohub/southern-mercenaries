"""Atlas 5 x 2 da cor base do Homem-Aranha: junta as 10 telas UDIM (1001 a 1010, 4K) em 1024 px cada (tela k na coluna k % 5 e na linha
k // 5 contada de baixo, como o espaço UV do Blender).
uso: python3 -I tools/assets/spiderman_atlas.py <pasta textures do TASM 2> <atlas.png>"""
import sys
from PIL import Image
tex, out = sys.argv[1:3]
T = 1024
atlas = Image.new("RGB", (T * 5, T * 2))
for k in range(10):
    im = Image.open("%s/Substance tasm 5_Tasm 2_BaseColor.%d.png" % (tex, 1001 + k)).convert("RGB").resize((T, T), Image.LANCZOS)
    atlas.paste(im, ((k % 5) * T, (1 - k // 5) * T))
atlas.save(out)
