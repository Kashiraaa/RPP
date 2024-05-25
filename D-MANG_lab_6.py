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

@app.route('/convert', methods=['GET'])
def convert_currency():
    currency_name = request.args.get('currency_name')
    amount = float(request.args.get('amount'))

    # Проверка наличия валюты в БД
    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
    if not cur.fetchone():
        return jsonify({'error': 'Currency does not exist'}), 404

    # Получение курса из БД для заданной валюты
    cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name,))
    rate = cur.fetchone()

    # Конвертация
    converted_amount = amount * rate

    return jsonify({'converted_amount': converted_amount}), 200

@app.route('/currencies', methods=['GET'])
def get_currencies():
    cur.execute("SELECT * FROM currencies WHERE currency_name = $s")
    currencies = cur.fetchall()
    currencies_list = [{"currency_name": currency, "rate": currency} for currency in currencies]

    return jsonify({'currencies': currencies_list}), 200

if __name__ == '__main__':
    app.run(port=5002)
