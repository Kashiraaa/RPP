from flask import Flask, jsonify, request

app = Flask(__name__)

rates = {"EUR": 100.1, "USD": 92.1}

@app.route('/rate', methods=['GET'])
def get_rate():
    currency = request.args.get('currency')
    if currency not in rates:
        return jsonify({"message": "UNKNOWN CURRENCY"}), 400
    try:
        return jsonify({"rate": rates[currency]})
    except Exception as e:
        return jsonify({"message": "UNEXPECTED ERROR"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)