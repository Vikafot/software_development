from flask import Flask, request, jsonify

app = Flask(__name__)

STATIC_RATES = {
    'USD': 74.24,
    'EUR': 87.35,
}

@app.route('/rate', methods=['GET'])
def get_rate():
    try:
        currency = request.args.get('currency', '').upper()
        
        if currency not in STATIC_RATES:
            return jsonify({'message': 'UNKNOWN CURRENCY'}), 400
        
        return jsonify({'rate': STATIC_RATES[currency]}), 200
        
    except Exception:
        return jsonify({'message': 'UNEXPECTED ERROR'}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
