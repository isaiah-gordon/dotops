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
@app.route('/api/token', methods=['GET', 'POST'])
@auth_required
def token():
    error = None
    if request.method == 'POST':
        if request.form['username'] != '40469' or request.form['password'] != 'password':
            error = 'Invalid Credentials. Please try again.'
        else:
            token = jwt.encode({'user': request.form['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=50)}, app.config['SECRET_KEY'])

            session['token'] = token
            return redirect(url_for('control'))

    return render_template('login.html', error=error)