import sqlite3
import json
import random
import time

USER_ID = 2019447611
CARDS_TO_GIVE = 11

# Загружаем всех рэперов
with open("rappers.json", "r", encoding="utf-8") as f:
    rappers = json.load(f)

conn = sqlite3.connect("bjt.db")
cursor = conn.cursor()

cursor.execute(
    "SELECT cards, last_drop, promo_used, progress_time FROM users WHERE user_id=?",
    (USER_ID,)
)

result = cursor.fetchone()

if result:
    cards, last_drop, promo_used, progress_time = result

    if cards:
        user_cards = cards.split(',')
    else:
        user_cards = []

    available = [
        r["name"]
        for r in rappers
        if r["name"] not in user_cards
    ]

    random_cards = random.sample(
        available,
        min(CARDS_TO_GIVE, len(available))
    )

    user_cards.extend(random_cards)

    progress_time = time.time()

    cursor.execute("""
    UPDATE users
    SET cards=?, progress_time=?
    WHERE user_id=?
    """, (
        ",".join(user_cards),
        progress_time,
        USER_ID
    ))

    conn.commit()

    print("Выданы карточки:")
    for card in random_cards:
        print("-", card)

else:
    print("Пользователь не найден")

conn.close()