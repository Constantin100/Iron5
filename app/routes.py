import sys
import os
from flask import render_template, jsonify, request
from . import create_app


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