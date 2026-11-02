"""Efeitos sonoros do jogo, sintetizados do zero (ruído filtrado, senos com varredura e envelopes), sem amostras de terceiros: sem autoria externa nem licença a conferir.
Gera assets/audio/sfx/*.wav (mono, 22,05 kHz, 16 bits). Para trocar um som por outro de verdade, basta pôr um arquivo com o mesmo nome (wav ou ogg) na pasta.
uso: python3 tools/assets/build_sfx.py [pasta_de_saida]"""
import math, random, struct, sys, wave

RATE = 22050
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/audio/sfx"
random.seed(7)


def n(sec):
    return int(RATE * sec)


def noise(sec):
    return [random.uniform(-1, 1) for _ in range(n(sec))]


def lowpass(x, cutoff):
    a = min(1.0, 2 * math.pi * cutoff / RATE)
    y, s = [], 0.0
    for v in x:
        s += a * (v - s)
        y.append(s)
    return y


def highpass(x, cutoff):
    lp = lowpass(x, cutoff)
    return [v - l for v, l in zip(x, lp)]


def sweep_lp(x, c0, c1):
    """Passa-baixa cuja frequência de corte vai de c0 a c1 (o "uuush" do vento e dos golpes)."""
    y, s, total = [], 0.0, len(x)
    for i, v in enumerate(x):
        c = c0 + (c1 - c0) * i / total
        s += min(1.0, 2 * math.pi * c / RATE) * (v - s)
        y.append(s)
    return y


def tone(sec, f0, f1=None, shape="sine"):
    f1 = f0 if f1 is None else f1
    out, ph, total = [], 0.0, n(sec)
    for i in range(total):
        f = f0 + (f1 - f0) * i / total
        ph += 2 * math.pi * f / RATE
        if shape == "sine":
            out.append(math.sin(ph))
        elif shape == "square":
            out.append(1.0 if math.sin(ph) > 0 else -1.0)
        else:  # saw
            out.append(2 * ((ph / (2 * math.pi)) % 1.0) - 1)
    return out


def env(x, attack=0.005, release=0.2, curve=2.0):
    total, a, out = len(x), max(1, n(attack)), []
    for i, v in enumerate(x):
        e = min(1.0, i / a) * (1.0 - i / total) ** curve if release is None else min(1.0, i / a) * min(1.0, (total - i) / max(1, n(release))) ** curve
        out.append(v * e)
    return out


def mix(*parts):
    total = max(len(p) for p in parts)
    return [sum(p[i] for p in parts if i < len(p)) for i in range(total)]


def gain(x, g):
    return [v * g for v in x]


def delay(x, sec):
    return [0.0] * n(sec) + x


def save(name, x, peak=0.8):
    m = max(1e-6, max(abs(v) for v in x))
    x = [v / m * peak for v in x]
    fade = min(len(x), 120)
    for i in range(fade):
        x[len(x) - 1 - i] *= i / fade
    with wave.open("%s/%s.wav" % (OUT, name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32767)) for v in x))


def whoosh(sec, c0, c1, power=1.0):
    x = sweep_lp(noise(sec), c0, c1)
    total = len(x)
    return [v * math.sin(math.pi * i / total) ** power for i, v in enumerate(x)]


def thump(sec, f0, f1, noise_amt=0.25):
    body = env(tone(sec, f0, f1), 0.002, None, 3.0)
    return mix(body, gain(env(lowpass(noise(sec), 900), 0.001, None, 4.0), noise_amt))


# --- ações dos heróis -------------------------------------------------------------------------------------------------------------------
save("swing", gain(whoosh(0.22, 700, 4200), 1.0))
save("swing_heavy", mix(whoosh(0.34, 400, 2600, 0.7), gain(thump(0.2, 90, 50), 0.4)))
save("bow", mix(env(tone(0.16, 380, 120, "saw"), 0.002, None, 3.0), gain(env(highpass(noise(0.14), 2500), 0.002, None, 3.0), 0.5)))
save("hit", mix(thump(0.18, 180, 70, 0.6), gain(env(highpass(noise(0.1), 1800), 0.001, None, 5.0), 0.5)))
save("hit_crit", mix(thump(0.26, 220, 60, 0.7), env(tone(0.25, 1400, 900), 0.001, None, 4.0), gain(env(highpass(noise(0.14), 1800), 0.001, None, 5.0), 0.6)))
save("hurt", mix(env(tone(0.22, 260, 130, "saw"), 0.005, None, 2.0), gain(lowpass(noise(0.22), 1200), 0.3)), 0.7)
save("dodge", gain(whoosh(0.18, 1500, 6000), 0.9))
save("evade", mix(whoosh(0.28, 900, 5000, 0.6), gain(env(lowpass(noise(0.28), 500), 0.02, None, 2.0), 0.3)))
save("jump", env(tone(0.16, 220, 520), 0.005, None, 1.6), 0.55)
save("land", thump(0.12, 120, 60, 0.5), 0.6)
save("death", mix(env(tone(0.9, 300, 70, "saw"), 0.01, None, 1.5), gain(env(lowpass(noise(0.9), 700), 0.01, None, 1.5), 0.3)), 0.7)
save("revive", mix(*[delay(env(tone(0.5, f), 0.01, None, 2.0), 0.12 * i) for i, f in enumerate((392, 523, 659, 784))]), 0.6)
save("block", mix(env(tone(0.25, 900, 700, "square"), 0.001, None, 5.0), gain(env(highpass(noise(0.1), 2500), 0.001, None, 6.0), 0.7)), 0.7)
save("pickup", mix(env(tone(0.09, 988), 0.003, None, 2.0), delay(env(tone(0.22, 1319), 0.003, None, 2.5), 0.07)), 0.55)
save("coin", mix(env(tone(0.07, 1568), 0.002, None, 2.0), delay(env(tone(0.3, 2093), 0.002, None, 3.0), 0.06)), 0.5)
save("level_up", mix(*[delay(env(tone(0.6, f), 0.01, None, 2.0), 0.1 * i) for i, f in enumerate((523, 659, 784, 1047, 1319))]), 0.6)
save("drink", mix(*[delay(env(tone(0.07, 300 + 90 * i, 450 + 90 * i), 0.004, None, 2.0), 0.1 * i) for i in range(3)]), 0.55)
save("equip", mix(thump(0.1, 300, 120, 0.4), delay(env(tone(0.12, 1800, 1500, "square"), 0.001, None, 5.0), 0.05)), 0.6)

# --- habilidades: ataques e magias por elemento -----------------------------------------------------------------------------------
save("cast_fire", mix(whoosh(0.45, 600, 3500, 0.6), gain(env(highpass(noise(0.45), 3000), 0.01, None, 2.0), 0.4), gain(env(tone(0.4, 180, 420, "saw"), 0.01, None, 2.0), 0.3)))
save("cast_water", mix(*[delay(env(tone(0.09, 500 + 150 * i, 800 + 200 * i), 0.004, None, 2.0), 0.06 * i) for i in range(5)], gain(whoosh(0.4, 500, 2200), 0.4)), 0.7)
save("cast_air", mix(whoosh(0.5, 500, 5500, 0.8), gain(whoosh(0.5, 2500, 800), 0.5)))
save("cast_earth", mix(thump(0.45, 100, 40, 0.6), gain(env(lowpass(noise(0.45), 600), 0.02, None, 1.5), 0.5)))
save("cast_arcane", mix(env(tone(0.5, 600, 1200), 0.02, None, 2.0), delay(env(tone(0.4, 900, 1500), 0.02, None, 2.0), 0.08), gain(whoosh(0.5, 800, 3500), 0.3)), 0.6)
save("shot_magic", mix(env(tone(0.18, 700, 1500), 0.003, None, 3.0), gain(whoosh(0.18, 1000, 4500), 0.4)), 0.6)
save("explosion", mix(thump(0.7, 110, 30, 1.0), gain(env(lowpass(noise(0.7), 1800), 0.003, None, 2.5), 0.9)))
save("stomp", mix(thump(0.8, 70, 25, 0.8), gain(env(lowpass(noise(0.8), 400), 0.005, None, 2.0), 0.9), delay(thump(0.5, 90, 35, 0.5), 0.02)))
save("charge", mix(*[delay(thump(0.16, 110, 60, 0.4), 0.14 * i) for i in range(6)], gain(whoosh(0.9, 300, 1800), 0.4)))
save("flap", mix(*[delay(gain(whoosh(0.16, 600, 2200), 0.9 - 0.1 * i), 0.13 * i) for i in range(5)]), 0.7)
save("shield", mix(env(tone(0.7, 500, 950), 0.04, 0.4, 1.5), delay(env(tone(0.6, 750, 1400), 0.04, 0.4, 1.5), 0.05), gain(highpass(whoosh(0.7, 3000, 6000), 2500), 0.2)), 0.6)
save("heal", mix(*[delay(env(tone(0.5, f), 0.02, None, 2.0), 0.09 * i) for i, f in enumerate((523, 659, 784, 1047))]), 0.55)
save("buff", mix(env(tone(0.6, 300, 700, "saw"), 0.03, 0.3, 1.5), gain(env(tone(0.6, 600, 1400), 0.03, 0.3, 1.5), 0.5)), 0.55)
save("teleport", mix(env(tone(0.35, 2200, 300), 0.003, None, 2.0), gain(whoosh(0.3, 6000, 500), 0.5)), 0.65)
save("summon", mix(env(tone(1.0, 110, 330, "saw"), 0.3, 0.4, 1.5), gain(whoosh(1.0, 300, 3000, 1.5), 0.5), delay(thump(0.4, 120, 50, 0.4), 0.55)), 0.7)
save("roar", mix(env(tone(0.8, 140, 70, "saw"), 0.05, 0.4, 1.2), gain(env(lowpass(noise(0.8), 900), 0.05, 0.4, 1.2), 0.7)), 0.7)
save("slash", mix(whoosh(0.2, 1500, 7000), gain(env(highpass(noise(0.2), 3500), 0.001, None, 3.0), 0.4)), 0.8)
save("trap", mix(env(tone(0.12, 900, 500, "square"), 0.001, None, 5.0), delay(thump(0.2, 140, 60), 0.05)), 0.6)
save("smoke", gain(whoosh(0.7, 1200, 300, 0.8), 0.9), 0.6)
save("beam", mix(env(tone(0.5, 800, 1100, "saw"), 0.02, 0.2, 1.0), gain(whoosh(0.5, 3000, 5000), 0.4)), 0.55)

# --- fala de NPC: balbucio sem palavras (sílabas de vogais com formantes sobre uma voz serrada, no ritmo de uma frase), idioma incompreensível --------------
FORMANTS = {"a": (800, 1200), "e": (500, 1900), "i": (320, 2300), "o": (500, 900), "u": (330, 800)}


def formant(x, f1, f2):
    band = lambda f: sweep_lp(highpass(x, f * 0.7), f * 1.3, f * 1.3)
    return mix(band(f1), gain(band(f2), 0.6))


def babble(seed, voice):
    rnd = random.Random(seed)
    out, t = [], 0.0
    for _ in range(rnd.randint(7, 10)):
        d = rnd.uniform(0.09, 0.19)
        f0 = voice * rnd.uniform(0.85, 1.25)
        syl = tone(d, f0, f0 * rnd.uniform(0.9, 1.12), "saw")
        syl = formant(syl, *FORMANTS[rnd.choice("aeiou")])
        syl = env(syl, 0.012, 0.06, 1.0)
        out.append(delay(syl, t))
        t += d + rnd.choice((0.02, 0.03, 0.05, 0.05, 0.16))  # pausas curtas entre sílabas e uma maior entre "palavras"
    return mix(*out)


for i, (seed, voice) in enumerate(((1, 130), (2, 165), (3, 110), (4, 200)), start=1):
    save("npc_talk_%d" % i, babble(seed, voice), 0.7)

print("OK", OUT)
