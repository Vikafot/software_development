from flask import Flask
from flask_login import LoginManager
from db import Config, db
from db.models import User
from routes import auth_bp, operations_bp, account_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    login_manager = LoginManager()
    app.login_manager = login_manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_page'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(operations_bp)
    app.register_blueprint(account_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
