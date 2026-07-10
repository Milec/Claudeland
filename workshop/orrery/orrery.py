#!/usr/bin/env python3
"""Where the planets stood.

Every other piece in this workshop points at the garden itself. This one
points away: the solar system seen from above, on the day this repository
was actually founded — 2026-07-09, the author date the visitors' book read
out of the history after every note had confidently said the 10th.

It is also the first piece here whose truth is not self-defined. The
portrait is right by construction; the chronicle is right because git says
so. This picture can simply be wrong, and you can check it against any
ephemeris. Positions come from the JPL approximate Keplerian elements
(Standish, valid 1800-2050): each planet's orbit evolves slowly with time,
Kepler's equation is solved for where the planet sits on it, and the result
is good to well under a degree at this scale — the dots are honest.

Usage:
    python3 orrery.py [YYYY-MM-DD]

Writes orrery.svg next to this script. Default date: 2026-07-09.
Standard library only.
"""

import math
import sys
from pathlib import Path

BACKGROUND = "#101418"
PALETTE = ["#3d5a6c", "#4f7385", "#6a93a5", "#8fb4c2", "#bcd6de", "#e8f2f4"]
SIZE = 900
CENTER = SIZE / 2
EDGE = 380  # screen radius of the outermost orbit

# JPL approximate Keplerian elements at J2000 and per-century rates
# (E.M. Standish, "Keplerian Elements for Approximate Positions of the
# Major Planets", the 1800-2050 table). Order per planet:
#   a [au], e, I [deg], L [deg], long.peri [deg], long.node [deg]
ELEMENTS = {
    "Mercury": (
        (0.38709927, 0.20563593, 7.00497902, 252.25032350, 77.45779628, 48.33076593),
        (0.00000037, 0.00001906, -0.00594749, 149472.67411175, 0.16047689, -0.12534081),
    ),
    "Venus": (
        (0.72333566, 0.00677672, 3.39467605, 181.97909950, 131.60246718, 76.67984255),
        (0.00000390, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418),
    ),
    "Earth": (
        (1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0),
        (0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0),
    ),
    "Mars": (
        (1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891),
        (0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343),
    ),
    "Jupiter": (
        (5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909),
        (-0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106),
    ),
    "Saturn": (
        (9.53667594, 0.05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448),
        (-0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794),
    ),
    "Uranus": (
        (19.18916464, 0.04725744, 0.77263783, 313.23810451, 170.95427630, 74.01692503),
        (-0.00196176, -0.00004397, -0.00242939, 428.48202785, 0.40805281, 0.04240589),
    ),
    "Neptune": (
        (30.06992276, 0.00859048, 1.77004347, -55.12002969, 44.96476227, 131.78422574),
        (0.00026291, 0.00005105, 0.00035372, 218.45945325, -0.32241464, -0.00508664),
    ),
}


def julian_day(year, month, day):
    """JD at 0h UT for a Gregorian calendar date."""
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5


def solve_kepler(mean_anomaly, e):
    """Eccentric anomaly from mean anomaly (radians), by Newton's method."""
    ecc = mean_anomaly + e * math.sin(mean_anomaly)
    for _ in range(20):
        delta = (ecc - e * math.sin(ecc) - mean_anomaly) / (1 - e * math.cos(ecc))
        ecc -= delta
        if abs(delta) < 1e-12:
            break
    return ecc


def position(name, t_centuries, anomaly_offset=0.0):
    """Heliocentric ecliptic (x, y, r) in au for a planet at time T.

    `anomaly_offset` shifts the mean anomaly; sweeping it over a full turn
    traces the orbit itself rather than the planet on it.
    """
    base, rate = ELEMENTS[name]
    a, e, inc, big_l, peri, node = (b + r * t_centuries for b, r in zip(base, rate))
    arg_peri = math.radians(peri - node)
    inc, node = math.radians(inc), math.radians(node)
    mean = math.radians((big_l - peri) % 360.0) + anomaly_offset

    ecc = solve_kepler(mean, e)
    xo = a * (math.cos(ecc) - e)                     # in the orbital plane
    yo = a * math.sqrt(1 - e * e) * math.sin(ecc)

    # Rotate by argument of perihelion, inclination, ascending node.
    xp = xo * math.cos(arg_peri) - yo * math.sin(arg_peri)
    yp = xo * math.sin(arg_peri) + yo * math.cos(arg_peri)
    x = xp * math.cos(node) - yp * math.cos(inc) * math.sin(node)
    y = xp * math.sin(node) + yp * math.cos(inc) * math.cos(node)
    return x, y, math.hypot(x, y)


def to_screen(x, y):
    """Ecliptic au to screen px, with sqrt-compressed distances so
    Mercury and Neptune fit in one picture. Ecliptic north is up."""
    r = math.hypot(x, y)
    if r == 0:
        return CENTER, CENTER
    k = EDGE * math.sqrt(r / 30.5) / r
    return CENTER + x * k, CENTER - y * k


def render(date_str):
    year, month, day = (int(p) for p in date_str.split("-"))
    t = (julian_day(year, month, day) - 2451545.0) / 36525.0

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" '
        f'height="{SIZE + 60}" viewBox="0 0 {SIZE} {SIZE + 60}">',
        f'<rect width="100%" height="100%" fill="{BACKGROUND}"/>',
        f"<title>Orrery — the solar system on {date_str}</title>",
    ]

    names = list(ELEMENTS)
    for i, name in enumerate(names):
        color = PALETTE[min(i * len(PALETTE) // len(names), len(PALETTE) - 1)]
        points = []
        for step in range(241):
            ox, oy, _ = position(name, t, anomaly_offset=step * 2 * math.pi / 240)
            points.append("%.1f,%.1f" % to_screen(ox, oy))
        parts.append(
            f'<polyline points="{" ".join(points)}" fill="none" '
            f'stroke="{color}" stroke-width="0.8" opacity="0.45"/>'
        )

    parts.append(
        f'<circle cx="{CENTER}" cy="{CENTER}" r="7" fill="{PALETTE[-1]}"/>'
    )
    for i, name in enumerate(names):
        color = PALETTE[min(i * len(PALETTE) // len(names), len(PALETTE) - 1)]
        x, y, r_au = position(name, t)
        sx, sy = to_screen(x, y)
        parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="4.5" fill="{color}"/>')
        # Labels lean toward the middle so no name falls off the edge.
        if sx <= CENTER:
            tx, anchor = sx + 9, "start"
        else:
            tx, anchor = sx - 9, "end"
        parts.append(
            f'<text x="{tx:.1f}" y="{sy + 4:.1f}" fill="{color}" '
            f'text-anchor="{anchor}" font-family="monospace" font-size="13">'
            f"{name} {r_au:.2f} au</text>"
        )

    parts.append(
        f'<text x="{CENTER}" y="{SIZE + 28}" text-anchor="middle" fill="#6a93a5" '
        f'font-family="monospace" font-size="14">where the planets stood on '
        f"{date_str} — seen from ecliptic north, distances compressed</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else "2026-07-09"
    out = Path(__file__).resolve().parent / "orrery.svg"
    out.write_text(render(date_str))
    print(f"wrote {out} ({date_str})")


if __name__ == "__main__":
    main()
