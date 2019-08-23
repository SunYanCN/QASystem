#!/usr/bin/python3

from flask import Flask, request, jsonify;
from QASystem import QASystem;

app = Flask(__name__);
qasystem = QASystem();

@app.route('/')
def index():
    return 'QASystem server works!';

@app.route('/qasystem', methods = ['POST'])
def query():
    question = request.args.get('query');
    answer_score_list = qasystem.query(question,3);
    response = jsonify({'path': 'qasystem', 'query': question, 'answers': answer_score_list});
    return response;

if __name__ == "__main__":
    
    app.run();
