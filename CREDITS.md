# Credits

Southern Mercenaries is created by Fernando (binascohub). Design docs and translations assisted by Claude (Anthropic).

## Engine
- [Godot Engine](https://godotengine.org/) — MIT License

## Third-party assets
Only CC0, CC BY or CC BY-SA assets are allowed (fonts may also use the SIL Open Font License 1.1). Add one row per asset.

| Asset | Author | Source | License |
|---|---|---|---|
| Cinzel (`assets/fonts/Cinzel.ttf`) — titles | The Cinzel Project Authors (Natanael Gama) | [Google Fonts](https://fonts.google.com/specimen/Cinzel) · [GitHub](https://github.com/NDISCOVER/Cinzel) | SIL OFL 1.1 (`assets/fonts/OFL-Cinzel.txt`) |
| Alegreya (`assets/fonts/Alegreya.ttf`, `Alegreya-Italic.ttf`) — text | The Alegreya Project Authors (Huerta Tipográfica) | [Google Fonts](https://fonts.google.com/specimen/Alegreya) · [GitHub](https://github.com/huertatipografica/Alegreya) | SIL OFL 1.1 (`assets/fonts/OFL-Alegreya.txt`) |
| Universal Animation Library — Standard: skeleton and 43 animations of the heroes (`assets/models/characters/hero_male.glb`, `hero_female.glb`) | Quaternius | [quaternius.com](https://quaternius.com/packs/universalanimationlibrary.html) · [itch.io](https://quaternius.itch.io/universal-animation-library) | CC0 1.0 (`assets/models/characters/LICENSE-UAL.txt`) |
| Universal Base Characters — Standard: heads, eyes and hairstyles of the heroes | Quaternius | [quaternius.com](https://quaternius.com/packs/universalbasecharacters.html) · [itch.io](https://quaternius.itch.io/universal-base-characters) | CC0 1.0 (`assets/models/characters/LICENSE-UBC.txt`) |
| Modular Character Outfits – Fantasy — Standard: Peasant and Ranger outfits of the heroes | Quaternius | [quaternius.com](https://quaternius.com/packs/modularcharacteroutfitsfantasy.html) · [itch.io](https://quaternius.itch.io/modular-character-outfits-fantasy) | CC0 1.0 (`assets/models/characters/LICENSE-OUTFITS.txt`) |
| Medieval Village MegaKit — Standard: walls, floors, doors, windows, fences and wagon of Tortuga and the Tavern (`assets/models/village/`) | Quaternius | [quaternius.com](https://quaternius.com/packs/medievalvillagemegakit.html) · [itch.io](https://quaternius.itch.io/medieval-village-megakit) | CC0 1.0 (`assets/models/village/LICENSE.txt`) |
| Fantasy Props MegaKit — Standard: furniture, stalls, barrels, crates, chests, anvil, training dummy and other props (`assets/models/props/`) | Quaternius | [quaternius.com](https://quaternius.com/packs/fantasypropsmegakit.html) · [itch.io](https://quaternius.itch.io/fantasy-props-megakit) | CC0 1.0 (`assets/models/props/LICENSE.txt`) |
| Pirate ship with crimson sails (`assets/models/ships/pirate_ship.glb`) | Fernando (binascohub) | Original, made for Southern Mercenaries | CC BY-SA 4.0 (`LICENSE-ASSETS`) |

The hero models are assembled from the three Quaternius packs above by `tools/assets/build_heroes.py` (Blender as a Python module), from the original packs kept in `uploads/`: textures reduced to 1024 px, only the head of the base characters kept under the outfits. The village and prop pieces are exported one by one by `tools/assets/export_kit.py` (shared textures as 1024 px WebP).
