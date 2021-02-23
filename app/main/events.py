from flask import request, current_app
from flask_socketio import emit, disconnect
import jwt
import json
from functools import wraps
from .. import socketio as sio
from app.sql import sql_master as database


active_sockets = {}
socket_id_lookup = {}


def socket_lookup(store_number, key):
    try:
        socket_id = socket_id_lookup[store_number]
        value = active_sockets[socket_id][key]
    except:
        return 'offline'

    return value


def socket_set(store_number, key, new_value):
    socket_id = socket_id_lookup[store_number]
    active_sockets[socket_id][key] = new_value


@sio.on('connect')
def connect():
    print(request.sid, 'connected')
    token = request.args.get('token')

    try:
        jwt.decode(token, current_app.config['SECRET_KEY'])

    except:
        disconnect()
        return

    sio.sleep(seconds=0.04)
    emit('handshake')


@sio.on('disconnect')
def disconnect():
    if socket_id_lookup[active_sockets[request.sid]['store_number']] == request.sid:
        socket_id_lookup.pop(active_sockets[request.sid]['store_number'], None)

    print(request.sid, 'disconnected')
    if request.sid in active_sockets:
        active_sockets.pop(request.sid, None)

    print('ACTIVE SOCKETS:', active_sockets)
    print('SOCKET LOOKUP:', socket_id_lookup)


@sio.on('handshake')
def handshake(data):

    active_sockets[request.sid] = data
    socket_id_lookup[data['store_number']] = request.sid
    print('ACTIVE SOCKETS:', active_sockets)
    print('SOCKET LOOKUP:', socket_id_lookup)


@sio.on('score_report')
def score_report(report_data):
    print('REPORT DATA:', report_data)

    game_scores_str = database.query("""
        SELECT scores
        FROM scheduled_games
        WHERE id = {0}
    """.format(report_data['game_id']))[0]['scores']

    print('INITIAL GAME SCORES:', game_scores_str)

    game_scores_dict = json.loads(game_scores_str)

    # game_scores_dict.update(report_data['client_score'])

    for key in game_scores_dict:
        if key in report_data['client_score']:
            game_scores_dict[key] = game_scores_dict[key] + report_data['client_score'][key]
        else:
            pass

    game_scores_str = json.dumps(game_scores_dict)

    print('DUMPED GAME SCORES:', game_scores_str)

    database.command("""
        UPDATE scheduled_games
        SET scores = '{0}'
        WHERE id = {1}
    """.format(game_scores_str, report_data['game_id']))

    print('UPDATED GAME SCORES:', game_scores_str)


@sio.on('pull_scores')
def pull_scores(game_id):
    print('HIT!')

    game_scores_str = database.query("""
        SELECT scores
        FROM scheduled_games
        WHERE id = {0}
    """.format(game_id))[0]['scores']

    game_scores_dict = json.loads(game_scores_str)

    sio.emit('receive_game_scores', game_scores_dict)


def activate(socket_id, data):
    sio.emit('activate', data, room=socket_id)

