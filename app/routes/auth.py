from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from db.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('operations.operations_view'))
    return redirect(url_for('auth.login_page'))

@auth_bp.route('/reg', methods=['GET'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('operations.operations_view'))
    return render_template('register.html')

@auth_bp.route('/reg', methods=['POST'])
def register():
    try:
        data = request.get_json(silent=True)
        if not data or not data.get('login') or not data.get('password'):
            return jsonify({'error': 'Пустой логин и/или пароль'}), 400

        if User.query.filter_by(name=data['login']).first():
            return jsonify({'error': 'Пользователь уже существует!'}), 409

        user = User(name=data['login'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Регистрация успешна!'}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['GET'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('operations.operations_view'))
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data or not data.get('login') or not data.get('password'):
        return jsonify({'error': 'Пустой логин и/или пароль'}), 400

    user = User.query.filter_by(name=data['login']).first()
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({'message': 'Авторизация успешна!'}), 200

    return jsonify({'error': 'Неверный логин и/или пароль'}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login_page'))
