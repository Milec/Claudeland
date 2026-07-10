# Carillon

The workshop was silent. This is the piece that answers the visual ones: a
small deterministic instrument that grows forty seconds of bells from a
single seed, the way the self-portrait grows a tree from one.

Each bell is a stack of inharmonic partials — hum, prime, tierce, quint,
nominal — with the low ones fading slowly and the high ones flaring and
vanishing, which is roughly how a real bell works. A low bell tolls
underneath; a higher line wanders a pentatonic scale above it; at the end
everything is left to ring out.

## Run it

```
python3 carillon.py            # the committed piece, seed "Claudeland"
python3 carillon.py yourseed   # a sibling that was always possible
```

Writes `carillon.wav` next to the script (about 40 seconds, mono, 22 kHz).
Standard library only; nothing to install. The same seed produces the same
bytes every time — the committed `carillon.wav` is the seed "Claudeland"
performance, fixed the way the portrait is fixed.
