import sqlite3
from flask import Blueprint, render_template, url_for, flash, redirect, request,session
from app.forms import RegistrationForm, LoginForm
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_user_by_id, list_users

main = Blueprint('main', __name__)


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Extract form data
        print(request.form)
        email = request.form.get('email')
        username = request.form.get('username')
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmpassword')  # Note the HTML form field name
        gender = request.form.get('gender')
        birthday = request.form.get('birthday')

        if confirm_password != password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('main.signup'))



        # Instantiate the form with extracted data
        form = RegistrationForm(email, username, last_name, first_name, password, confirm_password, gender, birthday)

        if form.validate():
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            # Assuming User model and database setup is correct
            new_user = User(email=email, username=username, last_name=last_name, first_name=first_name, password=hashed_password, gender=gender, birthday=birthday)

            # Database insertion logic (assuming it's correct and database is set up properly)
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, username, last_name, first_name, password, gender, birthday) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (new_user.email, new_user.username, new_user.last_name, new_user.first_name, new_user.password, new_user.gender, new_user.birthday))
            conn.commit()
            conn.close()

            flash('Registration successful!', 'success')
            return redirect(url_for('main.login'))
    else:
        form = RegistrationForm('', '', '', '', '', '', '', '')  # Empty form for GET request
    return render_template('signup.html', title='Register', form=form)

@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # Sonuçları terminale yazdır
    for user in users:
        print(user)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(email)
        print(password)
        form = LoginForm(email, password)
        if form.validate():
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (form.email,))
            user = cursor.fetchone()
            conn.close()
            print("User: ", check_password_hash(user[5], form.password))
            if user and check_password_hash(user[5], form.password):  # Assuming password is the 5th column in the users table
                flash('Login successful!', 'success')
                session['user_id'] = user[0] 
                return redirect(url_for('main.home'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
    else:
        form = LoginForm('', '')  # Empty form for GET request
    return render_template('login.html', title='Login', form=form)

@main.route('/home')
def home():
    user_id = session.get('user_id')  # Kullanıcı ID'sini session'dan alın
    if user_id:
        user_data = get_user_by_id(user_id)  # Veritabanından kullanıcı bilgilerini çekin
        if user_data:
            # Kullanıcı bilgilerini şablona argüman olarak geçirin
            return render_template('home.html', user=user_data)
    # Eğer kullanıcı bilgisi bulunamazsa veya kullanıcı giriş yapmamışsa, hata mesajı gösterin
    return 'User not found or not logged in', 404

@main.route('/logout')
def logout():
    session.pop('user_id', None)