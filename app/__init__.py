from flask import Flask
from config import Config
import logging

from .routes.permissions import permissions_bp
from .routes.assistant import assistant_bp

from .services.permissions import PermissionsService

user_data = {
    1: {'username': 'Julian Casablancas', 'permissions': {'read': True, 'write': False}},
    2: {'username': 'Thomas Bangalter', 'permissions': {'read': True, 'write': True}},
}

def create_app(config_class=Config):
    app = Flask(__name__)
    app.secret_key = 'super_secret_key'
    app.config.from_object(config_class)
    app.logger.setLevel(logging.INFO)
    app.register_blueprint(permissions_bp)
    app.register_blueprint(assistant_bp)
    
    app.permissions_service = PermissionsService(user_data)

    return app