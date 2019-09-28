#!/usr/bin/python3

from flask_socketio import SocketIO;
from celery import Celery;
from celery.utils.log import get_task_logger;
from celery.signals import worker_init, worker_process_init;
from celery.concurrency import asynpool;
from gevent import monkey;
from time import gmtime, strftime;
import MySQLdb;
from QASystem import QASystem;

monkey.patch_all();
asynpool.PROC_ALIVE_TIMEOUT = 100.0; # this is import for very long task.
celery = Celery('worker', broker = 'amqp://guest:guest@localhost:5672');
socketio = SocketIO(message_queue = "amqp://guest:guest@localhost:5672");
logger = get_task_logger(__name__);
qasystem = None;

@worker_process_init.connect()
def on_worker_init(**_):
    global qasystem;
    qasystem = QASystem();
    logger.info('model initialization completed!');

@celery.task
def query(question, session):

    assert type(question) is str;
    assert type(session) is str;
    # get answers
    answer_score_list = qasystem.query(question,3);
    response = {'path': 'qasystem', 'query': question, 'answers': answer_score_list};
    # send the retval value to message room which the client is in.
    socketio.emit('msg', namespace = "/socket", room = session, data = response);
    logger.info('query completed!');
    # record user's question.
    sql = "insert into wd_cust_questions (id, question, status, time) values ( NULL, \'" + question + "\', 0, \'" + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\')";
    try:
      db = MySQLdb.connect(host = 'bd.shuiwujia.cn', user = 'root', passwd = 'swj2016', db = 'cust_service_robot', charset='utf8');
      cur = db.cursor();
      cur.execute(sql.encode('utf-8'));
      db.commit();
      db.close();
    except: pass;

