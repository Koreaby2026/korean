#!/usr/bin/env python3
"""Build Anki .apkg decks from vocab.csv.

Generates two packages, each with per-unit sub-decks:
  - korean_forgotten.apkg — only forgotten words, split into Korean::Forgotten::Unit X
  - korean_full.apkg      — all words, split into Korean::All::Unit X

Re-run this whenever vocab.csv changes.
"""

import csv
import zlib
from pathlib import Path
import genanki

ROOT = Path(__file__).parent
VOCAB = list(csv.DictReader(open(ROOT / "vocab.csv", encoding="utf-8")))

# Stable IDs (don't change — Anki uses them to update existing cards)
MODEL_ID = 1607392319
DECK_FORGOTTEN_ID = 2059400110
DECK_FULL_ID = 2059400111


def subdeck_id(parent_id: int, unit: str) -> int:
    # Deterministic per-unit id derived from parent id + unit name.
    h = zlib.crc32(f"{parent_id}:{unit}".encode()) & 0x7FFFFFFF
    return 1_000_000_000 + (h % 1_000_000_000)

model = genanki.Model(
    MODEL_ID,
    "Korean (Hazyaeva)",
    fields=[
        {"name": "Korean"},
        {"name": "English"},
        {"name": "Romanization"},
        {"name": "Example"},
        {"name": "Unit"},
        {"name": "Topic"},
    ],
    templates=[
        {
            "name": "EN → 한 (recall)",
            "qfmt": "<div style='font-size:18px;color:#666'>{{English}}</div>"
                    "<div style='font-size:13px;color:#999;margin-top:6px'>type the Korean word</div>",
            "afmt": "{{FrontSide}}<hr id='answer'>"
                    "<div style='font-size:34px;font-weight:600'>{{Korean}}</div>"
                    "<div style='font-size:14px;color:#888;margin-top:10px'>{{Example}}</div>"
                    "<div style='font-size:11px;color:#bbb;margin-top:14px'>unit {{Unit}} · {{Topic}}</div>",
        },
        {
            "name": "한 → EN (recognition)",
            "qfmt": "<div style='font-size:36px;font-weight:600'>{{Korean}}</div>",
            "afmt": "{{FrontSide}}<hr id='answer'>"
                    "<div style='font-size:18px'>{{English}}</div>"
                    "<div style='font-size:14px;color:#888;margin-top:10px'>{{Example}}</div>"
                    "<div style='font-size:11px;color:#bbb;margin-top:14px'>unit {{Unit}} · {{Topic}}</div>",
        },
    ],
    css=(
        ".card { font-family: 'Helvetica Neue', sans-serif; text-align: center; "
        "background-color: #faf7f2; color: #1f1d1a; padding: 24px; }"
        "hr#answer { border: none; border-top: 1px solid #ddd; margin: 18px 0; }"
    ),
)


def unit_sort_key(u: str):
    # Sort: numeric units first (by number then letter suffix), then "base", then others.
    if u == "base":
        return (2, 0, "")
    head = "".join(c for c in u if c.isdigit())
    tail = "".join(c for c in u if not c.isdigit())
    if head:
        return (0, int(head), tail)
    return (1, 0, u)


def make_note(r):
    return genanki.Note(
        model=model,
        fields=[
            r["korean"],
            r["translation"],
            r["romanization"],
            r.get("example", ""),
            r["unit"],
            r["topic"],
        ],
        tags=[r["status"], f"unit{r['unit']}", r["topic"].replace(" ", "_")],
    )


def build_package(parent_id: int, parent_name: str, rows, out_file: str):
    by_unit = {}
    for r in rows:
        by_unit.setdefault(r["unit"], []).append(r)
    decks = []
    for unit in sorted(by_unit, key=unit_sort_key):
        deck_name = f"{parent_name}::Unit {unit}"
        deck = genanki.Deck(subdeck_id(parent_id, unit), deck_name)
        for r in by_unit[unit]:
            deck.add_note(make_note(r))
        decks.append((unit, deck))
    pkg = genanki.Package([d for _, d in decks])
    pkg.write_to_file(ROOT / out_file)
    return decks


forgotten = [r for r in VOCAB if r["status"] == "forgotten"]
f_decks = build_package(DECK_FORGOTTEN_ID, "Korean::Forgotten 🔥", forgotten, "korean_forgotten.apkg")
a_decks = build_package(DECK_FULL_ID, "Korean::All", VOCAB, "korean_full.apkg")

print(f"korean_forgotten.apkg — {len(forgotten)} notes across {len(f_decks)} unit decks:")
for unit, deck in f_decks:
    print(f"  Unit {unit:>4}: {len(deck.notes)} notes")
print(f"korean_full.apkg      — {len(VOCAB)} notes across {len(a_decks)} unit decks:")
for unit, deck in a_decks:
    print(f"  Unit {unit:>4}: {len(deck.notes)} notes")
print("Each note generates 2 cards (EN→한 and 한→EN), so totals double.")
