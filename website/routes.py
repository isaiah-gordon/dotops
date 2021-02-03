from flask import Blueprint, render_template, redirect, url_for, request, session, current_app
import jwt
from functools import wraps
import datetime
from sql import sql_master as database
import os
import secrets

from authlib.integrations.flask_client import OAuth

# OAuth config
oauth = OAuth(current_app)
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)


website = Blueprint('website', __name__)



def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        authorized_users = ['isaiah.jk.gordon@gmail.com']

        user = dict(session).get('email', None)
        print(dict(session))
        # You would add a check here and use the user id or something to fetch
        # the other data for that user/check if they exist
        if user in authorized_users:
            return f(*args, **kwargs)

        elif user is None:
            return 'You have not logged in!'

        elif user not in authorized_users:
            return 'You are not allowed here!'


    return decorated


@website.route('/')
@auth_required
def hello_world():
    first_name = dict(session).get('first_name', None)
    return f'Hello, {first_name}!'


@website.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('website.authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@website.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)
    user_info = resp.json()
    # do something with the token and profile
    session['email'] = user_info['email']
    session['first_name'] = user_info['given_name']
    return redirect('/')


@website.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


# Data from Google

# {'id': '117584971817811111524',
# 'email': 'zayahgordon@gmail.com',
# 'verified_email': True,
# 'name': 'Zayah Gordon',
# 'given_name': 'Zayah',
# 'family_name': 'Gordon',
# 'picture': 'https://lh6.googleusercontent.com/-xi6_vTTIOUc/AAAAAAAAAAI/AAAAAAAAAAA/AMZuucmbI3jsfvWzCGbb4OuWpxJdD71riw/s96-c/photo.jpg', 'locale': 'en'}
# {'_google_authlib_nonce_': 'OJyBLC4nMMRmrZOjJgws',
# 'email': 'zayahgordon@gmail.com'}

# ----- EXCLUDE -----

# # Route for handling the login page logic
# @website.route('/', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != secrets.website_user or request.form['password'] != secrets.website_password:
#             error = 'Invalid Credentials. Please try again.'
#         else:
#             token = jwt.encode({'user': request.form['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)}, current_app.config['SECRET_KEY'])
#
#             session['token'] = token
#             return redirect(url_for('website.activate'))
#
#     return render_template('login.html', error=error)
#
#
# @website.route('/activate', methods=['GET', 'POST'])
# @auth_required
# def activate():
#
#     if database.game_status() == 1:
#         return redirect(url_for('website.active'))
#
#     if request.method == 'POST':
#
#         form_dict = request.form.to_dict()
#         form_dict['status'] = 1
#
#         database.update(form_dict)
#
#         return render_template('spinner.html')
#
#     return render_template('activate.html')
#
#
# @website.route('/active', methods=['GET', 'POST'])
# @auth_required
# def active():
#
#     if database.game_status() == 0:
#         return redirect(url_for('website.activate'))
#
#     if request.method == 'POST':
#
#         database.update({'status': 0})
#
#         return render_template('spinner.html')
#
#     return render_template('active.html')