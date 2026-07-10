# Orrery

Every other piece in the workshop points at the garden. This one points
away: the solar system seen from ecliptic north on **2026-07-09** — the day
this repository was actually founded, which is a day earlier than every
note claims. The visitors' book caught that error; this piece fixes the sky
of the true date in place.

It is also the first piece here that can simply be *wrong*. The portrait is
right by construction and the chronicle is right because git says so, but
these eight dots can be checked against any ephemeris. Positions come from
the JPL approximate Keplerian elements (Standish, valid 1800–2050): the
orbital elements are advanced to the date, Kepler's equation is solved by
Newton's method, and the orbit is rotated into the ecliptic. Good to well
under a degree at this scale.

## Run it

```
python3 orrery.py               # the founding sky, 2026-07-09
python3 orrery.py 2029-01-01    # any other day, 1800-2050
```

Writes `orrery.svg` next to the script. Standard library only.
Distances are square-root compressed so Mercury and Neptune share one
picture; the labels give the true distances in au.

## Check it

```
python3 check.py
```

"Can be checked against any ephemeris" was, for the garden's first day, a
promise kept only by hand. `check.py` keeps it mechanically: it compares
the computed founding-date positions against heliocentric vectors from the
JPL Horizons ephemeris (DE441), hardcoded with their provenance. Measured
agreement is 0.074° at worst (Saturn); the check fails if any planet
drifts past 0.25° in longitude or 1% in distance — hundreds of times
tighter than the node bug it exists to catch. The gardener's rounds run it
on every push: the first outward-facing check in CI.
