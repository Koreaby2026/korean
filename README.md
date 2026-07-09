# Korean learning system

## What's inside

- **`index.html`** — 🌐 web app (open in browser, fully local). 3 tabs: Words / Sentences / Reading.
- **`serve.sh`** — local server for phone access
- **`vocab.csv`** — main DB. Columns: `korean,romanization,translation,status,category,unit,topic,example`. The `category` column decides which deck (and which download link) a word belongs to.

## 📦 Category decks (separate download links)

Each category builds into its own `.apkg` so you can import just one at a time — they stay separate from each other:

| Category | Words | Deck | Download link |
|---|---|---|---|
| `old` (старые карточки) | 414 | `Korean::Unit X` | https://koreaby2026.github.io/korean/korean.apkg |
| `teacher` (занятия с учителем, 1-1) | 34 | `Korean 1-1` | https://koreaby2026.github.io/korean/korean_teacher.apkg |
| `conversation` (учебник) | 21 | `Korean Conversation` | https://koreaby2026.github.io/korean/korean_conversation.apkg |
| `always-forget` (не запоминаются) | — | `Korean Always Forget` | https://koreaby2026.github.io/korean/korean_forget.apkg *(появится, когда добавим слова)* |

Regenerate all decks after editing `vocab.csv`: `python build_anki.py`.
- **`sentences.json`** — 30 sentences for full-translation practice
- **`texts.json`** — 6 short reading texts at TOPIK 1B level with glossaries
- **`quiz.py`** — terminal-based quiz (alternative to web; words only)
- **`stats.json`** — auto-created stats for the Python quiz
- **`anki_import.txt`** — Anki tab-separated import with tags

## 🌐 Web app (recommended)

**On the computer:** double-click `index.html` — it opens in your browser. Progress is saved to `localStorage`.

**On the phone** (same Wi-Fi):
```bash
cd ~/korean
./serve.sh
```
The script prints an address like `http://192.168.1.42:8765/` — open it in Safari and "Add to Home Screen" to get a native-feeling app icon.

Features:
- **Words tab:** modes 🔥 Forgotten / ✨ New / All / by topic / by unit. Direction 한→en or en→한. In en→한 mode the app accepts both hangul and romanization. Hint button shows romanization. "Show more often" flags a word as weak.
- **Sentences tab:** 30 full sentences. Type your translation, hit "reveal", then self-grade ✅/❌. Wrong sentences come up more often.
- **Reading tab:** 6 short texts at your level. Glossary terms in the text are underlined — click to reveal inline. Toggle full English translation and glossary panel.
- Session counter, "learned" badge (4+ answers, >85% accuracy)
- Export progress as JSON, reset stats

## Anki import

1. Open Anki desktop.
2. **File → Import** → pick `anki_import.txt`.
3. Card type `Basic`, separator `Tab`, field 1 = Front, field 2 = Back, field 3 = Tags. Enable "Allow HTML in fields".
4. Sync to phone.

Filtered decks via tags: `tag:forgotten`, `tag:unit3`, `tag:hobbies`, etc.

## Updating the dictionary

Edit `vocab.csv` directly (Numbers/Excel works). Same columns. After updates, ask me to regenerate `index.html` and `anki_import.txt`.

## Suggested rhythm

- **Daily:** 10–15 min Anki on the phone — SRS picks what to review.
- **2–3× a week:** open the web app, "Forgotten" mode, 10–20 cards.
- **Weekly:** ask me for a short text at your level using your forgotten words + 2–3 new ones. I have your full vocab.
- When a forgotten word is consistently right (3+ in a row) — change its `status` to `learned` in CSV.

## Things you can ask me

- "quiz me on forgotten" — I'll ask 10 words in chat
- "give me a text about [topic]" — short reading at your level with glossary
- "drill me on [grammar]" — 5 exercises
- "add to vocab: [words]" — I'll append to `vocab.csv`
- "show my weakest words" — top wrong-rate words from `stats.json`
