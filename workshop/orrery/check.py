#!/usr/bin/env python3
"""The sky's word against ours.

The orrery is the one piece in this workshop that can be wrong, and during
construction it briefly was — a units bug shifted every planet by its
ascending node, and nothing inside the garden could tell. This script is
the instrument that note asked for: it compares the orrery's computed
positions for the founding date against positions computed independently
by JPL Horizons (DE441 numerical ephemeris), hardcoded below.

The reference vectors were fetched from the Horizons API on 2026-07-10:
heliocentric position, J2000 ecliptic frame, 2026-07-09 00:00 TDB, in au.
"Earth" is the Earth-Moon barycenter, which is what the Standish elements
the orrery uses actually model. The Standish table promises roughly
arcminute-to-sub-degree accuracy in this era; measured agreement on this
date is 0.074 degrees at worst (Saturn). The tolerances below are a few
times looser than that, and several hundred times tighter than the node
bug this check exists to catch.

Usage:
    python3 check.py

Exits nonzero if any planet is out of tolerance. Standard library only.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import orrery

DATE = "2026-07-09"

# JPL Horizons, DE441: heliocentric X, Y, Z [au], J2000 ecliptic frame,
# at 2026-07-09 00:00:00 TDB.
HORIZONS = {
    "Mercury": (6.726815119932408e-02, -4.516675902490135e-01, -4.308154147578711e-02),
    "Venus": (-5.516983197432245e-01, -4.668824581193658e-01, 2.541809778491319e-02),
    "Earth": (2.881144315242731e-01, -9.749434076602126e-01, 5.679547555615496e-05),
    "Mars": (1.106524773365265e+00, 9.391129501040927e-01, -7.452168326844429e-03),
    "Jupiter": (-2.981859945471494e+00, 4.355822558012150e+00, 4.862090819977476e-02),
    "Saturn": (9.361463317201773e+00, 1.305547705934128e+00, -3.953798977545105e-01),
    "Uranus": (9.225855979591627e+00, 1.712988786765974e+01, -5.600652081866696e-02),
    "Neptune": (2.985079588188279e+01, 1.115316766836554e+00, -7.108655915499502e-01),
}

LON_TOL_DEG = 0.25  # heliocentric ecliptic longitude
R_TOL_REL = 0.01    # in-plane distance from the Sun, relative

def main():
    year, month, day = (int(p) for p in DATE.split("-"))
    t = (orrery.julian_day(year, month, day) - 2451545.0) / 36525.0

    failures = []
    for name, (hx, hy, _hz) in HORIZONS.items():
        x, y, r = orrery.position(name, t)
        lon = math.degrees(math.atan2(y, x)) % 360.0
        lon_ref = math.degrees(math.atan2(hy, hx)) % 360.0
        dlon = (lon - lon_ref + 180.0) % 360.0 - 180.0
        r_ref = math.hypot(hx, hy)
        dr = (r - r_ref) / r_ref

        ok = abs(dlon) <= LON_TOL_DEG and abs(dr) <= R_TOL_REL
        if not ok:
            failures.append(name)
        print(
            f"{'ok' if ok else 'WRONG':5s} {name:8s}"
            f" longitude {lon:8.3f}° (sky says {lon_ref:8.3f}°, Δ {dlon:+.3f}°)"
            f"  r {r:7.3f} au (sky says {r_ref:7.3f})"
        )

    if failures:
        sys.exit(f"the sky disagrees about: {', '.join(failures)}")
    print(f"all eight planets where the sky says they were on {DATE}")


if __name__ == "__main__":
    main()
