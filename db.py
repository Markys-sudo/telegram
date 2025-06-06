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
        user.username or "unknown",
        user.first_name or "unknown",
        user.language_code,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

def add_quiz_top(user, ranking):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            ranking INTEGER,
            saved_at TEXT
        )
    """)
    cur.execute("""
        INSERT INTO ranking (user_id, username, first_name, ranking, saved_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name,
            ranking=excluded.ranking,
            saved_at=excluded.saved_at
    """, (
        user.id,
        user.username or "unknown",
        user.first_name or "unknown",
        ranking,
        datetime.utcnow().isoformat()
        ))
    conn.commit()
    conn.close()

def get_top_users(limit=10):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT username, first_name, ranking
        FROM ranking
        ORDER BY ranking DESC, saved_at ASC
        LIMIT ?
    """, (limit,))
    top_users = cur.fetchall()
    conn.close()
    return top_users

def get_user_rank(user_id):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, ranking
        FROM ranking
        ORDER BY ranking DESC, saved_at ASC
    """)
    all_rows = cur.fetchall()
    conn.close()

    for i, row in enumerate(all_rows, 1):  # start from 1
        if row[0] == user_id:
            return i, len(all_rows)
    return None, len(all_rows)

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
    """, (
        user_id,
        recipe_text,
        datetime.utcnow().isoformat()
    ))
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