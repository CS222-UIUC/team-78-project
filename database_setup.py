import sqlite3
from werkzeug.security import generate_password_hash  

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorites (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id  INTEGER NOT NULL,
        symbol   TEXT NOT NULL,
        UNIQUE(user_id, symbol),          -- prevents duplicates
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
''')
connection.commit()

def add_user(username, plaintext_password):
    hashed_password = generate_password_hash(plaintext_password)
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                       (username, hashed_password.encode('utf-8')))
        connection.commit()
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists!")

connection.close()
print("All Done! db and user setup is success!")
