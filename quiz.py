#!/usr/bin/env python3
"""Korean vocabulary quiz with SRS-style weighting.

Forgotten words appear ~3x more often. Wrong answers boost weight further.
Run from terminal: python3 quiz.py
"""

import csv
import random
import sys
import json
from datetime import datetime
from pathlib import Path

VOCAB_PATH = Path(__file__).parent / "vocab.csv"
STATS_PATH = Path(__file__).parent / "stats.json"


def load_vocab():
    with open(VOCAB_PATH, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_stats():
    if STATS_PATH.exists():
        return json.loads(STATS_PATH.read_text(encoding="utf-8"))
    return {}


def save_stats(stats):
    STATS_PATH.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def weight(entry, stats):
    """Higher weight = more likely to be picked."""
    base = 3.0 if entry["status"] == "forgotten" else 1.0
    s = stats.get(entry["korean"], {})
    wrong = s.get("wrong", 0)
    right = s.get("right", 0)
    accuracy = right / (right + wrong) if (right + wrong) else 0
    base += wrong * 0.7
    base -= right * 0.15
    if accuracy > 0.85 and (right + wrong) >= 4:
        base *= 0.4
    return max(base, 0.2)


def pick(pool, stats):
    weights = [weight(e, stats) for e in pool]
    return random.choices(pool, weights=weights, k=1)[0]


def normalize(s):
    return s.strip().lower().replace("ё", "е")


def check_answer(user, correct):
    user_n = normalize(user)
    for variant in correct.split("/"):
        if normalize(variant) == user_n:
            return True
    return False


def filter_pool(vocab, mode, value=None):
    if mode == "all":
        return vocab
    if mode == "forgotten":
        return [e for e in vocab if e["status"] == "forgotten"]
    if mode == "new":
        return [e for e in vocab if e["status"] == "new"]
    if mode == "topic":
        return [e for e in vocab if e["topic"] == value]
    if mode == "unit":
        return [e for e in vocab if e["unit"] == value]
    return vocab


def menu(vocab):
    print("\n=== Korean Quiz ===")
    print(f"Всего слов в базе: {len(vocab)}")
    forgotten = sum(1 for e in vocab if e["status"] == "forgotten")
    new = sum(1 for e in vocab if e["status"] == "new")
    print(f"Забытые (приоритет): {forgotten} | Новые: {new}\n")
    print("1. Забытые слова (рекомендую)")
    print("2. Новые слова")
    print("3. Все слова (со взвешиванием)")
    print("4. По теме")
    print("5. По юниту")
    print("6. Направление: КР → РУС")
    print("7. Направление: РУС → КР (сложнее)")
    print("0. Выход")
    return input("> ").strip()


def pick_topic(vocab):
    topics = sorted(set(e["topic"] for e in vocab))
    for i, t in enumerate(topics, 1):
        cnt = sum(1 for e in vocab if e["topic"] == t)
        print(f"{i}. {t} ({cnt})")
    idx = input("номер темы > ").strip()
    if idx.isdigit() and 1 <= int(idx) <= len(topics):
        return topics[int(idx) - 1]
    return None


def pick_unit(vocab):
    units = sorted(set(e["unit"] for e in vocab))
    for i, u in enumerate(units, 1):
        cnt = sum(1 for e in vocab if e["unit"] == u)
        print(f"{i}. Unit {u} ({cnt})")
    idx = input("номер юнита > ").strip()
    if idx.isdigit() and 1 <= int(idx) <= len(units):
        return units[int(idx) - 1]
    return None


def run_quiz(pool, direction, stats):
    if not pool:
        print("Пул пуст.")
        return
    print(f"\nВ пуле: {len(pool)} слов. Enter — пропустить. 'q' — выход. 'h' — подсказка.\n")
    asked = 0
    correct = 0
    while True:
        entry = pick(pool, stats)
        if direction == "kr_ru":
            question = entry["korean"]
            answer = entry["translation"]
            prompt_label = "перевод"
        else:
            question = entry["translation"]
            answer = entry["korean"]
            prompt_label = "по-корейски"

        marker = " 🔥" if entry["status"] == "forgotten" else ""
        user = input(f"[{asked + 1}] {question}{marker}\n  {prompt_label}> ").strip()

        if user.lower() == "q":
            break
        if user.lower() == "h":
            print(f"  💡 {entry['romanization']}")
            user = input(f"  {prompt_label}> ").strip()

        s = stats.setdefault(entry["korean"], {"right": 0, "wrong": 0})
        if not user:
            print(f"  ⏭  пропуск. Ответ: {answer} ({entry['romanization']})")
        elif check_answer(user, answer):
            print(f"  ✅ верно! {entry['romanization']}")
            if entry.get("example"):
                print(f"     {entry['example']}")
            s["right"] += 1
            correct += 1
        else:
            print(f"  ❌ не то. Правильно: {answer} ({entry['romanization']})")
            if entry.get("example"):
                print(f"     {entry['example']}")
            s["wrong"] += 1
        s["last"] = datetime.now().isoformat(timespec="seconds")
        asked += 1
        print()

        if asked % 10 == 0:
            save_stats(stats)
            print(f"--- {correct}/{asked} ({100*correct//asked}%) — продолжаем? Enter / 'q'")
            if input().strip().lower() == "q":
                break

    save_stats(stats)
    if asked:
        print(f"\nИтог: {correct}/{asked} ({100*correct//asked}%)")


def main():
    vocab = load_vocab()
    stats = load_stats()
    direction = "kr_ru"

    while True:
        choice = menu(vocab)
        if choice == "0":
            break
        if choice == "6":
            direction = "kr_ru"
            print("→ КР → РУС")
            continue
        if choice == "7":
            direction = "ru_kr"
            print("→ РУС → КР")
            continue

        if choice == "1":
            pool = filter_pool(vocab, "forgotten")
        elif choice == "2":
            pool = filter_pool(vocab, "new")
        elif choice == "3":
            pool = filter_pool(vocab, "all")
        elif choice == "4":
            t = pick_topic(vocab)
            if not t:
                continue
            pool = filter_pool(vocab, "topic", t)
        elif choice == "5":
            u = pick_unit(vocab)
            if not u:
                continue
            pool = filter_pool(vocab, "unit", u)
        else:
            continue

        run_quiz(pool, direction, stats)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПока!")
        sys.exit(0)
