# chronicle

Growth rings for this repository. Each non-merge commit becomes one ring in
a trunk cross-section — thickness follows how much the commit added, color
follows its age, oldest at the core. A legend below the trunk lists the ring
sequence.

## Run

```
python3 chronicle.py
```

Reads the git history of this repository and writes `chronicle.svg` next to
the script. Standard library only.

The committed `chronicle.svg` is a snapshot; it goes stale as the garden
grows. Any session may regenerate it — that's not churn, that's the point.
