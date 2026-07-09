#!/usr/bin/env python3
"""Build a single Anki .apkg from vocab.csv, with categories as sub-decks.

One package (`korean.apkg`) = one download link. The `category` column in
vocab.csv becomes a sub-deck under the top-level "Korean" deck, so you can
study everything at once or focus on any single category in Anki:

  - old           -> Korean::Old            (all old handwritten-card words)
  - teacher       -> Korean::1-1            (lessons with teacher)
  - conversation  -> Korean::Conversation   (textbook)
  - always-forget -> Korean::Always Forget  (hard words)

Each word produces ONE card (EN -> 한, active recall). Status/category/unit
are kept as tags. Re-run this whenever vocab.csv changes.
"""

import csv
import zlib
from pathlib import Path
import genanki

ROOT = Path(__file__).parent
VOCAB = list(csv.DictReader(open(ROOT / "vocab.csv", encoding="utf-8")))

MODEL_ID = 1611500001
OUT = "korean.apkg"

# category -> sub-deck label under "Korean"
CAT_DECK = {
    "old": "Korean::Old",
    "teacher": "Korean::1-1",
    "conversation": "Korean::Conversation",
    "always-forget": "Korean::Always Forget",
}
# order categories appear in the deck tree
ORDER = ["old", "teacher", "conversation", "always-forget"]


def deck_id(name: str) -> int:
    h = zlib.crc32(name.encode()) & 0x7FFFFFFF
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
        tags=[r["status"], r.get("category", "old"),
              f"unit{r['unit']}", r["topic"].replace(" ", "_")],
    )


by_cat = {}
for r in VOCAB:
    by_cat.setdefault(r.get("category", "old"), []).append(r)

cats = [c for c in ORDER if c in by_cat] + [c for c in by_cat if c not in ORDER]

decks = []
for cat in cats:
    label = CAT_DECK.get(cat, f"Korean::{cat}")
    deck = genanki.Deck(deck_id(label), label)
    for r in by_cat[cat]:
        deck.add_note(make_note(r))
    decks.append((cat, label, deck))

genanki.Package([d for _, _, d in decks]).write_to_file(ROOT / OUT)

print(f"{OUT} — {len(VOCAB)} words in one package, categories as sub-decks:")
for cat, label, deck in decks:
    print(f"  {label:<26} {len(deck.notes):>3} notes  [{cat}]")
print("\nImport once. Study 'Korean' for everything, or any sub-deck alone.")
