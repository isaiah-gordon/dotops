from flask import render_template, redirect, url_for, request, session, current_app
from . import main, events, secrets
from functools import wraps
from app.sql import sql_master as database
import os
from datetime import datetime, timedelta

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

        user_email = dict(session).get('email', None)

        if user_email is None:
            return redirect(url_for('main.welcome'))

        user = database.find_user(user_email)

        if user:
            return f(*args, **kwargs)

        elif not user:
            email = dict(session).get('email', None)
            return f'Access denied: Your account \" {email} \" is not authorized!'

    return decorated


@main.route('/')
@auth_required
def index():
    return render_template('home.html')

@main.route('/welcome')
def welcome():
    return render_template('welcome.html')


@main.route('/info')
def info():
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

    user_profile = database.find_user(user_info['email'])
    if user_profile:
        session['store'] = user_profile['store']

    return redirect('/')


@main.route('/activate', methods=['GET', 'POST'])
@auth_required
def activate():

    if request.method == 'POST':

        form_dict = request.form.to_dict()
        form_dict['status'] = 'internal_game'
        form_dict['scoreboard_config'] = 'counters'

        utc_time_end = (datetime.utcnow() + timedelta(hours=int(form_dict['duration']))).time()
        form_dict['end_time'] = utc_time_end.strftime('%H:%M:%S')

        events.activate(events.socket_id_lookup[session['store']], form_dict)

        print(form_dict)

        return redirect(url_for('main.active'))

    status = events.socket_lookup(session['store'], 'status')

    if status == 'internal_game':
        return redirect(url_for('main.active'))

    if status == 'idle':
        return render_template('activate.html')

    return 'Client is offline!'


@main.route('/active', methods=['GET', 'POST'])
@auth_required
def active():

    status = events.socket_lookup(session['store'], 'status')

    if request.method == 'POST':

        events.activate(events.socket_id_lookup[session['store']], {'status': 'idle'})

        return redirect(url_for('main.activate'))

    if status == 'idle':
        return redirect(url_for('main.activate'))

    if status == 'internal_game':
        return render_template('active.html')

    return 'Client is offline!'


@main.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')
