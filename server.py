#!/usr/bin/python3

from threading import Thread, Lock;
from time import gmtime, strftime;
from flask import Flask, request, jsonify;
import MySQLdb;
import numpy as np;
from QASystem import QASystem;

bert_num = 10;

app = Flask(__name__);
qasystems = [(QASystem(), Lock()) for i in range(bert_num)];

@app.route('/')
def index():
    return 'QASystem server works!';

@app.route('/qasystem', methods = ['POST'])
def query():
    question = request.args.get('query');
    index = np.random.randint(bert_num);
    qasystems[index][1].acquire();
    print("calling " + str(index) + "th bert");
    answer_score_list = qasystems[index][0].query(question,3);
    print("ending " + str(index) + "th bert");
    qasystems[index][1].release();
    response = jsonify({'path': 'qasystem', 'query': question, 'answers': answer_score_list});
    sql = "insert into wd_cust_questions (id, question, status, time) values ( NULL, \'" + question + "\', 0, \'" + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\')";
    try:
      db = MySQLdb.connect(host = 'bd.shuiwujia.cn', user = 'root', passwd = 'swj2016', db = 'cust_service_robot', charset='utf8');
      cur = db.cursor();
      cur.execute(sql.encode('utf-8'));
      db.commit();
      db.close();
    except: pass;
    return response;

@app.after_request
def af_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return resp

if __name__ == "__main__":

    app.run(host = '172.17.0.2', port = 5000, threaded = True);
