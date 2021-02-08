from flask import session, request, current_app
from flask_socketio import emit, send, disconnect
import jwt
from functools import wraps
from .. import socketio as sio

test_dict = {
    'duration': 1,
    'manager_id': '331',
    'name1': 'Jack',
    'name2': 'Jill',
    'name3': 'Hill',
    'product': 'donut',
    'status': '1'
}

active_sessions = {}

status = 0


def check_status():
    global status

    sio.send('status_check')

    @sio.on('status')
    def handle_message(data):
        global status
        print('received message: ' + str(data))

        status = data

    sio.sleep(seconds=0.02)

    return status


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


@sio.on('disconnect')
def disconnect():
    print(request.sid, 'disconnected')
    active_sessions.pop(request.sid, None)
    print('ACTIVE SESSIONS:', active_sessions)



@sio.on('handshake')
def handshake(data):

    active_sessions[request.sid] = data
    print('ACTIVE SESSIONS:', active_sessions)
    emit('command', 'like tacos?')
