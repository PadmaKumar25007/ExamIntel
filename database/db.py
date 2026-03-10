import sqlite3

def create_connection():
    conn = sqlite3.connect("exam_ai.db", check_same_thread=False)
    return conn

conn = create_connection()
cursor = conn.cursor()

def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plans(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    title TEXT,
    analysis TEXT
    )
    """)

    conn.commit()
    
create_tables()