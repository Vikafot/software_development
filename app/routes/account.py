from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from db.models import db, User

account_bp = Blueprint('account', __name__)

@account_bp.route('/delete_account')
@login_required
def delete_account_page():
    return render_template('delete_account.html')

@account_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    try:
        user = db.session.get(User, current_user.id)
        if user:
            db.session.delete(user)
            db.session.commit()
        
        logout_user()
        flash('Аккаунт успешно удалён', 'success')
        return redirect(url_for('auth.register_page'))
    except Exception:
        db.session.rollback()
        flash('Ошибка при удалении аккаунта', 'error')
        return redirect(url_for('account.delete_account_page'))
