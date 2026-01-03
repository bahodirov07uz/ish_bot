import sqlite3

conn = sqlite3.connect("bot.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
)
""")
conn.commit()

def get_user(telegram_id):
    cur.execute("SELECT name FROM users WHERE telegram_id=?", (telegram_id,))
    return cur.fetchone()

def save_user(telegram_id, name):
    cur.execute(
        "INSERT OR REPLACE INTO users (telegram_id, name) VALUES (?, ?)",
        (telegram_id, name)
    )
    conn.commit()
