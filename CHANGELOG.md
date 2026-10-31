# Changelog

## [Unreleased]

### Phase 7 — The Tortuga Sewers (in progress)
- The real Sewers (`docs/03-2-areas.md`, section 3), four areas after the sewer grate: **Main Street Drains** (combat tutorial: a lone rat, then three, sludge puddles, the swarm of 8 and the Mutant Rat), **Refuse Canals** (Acid Toads, Plague Bats, rotten bridges, the pirates' smuggling cache), **Secret War Passage** (the Archer's kingdom crest — the Archer recognizes it —, flooded chambers, the **Old Gator** mini-boss) and **the Queen's Nest** (the Rat Queen). Each area starts at a checkpoint (Witch Doctor portals), has a secret chest, sludge puddles and 1–3 elites; the return portal is at the map entrance and appears after the boss.
- Sewer creatures (`data/monsters.json`, from `docs/03-inimigos.md`): Plague Rat (swarms), Mutant Rat (charge with a warning), Plague Bat (fast flyer), Acid Toad (keeps its distance and spits acid at a marked spot on the ground, leaving a toxic puddle), Sewer Gator (hidden in the water — only bubbles show — until someone gets close), Old Gator and the Rat Queen (1,000 × boss factor 4.3; her three phases come in the next delivery). Placeholder look per family and an aura for elites (gold), mini-bosses (purple) and bosses (red).
- Monster categories: elite (health x3, damage x1.5, 25 XP × level, 1–2 items, at least magic), mini-boss (x6/x1.8, rare guaranteed), boss; the toxic elite modifier leaves sludge puddles. Loot tables for elites, mini-bosses, bosses, chests and the Lost Treasure of the War.
- Moving on: the exit to the next area takes the group only when every standing hero is near it; otherwise everyone sees who is missing, and the host can press again to start a 10 s countdown (`docs/03-2-areas.md`, section 1). Rooms can have doors on any side, off-center.
- Only the last area of a map ends in victory ("The Rat Queen has fallen."): the quest is completed there, and the Lost Treasure of the War (loot for each player) and the return portal appear. The test area stays as the development area (attack to restart).
- Side quests now happen in Sewer areas 1–3 with the creatures that live there; a hunt brings its own pack (with an elite) to a spot of the area, since dead monsters never come back.
- Tests: Sewer data and category unit tests; a new CI step walks the four areas (sludge, ground strikes, the Toad's spit, the Gator's ambush, the Mutant Rat's charge, the toxic elite, the secret chest, the group exit); the town test goes from the grate to the Queen and the treasure.

### Phase 6 — Tortuga (in progress)
- Areas by name: the level scene loads any area of `data/arenas.json` (Tortuga's Main Street and port, the Tavern, the test area as the Sewer stand-in) and the server moves the whole group with `_load_area`, without changing scenes; players joining mid-game receive the current area. Area props: shops, NPCs, exits and signs, with an interact prompt.
- New campaigns start in the Tavern; the campaign keeps quests, what is unlocked and the ship of the day.
- Tavern NPCs (`data/npcs.json`): Old Drunk with the first quest (`data/quests.json`, unlocks the sewer grate), Tavern Keeper (rest), Bard; dialogue window with accept/decline; "!" over NPCs with a quest; active quest in the HUD with the target's weakness.
- Shops (`data/shops.json`, `Shops`, `Town`, shop window): Apothecary, Weaponsmith and Armorer (class commons of wood/cloth, iron and steel at 2x), Pirate Market (per-player stock of 3–6 magic/rare/unique items per ship at 3x, Elemental Potions at 100 + 25 × level, buys valuables at 80–120% of the day); selling equipment and consumables at 25%. Purchases and sales validated on the server.
- The Pirate Market is a pirate ship docked at the end of a pier in Tortuga's port, with a pirate vendor in front of the ship (author's decision, recorded in `docs/04-tortuga-e-missoes.md`); the quay and the pier have low walls so the sea and the ship are visible.
- Expedition cycle: clearing the quest's area completes it (provisional reward of 150 gold and 300 XP for each player); the return portal brings the group to Tortuga, ends the Elemental Potion and brings a new ship.
- Training yard (`docs/04-tortuga-e-missoes.md`, section 5.2) south of the Main Street: straw dummies per element, armored (50% damage), giant (boss rules) and small dummies that never die and give no XP or loot; group training panel (total, DPS, biggest hit, crits) in the HUD inside the yard; training board to reset the panel or the dummies and toggle free resources and cooldowns. Companions also attack dummies. Proposals still open (attacking dummy, testing locked skills, element altar) are not done.
- Witch Doctor (`docs/04-tortuga-e-missoes.md`, section 5.1) in a Main Street alley: portals to the map checkpoints reached (40 + 15 × area level, paid by each player; the warning names who lacks gold) and the Return Charm (150 gold, stacks to 5), which opens a portal on the ground back to Tortuga for 15 s on the maps and saves the checkpoint as the way back.
- Stash (shared by the player's characters, stored on their PC; the server moves items between bag and stash) and the Old Master (redistribute attribute and skill points for 50 × level gold, proposal).
- Tavern drinks are not implemented: they are an open decision in the docs.
- Bestiary (`data/bestiary.json`, from `docs/03-1-bestiario.md`): the six Sewer creatures with legend, element and hint in three languages; entries are added when a story is heard (Old Drunk, Bard, visitors); the Bard opens the bestiary window.
- Tavern visitors and generated side quests (`data/visitors.json`, `SideQuests`): 2–4 visitors per return with generated names and a story from templates — hunt (kill N), rumor (treasure, ambush or nothing at a spot) and retrieve (lost cargo at a spot); up to 5 active; progress and rewards for every player; quest spots and cargo appear on the map. Rescue and purge quests wait for real maps.
- Quest journal (from the inventory) with active and completed quests and the target's weakness.
- Refining (`docs/05-1-refino.md`, `data/refine.json`, `Refine`): weapon/armor scrolls per material (normal and blessed) and crystals; the Blacksmith's forge refines equipped or bag items (server roll; +1–+3 safe, +4 65%, +5 45%; normal failure breaks into crystals, blessed or unique/legendary reset to +0; risky attempts ask for confirmation), crystallizes items and crafts scrolls (10 crystals + 25% of the price, proposal); sells Iron and Steel scrolls. Aura around the hero by the weapon's refine in the origin element's color (pulsing at +4/+5) and a body glow with the full armor set at +4, which also gives +5% health.
- Tavern opening (`docs/06-mundo-e-historia.md`, section 5; `data/opening.json`, `Opening`): whoever is in the Tavern before the first quest is accepted hears the heroes' stories — the players' heroes first, in arrival order, then the heroes nobody picked as NPCs (Knight, Ninja, Archer, Mage, Summoner) who invite the group; Dorian/Dália and Ren/Rin have their own stories. It ends with the toast and the Old Drunk calling the group over. Each PC reads at its own pace with "Skip opening"; the journal's "Heroes' stories" replays it. Skipping in co-op is per player, not a host vote (simplification).
- Tutorial tips (`docs/14-tutorial.md`, section 4; `data/tips.json`, `TipManager` autoload, `TipWatcher`): 20 contextual tips (move, interact, attack, heavy strike, skill, dodge, potion, loot, equip, level up, element, checkpoint, revive, elite, boss, return portal, shop, refine, Elemental Potion, Knight mount) shown once per character, one at a time by priority, in a balloon with the current device's buttons, without pausing. Seen tips are stored in the character (`tutorial_seen`, older saves migrate with an empty list) through the server; Options → Tutorial tips turns them off; the journal's "Tips" lists the ones seen. `tip_map` and `tip_ally_arrow` wait for the map and the ally arrows.
- Starting kit per `docs/14-tutorial.md`: 150 gold, 3 health potions and 1 resource potion. Elemental Potions no longer drop as loot.
- Tests: shop rules, town rules, opening and tips unit tests; a full walk through Tortuga in CI (opening, first tip); `opening.png` capture.

### Phase 5 — Classes and skills
- Skill system (`data/skills.json`, `Skills`, `SkillSystem`): 10 skills per class, ranks 1–5, unlocked at levels 1, 2, 4… 18, one skill point per level; the element's basic skill comes at rank 1 on hotkey 1. Element skills are stored by unlock level, so an Elemental Potion swaps them for the new element's with the same ranks.
- Mage (`docs/02-1-mago.md`, section 6): Sharp Mind, Teleport, Mana Shield, Elemental Mastery and the 6 skills of each element (24), with effects for projectiles (Fireball explodes), novas, cones that push, lines, instant bolts, chains, buffs, shields, teleport, delayed strikes (Meteor, Earthquake) and lasting areas (Fire Wall, Blizzard freezing after 3 s, Tornado pulling, Storm bolts, Healing Rain). All damage goes through the element rules (weakness, combos, crits).
- Hotkeys `skill_1`–`skill_4` validated on the server (rank, mana, cooldown); HUD skill bar with cooldowns and gray when out of mana; Skills window (K, or from the inventory) to learn ranks and set hotkeys; shield shown on the health bar.
- Characters saved before phase 5 get the basic element skill without being flagged as edited.
- Archer (`docs/02-2-arqueiro.md`): Focus resource (regenerates 15/s standing, 5/s moving), Shot Power from DEX, 16 m arrows, 1.5 s charged shot, dodge every 3 s; bow, hunter's cap and leather vest item bases; bow and quiver placeholder visuals.
- Archer skills: 7 class skills imbued with the current element's basic state (Precise Shot with a guaranteed crit, Back Leap that slows, Eagle Eye crit chance/damage, Spike Trap that roots, Arrow Fan, Piercing Arrow, Mark Target that makes the target take more damage from everyone) and 3 per element (Campfire/Spring/Wind/Bulwark supports, Flaming/Frost/Thunder/Rockbreaker arrows, Fire/Hail/Stone rains and Storm Volley with jumping bolts).
- New states: hampered (40% slow), rooted (can't move but still attacks), marked.
- Ninja (`docs/02-4-ninja.md`): melee basic slashes and spinning strong attack, evasion (10% + 0.2% per DEX, plus the Evasion passive), teleport dodge, Energy +3 per crit, +10% gold found; daggers and mask item bases; dagger visuals.
- Ninja skills: Twin Slash, Shadow Step (behind the target, next hit +30%), Backstab (always crit from behind), Smoke Bomb (monsters lose the target; 50% misses in the cloud), Iron Body (-50% damage and taunt), Evasion, Blink Strike; seals, element cuts and the Thousand Cuts finals.
- Summoner (`docs/02-5-invocador.md`): Essence (120, +2 per INT, +3 per companion hit), book item base, book and shoulder-bird visuals.
- Friendly animals (`Companion`, `data/companions.json`): server AI like monsters, replicated by a spawner; follow the Summoner and attack awake monsters near them with the Summoner's current element; monsters attack them too; they flee when they fall; up to 5 per Summoner. Group buffs, shields and heals also reach animals.
- Summoner skills: Call Companion, Flock, Bond, Scatter Escape (animals taunt), Guardian Bear, Stampede, Rescue (revives a downed ally from afar) and 3 per element.
- Fix: woken monsters stayed in the sleep state and never chased or attacked (a `state = CHASE` line had ended up after a `return` in phase 3); found by the Summoner test, where companions only fight awake monsters.
- Knight (`docs/02-3-cavaleiro.md`): mounted with inertia (120%) or on foot (95%, -25% damage); auto-dismount in rooms marked `narrow` (the test area's corridors) and remount after leaving, or the `mount` action; Momentum resource (gallop, hits, idle drain); lance, helm and plate item bases; horse, lance and shield placeholder visuals; mounted strong attack lunges forward.
- Knight skills: Lance Thrust, Charge (mounted 15 m knockdown / on-foot shield rush), Heavy Armor, Challenge, Trample, Lance Sweep, Unstoppable, banners and three-charge finals with on-foot versions.
- Blocking (`block` action, C / LB — proposal added to `docs/08-controles.md`): frontal only; Mage barrier (mana per damage, up to 30% of max health), Summoner barrier (Essence per damage), Knight shield (-60%, 2 Momentum/s), Ninja parry (-50%, Energy per damage; within 0.3 s of pressing it cancels the hit and counter-attacks at 150% with a guaranteed crit). The Archer has no block.
- Horse barding: new `barding` equipment slot for the Knight (item base `barding`, armor 8, proposal), shown on the horse and counted only while mounted; older characters get the empty slot.
- Monsters' hits now carry the attacker, used for frontal blocks and parry counters.
- Not yet: Fire Wall does not block monsters; Book of Friends pages (with the maps).

### Phase 4 — Elements
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
