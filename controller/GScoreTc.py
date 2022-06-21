#! /usr/bin/python
#! coding:utf-8

from flask import Flask, render_template, request, redirect, flash, session
# from datetime import datetime, timedelta
from pymysql.converters import escape_string

import base
import collections
import database_main
import database_google
import json
import math
import pymysql
import re
import time


class ScoreTc():
    """取得地標細項任務條件
    """
    oDB = base.DB()
    oDB.connect("twd_SHU")


    def __init__(self, methods):
        try:
            page = request.args.get('page', '1')
            page = int(page)
            search_action = request.args.get('action', '')
            sort = request.args.get('sort', 'ASC')
            order = request.args.get('order', 's_tc_no')
            showcolnum = request.args.get('items', '10')
            search_options = request.args.get('search', 'All')
            search_key = request.args.get('search_key', '')
            func = request.args.get('func', '')

            aFunc_args = {}
            aFunc_args['page'] = page
            aFunc_args['search_action'] = search_action
            aFunc_args['order'] = order
            aFunc_args['sort'] = sort
            aFunc_args['showcolnum'] = showcolnum
            aFunc_args['search_options'] = search_options
            aFunc_args['search_key'] = search_key
            aFunc_args['func'] = func

            if search_action == 'search':
                if methods == 'POST':
                    aFunc_args['search_key'] = request.form['s_key']
                    aFunc_args['search_options'] = request.form['s_terms']
                self.Show(methods, aFunc_args)
            elif search_action == 'add':
                self.add(methods)
            elif search_action == 'generate_task':
                self.generate_task(methods)
            else:
                self.Show(methods, aFunc_args)

        except AttributeError as e:
            print("error: %s" % (e))
            self.app = redirect("/ScoreTc?page=1")
            flash('__init__ get value error')
        except IndexError as e:
            print("error: %s" % (e))
        except Exception as e:
            flash('__init__程序異常')
            self.app = redirect("/ScoreTc?page=1")
            print("error: %s" % (e))


    def Show(self, methods, aFunc_args):
        try:
            pagestart = (int(aFunc_args['page'] - 1)
                         * int(aFunc_args['showcolnum']))

            if aFunc_args['func'] == 'dosort':
                if aFunc_args['sort'] == 'ASC':
                    aFunc_args['sort'] = 'DESC'
                elif aFunc_args['sort'] == 'DESC':
                    aFunc_args['sort'] = 'ASC'

            if (aFunc_args['search_options'] == 'All') or (aFunc_args['search_key'] == ''):
                aScoreTc = self.oDB.select_all("lists_data_google_score_tc", '1=1', 'ORDER BY %s %s LIMIT %s, %s' % (aFunc_args['order'], aFunc_args['sort'], str(pagestart), str(aFunc_args['showcolnum'])))
                aScoreTcs_count = self.oDB.count_datas("lists_data_google_score_tc")

            elif (aFunc_args['search_options'] != 'All'):
                aScoreTc = self.oDB.select_all("lists_data_google_score_tc", "%s = '%s'" % (aFunc_args['search_options'], "%" + str(aFunc_args['search_key']) + "%"), "ORDER BY %s %s LIMIT %s, %s" % (aFunc_args['order'], aFunc_args['sort'], str(pagestart), str(aFunc_args['showcolnum'])))

                aScoreTcs_count = self.oDB.count_datas('lists_data_google_score_tc', "%s = '%s'" % (aFunc_args['search_options'], str(aFunc_args['search_key'])))

            else:
                aScoreTc = self.oDB.select_all(
                    "lists_data_google_score_tc", f"{aFunc_args['search_options']} LIKE '%{aFunc_args['search_key']}%' ORDER BY {aFunc_args['order']} {aFunc_args['sort']} LIMIT {str(pagestart)}, {str(aFunc_args['showcolnum'])}")

                aScoreTcs_count = self.oDB.count_datas('lists_data_google_score_tc', f"{aFunc_args['search_options']} LIKE '%{str(aFunc_args['search_key'])}%'")

            aProject = self.oDB.select_all("lists_data_project")

            # 存放各task_tc所屬project_no
            aProject_no = []
            for ScoreTc in aScoreTc:
                aTask_condition = json.loads(ScoreTc['task_condition'])
                for key, val in aTask_condition.items():
                    if key == 'project_no':
                        aProject_no.append(val)

            iCount_datas = int(aScoreTcs_count['total'])
            iLastpage = math.ceil(iCount_datas/int(aFunc_args['showcolnum']))

            iPage = int(aFunc_args['page'])  # 頁數

            # 頁碼判斷
            if iLastpage <= 10:
                iPagestart = 1
                iPageend = iLastpage + 1
            elif iPage <= 4:
                iPagestart = 1
                iPageend = 10
            elif iPage >= iLastpage - 5:
                iPagestart = iLastpage - 10
                iPageend = iLastpage + 1
            else:
                iPagestart = iPage - 4
                iPageend = iPage + 6

            iPagestart = 1 if iPagestart == 0 else iPagestart

            LastPageStyle = ''
            FirstPageStyle = ''
            if iPage == iLastpage:
                LastPageStyle = 'style=display:None'
            if iPage == 1:
                FirstPageStyle = 'style=display:None'

            if methods == 'GET' and aFunc_args['func'] == '':
                self.app = render_template('score_tc_list.html',
                            entries=(int(iPage) * int(aFunc_args['showcolnum'])),
                            page=iPage,
                            pageend=iPageend,
                            pagestart=iPagestart,
                            search_key=aFunc_args['search_key'],
                            search_options=aFunc_args['search_options'],
                            items=aFunc_args['showcolnum'],
                            lastpage=iLastpage,
                            FirstPageStyle=FirstPageStyle,
                            LastPageStyle=LastPageStyle,
                            count=iCount_datas,
                            pageprev=iPage - 1,
                            pagenext=iPage + 1,
                            sort=aFunc_args['sort'],
                            order=aFunc_args['order'],
                            aScoreTc=aScoreTc,
                            aProject_no=aProject_no,
                            colstart=(int(pagestart) + 1), 
                            aProject=aProject,
                            zip=zip,
                            sfunc='ScoreTc')
            elif methods == 'GET' and aFunc_args['func'] == 'dosort':
                self.app = redirect("/ScoreTc?page=%s&items=%s&order=%s&sort=%s&search=%s&search_key=%s" % (str(iPage), str(
                    aFunc_args['showcolnum']), aFunc_args['order'], aFunc_args['sort'], aFunc_args['search_options'], aFunc_args['search_key']), code=302)
            elif methods == 'POST':
                self.app = redirect("/ScoreTc?page=1&items=%s&order=s_tc_no&sort=ASC&search=%s&search_key=%s" % (
                    str(aFunc_args['showcolnum']), aFunc_args['search_options'], str(aFunc_args['search_key'])), code=302)
        except pymysql.OperationalError:
            flash('資料庫發生錯誤')
            print('database error')
            self.app = redirect("/ScoreTc?page=1")
        except Exception as e:
            print("Show: %s\nerror line: %s" % (e, e.__traceback__.tb_lineno))
            self.app = redirect("/ScoreTc?page=1")


    def add(self, methods):
        """新增評分任務條件資料

        Args:
            methods (_type_): _description_
        """
        try:
            if methods == 'GET':
                s_tc_no = request.args.get('s_tc_no')
                if int(s_tc_no) == 0:
                    aScoreTc = None
                else:
                    aScoreTc = self.oDB.select_single('lists_data_google_score_tc', 's_tc_no=%s' % (s_tc_no))

                self.app = render_template('score_tc_edit.html', s_tc_no=int(s_tc_no), aScoreTc=aScoreTc,  code=307)

            elif methods == 'POST':
                data_source = ''
                sFunction = ''
                project_no = ''
                target_num = ''
                target_no = ''
                target_date = ''

                s_tc_no = request.form['s_tc_no'] if request.form['s_tc_no'] else ''
                data_source = request.form.get('data_source', '')
                sFunction = request.form.get('selectFunc', '')
                project_no = request.form.get('project_no', '')
                target_num = request.form.get('target_num', '')
                target_no = request.form.get('target_no', '')
                target_date = request.form.get('target_date', '')

                aArgs = {}
                aArgs['project_no'] = project_no
                aArgs['target_num'] = target_num
                aArgs['target_no'] = target_no
                aArgs['target_date'] = target_date

                # 新增
                if s_tc_no == '':
                    oExecFunc = ExecFunc(data_source, sFunction, aArgs)
                if oExecFunc.aGs_no_NotExist:
                    flash("下列gs_no並不存在 : \n   %s\n" % (oExecFunc.aGs_no_NotExist))
                if oExecFunc.aGs_no_NotInTag:
                    flash("\n下列 gs_no 不符合 Tag 組別為 %s 範圍 : \n   %s\n" % (oExecFunc.sTarget_tag, oExecFunc.aGs_no_NotInTag))
                if oExecFunc.aGs_no_status2:
                    flash("下列gs_no已有 Google 評分資料 : \n   %s\n" % (oExecFunc.aGs_no_status2))

                self.app = redirect("/ScoreTc?page=1")

        except Exception as e:
            flash('新增任務條件失敗: %s' % e)
            print("新增任務條件失敗: %s\nerror line: %s" % (e, e.__traceback__.tb_lineno))
            self.app = redirect("/ScoreTc?page=1")


    def generate_task(self, methods):
        """產生任務

        Args:
            methods (str): 操作
        """
        try:
            s_tc_no = int(request.args.get('s_tc_no'))

            if s_tc_no == 0:
                aResult_datas = self.oDB.select_all("lists_data_google_score_tc", "status = 0")
            else:
                aResult_datas = self.oDB.select_all("lists_data_google_score_tc", "s_tc_no = %s AND status = 0" % s_tc_no)

            # 生成 result data 任務
            iCo_id_count = 0    
            iGs_no_count = 0

            iTotal_main_task = 0
            iTotal_google_task = 0
            
            for aResult_data in aResult_datas:
                aSave_data = collections.OrderedDict()
                sSearch_url = ''
                aTask_condition = json.loads(aResult_data['task_condition'])

                # according co_id in json format key
                if "co_id" in aTask_condition.keys():
                    iCo_id_count = 0  # 計算任務筆數
                    for sCo_id in aTask_condition['co_id']:
                        # 依co_id取得主庫資料
                        aItems_score_data = self.oDBM.select_single('items_data_google_score', 'co_id = %s' % (int(sCo_id)))
                        aItems_data = self.oDBM.select_single('items_data', 'co_id = %s' % (int(sCo_id)))
                        aGoogle_result = json.loads(aItems_score_data['google_result'])
                        aCo_info = json.loads(aItems_data['co_info'])

                        # 根據人工審核資料為優先採用 >> Google_score的url >>地址解析
                        if 'google_url' in aCo_info.keys():
                            sSearch_url = self.rebuild_url(
                                aCo_info['google_url'])
                        elif 'url' in aGoogle_result.keys():
                            sSearch_url = self.rebuild_url(aGoogle_result['url'])
                        elif 'co_addr' in aCo_info.keys():
                            match = re.search(
                                r'(.*?縣|.*?市)(\D*?區|\D*?市|\D*?鄉|\D*?鎮)?', aCo_info['co_addr'])

                            sCity_region = match.group(0)  # 縣市+行政區
                            sSearch_url = "https://www.google.com/maps/search/" + \
                                sCity_region + "+" + aCo_info['name']

                        aSave_data['origin_no'] = sCo_id
                        aSave_data['task_url'] = sSearch_url
                        aSave_data['s_tc_no'] = aResult_data['s_tc_no']
                        aSave_data['target_database'] = 'twd_source'

                        self.oDB.insert("score_task", "origin_no, s_tc_no, task_url, target_database, created", "%s, %s, '%s', '%s', NOW()" % (aSave_data['origin_no'], aSave_data['s_tc_no'], aSave_data['task_url'], aSave_data['target_database']))
                        iCo_id_count += 1

                if "gs_no" in aTask_condition.keys():
                    iGs_no_count = 0  # 計算任務筆數
                    for sGs_no in aTask_condition['gs_no']:
                        # 依gs_no取得google list資料庫資料
                        sTabledata = self.oDB.select_single(
                            'lists_data_project', "project_name = '%s'" % (aTask_condition['project_name']))

                        timeString = str(sTabledata['s_date'])
                        struct_time = time.strptime(
                            timeString, "%Y-%m-%d %H:%M:%S")
                        sTaskTime = time.strftime("%Y%m%d", struct_time)
                        sTableName = "lists_data_%s%s" % (
                            sTabledata['project_name'], sTaskTime)

                        lists_data = self.oDB.select_single(
                            sTableName, 'gs_no = %s' % (int(sGs_no)))

                        aGoogle_list = json.loads(lists_data['google_list'])

                        sSearch_url = aGoogle_list['url']

                        aSave_data['origin_no'] = sGs_no
                        aSave_data['task_url'] = escape_string(sSearch_url)
                        aSave_data['s_tc_no'] = aResult_data['s_tc_no']
                        aSave_data['target_database'] = 'twd_SHU'

                        self.oDB.insert("score_task", "origin_no, s_tc_no, task_url, target_database, created", "%s, %s, '%s', '%s', NOW()" % (aSave_data['origin_no'], aSave_data['s_tc_no'], aSave_data['task_url'], aSave_data['target_database']))
                        iGs_no_count += 1

                if iCo_id_count != 0:
                    print("已生成 %s 筆 主庫任務\n" % (iCo_id_count))
                    iTotal_main_task += iCo_id_count
                if iGs_no_count != 0:
                    print("已生成 %s 筆 Google_list任務\n" % (iGs_no_count))
                    iTotal_google_task += iGs_no_count

                # 修改 lists_data_google_score_tc 狀態
                self.oDB.update("lists_data_google_score_tc", "modified = NOW(), status = 1", "s_tc_no = %s" % (aResult_data['s_tc_no']))

            print("已生成 %s 筆 主庫任務\n       %s 筆 Google_list任務\n" % (iTotal_main_task, iTotal_google_task))

            self.app = redirect("/ScoreTc?page=1")
        except Exception as e :
            flash("產生任務錯誤: %s " % e)
            self.app = redirect("/ScoreTc?page=1")


class ExecFunc:
    oDBM = database_main.oDB()
    oDBG = database_google.oDB()

    oDB = base.DB()
    oDB.connect('twd_SHU')

    sData : str
    sExec : str

    # target_tag 組別所有 tag (string)
    sTarget_tag = ''
    # search_key list轉換string
    sSearch_key = ''
    # 執行g_no
    exe_g_no = []

    # 記錄開始時間
    start_time = ''
    # 記錄完成筆數
    finished_count = 0
    # 執行項目選擇
    function_input = ''

    # 不存在gs_no
    aGs_no_NotExist = []
    # 不符合Tag範圍
    aGs_no_NotInTag = []
    # 尚未取得評分資料
    aGs_no_status0 = []
    # 已有評分資料
    aGs_no_status2 = []


    def __init__(self, sData, sExec, aArgs):
        self.exe_g_no = []
        self.aGs_no_NotExist = []
        self.aGs_no_NotInTag = []
        self.aGs_no_status0 = []
        self.aGs_no_status2 = []

        if sData == "GoogleList":
            self.exec_google(sExec, aArgs)
        elif sData == "Main":
            self.exec_main(sExec, aArgs)


    def exec_google(self, sExec, aArgs):
        """執行google條件任務

        Args:
            sExec (str): 執行選項
            aArgs (dict): 執行任務變數
        """
        # 取得project資料
        aSelect_project = self.oDB.select_single("lists_data_project", "project_no = %s"%(aArgs['project_no']))

        # 專案資料表使用名稱
        sProject_table = aSelect_project['project_name'] + aSelect_project['s_date'].strftime('%Y%m%d')

        # 組成project lists_data 資料表名稱
        sLists_data = 'lists_data_' + aSelect_project['project_name'] + aSelect_project['s_date'].strftime('%Y%m%d')

        # 取得產業編號
        industry_no = aSelect_project['industry_no']

        # 取得產業名稱
        industry_data = self.oDB.select_single(
            "industry", "industry_no = %s" % (industry_no))

        # 取得該產業的target_tag資料
        target_tag_result = self.oDB.select_all(
            "target_tag", "industry_no = %s AND status = 1" % (industry_no))

        # target_tag 組別
        tmp_target_tag_list = []
        for target_tag in target_tag_result:
            if target_tag['tag_name'] not in tmp_target_tag_list:
                tmp_target_tag_list.append(target_tag['tag_name'])

        self.sTarget_tag = ','.join(map("'{0}'".format, tmp_target_tag_list))

        # search_key 組別
        search_key_result = self.oDB.select_all(
            "search_key", "industry_no = %s" % (industry_no))

        tmp_search_key_list = []
        for search_key in search_key_result:
            if search_key['sk_name'] not in tmp_search_key_list:
                tmp_search_key_list.append(search_key['sk_name'])

        self.sSearch_key = ','.join(map("'{0}'".format, tmp_search_key_list))

        # ============================== 新增多筆 ==============================
        if sExec == '新增多筆':

            total = self.oDBG.count_lists_data(sLists_data, "google_list->>'$.tag' IN (%s) AND status = 0" % (self.sTarget_tag))

            num_input = aArgs['target_num']
            # JS 處理輸入判斷

            count = 0
            if total and num_input == '':
                for nums in range(total):
                    # 隨機取得單筆資料
                    result = self.oDBG.find_google_data(
                        sLists_data, "google_list->>'$.tag' IN (%s) AND status = 0" % (self.sTarget_tag))
                    self.exe_g_no.append(result['gs_no'])
                    self.oDBG.update(
                        sLists_data, "status = 1, modified = NOW()", "gs_no = %s" % (result['gs_no']))
                    count += 1

            elif total and num_input != '' and (int(num_input) <= total):
                for nums in range(int(num_input)):
                    result = self.oDBG.find_google_data(
                        sLists_data, "google_list->>'$.tag' IN (%s) AND status = 0" % (self.sTarget_tag))
                    self.exe_g_no.append(result['gs_no'])
                    self.oDBG.update(
                        sLists_data, "status = 1, modified = NOW()", "gs_no = %s" % (result['gs_no']))
                    count += 1 

        # ============================== 更新多筆 ==============================
        elif sExec == '更新多筆':
            # 取得符合條件之資料筆數
            total = self.oDBG.count_google_score(sProject_table, "LDGS.modified <= '%s' AND LD.google_list->>'$.tag' IN (%s) AND status = 2" % (aArgs['target_date'], self.sTarget_tag)) if self.oDBG.count_google_score(sProject_table, "LDGS.modified <= '%s' AND LD.google_list->>'$.tag' IN (%s) AND status = 2" % (aArgs['target_date'], self.sTarget_tag)) else None

            if total:
                iCount = 0
                if total and aArgs['target_num'] == '':
                    for nums in range(total):
                        # 取得單筆資料
                        result = self.oDBG.search_google_score(sProject_table, "LDGS.modified <= '%s' AND LD.google_list->>'$.tag' IN (%s) AND LD.status = 2" % (aArgs['target_date'], self.sTarget_tag))

                        if (result) and (result['data_code'] is None):
                            result = self.oDBG.find_non_google_data(sProject_table, "LD.gs_no = %s AND LDGS.modified <= '%s' AND LD.status = 2" % (result['gs_no'], aArgs['target_date']))

                        if result:
                            self.exe_g_no.append(result['gs_no'])
                            self.oDBG.update(
                                sLists_data, "status = 1, modified = NOW()", "gs_no = %s" % (result['gs_no']))
                        iCount += 1

                elif total and aArgs['target_num'] != '' and (int(aArgs['target_num']) < total):
                    for nums in range(int(aArgs['target_num'])):
                        result = self.oDBG.search_google_score(
                            sProject_table, "LDGS.modified <= '%s' AND LD.google_list->>'$.tag' IN (%s) AND LD.status = 2" % (aArgs['target_date'], self.sTarget_tag))

                        if (result) and (result['data_code'] is None):
                            result = self.oDBG.find_non_google_data(
                                sProject_table, "LD.gs_no = %s AND LDGS.modified <= '%s' AND LD.status = 2" % (result['gs_no'], aArgs['target_date']))

                        if result:
                            self.exe_g_no.append(result['gs_no'])
                            self.oDBG.update(
                                sLists_data, "status = 1, modified = NOW()", "gs_no = %s" % (result['gs_no']))
                        iCount += 1

            elif total == None:
                flash("\n %s 前無資料須更新\n" % (aArgs['target_date']))

        # ============================== 新增單筆 ==============================
        elif sExec == '新增單筆':

            gs_no_input = [i for i in aArgs['target_no'].split(',')]

            for gs_no in gs_no_input:

                # 撿查輸入條件是否符合
                chk_gs_no = self.oDBG.check_lists_data(sProject_table, "gs_no = %s" % (gs_no))
                chk_tag = self.oDBG.check_lists_data(sProject_table, "gs_no = %s AND google_list->>'$.tag' IN (%s)" % (gs_no, self.sTarget_tag))

                if chk_tag and chk_tag['status'] == 0:
                    # 取得單筆資料
                    result = self.oDBG.find_google_data(sLists_data, "gs_no = %s" % (gs_no)) if self.oDBG.find_google_data(sLists_data, "gs_no = %s" % (gs_no)) else None

                    if result:
                        self.exe_g_no.append(result['gs_no'])
                        self.oDBG.update(sLists_data, "status = 1, modified = NOW()", "gs_no = %s" % (result['gs_no']))

                elif chk_tag and chk_tag['status'] == 2:
                    self.aGs_no_status2.append(gs_no)
                elif chk_gs_no and (chk_tag == None):
                    self.aGs_no_NotInTag.append(gs_no)
                else:
                    self.aGs_no_NotExist.append(gs_no)

            if self.aGs_no_NotExist:
                flash("下列gs_no並不存在 : \n   %s\n" % self.aGs_no_NotExist)
            if self.aGs_no_NotInTag:
                flash("\n下列 gs_no 不符合 Tag 組別為 %s 範圍 : \n   %s\n" % (self.sTarget_tag, self.aGs_no_NotInTag))
            if self.aGs_no_status2:
                flash("下列gs_no已有 Google 評分資料 : \n   %s\n" % self.aGs_no_status2)

        # ============================== 更新單筆 ==============================
        elif sExec == '更新單筆':

            gs_no_input = [i for i in aArgs['target_no'].split(',')]
            for gs_no in gs_no_input:

                # 撿查輸入條件是否符合
                chk_gs_no = self.oDBG.check_lists_data(sProject_table, "gs_no = %s" % (gs_no))
                chk_tag = self.oDBG.check_lists_data(sProject_table, "gs_no = %s AND google_list->>'$.tag' IN (%s)" % (gs_no, self.sTarget_tag))

                if chk_tag and chk_tag['status'] == 2:
                    # 取得單筆資料
                    result = self.oDBG.search_google_score(sProject_table, "LD.google_list->>'$.tag' IN (%s) AND LDGS.gs_no = %s" % (self.sTarget_tag, gs_no)) if self.oDBG.search_google_score(sProject_table, "LD.google_list->>'$.tag' IN (%s) AND LDGS.gs_no = %s" % (self.sTarget_tag, gs_no)) else None

                    if result['url'] is None:
                        result = self.oDBG.find_non_google_data(
                            "LD.gs_no = %s" % (result['gs_no']))

                    if result:
                        self.exe_g_no.append(result['gs_no'])
                        self.oDBG.update(sLists_data, "status = 1, modified = NOW()", "gs_no = %s" % (result['gs_no']))

                elif chk_tag and (chk_tag['status'] == 0 or chk_tag['status'] == 1):
                    self.aGs_no_status0.append(gs_no)
                elif chk_gs_no and (chk_tag == None):
                    self.aGs_no_NotInTag.append(gs_no)
                else:
                    self.aGs_no_NotExist.append(gs_no)

            if self.aGs_no_NotExist:
                flash("\n下列 gs_no 並不存在 : \n   %s\n" % self.aGs_no_NotExist)
            if self.aGs_no_NotInTag:
                flash("\n下列 gs_no 不符合 Tag 組別為 %s 範圍 : \n   %s\n" % (self.sTarget_tag, self.aGs_no_NotInTag))
            if self.aGs_no_status0:
                flash("\n下列 gs_no 請先執行「新增」Google評分資料 : \n   %s\n" % self.aGs_no_status0)

        if self.exe_g_no != []:
            score_task_condition = collections.OrderedDict()
            score_task_condition["gs_no"] = self.exe_g_no
            score_task_condition['function'] = sExec
            score_task_condition['data_source'] = 'Google_list'
            score_task_condition['project_name'] = aSelect_project['project_name']
            score_task_condition['industry'] = industry_data['industry_name']
            score_task_condition['project_no'] = aSelect_project['project_no']

            score_task_condition = json.dumps(score_task_condition, ensure_ascii=False)

            score_task_condition = escape_string(score_task_condition)

            self.oDBG.insert('lists_data_google_score_tc', 'task_condition, created, modified', "'%s', NOW(), NOW()" % (score_task_condition))

