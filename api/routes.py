from flask import Blueprint, render_template, redirect, url_for, request, current_app, make_response, jsonify
import jwt
from functools import wraps
import datetime
from sql import sql_master as database

import secrets

api = Blueprint('api', __name__, url_prefix='/api')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        try:
            token = request.headers.get('token')  # http://127.0.0.1:5000/route?token=nv8h4994hv4
        except:
            return 'Authentication token is required.'

        try:
            jwt.decode(token, current_app.config['SECRET_KEY'])

        except:
            return 'Invalid authentication token.'

        return f(*args, **kwargs)

    return decorated


@api.route('/')
def index():
    return 'Welcome to the Dotops API!'


# Route for handling the login page logic
@api.route('/generate_token')
def generate_token():
    auth = request.authorization

    if auth and auth.username != secrets.api_user or auth.password != secrets.api_password:
        return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required'})

    elif auth and auth.username == secrets.api_user and auth.password == secrets.api_password:
        token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3)}, current_app.config['SECRET_KEY'])

        return token

    return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required'})

@api.route('/next_product', methods=['GET', 'POST'])
@token_required
def next_product():
    json_post = jsonify({'next_product': database.read_next_product()})

    if request.method == 'POST':
        json_post = request.get_json()

        database.update_next_product(json_post['next_product'])

    return json_post

