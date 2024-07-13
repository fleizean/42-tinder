import sqlite3
from flask import Blueprint, render_template, url_for, flash, redirect, request
from app.forms import RegistrationForm, LoginForm
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(id=None, email=form.email.data, username=form.username.data, last_name=form.last_name.data, first_name=form.first_name.data, password=hashed_password, gender='', sexual_preferences='')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, username, last_name, first_name, password) VALUES (?, ?, ?, ?, ?)",
                       (new_user.email, new_user.username, new_user.last_name, new_user.first_name, new_user.password))
        conn.commit()
        conn.close()

        flash('Registration successful!', 'success')
        return redirect(url_for('main.index'))
    return render_template('signup.html', title='Register', form=form)

@main.route('/')
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        form = LoginForm(email, password)
        if form.validate():
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (form.email,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user[4], form.password):  # Assuming password is the 5th column in the users table
                flash('Login successful!', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
    else:
        form = LoginForm('', '')  # Empty form for GET request
    return render_template('login.html', title='Login', form=form)
