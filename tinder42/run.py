from flask import Flask, render_template_string, redirect, url_for
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
import sqlite3

app = Flask(__name__, template_folder='app/templates')
app.config['SECRET_KEY'] = 'q3s4d5f6g7h8j9k0l'

# Veritabanı bağlantısı oluşturmak için fonksiyon
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Örnek bir User sınıfı (ORM'siz)
class User:
    def __init__(self, email, username, last_name, first_name, password):
        self.email = email
        self.username = username
        self.last_name = last_name
        self.first_name = first_name
        self.password = password

# Örnek bir UserView sınıfı
class UserView(BaseView):
    @expose('/')
    def index(self):
        users = self.get_users()
        return self.render('users.html', users=users)

    def get_users(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        conn.close()
        return users

    def is_visible(self):
        return True

# Flask-Admin nesnesini oluşturun ve uygulamaya ekleyin
admin = Admin(app, name='Microblog', template_mode='bootstrap3')

# Örnek bir UserView'i Flask-Admin'e ekleme
admin.add_view(UserView(name='Users'))

if __name__ == '__main__':
    app.run(debug=True)
