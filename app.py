"""
Application de gestion des données médicales - Grand Magal de Touba
Région Médicale de Diourbel
"""

import os
from flask import Flask, send_from_directory, make_response
from extensions import db, login_manager
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'warning'

    # Register blueprints
    from routes.public import public_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.user import user_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')

    # Service Worker — servi depuis la racine pour que le scope couvre toute l'app
    @app.route('/sw.js')
    def service_worker():
        resp = make_response(send_from_directory('static', 'sw.js'))
        resp.headers['Content-Type'] = 'application/javascript'
        resp.headers['Service-Worker-Allowed'] = '/'
        resp.headers['Cache-Control'] = 'no-cache'
        return resp

    # Create tables
    with app.app_context():
        db.create_all()
        from models import seed_data
        seed_data()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)