# Southern Mercenaries

Dark co-op action RPG with a top-down camera, inspired by *Baldur's Gate: Dark Alliance II*. Play solo or with up to 4 players over LAN. Windows and Linux. Light enough to run on integrated graphics.

**Languages:** English · Español · Português (BR)

## Status
**Phase 7 — The Tortuga Sewers (in progress)** (`docs/01-escopo.md`, section 9). Phases 1–6 are done (Tortuga's Portal window waits for maps 2–5). Not the game yet: the technical base the next phases build on.

- **Combat (phase 1):** the Mage with the top-down camera: basic attack, charged strong attack and dodge (`docs/02-1-mago.md`).
- **Test area:** a start room (checkpoint), a corridor and two chambers to explore. Sewer rats are placed in **encounter groups** that sleep until a player gets close (~15 m) and alert nearby groups; dead monsters stay dead (`docs/03-inimigos.md`, no waves). Bites have a visible wind-up.
- **LAN co-op (phase 2):** authoritative host inside the game; solo runs the same server locally (peer 1). Clients send intent (movement, aim, buttons) and the server simulates; state at ~20 Hz with ~100 ms interpolation.
  - **Host LAN game** / **Join LAN game** in the main menu: automatic discovery by UDP broadcast, or manual `IP:port`.
  - The host refuses a different game version or different game data (content hash), and a full game.
  - Join mid-game (you appear next to the host). Monster strength per extra player — health +60%, damage +10% — is set when a group wakes up (`docs/13-balanceamento.md`, 2.5).
  - A client that drops leaves its hero standing still and invulnerable for 30 s; rejoining in time takes the same hero back (`docs/07-rede.md`, section 9).
  - A downed player is revived by an ally holding *Interact* for 3 s (interrupted if the reviver is hit); if everyone falls, back to the checkpoint (surviving groups go back to sleep).
  - No pause in co-op; gamepad disconnect only shows a warning.
- **Skills (phase 5, Mage):** 10 skills per class with up to 5 ranks, unlocked at levels 1, 2, 4… 18, one skill point per level (`docs/02-personagens.md`). The Mage has 4 class skills (Sharp Mind, Teleport, Mana Shield, Elemental Mastery) and 6 per element — 28 in all, from Fire Bolt to Earthquake (`docs/02-1-mago.md`, section 6). Four active skills on the hotkeys (Q E R F / A B X Y) with mana cost and cooldown shown in the HUD; the Skills window (K, or the button in the inventory) learns ranks and assigns hotkeys. An Elemental Potion swaps the element skills for the new element's with the same ranks.
- **Archer (phase 5):** Focus (100, +1 per DEX) that regenerates fast standing still (15/s) and slowly while moving (5/s); arrows with 16 m reach and a charged shot (1.5 s, 200%); dodge every 3 s instead of a block. 7 class skills that carry the current element's basic state — Precise Shot (always crits), Back Leap, Eagle Eye, Spike Trap (up to 3), Arrow Fan, Piercing Arrow, Mark Target — and 3 per element: a support (Campfire, Spring, Wind, Bulwark), a single-target arrow and a final rain or volley (`docs/02-2-arqueiro.md`). Bow, hunter's cap and leather vest drop for the Archer.
- **Ninja (phase 5):** agile melee tank — 130 health, quick dagger slashes and a charged spinning cut, 10% evasion (+0.2% per DEX), a 5 m teleport instead of a dodge roll, Energy that regenerates fast and refills on crits. 7 class skills (Twin Slash, Shadow Step behind the target, Backstab — always crits from behind, Smoke Bomb invisibility, Iron Body that taunts, Evasion, Blink Strike) and 3 per element: seals as supports, a heavy single-target cut and the "Thousand Cuts" finals that jump between enemies (`docs/02-4-ninja.md`). +10% gold found (thief trait, proposal). Parry comes later together with blocking.
- **Summoner (phase 5):** fights with friendly animals — a companion per element (fire fox, otter, falcon, boar), up to 2 (3 at rank 5), and a Guardian Bear that taunts; animals use the Summoner's current element, are attacked by monsters, flee instead of dying, and every hit gives back Essence. Pages of the book as projectiles; Flock, Bond, Scatter Escape, Stampede and Rescue (revives a downed ally from afar), plus 3 skills per element (`docs/02-5-invocador.md`). Book of Friends pages come with the maps.
- **Knight (phase 5):** mounted charge tank — on horseback 120% speed with inertia and a bigger body; dismounts by itself in narrow areas (the test area's corridors) and whistles the horse back when leaving, or toggles with Shift / L3; on foot 95% speed and -25% damage. Momentum fills while galloping (+10/s) and on hits (+5 mounted, +8 on foot) and drains standing still. Lance thrusts, Charge through a line, Heavy Armor, Challenge (taunt), Trample, Lance Sweep, Unstoppable, banners as supports and three-charge finals, with weaker on-foot versions (`docs/02-3-cavaleiro.md`).
- **The Sewers (phase 7):** the sewer grate leads to the four areas of the first map — the Main Street Drains (the combat tutorial), the Refuse Canals, the Secret War Passage (the Old Gator) and the Queen's Nest. Plague Rats in swarms, charging Mutant Rats, Plague Bats, Acid Toads that spit at a marked spot and leave toxic puddles, Gators hiding in the water; elites with a golden aura, sludge puddles, a secret chest in every area, a checkpoint at every entrance. The exit only takes the group when everyone is there (or the host counts down 10 s). Beating the Rat Queen opens the Lost Treasure of the War and the way back.
- **Tortuga (phase 6, first part):** a new campaign starts in the **Drowned Crow Tavern** with the **opening**: each hero tells their own story (in solo, the heroes you didn't pick are NPCs who invite you; "Skip opening" is always there, and the journal replays it). **Tutorial tips** show up once per character, right when they matter (move, attack, potion, loot, level up, element…), with the buttons of the device you're using and without pausing; turn them off in Options, reread them in the journal. Then the **Old Drunk** tells the story of the treasure under the town and gives the first quest (weak to Fire), which unlocks the **sewer grate**; the Tavern Keeper lets you rest; the Bard sings. Out on the **Main Street**: Apothecary, Weaponsmith and Armorer (common gear of your class at 2x value), and at the port the **Pirate Market**, a pirate ship docked at the pier with a pirate vendor in front of it — 3–6 magic/rare/unique items per player that change with every ship (3x value), Elemental Potions (100 + 25 × level), and the only buyer of valuables, at the price of the day. Shops buy equipment at 25%. The sewer grate leads to the test area (standing in for the Sewer until phase 7); clearing it completes the quest, and the return portal brings everyone back to Tortuga, ends the Elemental Potion and brings a new ship. The whole group travels together; prompts show what you can interact with (G / right click). The **Witch Doctor** opens portals to the checkpoints you've reached (40 + 15 × area level per player) and sells the **Return Charm** (150 gold), which opens a portal on the ground back to Tortuga for 15 s. The **stash** keeps items for all your characters on this PC, and the **Old Master** gives back attribute and skill points for gold (50 × level, proposal). Every return brings **2–4 visitors** to the Tavern (pirate, bounty hunter, deserter, merchant, stranger), each telling a story — what's going on, the creature's legend, the reward and the weakness hint — that becomes a **side quest** (hunt N creatures, a rumor that may be treasure, an ambush or nothing, or lost cargo to find; up to 5 active). Stories fill the **bestiary**, which the Bard opens; the **quest journal** is in the inventory. The **Blacksmith** sells Iron and Steel refining scrolls and refines your gear (+1 to +3 safe; +4 65% and +5 45% — a normal scroll breaks the item into crystals, a blessed one only resets it; uniques and legendaries never break), crystallizes items and makes scrolls from 10 crystals; refined weapons light an aura in your origin element's color, and a full armor set at +4 gives +5% health. Behind the Main Street, the **training yard**: straw dummies of each element (to see weakness and resistance), an armored one (half damage), a boss-sized one (gets a slow instead of control), a group of small ones; they never die and give nothing; the group's damage, DPS, biggest hit and crits show at the top while you're in the yard, and the training board resets the panel and the dummies or turns on free resources and cooldowns.
- **Blocking (phase 5):** hold C / LB facing the hit — Mage and Summoner raise a barrier that spends mana/Essence per damage blocked (the Mage's absorbs up to 30% of max health), the Knight raises the shield (-60% frontal damage, 2 Momentum per second), the Ninja parries (-50%; pressed up to 0.3 s before the hit it cancels it and counter-attacks with a guaranteed crit). The Archer doesn't block. The Knight's horse wears **barding** (new equipment slot; its armor only counts while mounted).
- **Elements (phase 4):**
  - Every character picks an origin element at creation (Water, Fire, Air, Earth); every monster has one too, shown as a colored gem above it.
  - Weakness cycle Water > Fire > Earth > Air > Water: +50% damage on the weakness, -50% on the same element. Damage numbers are bigger and in the element's color on a weakness, small and gray when resisted; criticals (5% base, x1.5) end with "!".
  - The strong attack applies the element's basic state: burning (damage over time), soaked (slower), shocked (+15% Air damage) or a 30% chance to stun (Earth). Frozen, knocked down and stunned stop monsters; bosses get a slow instead.
  - Combos between players: Electrocute (soaked + Air), Wildfire (burning + Air spreads the fire), Mud (soaked + Earth: slowing area), Steam (burning + Water: area where monsters miss 30% of attacks), Melt (stunned + Fire, +30%).
  - **Elemental Potion** (3 / D-pad right): switches the element until returning to Tortuga; for now they drop as loot, until the Pirate Market (phase 6).
- **RPG systems (phase 3):**
  - **Character sheet:** level up to 20, XP to the next level = 700 × level, +5 attribute points and +1 skill point per level; health, mana, power and armor from `docs/13-balanceamento.md`. The host validates the character a player brings (no edited attributes, items or levels).
  - **Items as data** (`data/*.json`): materials from cloth/wood to gold, rarities with affixes, Mage equipment, potions and valuables. Item names are built from translated parts.
  - **Individual loot:** rolled per player on the server and shown only to its owner; pick up with *Interact* or *Pick up all*; gold is picked up automatically; XP is divided among the players present.
  - **Inventory** (I / Back), navigable with the gamepad: equipment slots, 40-slot bag, attribute points and an item tooltip compared with what is equipped. Equipment shows on the hero for everyone.
  - **Potions** (1 health, 2 mana) with a shared cooldown; HUD with XP bar, gold, potions and "saving…".
  - **Trading in co-op:** *Trade with the nearest ally* in the inventory invites a player close by; each side offers bag items and gold, any change undoes both confirmations, and the server swaps everything at once only when both confirm (`docs/05-itens-e-loot.md`, section 8).
  - **Saves** (`docs/11-saves.md`): JSON with `save_version`, written through a temp file, 3 backups and recovery from a corrupted save. The character is saved on its owner's PC; the campaign (encounter groups already defeated, checkpoints reached, play time, heroes and a thumbnail) on the host. During play, saves are written on a background thread. Up to 12 characters and 6 campaigns per PC, with *Delete* in the lists. A character file edited outside the game is detected by its checksum and only triggers a warning.
  - Main menu: choose or create a character, *Continue* / *New campaign* / *Load campaign* (play solo or host it on the LAN). In-game menu: *Save and quit*.
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

Default controls — keyboard: WASD move, mouse aim, left click attack (hold for strong attack), Q/E/R/F skills, K skills window, Shift mount (Knight), C block, Space dodge, right click / G interact, Z pick up all, 1/2 potions, 3 Elemental Potion, I inventory, Esc pause. Gamepad: left stick move, right stick aim, RT attack, A/B/X/Y skills, L3 mount, LB block, LT dodge, RB pick up all, D-pad down/up potions, D-pad right Elemental Potion, Back inventory, Start pause.

## Tests
```bash
godot --headless --path . --import
godot --headless --path . --script res://tests/run_tests.gd            # translations and data
godot --headless --path . res://tests/rpg_tests.tscn                    # RPG formulas, bag, validation, saves, edited character, trade
godot --headless --path . --fixed-fps 60 res://tests/smoke_arena.tscn  # a bot clears every encounter, collects its loot, equips an item and checks the save
godot --headless --path . res://tests/smoke_arena.tscn -- revive        # downed, revive, back to checkpoint
godot --headless --path . res://tests/smoke_arena.tscn -- elements      # states, combos, burning, steam area, Elemental Potion on real monsters
godot --headless --path . res://tests/smoke_arena.tscn -- skills mage   # every Mage skill on real monsters, hotkeys, passives
godot --headless --path . res://tests/smoke_arena.tscn -- skills archer # every Archer skill
godot --headless --path . res://tests/smoke_arena.tscn -- skills ninja  # every Ninja skill
godot --headless --path . res://tests/smoke_arena.tscn -- skills summoner # every Summoner skill, companions, Rescue
godot --headless --path . res://tests/smoke_arena.tscn -- skills knight  # every Knight skill, mount/dismount in narrow areas
godot --headless --path . res://tests/smoke_arena.tscn -- town          # Tavern quest, rest, shops, Pirate Market, sewer, quest done, return portal
godot --headless --path . res://tests/smoke_arena.tscn -- trade         # invite, offers, confirmations, trade, cancel by distance
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
