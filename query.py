#!/usr/bin/python3

from flask import jsonify;
from flask_socketio import SocketIO;
from celery import Celery;
import MySQLdb;
from urllib3 import PoolManager;
from QASystem import QASystem;

celery = Celery('worker', broker = 'amqp://guest:guest@localhost:5672');
socketio = SocketIO(message_queue = "amqp://guest:guest@localhost:5672");
qasystem = QASystem();
http = PoolManager();

@celery.task
def query(question, session):

    global qasystem;
    room = session;
    namespace = '/query';
    # get answers
    answer_score_list = qasystem.query(question,3);
    response = {'path': 'qasystem', 'query': question, 'answers': answer_score_list};
    # record user's question.
    sql = "insert into wd_cust_questions (id, question, status, time) values ( NULL, \'" + question + "\', 0, \'" + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\')";
    try:
      db = MySQLdb.connect(host = 'bd.shuiwujia.cn', user = 'root', passwd = 'swj2016', db = 'cust_service_robot', charset='utf8');
      cur = db.cursor();
      cur.execute(sql.encode('utf-8'));
      db.commit();
      db.close();
    except: pass;
    # send the retval value to message room which the client is in.
    socketio.emit('msg', namespace, room, jsonify(response));

