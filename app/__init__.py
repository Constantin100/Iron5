# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Конфигурация
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    
    # Инициализация расширений
    db.init_app(app)
    
    # Регистрация Blueprint
    from app.routes import main
    app.register_blueprint(main)
    
    # Создание папки для загрузок, если её нет
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Создание администратора при первом запуске
    with app.app_context():
        from app.models import User
        db.create_all()
        
        # Проверяем, существует ли уже админ
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=generate_password_hash('password')
            )
            db.session.add(admin)
            db.session.commit()
    
    return app