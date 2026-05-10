from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from db.models import db, Operation
from datetime import datetime

operations_bp = Blueprint('operations', __name__)

@operations_bp.route('/operations')
@login_required
def operations_view():
    currency = request.args.get('currency', 'RUB').upper()
    if currency not in ('RUB', 'USD', 'EUR'):
        currency = 'RUB'

    ops = Operation.query.filter_by(user_id=current_user.id).order_by(Operation.date.desc()).all()

    RATES = {'RUB': 1.0, 'USD': 92.50, 'EUR': 100.10}
    rate = RATES.get(currency, 1.0)

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
        if request.is_json:
            data = request.get_json(silent=True)
            if not data or not all(k in data for k in ('type_operation', 'sum', 'date')):
                return jsonify({'error': 'Missing fields'}), 400
            try:
                op_date = datetime.fromisoformat(data['date'])
            except ValueError:
                return jsonify({'error': 'Invalid date'}), 400

            op = Operation(
                user_id=current_user.id,
                date=op_date,
                sum=float(data['sum']),
                chat_id=data.get('chat_id'),
                type_operation=data['type_operation']
            )
            db.session.add(op)
            db.session.commit()
            return '', 200
        else:
            op_type = request.form.get('type_operation')
            op_sum = request.form.get('sum')
            op_date_str = request.form.get('date')
            
            if not all([op_type, op_sum, op_date_str]):
                flash('Заполните все поля', 'error')
                return redirect(url_for('operations.add_operation_page'))
            
            try:
                op_date = datetime.fromisoformat(op_date_str)
            except ValueError:
                flash('Неверный формат даты', 'error')
                return redirect(url_for('operations.add_operation_page'))

            op = Operation(
                user_id=current_user.id,
                date=op_date,
                sum=float(op_sum),
                chat_id=request.form.get('chat_id'),
                type_operation=op_type
            )
            db.session.add(op)
            db.session.commit()
            flash('Операция добавлена', 'success')
            return redirect(url_for('operations.operations_view'))

    return render_template('add_operation.html')
