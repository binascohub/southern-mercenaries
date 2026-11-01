"""Paleta única da Fazenda: a madeira de todos os modelos (casa, serraria, carroças, barricada) tem o mesmo tom da cerca do
kit (T_WoodTrim_BaseColor, média 0,545 / 0,414 / 0,30), e as coberturas das construções são de palha (a do telhado da casa).
Uso nos scripts do Blender: sys.path.insert(0, pasta deste arquivo); from farm_palette import unify_wood
unify_wood(imagem) -> imagem nova: troca a cor dos pixels pouco saturados (madeira cinza, desbotada) pelo tom da cerca, mantendo o claro e
escuro do desenho; pixels bem saturados (palha, pontas claras das toras, ferro com ferrugem forte) ficam como estão."""
import numpy as np

WOOD = np.array([0.545, 0.414, 0.30], dtype=np.float32)
WOOD_LUM = 0.42  # luminância média da cerca do kit


def unify_wood(image, strength=1.0, sat_limit=0.32):
    w, h = image.size
    px = np.array(image.pixels[:], dtype=np.float32).reshape(-1, 4)
    rgb = px[:, :3]
    mx, mn = rgb.max(1), rgb.min(1)
    sat = (mx - mn) / np.maximum(mx, 1e-4)
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    opaque = px[:, 3] > 0.5
    mean = max(float(lum[opaque].mean()), 1e-4) if opaque.any() else 1.0
    # peso: 1 para cinza (sat 0), 0 acima de sat_limit; o claro/escuro vem da luminância relativa à média da imagem
    weight = np.clip(1.0 - sat / sat_limit, 0.0, 1.0) * strength
    target = WOOD[None, :] * np.clip(lum / mean, 0.15, 2.2)[:, None] * (WOOD_LUM / WOOD_LUM)
    px[:, :3] = np.clip(rgb * (1 - weight[:, None]) + target * weight[:, None], 0, 1)
    # O exportador do glTF lê o arquivo empacotado, não os pixels alterados em memória: devolve uma imagem NOVA já empacotada.
    import bpy
    fixed = bpy.data.images.new(image.name + "_farm", w, h, alpha=True)
    fixed.pixels = px.ravel().tolist()
    fixed.pack()
    return fixed
