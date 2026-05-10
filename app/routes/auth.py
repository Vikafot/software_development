from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, current_user
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
    if request.is_json:
        try:
            data = request.get_json()
            if not data or 'login' not in data or 'password' not in data:
                return jsonify({'error': 'Missing login or password'}), 400

            if User.query.filter_by(name=data['login']).first():
                return jsonify({'error': 'User already exists'}), 409

            user = User(name=data['login'])
            user.set_password(data['password'])
            db.session.add(user)
            db.session.commit()
            return '', 200
        except Exception:
            db.session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
    
    login = request.form.get('login')
    password = request.form.get('password')
    
    if not login or not password:
        flash('Логин и пароль обязательны', 'error')
        return redirect(url_for('auth.register_page'))
    
    if User.query.filter_by(name=login).first():
        flash('Пользователь уже существует', 'error')
        return redirect(url_for('auth.register_page'))
    
    user = User(name=login)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    flash('Регистрация успешна', 'success')
    return redirect(url_for('auth.login_page'))

@auth_bp.route('/login', methods=['GET'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('operations.operations_view'))
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    login = request.form.get('login')
    password = request.form.get('password')
    user = User.query.filter_by(name=login).first()
    
    if user and user.check_password(password):
        login_user(user)
        return redirect(url_for('operations.operations_view'))
    
    flash('Неверный логин или пароль', 'error')
    return redirect(url_for('auth.login_page'))

@auth_bp.route('/logout')
@login_required
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('auth.login_page'))
