from flask import request, current_app
from flask_socketio import emit, disconnect
import jwt
from functools import wraps
from .. import socketio as sio


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


def activate(data):
    sio.emit('command', data)

