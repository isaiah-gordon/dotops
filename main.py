from app import create_app, Flask

app = create_app()

if __name__ == '__main__':
    # socketio.run(app)
    Flask.run(app)
