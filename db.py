import sqlite3
from datetime import datetime

def save_user(user):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            language_code TEXT,
            created_at TEXT
        )
    """)
    cur.execute("""
        INSERT OR IGNORE INTO users (id, username, first_name, language_code, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user.id,
        user.username,
        user.first_name,
        user.language_code,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


def add_favorite(user_id, recipe_text):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            recipe_text TEXT,
            saved_at TEXT
        )
    """)
    cur.execute("""
        INSERT INTO favorites (user_id, recipe_text, saved_at)
        VALUES (?, ?, ?)
    """, (user_id, recipe_text, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_favorites(user_id):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT recipe_text FROM favorites
        WHERE user_id = ?
        ORDER BY saved_at DESC
        LIMIT 5
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]