from flask import render_template, redirect, url_for, request, session, current_app
from . import main, events
from functools import wraps
from app.sql import sql_master as database
from .. import socketio as sio
import os

from .. import socketio

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


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        authorized_users = ['isaiah.jk.gordon@gmail.com']

        user = dict(session).get('email', None)
        # You would add a check here and use the user id or something to fetch
        # the other data for that user/check if they exist
        if user in authorized_users:
            return f(*args, **kwargs)

        elif user is None:
            return redirect(url_for('main.welcome'))

        elif user not in authorized_users:
            email = dict(session).get('email', None)
            return f'Access denied: Your account \" {email} \" is not authorized!'

    return decorated


@main.route('/')
@auth_required
def index():
    return render_template('home.html')

@main.route('/welcome')
def welcome():
    return render_template('index.html')


@main.route('/info')
def info():
    socketio.send('Hello friend!')
    return render_template('info.html')


@main.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('main.authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@main.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)
    user_info = resp.json()
    # do something with the token and profile
    session['email'] = user_info['email']
    session['first_name'] = user_info['given_name']
    return redirect('/')


@main.route('/activate', methods=['GET', 'POST'])
@auth_required
def activate():

    if request.method == 'POST':

        form_dict = request.form.to_dict()
        form_dict['status'] = 1

        events.activate(form_dict)

        return redirect(url_for('main.active'))

    status = events.session_lookup('40469', 'status')

    if status == 1:
        return redirect(url_for('main.active'))

    if status == 0:
        return render_template('activate.html')

    return 'Client is offline!'


@main.route('/active', methods=['GET', 'POST'])
@auth_required
def active():

    status = events.session_lookup('40469', 'status')

    if request.method == 'POST':

        events.activate({'status': 0})

        return redirect(url_for('main.activate'))

    if status == 0:
        return redirect(url_for('main.activate'))

    if status == 1:
        return render_template('active.html')

    return 'Client is offline!'


@main.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')
