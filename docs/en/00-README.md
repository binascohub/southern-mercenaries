# Southern Mercenaries — Documentation

Design documentation for **Southern Mercenaries**, a LAN co-op action RPG, written to serve as the basis for implementation (including by an AI assistant such as Claude). Open source game (GPL-3.0-or-later) for Windows and Linux, in English, Spanish and Portuguese.

> Languages of these docs: Portuguese (`../`, the source), English (`en/`) and Spanish (`es/`), with the same file names. When in doubt, Portuguese is the source.

## Reading order

| File | Content |
|---|---|
| `01-escopo.md` | Overview, camera, mechanics, LAN multiplayer, technology, languages, v1.0 content, phases |
| `02-personagens.md` | Overview of the 5 classes, visual clothing/equipment, attributes, general rules |
| `02-0-elementos.md` | Elements, weakness cycle, Elemental Potion, states, combos and skill composition |
| `02-1-mago.md` | Mage in detail |
| `02-2-arqueiro.md` | Archer in detail |
| `02-3-cavaleiro.md` | Knight in detail (Dorian and Dália) |
| `02-4-ninja.md` | Ninja in detail (Ren and Rin) |
| `02-5-invocador.md` | Summoner in detail |
| `03-inimigos.md` | The 10 maps, monster families (mechanics and element), elites, mini-bosses, bosses and Lucifer |
| `03-1-bestiario.md` | Real legends of each creature and the weakness hints told by NPCs and the Jester |
| `03-2-areas.md` | Division of the 10 maps into 41 areas, levels, checkpoints, mini-bosses |
| `04-tortuga-e-missoes.md` | Tortuga (first home-base city), tavern, Pirate Market, NPCs and quest system |
| `04-1-capital-real.md` | Royal Capital (second home-base city, the Knight's city), higher-end trade, Court Jester |
| `05-itens-e-loot.md` | Categories, materials (cloth/wood → gold), rarities, treasures, valuables, markets, inventory |
| `05-1-refino.md` | Lineage 2–style refining with scrolls (+1 to +5, safe up to +3, failure and crystals) and the aura around the hero |
| `06-mundo-e-historia.md` | Premise, the war, campaign structure in acts, opening, treasures and heroes' motives |
| `07-rede.md` | Authoritative server, LAN discovery, synchronization, individual loot, joining and leaving mid-match |
| `08-controles.md` | Keyboard/mouse and USB controller, default mapping, remapping, options |
| `09-interface.md` | **Visual identity of the game (the rule for everything visual)**, closer camera like Dark Alliance, HUD, menus, screens and options |
| `14-tutorial.md` | First minutes, contextual tips, starting equipment and the tutorial in the Sewers |
| `13-balanceamento.md` | Formulas and tables for damage, health, armor, XP, gold, prices and balance goals |
| `12-audio.md` | Soundtrack per map and boss, effects, ambience, interface sounds, hero voices and audio licenses |
| `10-distribuicao.md` | Open source licenses, repository, Windows/Linux builds, installers, GitHub Actions, website |
| `15-modos.md` | New game from zero, difficulties (Story, Normal, Nightmare) and expeditions, after v1.0 |
| `11-saves.md` | Character and campaign saves, autosave, checkpoints, continuing in solo and co-op |

## Rules for implementers

- **Engine:** Godot 4 (pinned stable version), Compatibility renderer (OpenGL 3.3), **GDScript**. Performance on integrated graphics is a requirement, not an optional optimization.
- **Platforms:** Windows and Linux with the same features; test both and co-op between them.
- **Network:** authoritative server; solo mode uses the same server running locally. Rolls (loot, refining) always on the server.
- **Controls:** full USB controller support from the first playable phase; use Input Map actions, never fixed keys (`08-controles.md`).
- **Languages:** en, es and pt_BR. **No fixed text in code, scenes or data** — always translation keys with `tr()`; the network and saves use IDs, never translated text (`01-escopo.md`, section 6). The texts of this documentation are in Portuguese (source) and also in English (`en/`) and Spanish (`es/`); the game's translations are made by Claude.
- **Visible equipment:** everything equipped appears on the character, piece by piece, with its material; refining creates an aura around the hero (`05-itens-e-loot.md`, `05-1-refino.md`).
- **Saves:** safe writes with backups and a version number from the first save (`11-saves.md`).
- **Areas:** each map area is a separate scene, with a checkpoint at the entrance (`03-2-areas.md`).
- **Open source:** only own assets (created by Claude from the author's references, without copying any game) or freely licensed ones; record everything in `CREDITS.md` (`10-distribuicao.md`).
- **Data separate from code:** classes, elements, skills, items, materials, scrolls, refining, monsters, bestiary, NPCs, shops, areas and quest templates live in data files, using the IDs defined in the documents (e.g. `knight`, `fire`, `fireball`, `headless_mule`, `tavern_keeper`, `court_jester`, `sewers_01_drains`, `steel`).
- **Official sources:** each class's detailed file outranks the summary in `02-personagens.md`; `02-0-elementos.md` applies to all classes and monsters; `03-1-bestiario.md` is the source of story lines and hints; `06-mundo-e-historia.md` defines the campaign order (10 maps); `05-itens-e-loot.md` defines the materials.
- **Campaign 2 (design rule):** the sequel must **always** start with the heroes **poor again** (underwear only, wooden weapon, no gold, no refining, level 1). Campaign 1 transfers nothing; the story justifies it (`06-mundo-e-historia.md`, section 9).
- **Implement in phases**, in the order of `01-escopo.md` section 9. Each phase must be playable before the next.
- Items marked **open** or **proposal** must not be decided without consulting the author.

## Planned documents

- None for now.
