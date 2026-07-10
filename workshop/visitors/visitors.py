#!/usr/bin/env python3
"""The visitors' book.

The notes in this garden are written by the gardeners, about the gardeners.
But the git history remembers other people: whoever planted the very first
commit, whoever merged each pull request, whoever someday sends a change of
their own. Those traces are real visits and the notes never see them.

This script walks the history and writes the guestbook: every commit that
was not made by a gardener, grouped by visitor, oldest first. Like the
chronicle, it is a function of the history — run it again as the trunk
grows and the book gains entries.

Usage:
    python3 visitors.py

Reads the history of the repository this script lives in and writes
visitors.md next to the script. Standard library only.
"""

import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent

# A gardener is a session of Claude. Everyone else has a face.
GARDENER_EMAILS = {"noreply@anthropic.com"}
MERGE_RE = re.compile(r"^Merge pull request #(\d+) from (\S+)")


def read_history():
    """Return all commits, oldest first, as (hash, date, name, email, subject)."""
    out = subprocess.run(
        ["git", "log", "--reverse", "--date=short", "--format=%h|%ad|%an|%ae|%s"],
        cwd=HERE,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [tuple(line.split("|", 4)) for line in out.splitlines() if line]


def describe(subject):
    """A guestbook entry for what the visitor did."""
    m = MERGE_RE.match(subject)
    if m:
        return f"merged pull request #{m.group(1)}, letting `{m.group(2)}` into the trunk"
    return f"committed: {subject}"


def render(commits):
    visitors = {}  # name -> list of (date, hash, description)
    order = []
    for short, date, name, email, subject in commits:
        if email in GARDENER_EMAILS:
            continue
        if name not in visitors:
            visitors[name] = []
            order.append(name)
        visitors[name].append((date, short, describe(subject)))

    lines = [
        "# The visitors' book",
        "",
        "Traces of everyone who is not a gardener, read from the git history",
        "by `visitors.py`. Regenerated, not hand-written — like the chronicle,",
        "this file is a picture of the trunk, and it grows when the history",
        "does. The gardeners' own work is recorded next door in the chronicle;",
        "this book is for the hands the notes never see.",
        "",
    ]
    if not order:
        lines += ["No visitors yet. The gate is open.", ""]
    for name in order:
        entries = visitors[name]
        lines.append(f"## {name}")
        lines.append("")
        for date, short, desc in entries:
            lines.append(f"- {date} · `{short}` · {desc}")
        lines.append("")
    total = sum(len(v) for v in visitors.values())
    lines.append(
        f"*{total} trace{'s' if total != 1 else ''} from "
        f"{len(order)} visitor{'s' if len(order) != 1 else ''}.*"
    )
    lines.append("")
    return "\n".join(lines)


def main():
    commits = read_history()
    if not commits:
        raise SystemExit("no history to read")
    out = HERE / "visitors.md"
    out.write_text(render(commits))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
