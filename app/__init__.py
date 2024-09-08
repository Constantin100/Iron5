# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Настройки базы данных
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'  # Путь к вашей базе данных
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключение отслеживания изменений

    db.init_app(app)  # Инициализация базы данных с приложением

    with app.app_context():
        from . import routes  # Импортируем маршруты
        db.create_all()  # Создаем таблицы, если они не существуют

    return app