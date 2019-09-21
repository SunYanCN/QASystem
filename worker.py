#!/usr/bin/python3

from celery import Celery;
import MySQLdb;
from urllib3 import PoolManager;
from QASystem import QASystem;

celery = Celery('worker', broker = 'amqp://');
qasystem = QASystem();
http = PoolManager();

host = 'http://xxx.com';

class QAWorker(celery.Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc));

    def on_success(self, retval, task_id, args, kwargs):
        print('success! {0}'.format(retval));
        retval['task_id'] = task_id;
        # send session id to xxx
        http.request('POS', host, body = json.dumps(retval), headers = {"content-type": "application/json"});

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        print("retry..." + task_id);

@celery.task
def query(question):

    global qasystem;
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
    return response;
