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

def add_user(username, plaintext_password):
    hashed_password = generate_password_hash(plaintext_password)
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                       (username, hashed_password.encode('utf-8')))
        connection.commit()
        print(f"User '{username}' added successfully!")
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists!")

add_user('testuser', 'password123') # for debugging tried making sample user

connection.close()
print("All Done! db and user setup is success!")
