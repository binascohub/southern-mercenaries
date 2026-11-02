extends SceneTree
## Rasteriza as silhuetas SVG do game-icons.net (128 px, máscara branca) para tools/assets/glyph_icons.py.
##   SVGDIR=<pasta com os .svg> MASKDIR=<pasta de saída> godot --headless --path . --script tools/assets/glyph_masks.gd
func _init() -> void:
	var dir := OS.get_environment("SVGDIR")
	var out := OS.get_environment("MASKDIR")
	for f in DirAccess.get_files_at(dir):
		var s := FileAccess.get_file_as_string(dir + "/" + f)
		s = s.replace('<path d="M0 0h512v512H0z"/>', "")
		var img := Image.new()
		img.load_svg_from_string(s, 0.25)  # 512 -> 128
		img.save_png(out + "/" + f.get_basename() + ".png")
	quit()
