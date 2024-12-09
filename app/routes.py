import sys
import os
from flask import render_template, jsonify, request, redirect, url_for
from . import create_app
from app import db
from app.models.product import Product


# Добавляем текущую директорию в путь поиска модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app  # Импортируем create_app

app = create_app()

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/api/products')
def get_products():
    category = request.args.get('category')
    products = [
        {"id": 1, "name": "Нож", "category": "Ножи", "images": ["image1.jpg"]},
        {"id": 2, "name": "Топор", "category": "Топоры", "images": ["image2.jpg"]},
        # Добавьте другие товары
    ]
    filtered_products = [product for product in products if product['category'] == category]
    return jsonify(filtered_products)

# Удалите if __name__ == '__main__': и app.run(debug=True), так как это будет в run.py

@app.route('/add_product', methods=['GET', 'POST'])
@session_login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price', 0.0)
        in_stock = request.form.get('in_stock', '0')  # Значение по умолчанию
        quantity = request.form.get('quantity', 0)  # Новое поле для количества

        new_product = Product(
            name=name,
            description=description,
            price=price,
            in_stock=in_stock,
            quantity=quantity  # Сохраняем количество
        )
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('admin'))

    return render_template('add_product.html', product=None)