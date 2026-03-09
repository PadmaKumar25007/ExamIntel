from database.db import conn, cursor

def register_user(username, password):
    cursor.execute(
        "INSERT INTO users(username,password) VALUES (?,?)",
        (username,password)
    )
    conn.commit()

def login_user(username, password):
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password)
    )
    return cursor.fetchone()