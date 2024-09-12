# app/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)  # Изменено на 80 символов
    description = db.Column(db.String(200), nullable=True)  # Изменено на 200 символов
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Добавляем атрибут category
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # Изменено на db.func.current_timestamp()
    images = db.relationship('ProductImage', backref='product', lazy=True)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Product {self.name}>'

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __repr__(self):
        return f'<ProductImage {self.filename}>'