from flask import Flask
from flask_wtf import CSRFProtect
from flask_mail import Mail
from config import Config
from markupsafe import Markup
from app.database import create_database

csrf = CSRFProtect()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    csrf.init_app(app)
    mail.init_app(app)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        create_database()  # Veritabanını oluştur

    return app
