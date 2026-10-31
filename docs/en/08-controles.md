# Controls

> Version 1 · 2026-10-30 · Keyboard/mouse and USB controller (gamepad) on PC Linux.
> Points marked **proposal** are suggestions to review.

## 1. Requirements

- The game works with **keyboard + mouse** and with a **USB controller** connected to the PC.
- The player can **configure (remap) the buttons** of the controller and the keyboard in an options menu.
- **Hot plug/unplug:** plugging in a controller during the game must work without restarting. If the controller disconnects mid-match, the game **pauses** (solo) or shows a warning (co-op) until it reconnects.
- The interface switches the **button icons** automatically according to the last device used (keyboard or controller).
- The whole interface (menus, inventory, shops, dialogues, skill tree) must be **navigable with the controller alone**.

## 2. Implementation (Godot 4)

- Use Godot's **Input Map** with **actions** (never fixed keys in code). Each action has a keyboard/mouse event and a controller event.
- Godot uses the **SDL GameControllerDB**: Xbox, PlayStation (DualShock 4/DualSense), 8BitDo and generic USB controllers already come mapped on Linux.
- Remapping saved in `user://controles.cfg` (ConfigFile), loaded at startup. "Restore defaults" button.
- Signal `Input.joy_connection_changed` to detect connection/disconnection.
- Configurable analog stick **dead zone** (default 0.2).
- Vibration (`Input.start_joy_vibration`) on heavy damage taken and when a boss is defeated, with an option to turn it off.
- **One controller per PC:** since co-op is over LAN (each player on their own PC), there is no split screen; each PC uses one keyboard or one controller.

## 3. Actions and default mapping

| Action (ID) | Keyboard + mouse | Controller (Xbox default) |
|---|---|---|
| `move` | W A S D | Left stick |
| `aim` | Mouse position | Right stick (if released: aims in the movement direction) |
| `attack` | Left button | RT |
| `skill_1` | 1 | A |
| `skill_2` | 2 | B |
| `skill_3` | 3 | X |
| `skill_4` (ultimate skill) | 4 | Y |
| `evade` (dodge / Ninja teleport) | Space | LT |
| `mount` (Knight mounts/dismounts) | Shift | L3 |
| `potion_health` | Q | D-pad ↓ |
| `potion_mana` | E | D-pad ↑ |
| `potion_elemental` | R | D-pad → |
| `interact` (talk, open chest, pick up item) | Right button or G | A (when something is nearby; otherwise `skill_1`) — **proposal**: dedicated RB |
| `pickup_all` | Z | RB |
| `inventory` | I | Select / View |
| `menu` (pause in solo) | Esc | Start / Menu |
| `map` | M | D-pad ← |
| `chat_quick` (co-op quick phrases) | T | R3 |

- **Aiming with a controller:** ranged attacks use light **aim assist** (pulls toward the nearest enemy in the aim cone). Proposal: 15° assist, adjustable/can be turned off.
- On the controller, skills can be moved to other buttons in the skill tree.

## 4. Control options menu

- List of actions with the current button; select one and press the new button to change it.
- Warn if the button is already in use (swap between the two actions).
- Aim stick sensitivity, dead zone, invert Y axis, vibration on/off, aim assist on/off.
- Controller test (shows the buttons pressed).

## 5. Open decisions

- Interact: use a dedicated button (RB) or the same as the skills when something is nearby?
- Quick chat in co-op: which phrases (e.g. "Here!", "I need healing", "Watch out!")?
- Icons: show Xbox or PlayStation style depending on the detected controller?
