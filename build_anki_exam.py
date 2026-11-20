#!/usr/bin/env python3
"""Separate exam deck: the words of part 1 of Exam_prep_pack (user's own review list, Nov 2026).

Reads the vt(...) tables straight out of Печать_2A/build_exam_pack.py, so the deck always matches
the printed pack. One card per word, EN -> 한 with the example sentence on the back.
Output: korean_2a_exam.apkg (deck "Korean 2A Exam"). Does not touch vocab.csv or the other decks.
"""
import re, ast, zlib
from pathlib import Path
import genanki

ROOT = Path(__file__).parent
SRC = Path("/Users/jpu/Desktop/Korean book/Печать_2A/build_exam_pack.py").read_text(encoding="utf-8")
MODEL_ID = 1611500001  # same note type as the other decks


def deck_id(name):
    return 1_100_000_000 + ((zlib.crc32(name.encode()) & 0x7FFFFFFF) % 1_000_000_000)


model = genanki.Model(
    MODEL_ID, "Korean (Hazyaeva v2)",
    fields=[{"name": "Korean"}, {"name": "English"}, {"name": "Romanization"}, {"name": "Example"}, {"name": "Unit"}, {"name": "Topic"}],
    templates=[{
        "name": "EN → 한 (recall)",
        "qfmt": "<div style='font-size:18px;color:#666'>{{English}}</div>"
                "<div style='font-size:13px;color:#999;margin-top:6px'>recall the Korean word</div>",
        "afmt": "{{FrontSide}}<hr id='answer'>"
                "<div style='font-size:34px;font-weight:600'>{{Korean}}</div>"
                "<div style='font-size:14px;color:#aaa;margin-top:4px'>{{Romanization}}</div>"
                "<div style='font-size:14px;color:#888;margin-top:10px'>{{Example}}</div>"
                "<div style='font-size:11px;color:#bbb;margin-top:14px'>unit {{Unit}} · {{Topic}}</div>",
    }],
    css=(".card { font-family: 'Helvetica Neue', sans-serif; text-align: center; background-color: #faf7f2; color: #1f1d1a; padding: 24px; }"
         "hr#answer { border: none; border-top: 1px solid #ddd; margin: 18px 0; }"),
)

# vt("title", [(en, ko, sentence), ...], "note")  -> parse title + the list literal
rows, seen = [], set()
for m in re.finditer(r'vt\("([^"]+)",\s*(\[.*?\])(?:,\s*"[^"]*")?\)', SRC, re.S):
    topic = re.sub(r"^[①-⑨]\s*", "", m.group(1)).split(" · ")[0]
    for en, ko, sent in ast.literal_eval(m.group(2)):
        key = ko
        if key in seen:
            continue
        seen.add(key)
        rows.append((en, ko, sent, topic))

deck = genanki.Deck(deck_id("Korean 2A Exam"), "Korean 2A Exam")
for en, ko, sent, topic in rows:
    deck.add_note(genanki.Note(model=model, fields=[ko, en, "", sent, "2A exam", topic],
                               tags=["exam2A", "".join(c if c.isalnum() else "_" for c in topic)]))
genanki.Package([deck]).write_to_file(ROOT / "korean_2a_exam.apkg")
print(len(rows), "cards ->", ROOT / "korean_2a_exam.apkg")
