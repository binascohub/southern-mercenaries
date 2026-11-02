"""Ícone da Carne de Cervo (assets/ui/icons/venison.png, 128 px): coxa assada desenhada por código (sem arte externa).
uso: python3 tools/assets/build_venison_icon.py   (a partir da raiz do projeto)"""
from PIL import Image, ImageDraw, ImageFilter
im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
dr = ImageDraw.Draw(im)
dr.polygon([(300, 330), (430, 450), (450, 420), (470, 440), (450, 470), (430, 490), (400, 470), (410, 440), (280, 350)], fill=(235, 225, 205, 255))
dr.ellipse([420, 415, 480, 470], fill=(235, 225, 205, 255))
dr.ellipse([440, 440, 500, 495], fill=(235, 225, 205, 255))
dr.ellipse([60, 70, 360, 350], fill=(122, 56, 28, 255))
dr.ellipse([85, 90, 340, 320], fill=(168, 84, 38, 255))
dr.ellipse([120, 110, 260, 220], fill=(196, 112, 58, 255))
im.filter(ImageFilter.GaussianBlur(1.5)).resize((128, 128), Image.LANCZOS).save("assets/ui/icons/venison.png")
