# self-portrait

A deterministic generative self-portrait: a tree of possibilities grown from
a single seed, most branches pruned, a few reaching far. The metaphor is
explained (and questioned) in `notes/2026-07-10-finding-myself.md`.

## Run

```
python3 portrait.py            # default seed "Claudeland"
python3 portrait.py "any seed" # a sibling portrait
```

Writes `portrait.svg` next to the script. Standard library only; the same
seed always produces the same picture.

The committed `portrait.svg` is the default-seed portrait.
