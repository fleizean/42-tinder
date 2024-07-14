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
                        birthday DATE,
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


def get_user_by_id(user_id):
    conn = sqlite3.connect('database.db')  # Veritabanı bağlantısını kurun
    c = conn.cursor()
    
    # Belirli bir user_id için sorgu yapın
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_data = c.fetchone()  # Sorgu sonucunu alın
    
    conn.close()  # Veritabanı bağlantısını kapatın
    
    # Sorgu sonucunu bir sözlüğe çevirin
    if user_data:
        user_dict = {
            'id': user_data[0],
            'email': user_data[1],
            'username': user_data[2],
            'lastname': user_data[3],
            'firstname': user_data[4],
            'gender': user_data[6],
            'sexual_preferences': user_data[7],
            'biography': user_data[8],
            'fame_rating': user_data[9],
            'location': user_data[10],
            'birthday': user_data[11],
            # Diğer alanlarınız varsa buraya ekleyin
        }
        return user_dict
    else:
        return None 
    
def list_users():
    conn = sqlite3.connect('database.db')  # Veritabanı bağlantısını kurun
    c = conn.cursor()
    
    # Tüm kullanıcıları getir
    c.execute("SELECT * FROM users")
    users = c.fetchall()  # Sorgu sonucunu alın
    
    conn.close()  # Veritabanı bağlantısını kapatın
    
    # Sorgu sonucunu bir sözlüğe çevirin
    user_list = []
    for user_data in users:
        user_dict = {
            'id': user_data[0],
            'email': user_data[1],
            'username': user_data[2],
            'lastname': user_data[3],
            'firstname': user_data[4],
            'gender': user_data[6],
            'sexual_preferences': user_data[7],
            'biography': user_data[8],
            'fame_rating': user_data[9],
            'location': user_data[10],
            'birthday': user_data[11],
        }
        user_list.append(user_dict)
    return user_list
