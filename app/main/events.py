from flask import session, request, current_app
from flask_socketio import emit, send, disconnect
import jwt
from functools import wraps
from .. import socketio as sio


active_sessions = {}
session_id_lookup = {}


def session_lookup(store_number, key):
    try:
        session_id = session_id_lookup[store_number]
        value = active_sessions[session_id][key]
    except Exception as e:
        print(e)
        return 'offline'

    return value


def session_set(store_number, key, new_value):
    session_id = session_id_lookup[store_number]
    active_sessions[session_id][key] = new_value


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        try:
            token = request.headers.get('token')

        except:
            return 'Authentication token is required.'

        try:
            jwt.decode(token, current_app.config['SECRET_KEY'])

        except:
            return 'Invalid authentication token.'

        return f(*args, **kwargs)

    return decorated


@sio.on('connect')
def connect():
    print(request.sid, 'connected')
    token = request.args.get('token')

    try:
        jwt.decode(token, current_app.config['SECRET_KEY'])

    except Exception as e:
        print(e)
        print('Invalid authentication token.')
        disconnect()
        return

    sio.sleep(seconds=0.02)
    emit('handshake')


@sio.on('disconnect')
def disconnect():
    print(request.sid, 'disconnected')
    session_id_lookup.pop(active_sessions[request.sid]['store_number'])
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

