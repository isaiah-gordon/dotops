from flask import Flask

from website.routes import website
from api.routes import api

import secrets


app = Flask(__name__)

app.config['SECRET_KEY'] = secrets.secret_key

app.register_blueprint(website)
app.register_blueprint(api)

if __name__ == '__main__':
    app.run(debug=True)