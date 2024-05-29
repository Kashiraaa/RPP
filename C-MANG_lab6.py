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
cur = conn.cursor()


@app.route('/load', methods=['POST'])  # Декоратор для обработки POST запроса по указанному URL
def load_currency():
    data = request.get_json()  # Получение данных из POST запроса
    currency_name = data['currency_name']
    currency_rate = data['rate']

    # Проверка наличия валюты в БД
    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
    if cur.fetchone():
        return jsonify({'error': 'Currency already exists'}), 400

    # Сохранение валюты в БД
    cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)", (currency_name, currency_rate))
    conn.commit()

    return jsonify({'message': 'Currency loaded successfully'}), 200


@app.route('/update_currency', methods=['POST'])  # Декоратор для обработки POST запроса по указанному URL
def update_currency():
    data = request.get_json()  # Получение данных из POST запроса
    currency_name = data['currency_name']
    new_rate = data['rate']

    # Проверка наличия валюты в БД
    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
    if not cur.fetchone():
        return jsonify({'error': 'Currency does not exist'}), 404

    # Обновление данных валюты в БД
    cur.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s", (new_rate, currency_name))
    conn.commit()

    return jsonify({'message': 'Currency updated successfully'}), 200


@app.route('/delete', methods=['POST'])  # Декоратор для обработки POST запроса по указанному URL
def delete_currency():
    data = request.get_json()  # Получение данных из POST запроса
    currency_name = data['currency_name']

    # Проверка наличия валюты в БД
    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
    if not cur.fetchone():
        return jsonify({'error': 'Currency does not exist'}), 404

    # Удаление валюты из БД
    cur.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name,))
    conn.commit()

    return jsonify({'message': 'Currency deleted successfully'}), 200


if __name__ == '__main__':
    app.run(port=5001)  # Запуск приложения Flask на указанном порту