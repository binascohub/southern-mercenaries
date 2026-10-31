# Southern Mercenaries

Dark co-op action RPG with a top-down camera, inspired by *Baldur's Gate: Dark Alliance II*. Play solo or with up to 4 players over LAN. Windows and Linux. Light enough to run on integrated graphics.

**Languages:** English · Español · Português (BR)

## Status
**Phase 3 — RPG systems (in progress)** (`docs/01-escopo.md`, section 9). Not the game yet: the technical base the next phases build on.

- **Combat (phase 1):** the Mage with the top-down camera: basic attack, charged strong attack and dodge (`docs/02-1-mago.md`).
- **Test area:** a start room (checkpoint), a corridor and two chambers to explore. Sewer rats are placed in **encounter groups** that sleep until a player gets close (~15 m) and alert nearby groups; dead monsters stay dead (`docs/03-inimigos.md`, no waves). Bites have a visible wind-up.
- **LAN co-op (phase 2):** authoritative host inside the game; solo runs the same server locally (peer 1). Clients send intent (movement, aim, buttons) and the server simulates; state at ~20 Hz with ~100 ms interpolation.
  - **Host LAN game** / **Join LAN game** in the main menu: automatic discovery by UDP broadcast, or manual `IP:port`.
  - The host refuses a different game version or different game data (content hash), and a full game.
  - Join mid-game (you appear next to the host). Monster strength per extra player — health +60%, damage +10% — is set when a group wakes up (`docs/13-balanceamento.md`, 2.5).
  - A client that drops leaves its hero standing still and invulnerable for 30 s; rejoining in time takes the same hero back (`docs/07-rede.md`, section 9).
  - A downed player is revived by an ally holding *Interact* for 3 s (interrupted if the reviver is hit); if everyone falls, back to the checkpoint (surviving groups go back to sleep).
  - No pause in co-op; gamepad disconnect only shows a warning.
- **RPG systems (phase 3):**
  - **Character sheet:** level up to 20, XP to the next level = 700 × level, +5 attribute points and +1 skill point per level; health, mana, power and armor from `docs/13-balanceamento.md`. The host validates the character a player brings (no edited attributes, items or levels).
  - **Items as data** (`data/*.json`): materials from cloth/wood to gold, rarities with affixes, Mage equipment, potions and valuables. Item names are built from translated parts.
  - **Individual loot:** rolled per player on the server and shown only to its owner; pick up with *Interact* or *Pick up all*; gold is picked up automatically; XP is divided among the players present.
  - **Inventory** (I / Back), navigable with the gamepad: equipment slots, 40-slot bag, attribute points and an item tooltip compared with what is equipped. Equipment shows on the hero for everyone.
  - **Potions** (1 health, 2 mana) with a shared cooldown; HUD with XP bar, gold, potions and "saving…".
  - **Saves** (`docs/11-saves.md`): JSON with `save_version`, written through a temp file, 3 backups and recovery from a corrupted save. The character is saved on its owner's PC; the campaign (encounter groups already defeated) on the host.
  - Main menu: choose or create a character, *Continue* / *New campaign*.
- Keyboard + mouse **and** USB gamepad (rebinding, aim assist, dead zone, vibration); English, Spanish and Portuguese, switchable without restarting.
- GitHub Actions: tests (data, RPG, host + client in two processes), an inventory screenshot and Windows/Linux builds on every push; GitHub Release on every `v*` tag.

**LAN ports (proposal in `docs/07-rede.md`):** UDP **24567** (game) and **24568** (discovery). Allow them in the firewall of the host PC.

The complete game design lives in [`docs/`](docs/00-README.md).

## Running
Requires **Godot 4.7.2** (the project's pinned version).

```bash
godot --path .        # play
godot -e --path .     # open in the editor
```

Default controls — keyboard: WASD move, mouse aim, left click attack (hold for strong attack), Space dodge, right click / G interact, Z pick up all, 1/2 potions, I inventory, Esc pause. Gamepad: left stick move, right stick aim, RT attack, LT dodge, RB pick up all, D-pad down/up potions, Back inventory, Start pause.

## Tests
```bash
godot --headless --path . --import
godot --headless --path . --script res://tests/run_tests.gd            # translations and data
godot --headless --path . res://tests/rpg_tests.tscn                    # RPG formulas, bag, character validation, saves
godot --headless --path . --fixed-fps 60 res://tests/smoke_arena.tscn  # a bot clears every encounter, collects its loot, equips an item and checks the save
godot --headless --path . res://tests/smoke_arena.tscn -- revive        # downed, revive, back to checkpoint
tests/net_smoke.sh godot                                                # host + client together; version refusal; drop and rejoin
```

To try co-op on one PC, run the game twice: *Host LAN game* in one window and *Join LAN game* → `127.0.0.1` in the other.

`tests/screenshot.tscn` saves a screenshot of the arena: `godot --path . res://tests/screenshot.tscn -- out.png 135 [inventory] [join IP]` (`inventory` opens the inventory window first). CI uploads one as the `screenshots` artifact.

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
