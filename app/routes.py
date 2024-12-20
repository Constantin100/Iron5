from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, session, flash, abort
from app import db
from app.models import Product, ProductImage, Article, User
from werkzeug.utils import secure_filename
import os
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/articles')
def articles():
    articles = Article.query.filter_by(active=True).order_by(Article.created_at.desc()).all()
    return render_template('articles.html', articles=articles)

@main.route('/article/<int:article_id>')
def article(article_id):
    try:
        article = Article.query.get_or_404(article_id)
        if not article.active:
            abort(404)
        return render_template('article.html', article=article)
    except Exception as e:
        flash('Статья не найдена')
        return redirect(url_for('main.articles'))

@main.route('/api/products')
def get_products():
    category = request.args.get('category')
    if category:
        products = Product.query.filter_by(category=category, active=True).all()
    else:
        products = Product.query.filter_by(active=True).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'images': [img.filename for img in p.images]
    } for p in products])

@main.route('/add_product', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        try:
            quantity = int(request.form.get('quantity', 0))
        except (ValueError, TypeError):
            quantity = 0

        product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=float(request.form.get('price', 0)),
            quantity=quantity,
            in_stock=request.form.get('in_stock'),
            category=request.form.get('category'),
            active=True
        )
        
        db.session.add(product)
        db.session.flush()

        files = request.files.getlist('images')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                base, ext = os.path.splitext(filename)
                filename = f"{base}_{product.id}{ext}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                
                image = ProductImage(filename=filename, product_id=product.id)
                db.session.add(image)

        db.session.commit()
        return redirect(url_for('main.admin'))
    return render_template('add_product.html')

@main.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        try:
            quantity = int(request.form.get('quantity', 0))
        except (ValueError, TypeError):
            quantity = 0

        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price', 0))
        product.quantity = quantity
        product.in_stock = request.form.get('in_stock')
        product.category = request.form.get('category')

        # Обработка новых изображений
        files = request.files.getlist('images')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                base, ext = os.path.splitext(filename)
                filename = f"{base}_{product.id}{ext}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                
                image = ProductImage(filename=filename, product_id=product.id)
                db.session.add(image)

        db.session.commit()
        return redirect(url_for('main.admin'))
    return render_template('edit_product.html', product=product)

@main.route('/delete_image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    image = ProductImage.query.get_or_404(image_id)
    
    # Удаляем файл
    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image.filename))
    except:
        pass  # Игнорируем ошибку, если файл не существует
    
    # Удаляем запись из базы данных
    db.session.delete(image)
    db.session.commit()
    
    return jsonify({'success': True})

@main.route('/admin')
@admin_required
def admin():
    products = Product.query.all()
    articles = Article.query.all()
    return render_template('admin.html', products=products, articles=articles)

@main.route('/products')
@main.route('/products/<category>')
def products(category=None):
    try:
        if category:
            products = Product.query.filter_by(category=category, active=True).all()
        else:
            products = Product.query.filter_by(active=True).all()
        return render_template('products.html', products=products, category=category)
    except Exception as e:
        flash('Произошла ошибка при загрузке продуктов')
        return redirect(url_for('main.home'))

@main.route('/admin/add_article', methods=['GET', 'POST'])
@admin_required
def add_article():
    if request.method == 'POST':
        article = Article(
            title=request.form.get('title'),
            content=request.form.get('content'),
            active=True
        )
        
        # Обработка изображения
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                article.image = filename

        db.session.add(article)
        db.session.commit()
        return redirect(url_for('main.admin'))
    return render_template('add_article.html')

@main.route('/admin/edit_article/<int:article_id>', methods=['GET', 'POST'])
@admin_required
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    if request.method == 'POST':
        article.title = request.form.get('title')
        article.content = request.form.get('content')
        
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                article.image = filename

        db.session.commit()
        return redirect(url_for('main.admin'))
    return render_template('edit_article.html', article=article)

@main.route('/admin/delete_article/<int:article_id>', methods=['POST'])
@admin_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    
    # Удаляем изображение статьи, если оно есть
    if article.image:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], article.image))
        except:
            pass  # Игнорируем ошибку, если файл не существует
    
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('main.admin'))

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contacts')
def contacts():
    return render_template('contacts.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.admin'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Пожалуйста, заполните все поля')
            return render_template('login.html')
            
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('main.admin'))
        else:
            flash('Неверное имя пользователя или пароль')
    
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.home'))

@main.route('/delete_product/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Удаляем все изображения продукта
    for image in product.images:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image.filename))
        except:
            pass  # Игнорируем ошибку, если файл не существует
    
    db.session.delete(product)
    db.session.commit()
    
    return redirect(url_for('main.admin'))

@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

def save_file(file, folder):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], folder, filename)
        try:
            file.save(filepath)
            return filename
        except Exception as e:
            current_app.logger.error(f"Error saving file: {e}")
            return None
    return None

@main.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Получаем все URL изображений продукта
    image_urls = [
        url_for('static', filename='uploads/' + image.filename)
        for image in product.images
    ]
    
    return render_template(
        'product_detail.html',
        product=product,
        image_urls=image_urls
    )