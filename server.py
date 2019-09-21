#!/usr/bin/python3

from threading import Thread, Lock;
from time import gmtime, strftime;
from flask import Flask, request, jsonify, session;
import worker;

app = Flask(__name__);

@app.route('/')
def index():

    return 'QASystem server works!';

@app.route('/qasystem', methods = ['POST'])
def query():

    task = worker.query.delay(request.args.get('query'));
    return jsonify({'task_id': task.request.id});

@app.after_request
def af_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return resp

if __name__ == "__main__":

    socketio.run(app, host = '172.17.0.2', port = 5000);
