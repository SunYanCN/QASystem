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
from config import *;

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

@celery.task(name = 'query.answers')
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
        logger.info('appending question into table wd_cust_question...');
        db = MySQLdb.connect(host = db_host, user = db_usr, passwd = db_psw, db = db_name, charset='utf8');
        cur = db.cursor();
        cur.execute(sql.encode('utf-8'));
        db.commit();
        db.close();
    except Exception as e:
        logger.info(e);

@celery.task(name = 'query.update_bert')
def update_bert(session):

    assert type(session) is str;
    # download qa database from database.
    try:
        logger.info('get the latest knowledge from wd_qa_knowledge...');
        db = MySQLdb.connect(host = db_host, user = db_usr, passwd = db_psw, db = db_name, charset='utf8');
        sql = "select question,answer from wd_qa_knowledge";
        cur = db.cursor();
        cur.execute(sql.encode('utf-8'));
        qa = str();
        for row in cur.fetchall():
            qa += row[0] + "\t" + row[1] + "\n";
        with open("question_answer.txt","wb") as f:
            f.write(qa.encode('utf-8'));
        db.commit();
        db.close();
    except Exception as e:
        logger.info(e);
        response = jsonify({'status':'failure'});
        socketio.emit('msg', namespace = '/socket', room = session, data = response);
        return;
    # generate dataset.
    try:
        logger.info('generating training set...');
        from subprocess import call;
        call(["./create_dataset","-i","question_answer.txt","-o","dataset"]);
    except Exception as e:
        logger.info(e);
        response = jsonify({'status':'failure'});
        socketio.emit('msg', namespace = '/socket', room = session, data = response);
        return;
    # finetune model
    logger.info('training...');
    from Predictor import Predictor;
    predictor = Predictor();
    predictor.finetune('dataset');
    response = jsonify({"status": "success"});
    socketio.emit('msg', namespace = '/socket', room = session, data = response);

