from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required
from datetime import datetime
from flask_migrate import Migrate
from models import db, Product
import os


basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Добавьте секретный ключ для сессий
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance/product.db')  # Укажите путь к вашей базе данных
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Добавляем атрибут category
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('ProductImage', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __repr__(self):
        return f'<ProductImage {self.filename}>'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

@app.route('/products')
def products():
    category = request.args.get('category')
    products = Product.query.all()  # Получаем все продукты из базы данных
    if category:
        products = [product for product in products if product.category == category]
    if not products:
        return render_template('products.html', message="Товары на данный момент отсутствуют")
    return render_template('products.html', products=products)

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    print(f"Запрашиваемая категория: {category}")  # Отладочное сообщение
    products = Product.query.all()  # Получаем все продукты из базы данных
    if category:
        products = [product for product in products if product.category == category]
    if not products:
        return jsonify({"products": []}), 200
    product_list = [{"name": product.name, "description": product.description, "price": product.price} for product in products]
    print(f"Найденные продукты: {product_list}")  # Отладочное сообщение
    return jsonify({"products": product_list})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':  # Простой пример проверки
            session['logged_in'] = True
            print("Успешный вход в систему")  # Отладочное сообщение
            return redirect(url_for('admin'))
        else:
            flash('Неверное имя пользователя или пароль')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

def session_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            print("Пользователь не авторизован")  # Отладочное сообщение
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@session_login_required
def admin():
    products = Product.query.all()  # Получаем все продукты из базы данных
    return render_template('admin.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
@session_login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']  # Получаем значение category из формы
        price = request.form.get('price', 0.0)  # Устанавливаем значение по умолчанию для price
        images = request.files.getlist('images')
        active = 'active' in request.form
        in_stock = request.form['in_stock']
        # Логика для сохранения продукта
        new_product = Product(name=name, description=description, price=price, category=category)  # Передаем category
        db.session.add(new_product)
        db.session.commit()
        for image in images:
            new_image = ProductImage(filename=image.filename, product_id=new_product.id)
            db.session.add(new_image)
            db.session.commit()
        return redirect(url_for('admin'))
    return render_template('add_product.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаёт все таблицы
    app.run(debug=True)