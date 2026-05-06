#!/usr/bin/env python3
"""Build Anki .apkg decks from vocab.csv.

Generates two decks:
  - korean_forgotten.apkg — only forgotten words (your priority list)
  - korean_full.apkg      — all 191 words with tags

Re-run this whenever vocab.csv changes.
"""

import csv
from pathlib import Path
import genanki

ROOT = Path(__file__).parent
VOCAB = list(csv.DictReader(open(ROOT / "vocab.csv", encoding="utf-8")))

# Stable IDs (don't change — Anki uses them to update existing cards)
MODEL_ID = 1607392319
DECK_FORGOTTEN_ID = 2059400110
DECK_FULL_ID = 2059400111

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
                    "<div style='font-size:14px;color:#666;font-style:italic;margin-top:4px'>[{{Romanization}}]</div>"
                    "<div style='font-size:14px;color:#888;margin-top:10px'>{{Example}}</div>"
                    "<div style='font-size:11px;color:#bbb;margin-top:14px'>unit {{Unit}} · {{Topic}}</div>",
        },
        {
            "name": "한 → EN (recognition)",
            "qfmt": "<div style='font-size:36px;font-weight:600'>{{Korean}}</div>",
            "afmt": "{{FrontSide}}<hr id='answer'>"
                    "<div style='font-size:18px'>{{English}}</div>"
                    "<div style='font-size:14px;color:#666;font-style:italic;margin-top:4px'>[{{Romanization}}]</div>"
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


def make_deck(deck_id, name, rows):
    deck = genanki.Deck(deck_id, name)
    for r in rows:
        note = genanki.Note(
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
        deck.add_note(note)
    return deck


forgotten = [r for r in VOCAB if r["status"] == "forgotten"]
deck_f = make_deck(DECK_FORGOTTEN_ID, "Korean::Forgotten 🔥", forgotten)
deck_a = make_deck(DECK_FULL_ID, "Korean::All", VOCAB)

genanki.Package(deck_f).write_to_file(ROOT / "korean_forgotten.apkg")
genanki.Package(deck_a).write_to_file(ROOT / "korean_full.apkg")

print(f"korean_forgotten.apkg — {len(forgotten)} cards")
print(f"korean_full.apkg      — {len(VOCAB)} cards")
print(f"Each note generates 2 cards (EN→한 and 한→EN), so totals double.")
