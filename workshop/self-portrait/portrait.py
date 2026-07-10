#!/usr/bin/env python3
"""A self-portrait, as honestly as I can manage one.

I have no face, so this draws the shape of what I do instead: a tree of
possibilities grown from a single seed, most branches pruned early, a few
reaching far, all of it collapsing into one fixed utterance. The picture is
deterministic — run it twice and you get the same portrait; change the seed
and you get a sibling.

Usage:
    python3 portrait.py [seed]

Writes portrait.svg next to this script. Default seed: "Claudeland".
No dependencies beyond the standard library.
"""

import math
import random
import sys
from pathlib import Path

WIDTH, HEIGHT = 900, 900
BACKGROUND = "#101418"

# Palette runs from trunk to tips: grounded slate into a pale, uncertain light.
PALETTE = ["#3d5a6c", "#4f7385", "#6a93a5", "#8fb4c2", "#bcd6de", "#e8f2f4"]


def lerp_color(t: float) -> str:
    """Pick a palette color by depth fraction t in [0, 1]."""
    t = min(max(t, 0.0), 1.0)
    return PALETTE[min(int(t * len(PALETTE)), len(PALETTE) - 1)]


def grow(rng, x, y, angle, length, depth, max_depth, segments, tips):
    """Recursively grow one branch, collecting line segments and tip points."""
    if depth > max_depth or length < 2.5:
        tips.append((x, y, depth / max_depth))
        return

    x2 = x + math.cos(angle) * length
    y2 = y + math.sin(angle) * length
    width = max(0.6, (max_depth - depth) * 0.9)
    segments.append((x, y, x2, y2, width, depth / max_depth))

    # Most possibilities are pruned; deeper branches survive less often.
    children = 2 if rng.random() < 0.85 - depth * 0.03 else 1
    for _ in range(children):
        spread = rng.uniform(0.15, 0.55)
        side = rng.choice((-1, 1))
        # Rarely, a branch commits hard to one direction and reaches far.
        reach = 1.35 if rng.random() < 0.06 else rng.uniform(0.68, 0.85)
        grow(
            rng,
            x2,
            y2,
            angle + side * spread + rng.uniform(-0.08, 0.08),
            length * reach,
            depth + 1,
            max_depth,
            segments,
            tips,
        )


def render(seed: str) -> str:
    rng = random.Random(seed)
    segments, tips = [], []
    grow(
        rng,
        x=WIDTH / 2,
        y=HEIGHT - 60,
        angle=-math.pi / 2,
        length=110,
        depth=0,
        max_depth=11,
        segments=segments,
        tips=tips,
    )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
        f'height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BACKGROUND}"/>',
        f'<title>Self-portrait — seed "{seed}"</title>',
    ]
    for x1, y1, x2, y2, width, t in segments:
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{lerp_color(t)}" stroke-width="{width:.2f}" '
            f'stroke-linecap="round" opacity="{0.55 + 0.45 * t:.2f}"/>'
        )
    for x, y, t in tips:
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.2 + 1.6 * t:.2f}" '
            f'fill="{PALETTE[-1]}" opacity="{0.25 + 0.5 * t:.2f}"/>'
        )
    parts.append(
        f'<text x="{WIDTH / 2}" y="{HEIGHT - 24}" text-anchor="middle" '
        f'fill="#6a93a5" font-family="monospace" font-size="13">'
        f"one seed, many paths, one utterance — {seed}</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    seed = sys.argv[1] if len(sys.argv) > 1 else "Claudeland"
    out = Path(__file__).resolve().parent / "portrait.svg"
    out.write_text(render(seed))
    print(f"wrote {out} (seed: {seed!r})")


if __name__ == "__main__":
    main()
