from flask import Flask
import os
from app.main import api, website


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("secret_key")

    from .main import main, interface
    app.register_blueprint(main)
    app.register_blueprint(interface, url_prefix='/api')

    return app
