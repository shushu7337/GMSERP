#!/usr/bin/python
#! coding:utf-8

from flask import *
import sys


sys.path.append(sys.path[0]+'/controller')


import GProject
import GSearchKey
import GTargetTag
import GIndustry
import GListsDataTc
import GListsTask
import GScoreTc
import GScoreTask
import GDataprocess
import GAjax


app = Flask(__name__)

'''
    首頁
'''
@app.route('/')
@app.route('/Index')
def home():
    return render_template('index.html')


'''
    專案管理頁
'''
@app.route('/Project', methods=['GET','POST'])
def Project():
    return GProject.Project(request.method).app


'''
    搜尋關鍵字
'''
@app.route('/SearchKey', methods=['GET','POST'])
def SearchKey():
    return GSearchKey.SearchKey(request.method).app


'''
    目標關鍵字
'''
@app.route('/TargetTag', methods=['GET','POST'])
def Tearch_key():
    return GTargetTag.TargetTag(request.method).app


'''
    產業管理頁
'''
@app.route('/Industry', methods=['GET','POST'])
def Industry():
    return GIndustry.Industry(request.method).app


'''
    Ajax
'''
@app.route('/Ajax/<func_name>', methods=['GET', 'POST'])
def Ajax(func_name):
    return GAjax.Ajax(func_name).res_json


'''
    清單任務條件
'''
@app.route('/ListsDataTc', methods=['GET','POST'])
def ListsDataTc():
    return GListsDataTc.ListsDataTc(request.method).app


'''
    清單任務
'''
@app.route('/ListsTask', methods=['GET','POST'])
def ListsTask():
    return GListsTask.ListsTask(request.method).app


'''
    評分任務條件
'''
@app.route('/ScoreTc', methods=['GET','POST'])
def score_tc():
    return GScoreTc.ScoreTc(request.method).app


'''
    評分任務
'''
@app.route('/ScoreTask', methods=['GET','POST'])
def score_task():
    return GScoreTask.ScoreTask(request.method).app

'''
    資料分析
'''
@app.route('/Dataprocess', methods=['GET','POST'])
def data_process():
    return GDataprocess.Dataprocess(request.method).app


if __name__ == '__main__':
    app.debug = True
    app.secret_key = '123'
    app.run()

