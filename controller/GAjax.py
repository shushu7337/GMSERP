#! /usr/bin/python
#! coding:utf-8

from flask import Flask, request, session

import base
import json
import database_main
import database_google
import os

class Ajax():
    """ajax return data
    """


    oDB = base.DB()
    oDB.connect("twd_SHU")
    oDBA = base.DB()
    oDBA.connect("twd_adm")

    oDBM = database_main.oDB()
    oDBG = database_google.oDB()

    res_json = ''

    def __init__(self, func_name):
        try:
            Func = getattr(self, func_name)
            Func()

        except Exception as e:
            print("Ajax : %s\nerror line: %s" % (e, e.__traceback__.tb_lineno))


    def getProject(self):
        """取得「專案任務」資料
        """
        try:
            data_source = request.form['data_source']
            if data_source == 'Main':
                aDatas = self.oDBA.select_all('division', 'parent_tag_no = 0')
                res = list()

                for i in aDatas:
                    tmp = {}
                    tmp['item_no'] = i['division_no']
                    tmp['item_name'] = i['division_name']
                    res.append(tmp)
            elif data_source == 'GoogleList':
                aDatas = self.oDB.select_all('lists_data_project')
                res = list()

                for i in aDatas:
                    tmp = {}
                    tmp['item_no'] = i['project_no']
                    tmp['item_name'] = i['project_name']
                    res.append(tmp)

            self.res_json = json.dumps(res)
        except Exception as e:
            print("getProject: %s\nerror line: %s" % (e, e.__traceback__.tb_lineno))


    def getSearchKey(self):
        """取得「產業」-搜尋關鍵字(Tag)
        """
        try:
            industry_no  = request.form['industry_no']
            aSearch_key = self.oDB.select_all('search_key', 'industry_no = %s' % (industry_no))

            res = list()
            for i in aSearch_key:
                tmp = {}
                tmp['sk_no'] = i['sk_no']
                tmp['sk_name'] = i['sk_name']
                res.append(tmp)
            self.res_json = json.dumps(res)
        except Exception as e:
            print("getSearchKey: %s" % (e))


    def getRegion(self):
        """取得「縣市」行政區資料
        """
        try:
            c_no = request.form['c_no']
            aRegion = self.oDB.select_all('region', 'c_no = %s' % (c_no))

            res = list()
            for i in aRegion:
                tmp = {}
                tmp['r_no'] = i['r_no']
                tmp['r_name'] = i['r_name']
                res.append(tmp)
            self.res_json = json.dumps(res)
        except Exception as e:
            print("getRegion: %s" % (e))


    def getStreet(self):
        """取得該「縣市」-「行政區」的街道資料
        """
        try:
            r_no = request.form['r_no']
            aStreet = self.oDB.select_all('street', 'r_no IN (%s)' % (r_no))

            res = list()
            for i in aStreet:
                tmp = {}
                tmp['s_no'] = i['s_no']
                tmp['s_name'] = i['s_name']
                res.append(tmp)
            self.res_json = json.dumps(res)
        except Exception as e:
            print("getStreet: %s" % (e))


    def getScoreInfo(self):
        """取得 Google Score 資訊
        """
        try:
            item_no = request.form['item_no']
            data_source = request.form['data_source']

            if data_source == 'Main':
                # 尚未取得Google評分 筆數
                total_lists_data = self.oDBM.count_items_data(
                    item_no, 'ID.flag = 2') if self.oDBM.count_items_data(item_no, 'ID.flag = 2') else 0

                # 待取得Google評分 筆數
                stand_by_google_score = self.oDBM.count_items_data(
                    item_no, 'ID.flag = 3') if self.oDBM.count_items_data(item_no, 'ID.flag = 3') else 0

                # 已取得Google評分 筆數
                total_google_score = self.oDBM.count_google_score(
                    item_no, "ID.flag = 4") if self.oDBM.count_google_score(item_no, "ID.flag = 4") else 0

                # 取得最舊Google評分資料日期
                oldest_data_time = self.oDBM.find_google_score(
                    item_no, "IDGS.modified=(SELECT MIN(IDGS.modified) FROM items_data_google_score AS IDGS LEFT JOIN seo_company_division_rel AS SC ON IDGS.co_id=SC.co_id WHERE SC.division_no IN(%s))" % (item_no))['modified'] if self.oDBM.find_google_score(
                    item_no, "IDGS.modified=(SELECT MIN(IDGS.modified) FROM items_data_google_score AS IDGS LEFT JOIN seo_company_division_rel AS SC ON IDGS.co_id=SC.co_id WHERE SC.division_no IN(%s))" % (item_no)) else 0

                # 取得最新Google評分資料日期
                newest_data_time = self.oDBM.find_google_score(
                    item_no, "IDGS.modified=(SELECT MAX(IDGS.modified) FROM items_data_google_score AS IDGS LEFT JOIN seo_company_division_rel AS SC ON IDGS.co_id=SC.co_id WHERE SC.division_no IN(%s))" % (item_no))['modified'] if self.oDBM.find_google_score(
                    item_no, "IDGS.modified=(SELECT MAX(IDGS.modified) FROM items_data_google_score AS IDGS LEFT JOIN seo_company_division_rel AS SC ON IDGS.co_id=SC.co_id WHERE SC.division_no IN(%s))" % (item_no)) else 0
            elif data_source == 'GoogleList':
                # 取得project資料
                aSelect_project = self.oDB.select_single("lists_data_project", "project_no = '%s'"%(item_no))

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

                # 尚未建立target tag資料
                if not target_tag_result:
                    self.res_json = None
                    quit()

                # target_tag 組別
                tmp_target_tag_list = []
                for target_tag in target_tag_result:
                    if target_tag['tag_name'] not in tmp_target_tag_list:
                        tmp_target_tag_list.append(target_tag['tag_name'])

                sTarget_tag = ','.join(map("'{0}'".format, tmp_target_tag_list))

                # search_key 組別
                search_key_result = self.oDB.select_all(
                    "search_key", "industry_no = %s" % (industry_no))

                tmp_search_key_list = []
                for search_key in search_key_result:
                    if search_key['sk_name'] not in tmp_search_key_list:
                        tmp_search_key_list.append(search_key['sk_name'])

                sSearch_key = ','.join(map("'{0}'".format, tmp_search_key_list))

                # 該 專案產業關鍵字組 尚未取得Google評分 筆數
                total_lists_data = self.oDBG.count_lists_data(sLists_data, "google_list->>'$.tag' IN (%s) AND status = 0" % (
                    sTarget_tag)) if self.oDBG.count_lists_data(sLists_data, "google_list->>'$.tag' IN (%s) AND status = 0" % (sTarget_tag)) else 0

                # 該 專案產業關鍵字組 待取得Google評分 筆數
                stand_by_google_score = self.oDBG.count_lists_data(sLists_data, "google_list->>'$.tag' IN (%s) AND status = 1" % (sTarget_tag)) if self.oDBG.count_lists_data(sLists_data, "google_list->>'$.tag' IN (%s) AND status = 1" % (sTarget_tag)) else 0

                # 該 專案產業關鍵字組 已取得Google評分 筆數
                total_google_score = self.oDBG.count_lists_data(sLists_data, "google_list->>'$.tag' IN (%s) AND status IN (2,3)" % (sTarget_tag)) if self.oDBG.count_lists_data(sLists_data, "google_list->>'$.tag' IN (%s) AND status IN (2,3)" % (sTarget_tag)) else 0

                # 該關鍵字取得最舊Google評分資料日期
                oldest_data_time = self.oDBG.find_google_score(sProject_table, "LD.google_list->>'$.tag' IN (%s) AND LDGS.modified=(SELECT MIN(LDGS.modified) FROM lists_data_google_score_%s AS LDGS LEFT JOIN lists_data_%s AS LD ON LDGS.gs_no = LD.gs_no WHERE google_list->>'$.tag' IN (%s))" % (sSearch_key, sProject_table, sProject_table, sSearch_key))[
                        'modified'] if self.oDBG.find_google_score(sProject_table, "LD.google_list->>'$.tag' IN (%s) AND LDGS.modified=(SELECT MIN(LDGS.modified) FROM lists_data_google_score_%s AS LDGS LEFT JOIN lists_data_%s AS LD ON LDGS.gs_no = LD.gs_no WHERE google_list->>'$.tag' IN (%s))" % (sSearch_key, sProject_table, sProject_table, sSearch_key)) else 0

                # 該關鍵字取得最新Google評分資料日期
                newest_data_time = self.oDBG.find_google_score(sProject_table, "LD.google_list->>'$.tag' IN (%s) AND LDGS.modified=(SELECT MAX(LDGS.modified) FROM lists_data_google_score_%s AS LDGS LEFT JOIN lists_data_%s AS LD ON LDGS.gs_no = LD.gs_no WHERE google_list->>'$.tag' IN (%s))" % (sSearch_key, sProject_table, sProject_table, sSearch_key))[
                        'modified'] if self.oDBG.find_google_score(sProject_table, "LD.google_list->>'$.tag' IN (%s) AND LDGS.modified=(SELECT MAX(LDGS.modified) FROM lists_data_google_score_%s AS LDGS LEFT JOIN lists_data_%s AS LD ON LDGS.gs_no = LD.gs_no WHERE google_list->>'$.tag' IN (%s))" % (sSearch_key, sProject_table, sProject_table, sSearch_key)) else 0

            res = {}
            res['total_lists_data'] = total_google_score
            res['stand_by_google_score'] = stand_by_google_score
            res['total_google_score'] = total_lists_data
            res['oldest_data_time'] = str(oldest_data_time)
            res['newest_data_time'] = str(newest_data_time)

            self.res_json = json.dumps(res)
            
        except Exception as e:
            print("getScoreTc: %s\nerror line: %s" % (e, e.__traceback__.tb_lineno))


    def check_file_exists(self):
        """確認專案各項資料處理進度
        """
        try:
            data = request.get_json()
            res = list()

            """
                0: 可執行點擊
                1: 已執行不能點擊
                9: 未執行不能點擊
            """

            for project_no, project_name in zip(data['project_no'], data['project_name']):

                # check project是否存在於lists_data
                aProject_data = self.oDB.select_single('lists_data_project', "project_no = '%s'" % project_no)

                tmp = {}
                tmp['project_no'] = project_no
                tmp['project_name'] = project_name
                tmp['firstTag'] = 0
                tmp['secondTag'] = 0
                tmp['scoreData'] = 9
                tmp['nameTxt'] = 9
                tmp['addrTxt'] = 9
                tmp['lists_data_project_status'] = aProject_data['status']

                # check lists tc
                    # lists_data_tc => project 所有tc status = 2
                aList_tc = self.oDB.select_all('lists_data_tc',"project_tc->>'$.project_no' = '%s'" % project_no)
                if aList_tc:
                    for lists_tc in aList_tc:
                        if lists_tc['status'] != 2:
                            tmp['firstTag'] = 9
                else:
                    tmp['firstTag'] = 9

                # check score tc
                    # lists_data_google_score_tc => datatable 內所有 project tc status = 2
                aScore_tc = self.oDB.select_all('lists_data_google_score_tc', "task_condition->>'$.project_no' = '%s'" % project_no)
                if aScore_tc:
                    for score_tc in aScore_tc:
                        if score_tc['status'] != 2:
                            tmp['secondTag'] = 9
                            break
                else:
                    tmp['secondTag'] = 9

                # 確認 project 狀態
                iProject_status = self.oDB.select_single('lists_data_project', "project_no = '%s'" % project_no)['status']

                # lists_data_project 狀態 3 提供點擊
                if iProject_status == 1:
                    tmp['scoreData'] = 9

                # 確認待匯入主庫資料筆數
                if iProject_status == 3:
                    iCount_data = self.oDB.count_datas('lists_data', 'project_no = %s AND status = 1' % project_no)['total']

                    if iCount_data != 0:
                        tmp['export_datas'] = iCount_data
                    else:
                        tmp['export_datas'] = 'done'

                # 產業資料夾路徑
                sChkPath  = r"D:\\test\\Flask_test\\flask_sql\\各產業資料\\%s" % project_name

                # 1st Tag 檔案
                sChk1stTagFile = sChkPath + r'\\Google店家清單_%s_Tag總表.xlsx' % project_name

                # 2nd Tag 檔案
                sChk2ndTagFile = sChkPath + r'\\Google評分_%s_Tag總表.xlsx' % project_name

                # 店家清單檔案
                sChkScoreData = sChkPath + r'\\Google評分_%s_店家名單資訊.xlsx' % project_name

                # name txt 檔案共有三個, 僅檢查其ㄧ
                sChknameTxtFile = sChkPath + r'\\origin\\%s_Google_List_list_name.txt' % project_name

                # addr txt 檔案
                sChkaddrTxtFile = sChkPath + r'\\%s_Google_List待確認_list_addr.txt' % project_name

                # check first Tag
                if os.path.isfile(sChk1stTagFile):
                    tmp['firstTag'] = 1

                # check second Tag
                if os.path.isfile(sChk2ndTagFile):
                    tmp['secondTag'] = 1

                # check score Data
                if os.path.isfile(sChkScoreData):
                    tmp['scoreData'] = 1
                    # 有 專案excel 後即可產生nameTxt and addrTxt
                    tmp['nameTxt'] = 0
                    tmp['addrTxt'] = 0

                # check nameTxt
                if os.path.isfile(sChknameTxtFile):
                    tmp['nameTxt'] = 1

                # chekc addrTxt
                if os.path.isfile(sChkaddrTxtFile):
                    tmp['addrTxt'] = 1

                res.append(tmp)
            self.res_json = json.dumps(res)
        except Exception as e:
            print("專案各項資料處理進度: %s\nerror line: %s" %
                (e, e.__traceback__.tb_lineno))


    def check_data_status(self):
        """回傳條件任務狀態
        """
        try:
            data = request.get_json()

            res = list()

            for no in data['target_no']:
                aNo = self.oDB.select_single(data['table'], "%s = '%s'" % (data['no_name'], no))

                tmp = {}
                tmp['no'] = no
                tmp['status'] = aNo['status']

                res.append(tmp)

            self.res_json = json.dumps(res)
        except Exception as  e:
            print("回傳條件任務狀態: %s\nerror line:" % (e, e.__traceback__.tb_lineno))
