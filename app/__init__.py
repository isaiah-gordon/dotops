from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'G4zbymF@4$5E9Kyk8uZZS_#_hK=LAR'

    from .main import main, train
    app.register_blueprint(main)
    app.register_blueprint(train, url_prefix='/api')

    socketio.init_app(app)
    return app