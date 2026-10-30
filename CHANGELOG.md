# Changelog

## [Unreleased]

### Phase 2 — basic LAN network
- `NetworkManager` autoload: ENet host/client with authoritative server; solo uses the same server offline.
- LAN discovery by UDP broadcast and manual `IP:port` join; host refuses different version, different game data (content hash) or a full game.
- Players, monsters and projectiles replicated with MultiplayerSpawner/MultiplayerSynchronizer; client input sent as intent (~30 Hz, buttons immediate); state at ~20 Hz with ~100 ms interpolation.
- Test area to explore instead of waves: start room (checkpoint), corridor and two chambers; monsters in encounter groups that sleep until a player is near, alert nearby groups and stay dead (`docs/03-inimigos.md`).
- Join mid-game next to the host; monster health +60% and damage +10% per extra player, applied when a group wakes.
- Dropped client: hero waits 30 s still and invulnerable; rejoining in time takes it back. Normal leave removes the hero at once.
- Downed state and revive (hold Interact 3 s, interrupted when the reviver is hit); everyone down returns to the checkpoint.
- Co-op HUD: allies' health, player color rings, hosting IP; no pause in co-op.
- Network tests in CI (host + client in two processes, version refusal, drop and rejoin, revive).

### Phase 1 — solo combat prototype
- Godot 4.7.2 project (Compatibility renderer) with the repository layout from `docs/10-distribuicao.md`.
- Mage with basic attack, strong attack and dodge; sewer rats in 3 waves.
- Top-down camera with limited zoom.
- Keyboard/mouse and USB gamepad with rebinding, aim assist, dead zone, vibration and pause on disconnect.
- Key-based translation system (en, es, pt_BR), language switch without restarting.
- Automated tests and Windows/Linux builds on GitHub Actions.
