from flask import Flask, request, jsonify  # Импорт необходимых модулей
import psycopg2  # Импорт модуля для работы с PostgreSQL

app = Flask(__name__)  # Создание объекта приложения Flask

# Установка соединения с БД
conn = psycopg2.connect(
    database='microservice_bot',
    user='Kashira',
    password='54691452',
    host='127.0.0.1',
    port=5432
)
cur = conn.cursor()  # Создание курсора для работы с БД

@app.route('/convert', methods=['GET'])  # Обработчик маршрута для конвертации валюты
def convert_currency():
    currency_name = request.args.get('currency_name')  # Получение названия валюты из запроса
    amount = float(request.args.get('amount'))  # Получение суммы для конвертации из запроса

    # Проверка наличия валюты в БД
    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
    if not cur.fetchone():  # Если валюта не найдена
        return jsonify({'error': 'Currency does not exist'}), 404  # Возврат ошибки

    # Получение курса из БД для заданной валюты
    cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name,))
    rate = cur.fetchone()  # Получение курса валюты из БД

    # Конвертация
    converted_amount = amount * rate  # Вычисление сконвертированной суммы

    return jsonify({'converted_amount': converted_amount}), 200  # Возврат результата конвертации

@app.route('/currencies', methods=['GET'])  # Обработчик маршрута для получения списка валют
def get_currencies():
    cur.execute("SELECT * FROM currencies WHERE currency_name = $s")
    currencies = cur.fetchall()  # Получение всех записей о валютах из БД
    currencies_list = [{"currency_name": currency, "rate": currency} for currency in currencies]  # Формирование списка валют

    return jsonify({'currencies': currencies_list}), 200  # Возврат списка валют

if __name__ == '__main__':
    app.run(port=5002)  # Запуск приложения Flask