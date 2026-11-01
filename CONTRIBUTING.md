# Contributing

Thanks for your interest in Southern Mercenaries!

## Before you start
- Read `docs/00-README.md`: the design docs are the source of truth for the game.
- Items marked **em aberto** or **proposta** in the docs are undecided; open an Issue to discuss before implementing them.

## Rules
- Engine: Godot 4 (pinned stable version), Compatibility renderer, GDScript.
- No hardcoded text: use translation keys (`tr()`). Languages: `en`, `es`, `pt_BR`.
- Use Input Map actions, never fixed keys (keyboard and gamepad must work).
- Must run well on integrated GPUs and on both Windows and Linux.
- **One visual identity.** Everything visual (menus, windows, HUD, characters, clothes, scenery, effects, icons) follows the identity in `docs/09-interface.md`, section 7: Tortuga at night, gold / navy / wax-red on dark leather and parchment, Pirata One titles with the brass divider, the golden rabbit crest. Do not add pieces in another style: change the new piece to fit (or propose a change to the identity for the whole game). Check new art in a screenshot next to the existing screens.
- Only add assets that are your own or CC0 / CC BY / CC BY-SA, and list them in `CREDITS.md`. No Mixamo, no assets that forbid redistribution.

## License
By contributing, you agree that your code is licensed under GPL-3.0-or-later and your art/text under CC BY-SA 4.0.

## How
1. Fork and create a branch.
2. Make focused changes and test on your OS.
3. Open a Pull Request describing what and why.

## Translations
Texts live in `locale/*.po` (gettext). Add or fix translations there; new languages are welcome.

Bugs and ideas: use GitHub Issues.
