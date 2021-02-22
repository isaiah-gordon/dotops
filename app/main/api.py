from flask import request, current_app, make_response, jsonify
from . import interface, events, secrets
import jwt
import json
from functools import wraps
from datetime import datetime, timedelta
from app.sql import sql_master as database


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


@interface.route('/')
def index():
    return 'Welcome to the Dotops API!'


# Route for handling the login page logic
@interface.route('/generate_token')
def generate_token():
    auth = request.authorization

    if auth and (auth.username != secrets.api_user or auth.password != secrets.api_password):
        return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required'})

    elif auth and (auth.username == secrets.api_user and auth.password == secrets.api_password):
        token = jwt.encode({'user': auth.username, 'exp': datetime.utcnow() + timedelta(days=1095)}, current_app.config['SECRET_KEY'])

        return token

    return make_response('Authorization is required!', 401, {'WWW-Authenticate': 'Basic realm="Login Required'})


@interface.route('/check_schedule', methods=['GET'])
@token_required
def check_schedule():

    print('Checking the schedule...')

    utc_time = datetime.utcnow().time()
    utc_dt = datetime.utcnow()
    utc_day = utc_dt.strftime('%a')

    games_to_activate = database.query("""
            SELECT *
            FROM scheduled_games
            WHERE status = 0
            AND day_of_week = '{0}'
            AND '{1}' >= start_time
            AND '{1}' <= end_time
        """.format(utc_day, utc_time))

    print(games_to_activate)

    for game in games_to_activate:

        database.command("""
        UPDATE scheduled_games
        SET status = '1'
        WHERE id = '{0}'
        """.format(game['id']))


        stores_list = game['stores'].strip('][').split(', ')
        activation_specs = {'product': game['product'],
                            'end_time': str(game['end_time']),
                            'status': 'external_game',
                            'external_id': game['id'],
                            'stores_list': stores_list}

        if len(stores_list) == 2:
            activation_specs.update({'name1': database.store_profile_lookup(stores_list[0], 'store_short_name'),
                                     'name2': database.store_profile_lookup(stores_list[1], 'store_short_name'),
                                     'name3': '...',
                                     'scoreboard_config': 'dual_counters'})


        if len(stores_list) == 3:
            activation_specs.update({'name1': database.store_profile_lookup(stores_list[0], 'store_short_name'),
                                     'name2': database.store_profile_lookup(stores_list[1], 'store_short_name'),
                                     'name3': database.store_profile_lookup(stores_list[2], 'store_short_name'),
                                     'scoreboard_config': 'counters'})

        for store in stores_list:
            try:
                store_id = events.socket_id_lookup[store]
                print(store_id)
                events.activate(store_id, activation_specs)
            except KeyError:
                print(store, 'is offline!')

        print(activation_specs)




    return make_response('...', 200)
