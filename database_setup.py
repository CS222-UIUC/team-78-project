import sqlite3
import bcrypt  

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# cursor.execute("DROP TABLE IF EXISTS users") #done to restructure to add emails to db

# users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
''')


def add_user(username, plaintext_password, email):
    hashed_password = bcrypt.hashpw(plaintext_password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', 
                       (username, hashed_password.decode('utf-8'), email))
        
        connection.commit()
        print(f"User '{username}' with email '{email}' added successfully!")
    except sqlite3.IntegrityError:
        print(f"User '{username}' or email '{email}' already exists!")


# one username passsword set is username, password, email@gmail.com
# enasure that email domans beyond gmail like yahoo, hotmail, etc are inclided


# cursor.execute("DELETE FROM users") #done to restructure to add emails to db
# add_user('testUser', 'password123', 'testemail@gmail.com') #done AFTER restructure to add emails to db
add_user('testUser', 'password123', 'testemail@gmail.com')
add_user('sampleUser', 'securepassword', 'sampleuser@yahoo.com')
add_user('exampleUser', 'mypassword', 'exampleuser@hotmail.com')


rows = cursor.execute("SELECT * FROM users").fetchall()
for row in rows:
    print(row)

connection.close()
print("All Done! db and user setup is success!")