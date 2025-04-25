import sqlite3
import bcrypt  

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

    hashed_password = bcrypt.hashpw(plaintext_password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password.decode('utf-8')))
        connection.commit()
        print(f"User '{username}' added successfully!")
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists!")

# add_user('testuser', 'password123') # for debugging triad making sample user
# one username passsword set is username, password, email@gmail.com

connection.close()
print("All Done! db and user setup is success!")