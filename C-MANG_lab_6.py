from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Установка соединения с БД
conn = psycopg2.connect(
    database='microservice_bot',
    user='Kashira',
    password='54691452',
    host='127.0.0.1',
    port=5432
)
cur = conn.cursor()

@app.route('/load', methods=['POST'])
def load_currency():
    data = request.get_json()
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

@app.route('/update_currency', methods=['POST'])
def update_currency():
    data = request.get_json()
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

@app.route('/delete', methods=['POST'])
def delete_currency():
    data = request.get_json()
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
    app.run(port=5001)
