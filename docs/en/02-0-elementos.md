# Element System

> Version 3 · 2026-10-30 · Applies to **all classes** (`02-personagens.md`) and **all monsters** (`03-inimigos.md`)
> This file is the official source for elements, weakness cycle, element swapping, states, combos and the skill composition rule.

## 1. General rule

- Every character chooses **one element at creation**: **Water, Fire, Air or Earth**. This is the **origin element** and does not change.
- The element **changes the skills**, the effect of attacks and the visuals of effects.
- The player can **swap element temporarily** with an **Elemental Potion** bought at the Tortuga Market (section 4).
- **Every monster also has an element** and is **weak to another** (section 3).
- Sex and appearance affect nothing in gameplay; **class + element** define the character.

## 2. The four elements

| ID | Element | Identity | Strength | Weakness | Colors |
|---|---|---|---|---|---|
| `fire` | Fire | Maximum damage | Area and damage over time | Little control | Orange and red |
| `water` | Water | Control and support | Slow, freeze, light healing | Lower damage | Blue and white |
| `air` | Air | Speed and lightning | Fast attacks, knockbacks, chain damage | Little defense | White and violet |
| `earth` | Earth | Defense and stun | Stuns, barriers, protection | Slower | Green and brown |

## 3. Weakness cycle

```
Water ──beats──▶ Fire ──beats──▶ Earth ──beats──▶ Air ──beats──▶ Water
```

| Monster element | **Weak to** (+50% damage) | Resists (-50% damage) | Why |
|---|---|---|---|
| Fire | **Water** | Fire | Water puts out fire |
| Earth | **Fire** | Earth | Fire melts stone and burns the forest |
| Air | **Earth** | Air | Earth traps and brings down what flies |
| Water | **Air** | Water | Lightning runs through water |

- Attacks of the monster's **same element** deal **-50%** damage; of the element **strong against it**, **+50%**; the other two deal normal damage.
- Applies to all player damage (basic attacks, skills, Summoner minions).
- Control states (`frozen`, `stunned`…) work normally; only the damage changes.

### How the player discovers the weakness
1. **In the story:** whoever tells the quest at the tavern **always mentions the monster's/demon's element and what beats it** (e.g. "that Pegasus's fire can only be put out with water"). See `04-tortuga-e-missoes.md`.
2. **In the bestiary:** the Bard records each monster's element and weakness.
3. **On the map:** each monster shows an **element icon** next to its health bar; the damage number appears **bigger and colored** when it hits the weakness, and **gray and smaller** when the monster resists.

## 4. Element swap — Elemental Potion

| Item | Value |
|---|---|
| ID | `elemental_potion_water`, `elemental_potion_fire`, `elemental_potion_air`, `elemental_potion_earth` |
| Where to buy | **Tortuga Market** |
| Price | Grows with the character's level (proposal: 100 + 25 × gold level) |
| Duration | **One expedition**: from drinking it until returning to Tortuga |
| Limit | One active potion at a time; drinking another swaps the effect |

**Effect when drunk:**
- The character uses the **new element**: attacks, basic state and effect colors.
- The **element skills** are swapped for the equivalents of the new element, **with the same ranks** (the level 6 skill of the origin element becomes the level 6 skill of the new element, and so on).
- Class skills do not change.
- On returning to Tortuga, the character goes back to the **origin element**.

**Why it exists:** each map has monsters and a demon of one element; the stories warn of the weakness, and the group prepares by buying the right potions before leaving through the port.

## 5. Skill composition

### 5.1 Skill types

Every set of element skills must have all three types:

| ID | Type | Rule | Damage range (rank 1) |
|---|---|---|---|
| `aoe` | Area | Hits several enemies; **lower damage** per target | 60% to 180% of power (ultimate: 500% to 600%) |
| `single` | Single target | Hits one enemy; **higher damage** | 280% to 350% of power |
| `support` | Support | Helps the group (healing, shield, speed, damage bonus); little or no damage | 0% to 50% of power |

"Power" = the class's damage attribute (e.g. the Mage's Magic Power).

### 5.2 Division by class

Each class has **10 skills**:

| Class | Class skills (same for all) | Element skills |
|---|---|---|
| Mage | 4 | 6: basic (level 1), area (2), **support (6)**, **single target (10)**, area (14), ultimate area (18) |
| Knight, Archer, Ninja, Summoner | 7 | 3: **support (6)**, **single target (12)**, **ultimate area (18)** |

- **Class skills:** the mechanic is the same in every element, but the strike is **imbued** with the current element: it applies that element's basic state (section 5.3) and changes the color/visual effect.
- **Element skills:** exclusive to the class + element combination.
- **Strong attack:** applies the element's basic state.

### 5.3 Basic state of each element
| Element | Basic state applied by imbued strikes and strong attacks |
|---|---|
| Fire | `burning` |
| Water | `soaked` |
| Air | `shocked` |
| Earth | 30% chance of `stunned` |

### 5.4 Support by element (theme)
| Element | Type of support |
|---|---|
| Fire | Damage bonus for allies |
| Water | Healing |
| Air | Movement and attack speed |
| Earth | Shield / damage reduction |

## 6. Elemental states

| ID | State | Source | Effect | Default duration |
|---|---|---|---|---|
| `burning` | Burning | Fire | Damage over time (default: 30% of the hit's damage per s) | 3 s |
| `soaked` | Soaked | Water | -20% movement speed | 4 s |
| `frozen` | Frozen | Water (strong) | Cannot move or attack; takes guaranteed critical hits | 2 s |
| `shocked` | Shocked | Air | Takes +15% Air damage | 4 s |
| `knocked_down` | Knocked down | Air / Earth | Down, cannot act | 1 s |
| `stunned` | Stunned | Earth | Cannot act | 1.5 s |

- Bosses are never **frozen**, **knocked down** or **stunned**: they take 50% slow instead.
- Reapplying a state renews its duration, without stacking.
- Fire monsters cannot be `burning`; Water monsters cannot be `soaked`.

## 7. Element combos (co-op)

Any player can complete another player's combo, from any class. Example: the Water Archer soaks the enemies and the Air Ninja shocks them.

| State on the enemy | + strike of | Combo | Result |
|---|---|---|---|
| Soaked | Air | **Electrocute** | +50% Air damage and stuns for 1 s |
| Burning | Air | **Wildfire** | The fire spreads to nearby enemies (3 m radius) |
| Soaked | Earth | **Mud** | Mud area that slows enemies by 40% for 5 s |
| Burning | Water | **Steam** | Cloud that makes enemies miss 30% of their attacks for 4 s |
| Stunned | Fire | **Smelt** | +30% damage on the stunned enemy |

- A combo **consumes** the state that started it.
- The weakness bonus (section 3) stacks with the combo.

## 8. Visuals and performance

- Each element has its set of effects (color, particles, sound), reused by all classes and monsters.
- Simple particles in small quantity (requirement to run on integrated graphics).
- Each class's weapon gets a glow in the color of the current element (staff crystal, spear tip, arrows, dagger blades, book pages); it changes instantly on drinking an Elemental Potion.

## 9. Open decisions

- Do items with element bonuses (e.g. "+10% Fire damage") work for any class?
- Elemental Potion price (proposal: 100 + 25 × level)?
