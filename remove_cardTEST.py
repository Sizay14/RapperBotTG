import sqlite3

USER_ID = 2019447611
REMOVE_COUNT = 32

conn = sqlite3.connect("bjt.db")
cursor = conn.cursor()

cursor.execute(
    "SELECT cards FROM users WHERE user_id=?",
    (USER_ID,)
)

result = cursor.fetchone()

if result:
    cards = result[0]

    if cards:
        user_cards = cards.split(',')
    else:
        user_cards = []

    removed = user_cards[-REMOVE_COUNT:]

    user_cards = user_cards[:-REMOVE_COUNT]

    cursor.execute("""
    UPDATE users
    SET cards=?
    WHERE user_id=?
    """, (
        ",".join(user_cards),
        USER_ID
    ))

    conn.commit()

    print("Удалены карточки:")
    for card in removed:
        print("-", card)

else:
    print("Пользователь не найден")

conn.close()