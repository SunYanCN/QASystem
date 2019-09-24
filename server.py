#!/usr/bin/python3

from threading import Thread, Lock;
from time import gmtime, strftime;
from flask import Flask, request, jsonify, session;
from flask_socketio import SocketIO, join_room;
import uuid;
import worker;

app = Flask(__name__);
app.secret_key = 'swj*2019!'; # secret key for using session
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
    task = worker.query.delay(request.args.get('query'), session = session['uid']);
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

@app.after_request
def af_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*';
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST';
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type';
    return resp;

if __name__ == "__main__":

    socketio.run(app, host = '192.168.1.102', port = 5000);
