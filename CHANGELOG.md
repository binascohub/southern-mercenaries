# Changelog

## [Unreleased]

### Phase 4 — Elements (in progress)
- `data/elements.json` and `Elements` / `StatusSet`: weakness cycle (x1.5 / x0.5), basic state per element, states (burning, soaked, frozen, shocked, knocked down, stunned) with refresh-not-stack, immunities (fire monsters don't burn, water monsters aren't soaked) and bosses getting a slow instead of control (`docs/02-0-elementos.md`).
- Combos completed by any player: Electrocute, Wildfire, Mud and Steam (areas on the ground), Melt; a combo consumes the state that started it and stacks with the weakness bonus.
- Critical hits: 5% base plus the `crit` affix, x1.5; frozen targets always take a critical.
- Characters choose an origin element at creation (shown in the character list); characters saved before phase 4 become Fire without being flagged as edited.
- Elemental Potions (`elemental_potion_<element>`, 100 + 25 × level): switch the element until returning to Tortuga; one active at a time; hotkey drinks the first one of another element. They drop as loot until the Pirate Market exists.
- Monsters have an element (sewer rats: Earth) with a colored gem above them and a body tint per state; damage numbers show weakness, resistance, criticals and combo names. The staff crystal and the projectiles take the current element's color. HUD shows the current element.
- Tests: element rules, states and combos unit tests; elements test on real monsters in the arena, run in CI.

### Phase 3 — RPG systems (in progress)
- Character sheet (`CharacterData`): level up to 20, XP 700 × level, +5 attribute and +1 skill point per level; health, mana, power and armor from `docs/13-balanceamento.md`. Validated by the host when a player joins (`NET_CHARACTER_INVALID`).
- Items as data: materials (cloth/wood to gold), rarities and affixes, Mage equipment bases, potions and valuables (`data/*.json`); names built with `tr()` in en, es and pt_BR.
- Individual loot rolled per player on the server and shown only to its owner; pickup validated by the server (*Interact* / *Pick up all*); gold picked up automatically; XP divided among present players. A hero who rejoins in time keeps their loot.
- Inventory window, navigable with the gamepad: equipment slots, 40-slot bag, attribute points, tooltip compared with the equipped item; equipment visible on the hero for everyone.
- Potions with a shared cooldown; HUD with XP bar, gold, potions, toasts and "saving…".
- `SaveSystem` (`docs/11-saves.md`): JSON with `save_version`, temp-file write, 3 backups and recovery from a corrupted save; character saved on its owner's PC, campaign (defeated encounter groups) on the host.
- Main menu: character select/create, *Continue* / *New campaign* / *Load campaign* (list with area, date, play time and heroes; play solo or host on the LAN).
- In-game menu: *Save and quit* saves the character (and the campaign on the host) and returns to the main menu (`docs/11-saves.md`, section 4).
- Trading between players in co-op (`docs/05-itens-e-loot.md`, section 8): invite the nearest ally, offer bag items and gold, both confirm; any change undoes the confirmations; the server validates and swaps atomically; cancelled when the players move apart, fall or disconnect.
- Saves during play are written on a background thread (reads, `flush()` and synchronous saves wait for it; queued writes of the same file are merged).
- Campaign thumbnail (`thumb.png`, captured during play without menus open) shown in *Load campaign*; list of checkpoints reached; older campaigns get the new fields on load.
- Save slots (`docs/11-saves.md`, section 3, proposal): up to 12 characters and 6 campaigns per PC (`data/balance.json`); *Delete* (press twice) in the character and campaign lists.
- Character checksum: a character file edited outside the game is detected when it joins and only shows a warning to the group (`docs/11-saves.md`, section 5); old saves without a checksum are not flagged.
- Tests: RPG unit tests (formulas, bag, validation, saves, campaign list, edited character, trade), now run in CI; trade test in the arena with a simulated ally; the bot levels up, collects loot, equips an item and checks the save on disk.
- CI: the smoke-test bot equips an item for an empty slot (swapping only the starting staff made the network test fail at random); the host waits for clients to leave before quitting; network-test failures also appear as annotations; an inventory screenshot is uploaded as an artifact; `actions/checkout@v5` (Node 24).

### Phase 2 — basic LAN network
- `NetworkManager` autoload: ENet host/client with authoritative server; solo uses the same server offline.
- LAN discovery by UDP broadcast and manual `IP:port` join; host refuses different version, different game data (content hash) or a full game.
- Players, monsters and projectiles replicated with MultiplayerSpawner/MultiplayerSynchronizer; client input sent as intent (~30 Hz, buttons immediate); state at ~20 Hz with ~100 ms interpolation.
- Test area to explore instead of waves: start room (checkpoint), corridor and two chambers; monsters in encounter groups that sleep until a player is near, alert nearby groups and stay dead (`docs/03-inimigos.md`).
- Join mid-game next to the host; monster health +60% and damage +10% per extra player, applied when a group wakes.
- Dropped client: hero waits 30 s still and invulnerable; rejoining in time takes it back. Normal leave removes the hero at once.
- Downed state and revive (hold Interact 3 s, interrupted when the reviver is hit); everyone down returns to the checkpoint.
- Translations moved from CSV to gettext (`locale/messages.pot`, `en.po`, `es.po`, `pt_BR.po`), as decided in `docs/01-escopo.md`.
- Co-op HUD: allies' health, player color rings, hosting IP; no pause in co-op.
- Network tests in CI (host + client in two processes, version refusal, drop and rejoin, revive).

### Phase 1 — solo combat prototype
- Godot 4.7.2 project (Compatibility renderer) with the repository layout from `docs/10-distribuicao.md`.
- Mage with basic attack, strong attack and dodge; sewer rats in 3 waves.
- Top-down camera with limited zoom.
- Keyboard/mouse and USB gamepad with rebinding, aim assist, dead zone, vibration and pause on disconnect.
- Key-based translation system (en, es, pt_BR), language switch without restarting.
- Automated tests and Windows/Linux builds on GitHub Actions.
