from flask import request, current_app, make_response, jsonify
from . import interface, secrets
import jwt
import json
from functools import wraps
from datetime import datetime, timedelta
from app.sql import sql_master as database


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        try:
            token = request.headers.get('token')
        except:
            return 'Authentication token is required.'

        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'])
            print(decoded_token)

        except:
            return 'Invalid authentication token.'

        return f(decoded_token, *args, **kwargs)

    return decorated


@interface.route('/')
def index():
    return 'Welcome to the Dotops API!'


# Route for handling the login page logic
@interface.route('/generate_token/<store_number>')
def generate_token(store_number):
    auth = request.authorization

    if auth and (auth.username != secrets.api_user or auth.password != secrets.api_password):
        return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required'})

    elif auth and (auth.username == secrets.api_user and auth.password == secrets.api_password):
        token = jwt.encode({'store': store_number, 'issuer': auth.username, 'exp': datetime.utcnow() + timedelta(days=1095)}, current_app.config['SECRET_KEY'])

        return token

    return make_response('Authorization is required!', 401, {'WWW-Authenticate': 'Basic realm="Login Required'})


@interface.route('/find_next_game', methods=['GET'])
@token_required
def find_next_game(decoded_token):
    print('Checking the schedule for next game at {0}'.format(decoded_token['store']))

    utc_time = datetime.utcnow().time()
    utc_dt = datetime.utcnow()
    utc_day = utc_dt.strftime('%a')

    next_game = database.query("""
            SELECT id, start_time, end_time, product, stores
            FROM scheduled_games

            WHERE start_time = (
            SELECT MIN(start_time)
            FROM scheduled_games
            WHERE status = 0
            AND day_of_week = '{0}'
            AND '{1}' <= start_time
            AND stores LIKE '%{2}%'
            )
            
            
        """.format(utc_day, utc_time, decoded_token['store']))

    next_game = next_game[0]

    next_game['start_time'] = str(next_game['start_time'])
    next_game['end_time'] = str(next_game['end_time'])
    next_game['stores'] = next_game['stores'].strip('][').split(', ')

    json_next_game = json.dumps(next_game)

    return make_response(json_next_game, 200)


@interface.route('/lookup_stores/<store_list>', methods=['GET'])
@token_required
def lookup_stores(self, store_list):

    sql_store_list = store_list.replace('[', '(').replace(']', ')')
    store_list = store_list.strip('][').split(', ')

    store_details = database.query("""
                SELECT store_number, store_name, store_short_name, store_image
                FROM store_profiles
                WHERE store_number IN {0}
            """.format(sql_store_list))

    store_dict = {}
    for store in store_details:
        store_number = store.pop('store_number')
        store_dict[store_number] = store

    json_store_dict = json.dumps(store_dict)

    return make_response(json_store_dict, 200)


@interface.route('/add_score/<game_id>', methods=['POST'])
@token_required
def add_score(decoded_token, game_id):
    json_post = request.get_json()

    print(json_post)

    database.command("""
                UPDATE scheduled_games
                SET total_sold{0} = total_sold{0} + {1},
                transactions{0} = transactions{0} + {2}
                WHERE id = {3}
            """.format(json_post['score_index'], json_post['total_sold'], json_post['transactions'], game_id))

    return make_response('Success 200!', 200)


@interface.route('/get_score/<game_id>', methods=['GET'])
@token_required
def get_score(self, game_id):

    all_scores = database.query("""
                SELECT total_sold0, transactions0, total_sold1, transactions1, total_sold2, transactions2
                FROM scheduled_games
                WHERE id = {0}
            """.format(game_id))

    print(all_scores)

    json_all_scores = json.dumps(all_scores[0])

    return make_response(json_all_scores, 200)


# DEPRECATED CRON ENDPOINT
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
