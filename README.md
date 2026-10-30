# Southern Mercenaries

Dark co-op action RPG with a top-down camera, inspired by *Baldur's Gate: Dark Alliance II*. Play solo or with up to 4 players over LAN. Windows and Linux. Light enough to run on integrated graphics.

**Languages:** English · Español · Português (BR)

## Status
**Phase 1 — solo combat prototype** (`docs/01-escopo.md`, section 9). Not the game yet: the technical base the next phases build on.

- The Mage in a test cellar with the top-down camera (~55°, no rotation, limited zoom): basic attack, charged strong attack (hold 1 s, pierces 1 enemy) and dodge, using the numbers in `docs/02-1-mago.md`.
- Sewer rats in 3 waves, with a visible wind-up before each bite; victory/defeat and restart.
- Keyboard + mouse **and** USB gamepad: Input Map actions only, rebinding saved to `user://controls.cfg`, button hints follow the last device used, 15° aim assist, configurable dead zone, vibration, pause on gamepad disconnect.
- English, Spanish and Portuguese, switchable in Options without restarting; language picker on first launch.
- Game data in `data/*.json` (IDs and translation keys only); texts in `locale/texts.csv` (`keys,en,es,pt_BR`).
- GitHub Actions: tests + Windows/Linux builds on every push, GitHub Release on every `v*` tag.

The complete game design lives in [`docs/`](docs/00-README.md).

## Running
Requires **Godot 4.7.2** (the project's pinned version).

```bash
godot --path .        # play
godot -e --path .     # open in the editor
```

Default controls — keyboard: WASD move, mouse aim, left click attack (hold for strong attack), Space dodge, Esc pause. Gamepad: left stick move, right stick aim, RT attack, LT dodge, Start pause.

## Tests
```bash
godot --headless --path . --import
godot --headless --path . --script res://tests/run_tests.gd            # translations and data
godot --headless --path . --fixed-fps 60 res://tests/smoke_arena.tscn  # a bot plays the arena until it wins
```

`tests/screenshot.tscn` saves a screenshot of the arena: `godot --path . res://tests/screenshot.tscn -- out.png 135`.

## The game
- 5 classes (Knight, Ninja, Archer, Mage, Summoner) × 4 elements (Water, Fire, Air, Earth)
- 10 maps / 41 areas, from the sewers of Tortuga to Hell
- Elemental weakness cycle, loot, material tiers and Lineage-2-style refining
- LAN co-op, gamepad support, save and continue

## Tech
Godot 4.7.2 (Compatibility renderer), GDScript, ENet multiplayer.

## Docs (Portuguese)
Start at [`docs/00-README.md`](docs/00-README.md).

## License
- Code: [GPL-3.0-or-later](LICENSE) — anyone can use, study, modify and contribute
- Art, audio and story text: [CC BY-SA 4.0](LICENSE-ASSETS)

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CREDITS.md](CREDITS.md).
