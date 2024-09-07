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
                        comment_count INTEGER DEFAULT 0,
                        match_count INTEGER DEFAULT 0,
                        latitude TEXT,
                        longitude TEXT,
                        birthday DATE,
                        verification_token TEXT,
                        verify_email BOOLEAN DEFAULT 0,
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
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = c.fetchone()
        if user_data:
            user_dict = {
                'id': user_data[0],
                'email': user_data[1],
                'username': user_data[2],
                'last_name': user_data[3],
                'first_name': user_data[4],
                'password': user_data[5],
                'gender': user_data[6],
                'sexual_preferences': user_data[7],
                'biography': user_data[8],
                'fame_rating': user_data[9],
                'comment_count': user_data[10],
                'match_count': user_data[11],
                'latitude': user_data[12],
                'longitude': user_data[13],
                'birthday': user_data[14],
                'verification_token': user_data[15],
                'verify_email': user_data[16],
                'created_at': user_data[17],
                'updated_at': user_data[18],
                'profile_pictures': []
            }
            
            # Profil fotoğraflarını getirme
            c.execute("SELECT image_path, is_profile_picture FROM profile_pictures WHERE user_id = ?", (user_data[0],))
            profile_pictures_data = c.fetchall()

            for picture in profile_pictures_data:
                user_dict['profile_pictures'].append({
                    'image_path': picture[0],
                    'is_profile_picture': picture[1]
                })
            
            return user_dict
        else:
            return None

def list_users():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        users = c.fetchall()
        user_list = []
        for user_data in users:
            user_dict = {
                'id': user_data[0],
                'email': user_data[1],
                'username': user_data[2],
                'last_name': user_data[3],
                'first_name': user_data[4],
                'password': user_data[5],
                'gender': user_data[6],
                'sexual_preferences': user_data[7],
                'biography': user_data[8],
                'fame_rating': user_data[9],
                'comment_count': user_data[10],
                'match_count': user_data[11],
                'latitude': user_data[12],
                'longitude': user_data[13],
                'birthday': user_data[14],
                'verification_token': user_data[15],
                'verify_email': user_data[16],
                'created_at': user_data[17],
                'updated_at': user_data[18]
            }
            user_list.append(user_dict)
        return user_list

def get_user_by_verification_token(verification_token):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE verification_token = ?", (verification_token,))
        user_data = c.fetchone()
        if user_data:
            user_dict = {
                'id': user_data[0],
                'email': user_data[1],
                'username': user_data[2],
                'last_name': user_data[3],
                'first_name': user_data[4],
                'password': user_data[5],
                'gender': user_data[6],
                'sexual_preferences': user_data[7],
                'biography': user_data[8],
                'fame_rating': user_data[9],
                'comment_count': user_data[10],
                'match_count': user_data[11],
                'latitude': user_data[12],
                'longitude': user_data[13],
                'birthday': user_data[14],
                'verification_token': user_data[15],
                'verify_email': user_data[16],
                'created_at': user_data[17],
                'updated_at': user_data[18]
            }
            return user_dict
        else:
            return None

def get_user_by_username(username):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = c.fetchone()
        if user_data:
            user_dict = {
                'id': user_data[0],
                'email': user_data[1],
                'username': user_data[2],
                'last_name': user_data[3],
                'first_name': user_data[4],
                'password': user_data[5],
                'gender': user_data[6],
                'sexual_preferences': user_data[7],
                'biography': user_data[8],
                'fame_rating': user_data[9],
                'comment_count': user_data[10],
                'match_count': user_data[11],
                'latitude': user_data[12],
                'longitude': user_data[13],
                'birthday': user_data[14],
                'verification_token': user_data[15],
                'verify_email': user_data[16],
                'created_at': user_data[17],
                'updated_at': user_data[18],
                'profile_pictures': []
            }

            # Profil fotoğraflarını getirme
            c.execute("SELECT image_path, is_profile_picture FROM profile_pictures WHERE user_id = ?", (user_data[0],))
            profile_pictures_data = c.fetchall()

            for picture in profile_pictures_data:
                user_dict['profile_pictures'].append({
                    'image_path': picture[0],
                    'is_profile_picture': picture[1]
                })

            return user_dict
        else:
            return None

def get_interests_by_user_id(user_id):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM interests WHERE user_id = ?", (user_id,))
        interests = c.fetchall()
        interests_list = []
        for interest in interests:
            interest_dict = {
                'id': interest[0],
                'name': interest[1],
                'user_id': interest[2],
            }
            interests_list.append(interest_dict)
        return interests_list

def get_profile_picture_by_user_id(user_id):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT image_path FROM profile_pictures WHERE user_id = ? AND is_profile_picture = 1", (user_id,))
        profile_picture = c.fetchone()
        if profile_picture:
            return "/media/" + profile_picture[0]
        else:
            return "../../static/assets/defaultpic.jpeg"