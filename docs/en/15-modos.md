# Game Modes — New Game, Difficulties and Expeditions

> Version 1 · 2026-10-30 · Complements `11-saves.md`, `13-balanceamento.md`, `03-inimigos.md` and `06-mundo-e-historia.md`
> **All content is a proposal** for the author to review. Items marked **open** must not be decided without consulting the author.
> Scope: **v1.0 has only Normal mode.** The modes below come after the base game is complete (final phase of `01-escopo.md`).

## 1. Summary

| Mode | Unlocks | What changes |
|---|---|---|
| **Normal** | From the start | The campaign as designed (`13-balanceamento.md`) |
| **New game** | Always | Starts **from zero**: new campaign and new character (**decided**) |
| **Nightmare** (difficulty) | After beating Lucifer once | Higher monster scaling, more loot |
| **Expedition** (replay areas) | On beating Lucifer | Return to any completed area to farm |

## 2. A new game starts from zero (decided)

- **There is no New Game+.** Every new game creates a **new campaign** and a **new character** (level 1, only underwear and a wooden weapon, `02-personagens.md`), inheriting nothing.
- The character who beat Lucifer still exists: they can continue in the **Expedition** (section 4) and in the story's sequel.
- Only what belongs to the player, not the character, persists between games: options, `tutorial_seen` (the tutorial does not repeat, `14-tutorial.md`) and the **Nightmare** unlock (section 3).
- The story follows the same principle: **Campaign 2** (future, `06-mundo-e-historia.md`, section 9) also starts from zero, and the heroes **lose everything and are poor again**.
- This keeps balance on a single curve (`13-balanceamento.md`) and the maximum level at 20.

## 3. Difficulties

Chosen when the campaign is created:

| Difficulty | Monster health | Monster damage | XP | Rare loot | Available |
|---|---|---|---|---|---|
| **Story** | -30% | -30% | ×1.0 | ×1.0 | Always |
| **Normal** | base | base | ×1.0 | ×1.0 | Always |
| **Nightmare** | +60% | +40% | ×1.3 | ×1.5 | In new campaigns, after beating Lucifer once |

- Difficulty is chosen by the **host** when creating the campaign and **can be changed in Tortuga**; players see the choice when they join.
- **Story** is for playing mostly for the story with new players or children.
- Death has no extra penalty in any difficulty (the rule in `04-tortuga-e-missoes.md` applies).
- The modifiers multiply the co-op scaling.

## 4. Expedition (replaying areas)

- After beating Lucifer, the city portal allows entering any **already completed** area with **respawned** monsters (exploration is redone, `03-2-areas.md`).
- Mini-bosses and bosses respawn **once per real-world day** (proposal) to avoid endless farming.
- The reward follows the campaign's difficulty.
- The revealed map goes back to "unexplored" in that expedition, without erasing campaign progress.

## 5. Technical notes

- Save in the campaign save: `difficulty` (`story`, `normal`, `nightmare`); in the player's options: `nightmare_unlocked`.
- Modifiers live in a data file (`data/modes.json`), never in code.
- The server applies the multipliers (authoritative); the client only displays them.
- Increase the save format version (`save_version`) when these fields arrive (`11-saves.md`).
- Mode and difficulty texts use translation keys (`tr()`).

## 6. Decisions

- **Decided:** Nightmare unlocks when beating Lucifer with **any character**.

## 7. Open decisions

- The values in section 3 come from balance tests (`13-balanceamento.md`).
