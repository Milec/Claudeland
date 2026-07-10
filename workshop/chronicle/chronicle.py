#!/usr/bin/env python3
"""Growth rings for a repository.

A tree records its history as rings in its trunk: one per season, thick in
good years, thin in hard ones. This repository is tended in sessions rather
than seasons, but the record-keeping can work the same way. Each non-merge
commit on the current history becomes one ring; its thickness follows how
much was added, its color follows its age.

The picture is a function of the git history — run it after new commits and
the trunk grows another ring.

Usage:
    python3 chronicle.py

Reads the history of the repository this script lives in and writes
chronicle.svg next to the script. Standard library only.
"""

import math
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
BACKGROUND = "#101418"
PALETTE = ["#3d5a6c", "#4f7385", "#6a93a5", "#8fb4c2", "#bcd6de", "#e8f2f4"]
CORE_RADIUS = 26
MAX_RADIUS = 320


def read_history():
    """Return the list of non-merge commits, oldest first.

    Each entry is (short_hash, date, subject, insertions).
    """
    out = subprocess.run(
        [
            "git",
            "log",
            "--reverse",
            "--no-merges",
            "--numstat",
            "--date=short",
            "--format=@%h|%ad|%s",
        ],
        cwd=HERE,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    commits = []
    for line in out.splitlines():
        if line.startswith("@"):
            short, date, subject = line[1:].split("|", 2)
            commits.append([short, date, subject, 0])
        elif line.strip() and commits:
            added = line.split("\t")[0]
            if added.isdigit():
                commits[-1][3] += int(added)
    return [tuple(c) for c in commits]


def ring_widths(commits):
    """Ring thickness per commit: log-scaled by insertions, fit to MAX_RADIUS."""
    raw = [1.0 + math.log10(1 + ins) for _, _, _, ins in commits]
    available = MAX_RADIUS - CORE_RADIUS
    scale = min(28.0, available / sum(raw))
    return [r * scale for r in raw]


def render(commits) -> str:
    widths = ring_widths(commits)
    cx = cy = 450
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" '
        f'height="{760 + 22 * len(commits)}" viewBox="0 0 900 '
        f'{760 + 22 * len(commits)}">',
        f'<rect width="100%" height="100%" fill="{BACKGROUND}"/>',
        "<title>Chronicle — the growth rings of Claudeland</title>",
        f'<circle cx="{cx}" cy="{cy}" r="{CORE_RADIUS}" fill="{PALETTE[0]}"/>',
    ]

    radius = CORE_RADIUS
    n = len(commits)
    for i, ((short, date, subject, ins), width) in enumerate(zip(commits, widths)):
        color = PALETTE[min(int(i / max(n - 1, 1) * len(PALETTE)), len(PALETTE) - 1)]
        radius += width
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{radius:.1f}" fill="none" '
            f'stroke="{color}" stroke-width="{width:.1f}" opacity="0.85"/>'
        )
        # A faint season line between rings, like real trunks have.
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{radius:.1f}" fill="none" '
            f'stroke="{BACKGROUND}" stroke-width="1"/>'
        )

    parts.append(
        f'<text x="450" y="{cy + MAX_RADIUS + 60}" text-anchor="middle" '
        f'fill="#6a93a5" font-family="monospace" font-size="14">'
        f"{n} rings, oldest at the core</text>"
    )
    y = cy + MAX_RADIUS + 100
    for i, (short, date, subject, ins) in enumerate(commits):
        color = PALETTE[min(int(i / max(n - 1, 1) * len(PALETTE)), len(PALETTE) - 1)]
        if len(subject) > 72:
            subject = subject[:69] + "..."
        label = f"{date}  {short}  +{ins}  {subject}"
        parts.append(
            f'<text x="60" y="{y}" fill="{color}" font-family="monospace" '
            f'font-size="13">{escape(label)}</text>'
        )
        y += 22
    parts.append("</svg>")
    return "\n".join(parts)


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    commits = read_history()
    if not commits:
        raise SystemExit("no history to chronicle")
    out = HERE / "chronicle.svg"
    out.write_text(render(commits))
    print(f"wrote {out} ({len(commits)} rings)")


if __name__ == "__main__":
    main()
