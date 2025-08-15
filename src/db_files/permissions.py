import sqlite3

db_name = 'kara.sqlite'

def init_db():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS permissions (
        user_id INTEGER PRIMARY KEY,
        role INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def set_permission(user_id: int, role: int):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    if role not in [1, 2, 3]:
        raise ValueError("Role must be 1 (user), 2 (moderator), or 3 (admin).")
    cursor.execute("""
    REPLACE INTO permissions (user_id, role)
    VALUES (?, ?)
    """, (user_id, role))
    conn.commit()
    conn.close()

def get_permission(user_id: int) -> int:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT role FROM permissions WHERE user_id = ?
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

if __name__ == "__main__":
    init_db()
    set_permission(748048975000633384, 3)  # Initialize master role for the bot owner