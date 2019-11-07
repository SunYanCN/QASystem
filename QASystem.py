#!/usr/bin/python3

import sys;
import operator;
from math import exp, log;
from os.path import exists, join;
from search_engine import SearchEngine;
from Predictor import Predictor;

class QASystem(object):

    def __init__(self):

        if exists('database.dat'):
            # deserialize database is much faster.
            print('deserialize the QA database...');
            self.search_engine = SearchEngine('cc/cppjieba/dict', 'database.dat');
        else:
            # load database from txt is slower.
            print('load from QA database from txt format...');
            self.search_engine = SearchEngine('cc/cppjieba/dict');
            self.search_engine.loadFromTxt('question_answer.txt');
            self.search_engine.save('database.dat');
        self.predictor = Predictor();

    def query(self, question, count = 3):

        answer_scores = self.search_engine.query(question, count);
        answer_totalscores = dict();
        for answer, match in answer_scores.items():
            _, relevance = self.predictor.predict(question, answer);
            if match[0] > sys.float_info.min:
                answer_totalscores[answer] = (log(match[0]) * relevance, match[1],);
            else:
                answer_totalscores[answer] = (log(sys.float_info.min) * relevance, match[1],);
        return answer_totalscores;
    
    def updateDB(self, file):

        assert type(file) is str;
        self.search_engine.loadFromTxt(file);
        self.search_engine.save('database.dat');

if __name__ == "__main__":

  qasystem = QASystem();
