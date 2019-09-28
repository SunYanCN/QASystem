#!/usr/bin/python3

from flask import Flask, request, render_template, jsonify, session;
from flask_socketio import SocketIO, join_room;
from flask_cors import CORS;
from gevent import monkey;
from uuid import uuid4;
from query import query;

monkey.patch_all();
app = Flask(__name__);
app.secret_key = 'swj*2019!'; # secret key for using sessiona
cors = CORS(app, resources = {r"/*":{"origins":"*"}});
socketio = SocketIO(app, message_queue = 'amqp://guest:guest@localhost:5672');

@app.route('/')
def index():
    # test page
    if 'uid' not in session:
        session['uid'] = str(uuid4());
    return render_template('index.html');

@app.route('/qasystem', methods = ['POST'])
def dispatcher():
    # if calling client has not been in a message room,
    # create one for the client. one client in one room.
    if 'uid' not in session:
        session['uid'] = str(uuid4());
    inputs = request.json;
    task = query.delay(inputs['query'], session['uid']);
    return jsonify({'id': session['uid']});

@socketio.on('connect', namespace = '/socket')
def socket_connect():
    print('connected to client!');

@socketio.on('listening', namespace = '/socket')
def on_listening():
    # client start to join the room and wait for reply.
    room = str(session['uid']);
    print("joining room " + room);
    join_room(room);

if __name__ == "__main__":

    socketio.run(app, host = '192.168.1.102', port = 5000);
