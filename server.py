#!/usr/bin/python3

from flask import Flask, request, render_template, jsonify, session;
from flask_socketio import SocketIO, join_room;
from flask_cors import CORS;
from gevent import monkey;
from uuid import uuid4;
import MySQLdb;
from query import query, update_bert, update_corpus;
from config import *;

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

@app.route('/update_bert')
def update_model():
    if 'uid' not in session:
        session['uid'] = str(uuid4());
    task = update_bert.delay(session['uid']);
    return jsonify({'id': session['uid']});

@app.route('/update_corpus')
def update_jieba():
    if 'uid' not in session:
        session['uid'] = str(uuid4());
    task = update_corpus.delay(session['uid']);
    return jsonify({'id': session['uid']});

@app.route("/restart")
def restart():
    import os;
    os.system("bash stop_workers.sh");
    os.system("CUDA_VISIBLE_DEVICES='' bash start_workers.sh");
    # change url to some address meaningful
    return redirect("/", code = 302);

@app.route('/corpus', methods = ['POST'])
def corpus():
    params = request.json;
    status = "success";
    retval = list();
    if "mode" not in params or params["mode"] == "get":
        sql = "select * from wd_corpus_lib;";
        try:
            db = MySQLdb.connect(host = db_host, user = db_usr, passwd = db_psw, db = db_name, charset = 'utf8');
            cur = db.cursor();
            cur.execute(sql.encode('utf-8'));
            for row in cur.fetchall():
                retval.append((row[0],row[1],row[2],row[3]));
            db.commit();
            db.close();
        except:
            print("failed to get table wd_corpus_lib!");
    elif params["mode"] == "add":
        assert "data" in params;
        data = params["data"];
        assert type(data) is list;
        sql = "insert into wd_corpus_lib values (null, '" + data[0] + "', " + str(data[1]) + ", '" + data[2] + "')";
        try:
            db = MySQLdb.connect(host = db_host, user = db_usr, passwd = db_psw, db = db_name, charset = 'utf8');
            cur = db.cursor();
            cur.execute(sql.encode('utf-8'));
            db.commit();
            if cursor.rowcount == 1: status = "success";
            else: status = "failure";
            db.close();
        except:
            print("failed to add data to table wd_corpus_lib!");
    elif params["mode"] == "delete":
        assert "data" in params;
        data = params["data"];
        assert type(data) is int;
        sql = "delete from wd_corpus_lib where id = " + str(data);
        try:
            db = MySQLdb.connect(host = db_host, user = db_usr, passwd = db_psw, db = db_name, charset = 'utf8');
            cur = db.cursor();
            cur.execute(sql.encode('utf-8'));
            db.commit();
            if cursor.rowcount == 1: status = "success";
            else: status = "failure";
            db.close();
        except:
            print("failed to delete data from table wd_corpus_lib!");
    elif params["mode"] == "update":
        assert "data" in params;
        data = params["data"];
        assert type(data) is list;
        sql = "update wd_corpus_lib set corpus = '" + data[1] + "', type = " + str(data[2]) + ", date = '" + data[3] + "' where id = " + str(data[0]);
        try:
            db = MySQLdb.connect(host = db_host, user = db_usr, passwd = db_psw, db = db_name, charset = 'utf8');
            cur = db.cursor();
            cur.execute(sql.encode('utf-8'));
            db.commit();
            if cursor.rowcount == 1: status = "success";
            else: status = "failure";
            db.close();
        except:
            print("failed to update data in table wd_corpus_lib!");
    else:
        status = "failure";
        print("invalid mode for corpus method!");
    return jsonify({"status": status, "retval": retval});

@app.route('/knowledge', methods = ['POST'])
def knowledge():
    params = request.json;
    status = "success";
    retval = list();
    if "mode" not in params or params["mode"] == "get":
        sql = "select * from wd_qa_knowledge";
        try:
            db = MySQLdb.connect(host = db_host, user = db_usr, passwd = db_psw, db = db_name, charset = 'utf8');
            cur = db.cursor();
            cur.execute(sql.encode('utf-8'));
            for row in cur.fetchall():
                retval.append((row[0], row[1], row[2], row[3], row[4]));
            db.commit();
            db.close();
        except:
            print("failed to get table wd_qa_knowledge!");
    elif params["mode"] == "add":
        assert "data" in params;
        data = params["data"];
        assert type(data) is list;
        sql = "insert into wd_qa_knowledge values (null, '" + data[0] + "', '" + data[1] + "', " + str(data[2]) + ", '" + data[3] + "')";
        try:
            db = MySQLdb.connect(host = db_host, user = db_usr, passwd = db_psw, db = db_name, charset = "utf8");
            cur = db.cursor();
            cur.execute(sql.encode('utf-8'));
            db.commit();
            if cursor.rowcount == 1: status = "success";
            else: status = "failure";
            db.close();
        except:
            print("failed to add data to table wd_qa_knowledge!");
    elif params["mode"] == "delete":
        assert "data" in params;
        data = params["data"];
        assert type(data) is int;
        sql = "delete from wd_qa_knowledge where id = " + str(data);
        try:
            db = MySQLdb.connect(host = db_host, user = db_usr, passwd = db_psw, db = db_name, charset = "utf8");
            cur = db.cursor();
            cur.execute(sql.encode("utf-8"));
            db.commit();
            if cursor.rowcount == 1: status = "success";
            else: status = "failure";
            db.close();
        except:
            print("failed to delete data from table wd_qa_knowledge!");
    elif params["mode"] == "update":
        assert "data" in params;
        data = params["data"];
        assert type(data) is list;
        sql = "update wd_qa_knowledge set question = '" + data[1] + "', answer = '" + data[2] + "', type = " + str(data[3]) + ", expiry_date = '" + data[4] + "' where id = " + str(data[0]);
        try:
            db = MySQLdb.connect(host = db_host, user = db_usr, passwd = db_psw, db = db_name, charset = "utf8");
            cur = db.cursor();
            cur.execute(sql.encode("utf-8"));
            db.commit();
            if cursor.rowcount == 1: status = "success";
            else: status = "failure";
            db.close();
        except:
            print("failed to update data in table wd_qa_knowledge!");
    else:
        status = "failure";
        print("invalid mode for qa knowledge method!");
    return jsonify({"status": status, "retval": retval});

@app.route('/cust_questions')
def questions():
    retval = list();
    sql = "select * from wd_cust_questions";
    try:
        db = MySQLdb.connect(host = db_host, user = db_usr, passwd = db_psw, db = db_name, charset = 'utf8');
        cur = db.cursor();
        cur.execute(sql.encode('utf-8'));
        for row in cur.fetchall():
            retval.append((row[0], row[1], row[2], row[3]));
        db.commit();
        db.close();
    except:
        print("failed to get table wd_cust_questions!");
    return jsonify(retval);

@app.route('/chat_history')
def history():
    retval = list();
    sql = "select * from wd_robot_chat_history";
    try:
        db = MySQLdb.connect(host = db_host, user = db_usr, passwd = db_psw, db = db_name, charset = 'utf8');
        cur = db.cursor();
        cur.execute(sql.encode('utf-8'));
        for row in cur.fetchall():
            retval.append((row[0], row[1], row[2], row[3], row[4]));
        db.commit();
        db.close();
    except:
        print("failed to get table wd_robot_chat_history!");
    return jsonify(retval);

@socketio.on('connect', namespace = '/socket')
def socket_connect():
    print('connected to client!');

@socketio.on('listening', namespace = '/socket')
def on_listening():
    # client start to join the room and wait for reply.
    if 'uid' not in session:
        session['uid'] = str(uuid4());
    room = str(session['uid']);
    print("joining room " + room);
    join_room(room);

if __name__ == "__main__":

    socketio.run(app, host = '192.168.1.102', port = 5000);
