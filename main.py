from flask import Flask, render_template, redirect, url_for, request, session
import jwt
from functools import wraps
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'supersecretkey'

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        try:
            token = session['token']
        except:
            return ('No authentication!')

        try:
            jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return ('Invalid authentication!')

        return f(*args, **kwargs)

    return decorated

# Route for handling the login page logic
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            token = jwt.encode({'user': request.form['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1)}, app.config['SECRET_KEY'])

            session['token'] = token
            return redirect(url_for('control'))

    return render_template('login.html', error=error)

@app.route('/control')
@auth_required
def control():
    return render_template('control.html')

if __name__ == '__main__':
    app.run(debug=True)
