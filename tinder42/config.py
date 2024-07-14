import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Replace 'default_secret_key' with a real secret key in production
    PASSWORD_RESET_SALT = os.getenv('PASSWORD_RESET_SALT', 'default_password_reset_salt')  # Replace 'default_password_reset_salt' with a real password reset salt in production
    DATABASE_URL = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    DEBUG = os.getenv('DEBUG', 'false').lower() in ['true', '1', 't']

    print(f"SECRET_KEY: {SECRET_KEY}")

config = Config
