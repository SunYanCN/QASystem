#!/usr/bin/python3

from flask import Flask, request, jsonify;
from subprocess import call;
import MySQLdb;
from Predictor import Predictor;

app = Flask(__name__);

@app.route('/update_bert')
def update_bert():
    # download qa database from database.
    try:
      db = MySQLdb.connect(host = 'bd.shuiwujia.cn', user = 'root', passwd = 'swj2016', db = 'cust_service_robot', charset='utf8');
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
      print(e);
      response = jsonify({'status':'failure'});
      return response;
    # generate dataset.
    try:
      call(["./create_dataset","-i","question_answer.txt","-o","dataset"]);
    except Exception as e:
      print(e);
      response = jsonify({'status':'failure'});
      return response;
    # finetune model
    predictor = Predictor();
    predictor.finetune('dataset');
    # return status
    response = jsonify({'status':'success'});
    return response;

@app.route('/update_jieba')
def update_jieba():
    # download corpus database from mysql.
    try:
      db = MySQLdb.connect(host = 'bd.shuiwujia.cn', user = 'root', passwd = 'swj2016', db = 'cust_service_robot', charset='utf8');
      sql = "select corpus from wd_corpus_lib where type = 1";
      cur = db.cursor();
      cur.execute(sql.encode('utf-8'));
      corpus = str();
      for row in cur.fetchall():
        corpus += row[0] + "\n";
      with open("cppjieba/dict/stop_words.utf8","wb") as f:
        f.write(corpus.encode("utf-8"));
      db.commit();
      db.close();
    except Exception as e:
      print(e);
      response = jsonify({"status":"failure"});
      return response;
    response = jsonify({"status":"success"});
    return response;

@app.after_request
def af_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*';
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST';
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type';
    return resp;

if __name__ == "__main__":

    app.run(host = '172.17.0.2', port = 5001, threaded = True);

