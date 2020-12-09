from flask import Blueprint, render_template, redirect, url_for, request, session, current_app
import jwt
from functools import wraps
import datetime
from sql import sql_master as database

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
            token = jwt.encode({'user': request.form['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=3)}, current_app.config['SECRET_KEY'])

            session['token'] = token
            return redirect(url_for('website.control'))

    return render_template('login.html', error=error)


@website.route('/control', methods=['GET', 'POST'])
@auth_required
def control():

    if request.method == 'POST':
        product = request.form['products']

        database.update_next_product(product)

    return render_template('control.html', product=database.read_next_product())
