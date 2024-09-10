from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

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
    products = {
        "Ножи": ["Нож 1", "Нож 2"],
        "Топоры": [],
        "Сувениры": ["Сувенир 1", "Сувенир 2"],
        "Ковка в интерьер": ["Ковка 1", "Ковка 2"],
    }
    if category in products:
        if not products[category]:  # Проверка на наличие товаров
            return render_template('products.html', message="Товары на данный момент отсутствуют")
        return render_template('products.html', products=products[category])
    return render_template('products.html', error="Категория не найдена")

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    print(f"Запрашиваемая категория: {category}")  # Отладочное сообщение
    products = {
        "Ножи": ["Нож 1", "Нож 2"],
        "Топоры": [],
        "Сувениры": ["Сувенир 1", "Сувенир 2"],
        "Ковка в интерьер": ["Ковка 1", "Ковка 2"],
    }
    if category in products:
        if not products[category]:  # Проверка на наличие товаров
            return jsonify({"message": "Товары на данный момент отсутствуют"}), 200
        print(f"Найденные продукты: {products[category]}")  # Отладочное сообщение
        return jsonify({"products": products[category]})
    return jsonify({"error": "Категория не найдена"}), 404

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)