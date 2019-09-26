#!/usr/bin/python3

from flask import Flask, request, jsonify, session;
from flask_cors import CORS;
from flask_socketio import SocketIO, join_room;
import uuid;
from worker import query;

app = Flask(__name__);
app.secret_key = 'swj*2019!'; # secret key for using session
cors = CORS(app, resources = {r"/*":{"origins":"*"}});
socketio = SocketIO(app, message_queue = 'amqp://guest:guest@localhost:5672');

@app.route('/')
def index():

    return 'QASystem server works!';

@app.route('/qasystem', methods = ['POST'])
def query():
    # if calling client has not been in a message room,
    # create one for the client. one client in one room.
    if 'uid' not in session:
        session['uid'] = str(uuid.uuid4());
    task = query.delay(request.args.get('query'), session = session['uid']);
    return jsonify({'id': task.id});

@socketio.on('connect')
def socket_connect():
    # nothing need to be done when client connect with server
    pass;

@socketio.on('join_room', namespace = '/query')
def on_room():
    # client start to join the room and wait for reply.
    room = str(session['uid']);
    join_room(room);

if __name__ == "__main__":

    socketio.run(app, host = '192.168.1.102', port = 5000);
