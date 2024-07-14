from flask_mail import Message
from app import mail
from config import Config
from flask import render_template

def send_password_reset_email(to_email, reset_url, firstname, username):
    msg = Message("Password Reset Request",
                  sender=Config.MAIL_USERNAME,
                  recipients=[to_email])
    # HTML şablonunu kullanarak mesaj gövdesini oluşturun
    msg.html = render_template('password_reset_email.html', reset_url=reset_url, email=to_email, firstname=firstname, username=username)
    mail.send(msg)