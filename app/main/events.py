from flask import request, current_app
from flask_socketio import emit, disconnect
import jwt
from functools import wraps
from .. import socketio as sio


active_sessions = {}
session_id_lookup = {}


def session_lookup(store_number, key):
    try:
        session_id = session_id_lookup[store_number]
        value = active_sessions[session_id][key]
    except:
        return 'offline'

    return value


def session_set(store_number, key, new_value):
    session_id = session_id_lookup[store_number]
    active_sessions[session_id][key] = new_value

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
    print('THIS:   ', session_id_lookup[active_sessions[request.sid]['store_number']])

    if session_id_lookup[active_sessions[request.sid]['store_number']] == request.sid:
        session_id_lookup.pop(active_sessions[request.sid]['store_number'], None)

    print(request.sid, 'disconnected')
    if request.sid in active_sessions:
        active_sessions.pop(request.sid, None)

    print('ACTIVE SESSIONS:', active_sessions)
    print('SESSION LOOKUP:', session_id_lookup)


@sio.on('handshake')
def handshake(data):

    active_sessions[request.sid] = data
    session_id_lookup[data['store_number']] = request.sid
    print('ACTIVE SESSIONS:', active_sessions)
    print('SESSION LOOKUP:', session_id_lookup)


def activate(data):
    sio.emit('command', data)

