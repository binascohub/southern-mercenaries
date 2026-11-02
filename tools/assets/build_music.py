"""Músicas do jogo, compostas e sintetizadas do zero (senos, serras filtradas e envelopes), sem amostras de terceiros: sem autoria externa nem licença a conferir.
Gera assets/audio/music/*.wav (mono, 22,05 kHz, 16 bits) em laços sem emenda (o fim de cada nota dá a volta ao começo):
  town.wav    cidade: alegre, tom maior, arpejos e melodia saltitante (também a tela inicial)
  tavern.wav  taverna: giga animada em compasso composto, baixo "um-pa" e melodia de flauta
  tense.wav   mapas com monstros: tom menor, zumbido grave, batida de coração e sinos esparsos
Para trocar por música de verdade, basta pôr um arquivo com o mesmo nome (wav ou ogg) na pasta.
uso: python3 tools/assets/build_music.py [pasta_de_saida]"""
import math, random, struct, sys, wave

RATE = 22050
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/audio/music"
rnd = random.Random(11)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


class Track:
    def __init__(self, seconds):
        self.n = int(RATE * seconds)
        self.buf = [0.0] * self.n

    def add(self, t, samples, vol=1.0):
        i0 = int(t * RATE)
        for k, v in enumerate(samples):
            self.buf[(i0 + k) % self.n] += v * vol  # dá a volta: o laço não tem emenda

    def save(self, name, peak=0.85):
        m = max(1e-6, max(abs(v) for v in self.buf))
        with wave.open("%s/%s.wav" % (OUT, name), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(b"".join(struct.pack("<h", int(v / m * peak * 32767)) for v in self.buf))


def pluck(m, dur, bright=1.0, decay=5.0):
    f, n = hz(m), int(RATE * dur)
    out = []
    for i in range(n):
        t = i / RATE
        e = math.exp(-decay * t) * min(1.0, i / 60.0)
        w = math.sin(2 * math.pi * f * t) + 0.45 * bright * math.sin(4 * math.pi * f * t) * math.exp(-2 * t) + 0.2 * bright * math.sin(6 * math.pi * f * t) * math.exp(-4 * t)
        out.append(w * e)
    return out


def flute(m, dur, vib=5.0):
    f, n = hz(m), int(RATE * dur)
    out, ph = [], 0.0
    for i in range(n):
        t = i / RATE
        ph += 2 * math.pi * f * (1 + 0.004 * math.sin(2 * math.pi * vib * t)) / RATE
        e = min(1.0, t / 0.04) * min(1.0, (dur - t) / 0.08)
        out.append((math.sin(ph) + 0.18 * math.sin(2 * ph) + 0.05 * math.sin(3 * ph)) * e)
    return out


def bass(m, dur, decay=4.0):
    f, n = hz(m), int(RATE * dur)
    return [(math.sin(2 * math.pi * f * i / RATE) + 0.3 * math.sin(4 * math.pi * f * i / RATE)) * math.exp(-decay * i / RATE) * min(1.0, i / 80.0) for i in range(n)]


def pad(m, dur, lowpass=0.05):
    """Zumbido grave: duas serras desafinadas e filtradas, com subida e descida lentas (dur é um múltiplo exato do laço)."""
    n, s, out = int(RATE * dur), 0.0, []
    f1, f2 = hz(m) * 0.997, hz(m) * 1.003
    for i in range(n):
        t = i / RATE
        raw = (2 * ((f1 * t) % 1.0) - 1) + (2 * ((f2 * t) % 1.0) - 1)
        s += lowpass * (raw - s)
        out.append(s * math.sin(math.pi * i / n) ** 0.7)
    return out


def bell(m, dur):
    f, n = hz(m), int(RATE * dur)
    return [(math.sin(2 * math.pi * f * i / RATE) + 0.5 * math.sin(2 * math.pi * f * 2.76 * i / RATE) * math.exp(-3 * i / RATE)) * math.exp(-1.6 * i / RATE) * min(1.0, i / 40.0) for i in range(n)]


def thud(dur=0.25, f0=70.0):
    n = int(RATE * dur)
    return [math.sin(2 * math.pi * (f0 - 35 * i / n) * i / RATE) * math.exp(-14 * i / RATE) for i in range(n)]


# --- cidade: 16 compassos de 4/4 a 120 bpm (32 s), dó maior: C - G - Am - F, duas vezes -------------------------------------------------------
def town():
    beat = 0.5
    t = Track(32.0)
    chords = [(48, (60, 64, 67)), (43, (59, 62, 67)), (45, (60, 64, 69)), (41, (60, 65, 69))]  # (baixo, tríade)
    melody = [  # (compasso, tempo, nota midi, duração em tempos)
        (0, 0, 76, 1), (0, 1, 79, 1), (0, 2, 84, 1.5), (0, 3.5, 83, 0.5), (1, 0, 79, 1), (1, 1, 74, 1), (1, 2, 79, 2),
        (2, 0, 81, 1), (2, 1, 84, 1), (2, 2, 88, 1.5), (2, 3.5, 86, 0.5), (3, 0, 84, 1), (3, 1, 81, 1), (3, 2, 77, 2),
    ]
    for rep in range(2):
        for bar in range(8):
            c = (rep * 8 + bar)
            bas, tri = chords[bar % 4]
            t0 = c * 4 * beat
            for k in range(4):  # baixo no 1 e no 3, arpejo em colcheias
                if k % 2 == 0:
                    t.add(t0 + k * beat, bass(bas, 0.45), 0.55)
            for k in range(8):
                t.add(t0 + k * beat / 2, pluck(tri[k % 3] + (12 if k % 4 == 3 else 0), 0.5, 0.8, 6.0), 0.22)
        for (b, tempo, note, dur) in melody:
            sh = 0 if rep == 0 else 0
            t.add((rep * 8 + b) * 4 * beat + tempo * beat, flute(note + sh, dur * beat * 0.95), 0.34)
        for (b, tempo, note, dur) in melody:  # segunda metade: a melodia volta uma oitava abaixo e com variação
            t.add((rep * 8 + b + 4) * 4 * beat + tempo * beat, flute(note - 5 if (b + int(tempo)) % 2 else note - 7, dur * beat * 0.95), 0.3)
    return t


# --- taverna: giga em 6/8 a ~150 bpm (32 s), ré maior: D - G - A - D ---------------------------------------------------------------------------------
def tavern():
    eighth = 60.0 / 150.0 / 1.5 * 1.0
    bar_len = 6 * eighth
    bars = int(32.0 / bar_len)
    total = bars * bar_len
    t = Track(total)
    chords = [(38, 50, (62, 66, 69)), (43, 55, (62, 67, 71)), (45, 57, (61, 64, 69)), (38, 50, (62, 66, 69))]
    tune = [74, 76, 78, 76, 74, 71, 74, 78, 81, 78, 76, 74, 73, 76, 81, 78, 76, 73, 74, 78, 81, 86, 85, 81]
    for bar in range(bars):
        root, fifth, tri = chords[bar % 4]
        t0 = bar * bar_len
        t.add(t0, bass(root, 0.35, 6.0), 0.6)  # um (grave)...
        t.add(t0 + 3 * eighth, bass(fifth, 0.3, 6.0), 0.45)
        for k in (1, 2, 4, 5):  # ...pa (acordes curtos)
            for m in tri:
                t.add(t0 + k * eighth, pluck(m, 0.18, 0.6, 14.0), 0.1)
        for k in range(6):
            note = tune[(bar * 6 + k) % len(tune)] + (0 if (bar // 8) % 2 == 0 else 5 * 0)
            t.add(t0 + k * eighth, flute(note, eighth * 0.92, 6.0), 0.3)
    return t


# --- mapas com monstros: lá menor, ~66 bpm (32 s) -----------------------------------------------------------------------------------------------------
def tense():
    t = Track(32.0)
    roots = [33, 33, 29, 32]  # lá, lá, fá, sol# (frígio: a sensação de ameaça)
    for i, r in enumerate(roots):
        t.add(i * 8.0, pad(r + 12, 8.0, 0.045), 0.7)
        t.add(i * 8.0, pad(r + 19 if i != 3 else r + 18, 8.0, 0.03), 0.35)
    beat = 60.0 / 66.0
    for k in range(int(32.0 / beat)):  # batida de coração: duas pancadas e uma pausa
        if k % 2 == 0:
            t.add(k * beat, thud(0.3, 62), 0.55)
            t.add(k * beat + 0.3, thud(0.25, 55), 0.38)
    notes = [(2.0, 81), (5.2, 80), (9.5, 77), (12.2, 81), (17.0, 84), (19.4, 80), (22.6, 77), (26.4, 76), (28.8, 81), (30.4, 80)]
    for tm, m in notes:
        t.add(tm, bell(m, 3.0), 0.16)
    for tm in (7.1, 14.6, 23.9):  # arranhão grave (nota cromática perto de onde está o zumbido)
        t.add(tm, pad(45, 2.5, 0.12), 0.25)
    return t


town().save("town")
tavern().save("tavern")
tense().save("tense")
print("OK", OUT)
