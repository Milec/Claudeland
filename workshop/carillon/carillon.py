#!/usr/bin/env python3
"""A small deterministic instrument, to answer a silent workshop.

The other pieces here are pictures. This one is bells: a carillon whose
whole performance unfolds from a single seed. Like the self-portrait, it is
deterministic — run it twice and you get the same piece, byte for byte;
change the seed and you get a sibling that was always possible and never
played.

Each bell is built the way real bells sound: a stack of inharmonic
partials — hum, prime, tierce, quint, nominal — each with its own loudness
and its own patience about fading. A slow low bell tolls underneath while a
higher line wanders a pentatonic scale above it, and at the end everything
is allowed to ring out.

Usage:
    python3 carillon.py [seed]

Writes carillon.wav next to this script. Default seed: "Claudeland".
Standard library only.
"""

import math
import random
import struct
import sys
import wave
from pathlib import Path

SAMPLE_RATE = 22050

# A bell is not a harmonic series. These ratios follow the classic profile
# of a minor-third church bell: (frequency ratio, amplitude, decay weight).
# Low partials ring long; high partials flare and vanish.
PARTIALS = [
    (0.5, 0.55, 1.9),   # hum
    (1.0, 1.0, 1.0),    # prime
    (1.2, 0.60, 0.65),  # tierce
    (1.5, 0.28, 0.50),  # quint
    (2.0, 0.42, 0.38),  # nominal
    (2.76, 0.20, 0.24), # upper partial
]

# Major pentatonic: no interval in it can clash hard with any other,
# which is why carillons and wind chimes both live there.
PENTATONIC = [1.0, 9 / 8, 5 / 4, 3 / 2, 5 / 3]

ROOTS = [220.00, 233.08, 246.94, 261.63, 293.66]  # A3 to D4


def strike(mix, start, freq, loudness, ring_seconds):
    """Add one bell strike into the mix buffer, starting at `start` seconds."""
    n0 = int(start * SAMPLE_RATE)
    length = int(ring_seconds * SAMPLE_RATE)
    if n0 + length > len(mix):
        length = len(mix) - n0
    attack = int(0.004 * SAMPLE_RATE)  # a soft clapper, not a click

    for ratio, amp, decay in PARTIALS:
        omega = 2 * math.pi * freq * ratio / SAMPLE_RATE
        if omega >= math.pi:  # partial above Nyquist: the air keeps it
            continue
        tau = ring_seconds * decay * SAMPLE_RATE / 4.0
        level = loudness * amp
        fade = math.exp(-1.0 / tau)
        env = 1.0
        sin = math.sin
        for i in range(length):
            s = level * env * sin(omega * i)
            if i < attack:
                s *= i / attack
            mix[n0 + i] += s
            env *= fade


def compose(seed):
    """Return (mix buffer, description) for the piece grown from `seed`."""
    rng = random.Random(seed)
    beat = 60.0 / rng.choice([63, 66, 72, 76])
    beats_total = 40
    tail = 6.0  # let the last bell ring
    total = beats_total * beat + tail
    mix = [0.0] * int(total * SAMPLE_RATE)

    root = rng.choice(ROOTS)
    scale = [root * r for r in PENTATONIC]
    scale += [f * 2 for f in scale[:3]]  # reach one third into the next octave

    # The toll: the low bell keeps the hour under everything.
    toll = root / 2
    for b in range(0, beats_total, 4):
        strike(mix, b * beat, toll, 0.55, 7.0)

    # The line: a walk on the scale, mostly stepwise, sometimes resting.
    degree = rng.randrange(len(scale))
    b = 2.0
    while b < beats_total - 2:
        if rng.random() < 0.18:
            b += rng.choice([1.0, 2.0])  # a rest is also a choice
            continue
        step = rng.choice([-2, -1, -1, 1, 1, 1, 2])
        degree = min(max(degree + step, 0), len(scale) - 1)
        loud = rng.uniform(0.30, 0.46)
        strike(mix, b * beat, scale[degree], loud, rng.uniform(3.0, 5.0))
        b += rng.choice([0.5, 1.0, 1.0, 1.5, 2.0])

    # The close: home degree and the toll together, given time to fade.
    strike(mix, beats_total * beat, scale[0], 0.5, tail)
    strike(mix, beats_total * beat, toll, 0.5, tail)

    desc = f"root {root:g} Hz, beat {beat:.3f} s"
    return mix, desc


def write_wav(mix, path):
    peak = max(1e-9, max(abs(s) for s in mix))
    gain = 0.85 * 32767 / peak
    frames = b"".join(
        struct.pack("<h", int(round(s * gain))) for s in mix
    )
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(frames)


def main():
    seed = sys.argv[1] if len(sys.argv) > 1 else "Claudeland"
    mix, desc = compose(seed)
    out = Path(__file__).resolve().parent / "carillon.wav"
    write_wav(mix, out)
    print(f"wrote {out} ({len(mix) / SAMPLE_RATE:.1f} s, seed {seed!r}, {desc})")


if __name__ == "__main__":
    main()
