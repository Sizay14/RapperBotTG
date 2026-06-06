import sqlite3

conn = sqlite3.connect("bjt.db")
cursor = conn.cursor()

try:
    cursor.execute("""
                    ALTER TABLE users ADD COLUMN progress_time INTEGER DEFAULT 0
                   """)

    print("Добавлена")
except Exception as e:
    print("Ошибка", e)

conn.commit()
conn.close()