import sqlite3
from flask import Blueprint, render_template, url_for, flash, redirect, request,session
from app.forms import RegistrationForm, LoginForm
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_user_by_id, list_users
from config import Config
from itsdangerous import URLSafeTimedSerializer
from app.utils.mailservice import send_password_reset_email


main = Blueprint('main', __name__)


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('main.home'))

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
            conn = sqlite3.connect(Config.DATABASE_URL)
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
    if 'user_id' in session:
        return redirect(url_for('main.home'))
    conn = sqlite3.connect(Config.DATABASE_URL)
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
            conn = sqlite3.connect(Config.DATABASE_URL)
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

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session.get('user_id')  # Kullanıcı ID'sini session'dan alın
    if user_id:
        user_data = get_user_by_id(user_id)  # Veritabanından kullanıcı bilgilerini çekin
        if user_data:
            # Kullanıcı bilgilerini şablona argüman olarak geçirin
            return render_template('home.html', title="Home", user=user_data)
    # Eğer kullanıcı bilgisi bulunamazsa veya kullanıcı giriş yapmamışsa, hata mesajı gösterin
    return 'User not found or not logged in', 404

@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        conn = sqlite3.connect(Config.DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        if user:
            serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
            token = serializer.dumps(user[0], salt=Config.PASSWORD_RESET_SALT)
            reset_url = url_for('main.change_password', token=token, _external=True, token_expires=int(time.time()) + 3600)
            send_password_reset_email(email, reset_url, user[5], user[3])
            flash('Password reset email sent!', 'info')
            return redirect(url_for('main.login'))
        else:
            flash('User not found!', 'danger')
    return render_template('forgot-password.html', title='Forgot Password')

@main.route('/change-password/<token>', methods=['GET', 'POST'])
def change_password(token):
    if 'token_expires' in request.args:
        token_expires = request.args['token_expires']
        if int(token_expires) < int(time.time()):
            flash('The password reset link has expired.', 'error')
            return redirect(url_for('main.forgot_password'))

    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirmpassword']
        if new_password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('main.change_password', token=token))
        try:
            serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
            user_id = serializer.loads(token, salt=Config.PASSWORD_RESET_SALT, max_age=3600)
            conn = sqlite3.connect(Config.DATABASE_URL)
            cursor = conn.cursor()
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
            conn.commit()
            conn.close()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('main.login'))
        except:
            flash('The password reset link is invalid or has expired.', 'error')
            return redirect(url_for('main.forgot_password'))
    else:
        try:
            serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
            email = serializer.loads(token, salt=Config.PASSWORD_RESET_SALT, max_age=3600)
            return render_template('change-password.html', title='Reset Password')
        except:
            flash('The password reset link is invalid or has expired.', 'error')
            return redirect(url_for('main.forgot_password'))