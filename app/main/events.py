from flask import session
from flask_socketio import emit, send
from .. import socketio

test_dict = {
    'duration': 1,
    'manager_id': '331',
    'name1': 'Jack',
    'name2': 'Jill',
    'name3': 'Hill',
    'product': 'donut',
    'status': '1'
}


@socketio.on('connect')
def test_connect():
    print('Hi!')


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
