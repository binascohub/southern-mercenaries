"""Comidas do Food Kit da Kenney (CC0) para as feiras, a mesa do rei e as carroças da Fazenda: copia só os modelos que cabem num porto pirata
medieval (frutas, legumes, pães, queijos, carnes, peixe, tortas, vinho, pratos e canecas; nada de hambúrguer, refrigerante ou sushi) para
assets/models/food/ com o prefixo "Fk_" (peças do Kit: "Fk_Turkey", "Fk_Loaf_Round"...) e a textura de cores compartilhada (Textures/colormap.png),
um pouco menos saturada e mais escura (docs/09-interface.md, seção 7: tons terrosos, nada de cor chapada e vibrante).
uso: python3 tools/assets/import_food_kit.py <pasta "Models/GLB format" do kenney_food-kit.zip>   (a partir da raiz do projeto)"""
import os, shutil, sys
from PIL import Image, ImageEnhance

SRC = sys.argv[1]
OUT = "assets/models/food"
MODELS = ["apple", "apple-half", "pear", "grapes", "cherries", "strawberry", "lemon", "orange", "banana", "pineapple", "coconut", "coconut-half",
          "watermelon", "pumpkin", "pumpkin-basic", "cabbage", "carrot", "beet", "onion", "leek", "radish", "cauliflower", "corn", "eggplant",
          "mushroom", "paprika", "bread", "loaf", "loaf-round", "loaf-baguette", "cheese", "cheese-cut", "fish", "meat-cooked", "meat-raw",
          "meat-ribs", "meat-sausage", "whole-ham", "turkey", "pie", "mincemeat-pie", "cake", "honey", "egg", "barrel", "bag", "bag-flat",
          "wine-red", "wine-white", "glass-wine", "mug", "plate-dinner", "plate", "bowl", "bowl-soup", "pot-stew", "skewer", "mussel", "pan-stew"]


def piece_name(model):
    return "Fk_" + "_".join(part.capitalize() for part in model.split("-"))


os.makedirs(os.path.join(OUT, "Textures"), exist_ok=True)
for model in MODELS:
    shutil.copyfile(os.path.join(SRC, model + ".glb"), os.path.join(OUT, piece_name(model) + ".glb"))
colors = Image.open(os.path.join(SRC, "Textures", "colormap.png")).convert("RGBA")
alpha = colors.getchannel("A")
rgb = ImageEnhance.Brightness(ImageEnhance.Color(colors.convert("RGB")).enhance(0.72)).enhance(0.88)
rgb.putalpha(alpha)
rgb.save(os.path.join(OUT, "Textures", "colormap.png"))
print("OK", len(MODELS), "comidas em", OUT)
