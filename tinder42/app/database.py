import sqlite3

def create_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL UNIQUE,
                        username TEXT NOT NULL UNIQUE,
                        last_name TEXT NOT NULL,
                        first_name TEXT NOT NULL,
                        password TEXT NOT NULL,
                        gender TEXT,
                        sexual_preferences TEXT,
                        biography TEXT,
                        fame_rating INTEGER DEFAULT 0,
                        location TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS interests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS profile_pictures (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_path TEXT NOT NULL,
                        is_profile_picture BOOLEAN NOT NULL,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(sender_id) REFERENCES users(id),
                        FOREIGN KEY(receiver_id) REFERENCES users(id)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        message TEXT NOT NULL,
                        is_read BOOLEAN NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )''')
    conn.commit()
    conn.close()