from flask import Flask, jsonify, request

app = Flask(__name__)

# Создаем словарь с курсами валют
rates = {"EUR": 100.1, "USD": 92.1}

# Обработчик маршрута для получения курса валюты
@app.route('/rate', methods=['GET'])
def get_rate():
    # Получаем запрашиваемую валюту из параметров запроса
    currency = request.args.get('currency')
    # Проверяем, есть ли такая валюта в словаре
    if currency not in rates:
        # Если валюта не найдена, возвращаем сообщение об ошибке и статус 400
        return jsonify({"message": "UNKNOWN CURRENCY"}), 400
    try:
        # Возвращаем курс запрашиваемой валюты
        return jsonify({"rate": rates[currency]})
    except Exception as e:
        # Если произошла неожиданная ошибка, возвращаем сообщение и статус 500
        return jsonify({"message": "UNEXPECTED ERROR"}), 500

if __name__ == '__main__':
    # Запускаем приложение на localhost по порту 8000 в режиме отладки
    app.run(host='0.0.0.0', port=8000, debug=True)