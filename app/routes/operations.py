import requests
from flask import Blueprint, request, render_template, jsonify, current_app
from flask_login import login_required, current_user
from db.models import db, Operation
from datetime import datetime

operations_bp = Blueprint('operations', __name__)

RATE_SERVICE_URL = 'http://127.0.0.1:5001'

def fetch_exchange_rate(currency: str) -> float:
    fallback_rates = {'RUB': 1.0, 'USD': 74.24, 'EUR': 87.35}
    if currency == 'RUB':
        return 1.0
    try:
        resp = requests.get(
            f"{RATE_SERVICE_URL}/rate",
            params={'currency': currency},
            timeout=3
        )
        if resp.status_code == 200:
            return resp.json()['rate']
    except Exception:
        current_app.logger.warning(f"Rate service unavailable, using fallback for {currency}")
    return fallback_rates.get(currency, 1.0)

@operations_bp.route('/operations')
@login_required
def operations_view():
    currency = request.args.get('currency', 'RUB').upper()
    if currency not in ('RUB', 'USD', 'EUR'):
        currency = 'RUB'

    ops = Operation.query.filter_by(user_id=current_user.id).order_by(Operation.date.desc()).all()
    rate = fetch_exchange_rate(currency)

    for op in ops:
        op.converted_sum = op.sum / rate if currency != 'RUB' else op.sum

    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'currency': currency,
            'rate': rate,
            'operations': [
                {'date': op.date.isoformat(), 'sum': op.converted_sum, 'type': op.type_operation}
                for op in ops
            ]
        })

    return render_template('operations.html', operations=ops, currency=currency)

@operations_bp.route('/add_operation', methods=['GET', 'POST'])
@login_required
def add_operation_page():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        if not data or not all(k in data for k in ('type_operation', 'sum', 'date')):
            return jsonify({'error': 'не все поля заполнены!'}), 400
        
        try:
            op_date = datetime.fromisoformat(data['date'])
        except ValueError:
            return jsonify({'error': 'Неправильный формат даты'}), 400

        try:
            op = Operation(
                user_id=current_user.id,
                date=op_date,
                sum=float(data['sum']),
                chat_id=data.get('chat_id'),
                type_operation=data['type_operation']
            )
            db.session.add(op)
            db.session.commit()
            return jsonify({'message': 'Операция добавлена'}), 200
        except Exception:
            db.session.rollback()
            return jsonify({'error': 'Internal server error'}), 500

    return render_template('add_operation.html')
