# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Импортируем Flask-Migrate

db = SQLAlchemy()
migrate = Migrate()  # Создаем экземпляр Migrate

def create_app():
    app = Flask(__name__)
    
    # Настройки базы данных
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'  # Путь к вашей базе данных
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключение отслеживания изменений

    db.init_app(app)  # Инициализация базы данных с приложением
    migrate.init_app(app, db)  # Инициализация миграций с приложением и базой данных

    with app.app_context():
        from . import routes  # Импортируем маршруты
        db.create_all()  # Создаем таблицы, если они не существуют

    return app