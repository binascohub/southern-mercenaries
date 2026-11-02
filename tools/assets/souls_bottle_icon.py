"""Ícone de inventário da Garrafa de Almas (128 px): render do Souls_Bottle.glb em 3/4, fundo transparente, mais o contorno escuro dos outros ícones.
1) blender -b -P tools/assets/souls_bottle_icon.py -- <Souls_Bottle.glb> <render.png>   2) python3 -I tools/assets/souls_bottle_icon.py <render.png> <saida.png>"""
import sys
try:
    import bpy, math
    RENDER = True
except ImportError:
    RENDER = False

if RENDER:
    src, out = sys.argv[sys.argv.index("--") + 1:][:2]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=src)
    sc = bpy.context.scene
    cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = 0.5
    cam.location = (-3.0, -3.0, 2.4)  # 3/4 de cima, olhando para o meio da garrafa
    target = bpy.data.objects.new("t", None); target.location = (0, 0, 0.2); sc.collection.objects.link(target)
    track = cam.constraints.new('TRACK_TO'); track.target = target; track.track_axis = 'TRACK_NEGATIVE_Z'; track.up_axis = 'UP_Y'
    l = bpy.data.objects.new("l", bpy.data.lights.new("l", 'SUN')); sc.collection.objects.link(l); l.data.energy = 4; l.rotation_euler = (0.9, 0, 0.6)
    sc.render.engine = 'BLENDER_WORKBENCH'; sc.render.film_transparent = True
    sc.render.resolution_x = 512; sc.render.resolution_y = 512
    sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'TEXTURE'
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
else:
    from PIL import Image, ImageFilter
    src, out = sys.argv[1:3]
    im = Image.open(src).convert("RGBA")
    a = im.getchannel("A")
    box = a.getbbox()
    im = im.crop(box)
    k = 104 / max(im.size)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    canvas.paste(im, ((128 - im.width) // 2, (128 - im.height) // 2))
    alpha = canvas.getchannel("A")
    outline = alpha.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(0.5))
    result = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    result.paste(Image.new("RGBA", (128, 128), (26, 18, 8, 255)), (0, 0), outline)
    result.alpha_composite(canvas)
    result.save(out)
    print("OK", out)
