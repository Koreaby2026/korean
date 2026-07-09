#!/usr/bin/env python3
"""Build Anki .apkg decks from vocab.csv — one package (and one link) per category.

The `category` column in vocab.csv maps to a separate .apkg file so each has its
own download link and can be imported independently:

  - old          -> korean.apkg             (all old handwritten-card words,
                                              split into Korean::Unit X)
  - teacher      -> korean_teacher.apkg      (Korean 1-1 — lessons with teacher)
  - conversation -> korean_conversation.apkg (Korean Conversation — textbook)
  - always-forget-> korean_forget.apkg       (Korean Always Forget — hard words)

Each word produces ONE card (EN -> 한, active recall). Status/category/unit kept
as tags. Re-run this whenever vocab.csv changes.
"""

import csv
import zlib
from pathlib import Path
import genanki

ROOT = Path(__file__).parent
VOCAB = list(csv.DictReader(open(ROOT / "vocab.csv", encoding="utf-8")))

MODEL_ID = 1611500001

# category -> (apkg filename, deck label, split_by_unit)
CAT_META = {
    "old": ("korean.apkg", "Korean", True),
    "teacher": ("korean_teacher.apkg", "Korean 1-1", False),
    "conversation": ("korean_conversation.apkg", "Korean Conversation", False),
    "always-forget": ("korean_forget.apkg", "Korean Always Forget", False),
}
ORDER = ["old", "teacher", "conversation", "always-forget"]


def slug(s):
    return "".join(c if c.isalnum() else "_" for c in s)


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
        tags=[r["status"], r.get("category", "old"),
              f"unit{r['unit']}", r["topic"].replace(" ", "_")],
    )


by_cat = {}
for r in VOCAB:
    by_cat.setdefault(r.get("category", "old"), []).append(r)

cats = [c for c in ORDER if c in by_cat] + [c for c in by_cat if c not in ORDER]

for cat in cats:
    rows = by_cat[cat]
    fname, label, split = CAT_META.get(
        cat, (f"korean_{slug(cat)}.apkg", f"Korean {cat}", False))
    decks = []
    if split:
        by_unit = {}
        for r in rows:
            by_unit.setdefault(r["unit"], []).append(r)
        for u in sorted(by_unit, key=unit_sort_key):
            d = genanki.Deck(deck_id(f"{label}::Unit {u}"), f"{label}::Unit {u}")
            for r in by_unit[u]:
                d.add_note(make_note(r))
            decks.append(d)
    else:
        d = genanki.Deck(deck_id(label), label)
        for r in rows:
            d.add_note(make_note(r))
        decks.append(d)
    genanki.Package(decks).write_to_file(ROOT / fname)
    print(f"  {fname:<28} {len(rows):>3} notes  [{cat}] -> deck '{label}'")

print(f"\n{len(VOCAB)} words across {len(cats)} separate category packages (one link each).")
