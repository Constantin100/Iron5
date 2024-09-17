from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required
from datetime import datetime
from flask_migrate import Migrate
import os
import io
from werkzeug.utils import secure_filename

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Добавьте секретный ключ для сессий
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance/product.db')  # Укажите путь к вашей базе данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('ProductImage', backref='product', lazy=True)
    active = db.Column(db.Boolean, default=True)
    in_stock = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'created_at': self.created_at,
            'active': self.active,
            'in_stock': self.in_stock
        }

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    data = db.Column(db.LargeBinary, nullable=True)  # Поле допускает NULL
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __repr__(self):
        return f'<ProductImage {self.filename}>'

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'product_id': self.product_id
        }

# Функция для обработки события перед вставкой
def insert_default_image(mapper, connection, target):
    if target.data is None:
        with open(os.path.join(basedir, 'static/images/no_image.jpg'), 'rb') as file:
            target.data = file.read()

# Привязка события к модели
from sqlalchemy import event
event.listen(ProductImage, 'before_insert', insert_default_image)

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
    products = Product.query.filter_by(active=True).all()
    if category:
        products = [product for product in products if product.category == category]
    if not products:
        return render_template('products.html', message="Товары на данный момент отсутствуют")
    return render_template('products.html', products=products)

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    print(f"Запрашиваемая категория: {category}")  # Отладочное сообщение
    if category:
        products = Product.query.filter_by(category=category, active=True).all()
    else:
        products = Product.query.filter_by(active=True).all()
    
    product_list = []
    for product in products:
        images = []
        for image in product.images:
            if image.data:
                images.append(url_for('get_image', image_id=image.id))
            else:
                images.append(url_for('static', filename='images/no_image.jpg'))
        
        product_list.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "in_stock": product.in_stock,
            "images": images
        })
    
    print(f"Найденные продукты: {product_list}")  # Отладочное сообщение
    return jsonify({"products": product_list})

@app.route('/image/<int:image_id>')
def get_image(image_id):
    image = ProductImage.query.get_or_404(image_id)
    return send_file(io.BytesIO(image.data), mimetype='image/jpeg', as_attachment=False, download_name=image.filename)

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
        new_product = Product(name=name, description=description, price=price, category=category, active=active, in_stock=in_stock)  # Передаем category и другие поля
        db.session.add(new_product)
        db.session.commit()
        
        if not images:
            # Добавляем шаблонное изображение, если изображения не загружены
            with open(os.path.join(basedir, 'static/images/no_image.jpg'), 'rb') as file:
                filename = 'no_image.jpg'
                new_image = ProductImage(filename=filename, data=file.read(), product_id=new_product.id)
                db.session.add(new_image)
                db.session.commit()
        else:
            for image in images:
                filename = secure_filename(image.filename)
                new_image = ProductImage(filename=filename, data=image.read(), product_id=new_product.id)
                db.session.add(new_image)
                db.session.commit()
                
        return redirect(url_for('admin'))
    return render_template('add_product.html')

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@session_login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = request.form['price']
        product.category = request.form['category']
        product.active = 'active' in request.form
        product.in_stock = request.form['in_stock']
        db.session.commit()
        flash('Продукт успешно обновлен')
        return redirect(url_for('admin'))
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@session_login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Продукт успешно удален')
    return redirect(url_for('admin'))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    image_urls = [url_for('get_image', image_id=image.id) for image in product.images]
    return render_template('product_detail.html', product=product, image_urls=image_urls)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаёт все таблицы
    app.run(debug=True)