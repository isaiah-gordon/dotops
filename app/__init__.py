from flask import Flask
from flask_socketio import SocketIO
import os

socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("secret_key")

    from .main import main, interface
    app.register_blueprint(main)
    app.register_blueprint(interface, url_prefix='/api')

    socketio.init_app(app)

    return app
