#!/usr/bin/env python3
"""Build Anki .apkg deck from vocab.csv.

Generates one package with per-unit sub-decks:
  - korean.apkg — all words, split into Korean::Unit X

Each word produces ONE card (EN → 한, active recall only).
Forgotten status is preserved as a tag for filtering inside Anki.

Re-run this whenever vocab.csv changes.
"""

import csv
import zlib
from pathlib import Path
import genanki

ROOT = Path(__file__).parent
VOCAB = list(csv.DictReader(open(ROOT / "vocab.csv", encoding="utf-8")))

# New IDs (changed from previous version to force Anki to import as fresh deck
# and reset spaced-repetition progress).
MODEL_ID = 1611500001
DECK_ID = 2070000001


def subdeck_id(unit: str) -> int:
    h = zlib.crc32(f"{DECK_ID}:{unit}".encode()) & 0x7FFFFFFF
    return 1_100_000_000 + (h % 1_000_000_000)


model = genanki.Model(
    MODEL_ID,
    "Korean (Hazyaeva v2)",
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
                    "<div style='font-size:13px;color:#999;margin-top:6px'>recall the Korean word</div>",
            "afmt": "{{FrontSide}}<hr id='answer'>"
                    "<div style='font-size:34px;font-weight:600'>{{Korean}}</div>"
                    "<div style='font-size:14px;color:#aaa;margin-top:4px'>{{Romanization}}</div>"
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


by_unit = {}
for r in VOCAB:
    by_unit.setdefault(r["unit"], []).append(r)

decks = []
for unit in sorted(by_unit, key=unit_sort_key):
    deck = genanki.Deck(subdeck_id(unit), f"Korean::Unit {unit}")
    for r in by_unit[unit]:
        deck.add_note(make_note(r))
    decks.append((unit, deck))

genanki.Package([d for _, d in decks]).write_to_file(ROOT / "korean.apkg")

print(f"korean.apkg — {len(VOCAB)} notes across {len(decks)} unit decks:")
for unit, deck in decks:
    print(f"  Unit {unit:>4}: {len(deck.notes)} notes")
print("\nOne card per note (EN → 한). Import into Anki — old deck should be deleted first.")
