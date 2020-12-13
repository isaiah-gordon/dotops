from flask import Blueprint, render_template, redirect, url_for, request, session, current_app
import jwt
from functools import wraps
import datetime
from sql import sql_master as database
import time

import secrets

website = Blueprint('website', __name__)



def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        try:
            token = session['token']
        except:
            return redirect(url_for('website.login'))

        try:
            jwt.decode(token, current_app.config['SECRET_KEY'])
        except:
            return redirect(url_for('website.login'))

        return f(*args, **kwargs)

    return decorated


# Route for handling the login page logic
@website.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != secrets.website_user or request.form['password'] != secrets.website_password:
            error = 'Invalid Credentials. Please try again.'
        else:
            token = jwt.encode({'user': request.form['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)}, current_app.config['SECRET_KEY'])

            session['token'] = token
            return redirect(url_for('website.activate'))

    return render_template('login.html', error=error)


@website.route('/activate', methods=['GET', 'POST'])
@auth_required
def activate():

    if database.game_status() == 1:
        return redirect(url_for('website.active'))

    if request.method == 'POST':

        form_dict = request.form.to_dict()
        print(form_dict)
        form_dict['status'] = 1

        database.update(form_dict)

        return render_template('spinner.html')

    return render_template('activate.html')


@website.route('/active', methods=['GET', 'POST'])
@auth_required
def active():

    if database.game_status() == 0:
        return redirect(url_for('website.activate'))

    if request.method == 'POST':

        database.update({'status': 0})

        return render_template('spinner.html')

    return render_template('active.html')