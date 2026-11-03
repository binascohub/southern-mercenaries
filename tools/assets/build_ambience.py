"""Sons ambientes dos mapas (assets/audio/music/ambience_<nome>.ogg), sintetizados do zero (sem pacote de terceiros), laços de 30 s sem emenda:
  forest      grilos, pássaros, coruja, folhas ao vento, riacho distante     darkwoods   vento frio, coruja, lobo ao longe, galhos rangendo, morcegos
  ruins       vento, corvos, madeira rangendo, uivo ao longe                 cemetery    (o laço de gemidos já existente) + vento forte, corvo e sino distante
  fort        vento, bandeiras, sino, tambor distante, murmúrio de guarnição  catacombs   gotas com eco, ossos, drone grave, vento de túnel
  capital     sinos de catedral, murmúrio da corte, passos, pássaros         harbor      ondas, gaivotas, madeira do cais, sino de boia (Tortuga e Docas)
  farm        galo, ovelhas, grilos, pássaros, riacho e roda d'água          mine        picaretas ao longe, gotas, rangido de vigas, zumbido de cristais
  bunker      zumbido elétrico, vapor, estalos de metal, gotas, ventilação   desert      vento forte e areia, grilos secos, grito de ave de rapina
uso: python3 tools/assets/build_ambience.py [nome ...]   (a partir da raiz do projeto; precisa do ffmpeg)"""
import math, os, random, subprocess, sys, wave, array

SR = 22050
SECS = 30
N = SR * SECS
OUT = "assets/audio/music/"
TAU = math.tau


def zeros():
    return [0.0] * N


def noise(rng):
    return [rng.uniform(-1, 1) for _ in range(N)]


def lowpass(x, fc):
    a = 1 - math.exp(-TAU * fc / SR)
    y, s = [0.0] * N, 0.0
    for _ in range(2):  # duas voltas: a segunda começa onde a primeira terminou, então o laço fecha sem emenda
        for i in range(N):
            s += a * (x[i] - s)
            y[i] = s
    return y


def highpass(x, fc):
    lp = lowpass(x, fc)
    return [a - b for a, b in zip(x, lp)]


def bandpass(x, lo, hi):
    return lowpass(highpass(x, lo), hi)


def lfo(rng, parts, floor=0.0):
    """Envelope lento, soma de senoides com número inteiro de ciclos em 30 s (fecha o laço); normalizado de floor a 1."""
    ph = [(k, rng.uniform(0, TAU), w) for k, w in parts]
    raw = [sum(w * math.sin(TAU * k * i / N + p) for k, p, w in ph) for i in range(N)]
    lo, hi = min(raw), max(raw)
    return [floor + (1 - floor) * (v - lo) / (hi - lo) for v in raw]


def layer(x, env, gain):
    return [a * b * gain for a, b in zip(x, env)]


def mix(*layers):
    out = zeros()
    for l in layers:
        for i, v in enumerate(l):
            out[i] += v
    return out


def add(buf, t, sig, gain=1.0):
    s = int(t * SR) % N
    for i, v in enumerate(sig):
        buf[(s + i) % N] += v * gain


def tone(dur, freq, amp, harm=((1, 1.0),), vib=(0, 0), noise_amt=0.0, rng=None):
    """Voz sintetizada: freq(t) em Hz, amp(t) de 0 a 1, harmônicos (n, peso), vibrato (Hz, profundidade relativa)."""
    n = int(dur * SR)
    out, ph = [0.0] * n, 0.0
    for i in range(n):
        t = i / SR
        f = freq(t) * (1 + vib[1] * math.sin(TAU * vib[0] * t))
        ph += TAU * f / SR
        v = sum(w * math.sin(ph * h) for h, w in harm)
        if noise_amt:
            v = v * (1 - noise_amt) + noise_amt * rng.uniform(-1, 1)
        out[i] = v * amp(t)
    return out


def sine_env(dur, power=1.0):
    return lambda t: max(0.0, math.sin(math.pi * min(t / dur, 1.0))) ** power


def decay_env(dur, k=5.0, attack=0.004):
    return lambda t: (min(t / attack, 1.0)) * math.exp(-k * t / dur)


# ---------------------------------------------------------------- eventos
def chirp(rng, base=None):
    f0 = base or rng.uniform(2200, 4200)
    out = []
    for _ in range(rng.randint(2, 4)):
        d = rng.uniform(0.05, 0.1)
        up = rng.choice([-1, 1])
        out += tone(d, lambda t, f0=f0, up=up, d=d: f0 * (1 + up * 0.25 * t / d), sine_env(d, 0.7), ((1, 1.0), (2, 0.15)))
        out += [0.0] * int(rng.uniform(0.03, 0.08) * SR)
    return out


def hoot(rng, f=380):
    out = []
    for d, gap in ((0.28, 0.18), (0.55, 0.0)):
        out += tone(d, lambda t, d=d: f * (1 - 0.1 * t / d), sine_env(d, 0.8), ((1, 1.0), (2, 0.25), (3, 0.08)), vib=(6, 0.01))
        out += [0.0] * int(gap * SR)
    return out


def howl(rng, f=340, dur=4.0):
    return tone(dur, lambda t: f * (0.75 + 0.55 * math.sin(math.pi * min(t / dur, 1.0)) ** 0.8 - 0.05 * t / dur), sine_env(dur, 1.6),
                ((1, 1.0), (2, 0.45), (3, 0.2), (4, 0.08)), vib=(5.5, 0.012), noise_amt=0.05, rng=rng)


def caw(rng):
    out = []
    for _ in range(rng.randint(2, 3)):
        d = rng.uniform(0.18, 0.28)
        f = rng.uniform(520, 700)
        out += tone(d, lambda t, f=f, d=d: f * (1 - 0.25 * t / d), sine_env(d, 0.6), ((1, 1.0), (2, 0.7), (3, 0.6), (4, 0.4), (5, 0.3)), noise_amt=0.25, rng=rng)
        out += [0.0] * int(rng.uniform(0.12, 0.2) * SR)
    return out


def gull(rng):
    d = rng.uniform(0.6, 1.0)
    return tone(d, lambda t: 1500 + 900 * math.sin(math.pi * min(t / d, 1.0)) ** 2 - 300 * t / d, lambda t: sine_env(d, 0.5)(t) * (0.8 + 0.2 * math.sin(TAU * 18 * t)),
                ((1, 1.0), (2, 0.5), (3, 0.3)), vib=(11, 0.03), noise_amt=0.06, rng=rng)


def hawk(rng):
    d = 1.1
    return tone(d, lambda t: 2600 - 1200 * t / d, sine_env(d, 0.4), ((1, 1.0), (2, 0.4), (3, 0.2)), vib=(14, 0.02), noise_amt=0.15, rng=rng)


def cricket_burst(rng, f=4300):
    out = []
    for _ in range(rng.randint(3, 5)):
        out += tone(0.035, lambda t: f, lambda t: math.sin(math.pi * t / 0.035) ** 2, ((1, 1.0), (2, 0.1)))
        out += [0.0] * int(0.03 * SR)
    return out


def frog(rng):
    out = []
    f = rng.uniform(150, 230)
    for _ in range(rng.randint(2, 4)):
        out += tone(0.14, lambda t: f * (1 + 0.5 * t / 0.14), lambda t: sine_env(0.14, 0.7)(t) * (0.6 + 0.4 * math.sin(TAU * 70 * t)), ((1, 1.0), (2, 0.6), (3, 0.3)))
        out += [0.0] * int(0.09 * SR)
    return out


def bell(rng, f=262, dur=5.0):
    parts = ((1.0, 1.0, 1.0), (2.0, 0.6, 0.7), (2.76, 0.5, 0.55), (5.4, 0.3, 0.35), (8.93, 0.15, 0.2))
    out = [0.0] * int(dur * SR)
    for m, w, d in parts:
        env = decay_env(dur * d, 6.0, 0.003)
        seg = tone(dur * d, lambda t, m=m: f * m, env, ((1, 1.0),))
        for i, v in enumerate(seg):
            out[i] += v * w
    return out


def creak(rng, f=90, dur=0.9):
    return tone(dur, lambda t: f + 40 * math.sin(TAU * 3 * t) + 30 * t / dur, lambda t: sine_env(dur, 0.8)(t) * (0.7 + 0.3 * math.sin(TAU * 17 * t)),
                ((1, 1.0), (2, 0.8), (3, 0.7), (4, 0.5), (5, 0.4)), noise_amt=0.2, rng=rng)


def drip(rng, f=None):
    f = f or rng.uniform(900, 1700)
    return tone(0.22, lambda t: f * (1 + 0.6 * math.exp(-t * 35)), decay_env(0.22, 7.0, 0.001), ((1, 1.0), (2, 0.2)))


def clink(rng):
    f = rng.uniform(1800, 2600)
    out = [0.0] * int(0.25 * SR)
    for m, w, k in ((1.0, 1.0, 9.0), (1.52, 0.6, 12.0), (2.31, 0.3, 16.0)):
        seg = tone(0.25, lambda t, m=m: f * m, decay_env(0.25, k, 0.0005), ((1, 1.0),))
        for i, v in enumerate(seg):
            out[i] += v * w
    return out


def bone_click(rng):
    d = int(0.012 * SR)
    return [rng.uniform(-1, 1) * math.exp(-i / (d / 4)) for i in range(d)]


def baa(rng):
    d = rng.uniform(0.6, 0.9)
    f = rng.uniform(280, 380)
    return tone(d, lambda t: f * (1 - 0.15 * t / d), sine_env(d, 0.5), ((1, 0.4), (2, 0.6), (3, 1.0), (4, 0.9), (5, 0.7), (6, 0.4)), vib=(26, 0.07), noise_amt=0.08, rng=rng)


def rooster(rng):
    out = []
    for f0, d in ((560, 0.18), (760, 0.16), (900, 0.22), (700, 0.55)):
        out += tone(d, lambda t, f0=f0, d=d: f0 * (1 + 0.25 * math.sin(math.pi * t / d)) - (150 * t / d if d > 0.5 else 0), sine_env(d, 0.5),
                    ((1, 1.0), (2, 0.7), (3, 0.5), (4, 0.3)), vib=(30, 0.03) if d > 0.5 else (0, 0), noise_amt=0.1, rng=rng)
        out += [0.0] * int(0.04 * SR)
    return out


def clank(rng):
    f = rng.uniform(500, 900)
    out = [0.0] * int(0.7 * SR)
    for m, w, k in ((1.0, 1.0, 5.0), (1.47, 0.7, 6.0), (2.09, 0.5, 8.0), (3.2, 0.3, 10.0)):
        seg = tone(0.7, lambda t, m=m: f * m, decay_env(0.7, k, 0.001), ((1, 1.0),))
        for i, v in enumerate(seg):
            out[i] += v * w
    return out


def drum(rng):
    d = 0.5
    return tone(d, lambda t: 70 * (1 + 0.8 * math.exp(-t * 18)), decay_env(d, 7.0, 0.002), ((1, 1.0), (2, 0.3)), noise_amt=0.05, rng=rng)


def place(buf, rng, count, make, gain, tmin=0.0, tmax=SECS, spacing=0.0, **kw):
    times = []
    for _ in range(count * 6):
        if len(times) >= count:
            break
        t = rng.uniform(tmin, tmax)
        if all(abs(t - u) > spacing for u in times):
            times.append(t)
    for t in times:
        add(buf, t, make(rng, **kw) if kw else make(rng), gain * rng.uniform(0.7, 1.0))


def echo(x, delays=((0.19, 0.38), (0.37, 0.25), (0.61, 0.15))):
    out = list(x)
    for d, g in delays:
        k = int(d * SR)
        for i in range(N):
            out[i] += x[(i - k) % N] * g
    return out


def wind(rng, gain, fc=500, gust=((2, 1), (5, 0.6), (11, 0.3)), floor=0.25, whistle=0.0):
    n = lowpass(noise(rng), fc)
    out = layer(n, lfo(rng, gust, floor), gain * 6)
    if whistle:
        w = bandpass(noise(rng), 700, 900)
        out = mix(out, layer(w, lfo(rng, ((3, 1), (7, 0.5)), 0.0), whistle * 12))
    return out


def brook(rng, gain, lo=700, hi=3500):
    n = bandpass(noise(rng), lo, hi)
    return layer(n, lfo(rng, ((97, 1), (131, 0.7), (53, 0.8), (17, 0.5)), 0.4), gain * 5)


def waves(rng, gain, swells=3):
    n = lowpass(noise(rng), 700)
    hiss = highpass(lowpass(noise(rng), 5000), 1500)
    env = lfo(rng, ((swells, 1), (swells * 2 + 1, 0.3)), 0.05)
    env = [e ** 2 for e in env]
    return mix(layer(n, env, gain * 8), layer(hiss, env, gain * 3))


def murmur(rng, gain):
    n = bandpass(noise(rng), 250, 1800)
    return layer(n, lfo(rng, ((120, 1), (181, 0.8), (63, 0.6), (9, 0.5)), 0.2), gain * 6)


def crackle(rng, gain, count):
    out = zeros()
    for _ in range(count):
        d = rng.randint(8, 60)
        t = rng.randrange(N)
        a = rng.uniform(0.3, 1.0)
        for i in range(d):
            out[(t + i) % N] += rng.uniform(-1, 1) * a * math.exp(-i / (d / 4)) * gain
    return out


def hum(rng, gain, f=50):
    env = lfo(rng, ((6, 1), (13, 0.4)), 0.7)
    return [(math.sin(TAU * f * i / SR) + 0.5 * math.sin(TAU * f * 2 * i / SR + 1) + 0.25 * math.sin(TAU * f * 3 * i / SR)) * env[i] * gain for i in range(N)]


def hiss(rng, gain, pulses=6):
    n = highpass(lowpass(noise(rng), 9000), 3000)
    return layer(n, [e ** 3 for e in lfo(rng, ((pulses, 1), (pulses * 3 + 1, 0.2)), 0.0)], gain * 6)


def normalize(x, peak=0.85):
    m = max(abs(v) for v in x) or 1.0
    return [v * peak / m for v in x]


# ---------------------------------------------------------------- mapas
def build_forest(rng):
    b = mix(wind(rng, 0.10, 350, floor=0.3), brook(rng, 0.05, 900, 3000), murmur(rng, 0.0))
    for _ in range(3):
        place(b, rng, 14, cricket_burst, 0.10)
    place(b, rng, 9, chirp, 0.22)
    place(b, rng, 2, hoot, 0.25, spacing=10)
    place(b, rng, 3, creak, 0.05, spacing=5)
    place(b, rng, 2, caw, 0.12, spacing=8)
    return b


def build_darkwoods(rng):
    b = mix(wind(rng, 0.22, 420, floor=0.2, whistle=0.03), crackle(rng, 0.0, 0))
    place(b, rng, 2, hoot, 0.28, spacing=10, f=310)
    place(b, rng, 1, howl, 0.20, tmin=5, tmax=22)
    place(b, rng, 5, creak, 0.08, spacing=3)
    place(b, rng, 6, bone_click, 0.12)
    place(b, rng, 7, chirp, 0.10, base=5200)  # morcegos: guinchos agudos
    return echo(b, ((0.31, 0.2), (0.55, 0.1)))


def build_ruins(rng):
    b = wind(rng, 0.20, 450, floor=0.15, whistle=0.04)
    place(b, rng, 5, caw, 0.2, spacing=4)
    place(b, rng, 5, creak, 0.09, spacing=3)
    place(b, rng, 1, howl, 0.14, tmin=6, tmax=22, f=300)
    place(b, rng, 10, bone_click, 0.12)
    return b


def build_fort(rng):
    b = mix(wind(rng, 0.14, 600, floor=0.25), murmur(rng, 0.045), crackle(rng, 0.10, 120))
    add(b, 3.0, bell(rng, 196, 5.0), 0.14)
    add(b, 18.0, bell(rng, 196, 5.0), 0.14)
    for t in (7, 7.8, 8.6, 9.4):
        add(b, t, drum(rng), 0.24)
    for t in (22, 22.8, 23.6):
        add(b, t, drum(rng), 0.24)
    place(b, rng, 6, clank, 0.07, spacing=3)
    place(b, rng, 3, caw, 0.10, spacing=8)
    return b


def build_catacombs(rng):
    b = mix(hum(rng, 0.10, 41), wind(rng, 0.12, 260, floor=0.2), layer(lowpass(noise(rng), 90), lfo(rng, ((4, 1), (9, 0.5)), 0.2), 1.3))
    place(b, rng, 10, drip, 0.35, spacing=1.5)
    place(b, rng, 14, bone_click, 0.22)
    place(b, rng, 2, howl, 0.12, tmin=4, tmax=24, f=250, dur=5.0)
    place(b, rng, 3, creak, 0.07, spacing=6)
    return echo(b, ((0.23, 0.45), (0.47, 0.32), (0.83, 0.2), (1.3, 0.12)))


def build_capital(rng):
    b = mix(murmur(rng, 0.075), wind(rng, 0.04, 500, floor=0.4), crackle(rng, 0.03, 30))
    add(b, 2.0, bell(rng, 220, 6.0), 0.2)
    add(b, 5.0, bell(rng, 294, 6.0), 0.16)
    add(b, 17.0, bell(rng, 220, 6.0), 0.2)
    place(b, rng, 12, chirp, 0.16)
    place(b, rng, 8, clank, 0.04, spacing=2)
    place(b, rng, 3, caw, 0.06, spacing=8)
    return b


def build_harbor(rng):
    b = mix(waves(rng, 0.18, 3), wind(rng, 0.07, 700, floor=0.3), murmur(rng, 0.02))
    place(b, rng, 7, gull, 0.2, spacing=3)
    place(b, rng, 6, creak, 0.10, spacing=3, f=70, dur=1.1)
    add(b, 11.0, bell(rng, 330, 3.5), 0.10)
    add(b, 11.9, bell(rng, 330, 3.5), 0.08)
    place(b, rng, 4, clank, 0.04, spacing=4)
    return b


def build_farm(rng):
    b = mix(wind(rng, 0.07, 400, floor=0.35), brook(rng, 0.06, 800, 3200), layer(lowpass(noise(rng), 180), lfo(rng, ((8, 1),), 0.3), 0.4))  # roda d'água
    for _ in range(2):
        place(b, rng, 10, cricket_burst, 0.08)
    place(b, rng, 12, chirp, 0.2)
    place(b, rng, 5, baa, 0.14, spacing=3)
    add(b, 9.0, rooster(rng), 0.18)
    place(b, rng, 4, creak, 0.05, spacing=5, f=110)
    return b


def build_mine(rng):
    b = mix(hum(rng, 0.045, 63), wind(rng, 0.08, 220, floor=0.25), layer(lowpass(noise(rng), 70), lfo(rng, ((3, 1),), 0.3), 1.0))
    for t in (4.0, 4.9, 5.8, 6.7, 17.0, 17.9, 18.8):
        add(b, t, clink(rng), 0.14)
    place(b, rng, 9, drip, 0.28, spacing=1.2)
    place(b, rng, 5, creak, 0.10, spacing=4, f=70, dur=1.1)
    place(b, rng, 6, bone_click, 0.16)
    place(b, rng, 3, clank, 0.06, spacing=6)
    return echo(b, ((0.21, 0.4), (0.44, 0.28), (0.78, 0.16)))


def build_bunker(rng):
    b = mix(hum(rng, 0.10, 50), hiss(rng, 0.05, 5), wind(rng, 0.07, 260, floor=0.4))
    place(b, rng, 5, clank, 0.18, spacing=4)
    place(b, rng, 8, drip, 0.22, spacing=2)
    place(b, rng, 3, creak, 0.09, spacing=7, f=75)
    place(b, rng, 6, bone_click, 0.12)
    return echo(b, ((0.17, 0.35), (0.39, 0.22), (0.7, 0.12)))


def build_desert(rng):
    b = mix(wind(rng, 0.26, 900, gust=((1, 1), (3, 0.7), (7, 0.4)), floor=0.2, whistle=0.02), layer(highpass(lowpass(noise(rng), 6000), 2500), lfo(rng, ((2, 1), (5, 0.5)), 0.1), 0.3))
    place(b, rng, 14, cricket_burst, 0.05, f=5200)
    place(b, rng, 2, hawk, 0.18, spacing=10)
    place(b, rng, 1, howl, 0.10, tmin=8, tmax=22, f=420, dur=3.0)
    place(b, rng, 3, creak, 0.04, spacing=8, f=100)
    return b


def build_cemetery(rng):
    out = "/tmp/_cemetery_ghosts.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", OUT + "ambience_cemetery_ghosts.ogg", "-ar", str(SR), "-ac", "1", out], check=True)
    w = wave.open(out)
    raw = array.array("h")
    raw.frombytes(w.readframes(w.getnframes()))
    w.close()
    ghosts = [raw[i % len(raw)] / 32768 for i in range(N)]
    # o laço original tem 40 s: usamos 30 s dele (os gemidos ficam um pouco mais próximos) e misturamos vento forte, corvo e um sino
    b = mix(ghosts, wind(rng, 0.26, 500, floor=0.15, whistle=0.05))
    place(b, rng, 3, caw, 0.12, spacing=8)
    place(b, rng, 4, creak, 0.08, spacing=4)
    add(b, 14.0, bell(rng, 175, 6.0), 0.14)
    place(b, rng, 1, hoot, 0.14, spacing=1)
    return b


BUILDERS = {"forest": build_forest, "darkwoods": build_darkwoods, "ruins": build_ruins, "fort": build_fort, "catacombs": build_catacombs, "capital": build_capital,
            "harbor": build_harbor, "farm": build_farm, "mine": build_mine, "bunker": build_bunker, "desert": build_desert, "cemetery": build_cemetery}


def export(name, x):
    x = normalize(x)
    tmp = "/tmp/_amb_%s.wav" % name
    w = wave.open(tmp, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(array.array("h", [int(max(-1, min(1, v)) * 32000) for v in x]).tobytes())
    w.close()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-c:a", "libvorbis", "-q:a", "3", OUT + "ambience_%s.ogg" % name], check=True)
    os.remove(tmp)
    print("OK ambience_%s.ogg" % name)


if __name__ == "__main__":
    names = sys.argv[1:] or list(BUILDERS)
    ghosts = OUT + "ambience_cemetery_ghosts.ogg"
    if "cemetery" in names and not os.path.exists(ghosts):
        os.rename(OUT + "ambience_cemetery.ogg", ghosts)  # guarda o laço de gemidos original (fonte) ao lado do resultado misturado
    for n in names:
        export(n, BUILDERS[n](random.Random("amb-" + n)))
