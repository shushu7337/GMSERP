#!/usr/bin/python
#! coding:utf-8

from flask import Flask, render_template, request, redirect, flash, session, jsonify

import base
import json
import math
import pymysql


class ListsDataTc():
    """地標清單任務條件
    """

    oDB = base.DB()
    oDB.connect("twd_SHU")


    def __init__(self, methods):
        try:
            page = request.args.get('page', '1')
            page = int(page)
            search_action = request.args.get('action', '')
            sort = request.args.get('sort', 'ASC')
            order = request.args.get('order', 'l_tc_no')
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
            elif search_action != '':
                MyFunc = getattr(self, search_action)
                # self.add(methods)
                MyFunc(methods)
            else:
                self.Show(methods, aFunc_args)

        except AttributeError as e:
            print("error: %s" % (e))
            self.app = redirect("/ListsDataTc?page=1")
            flash('__init__ get value error')
        except IndexError as e:
            print("error: %s" % (e))
        except Exception as e:
            flash('__init__程序異常')
            self.app = redirect("/ListsDataTc?page=1")
            print("error: %s" % (e))


    def Show(self, methods, aFunc_args):
        """顯示頁面資料

        Args:
            methods (str)): 頁面操作
            aFunc_args (str)): 函式變數
        """
        try:
            pagestart = (int(aFunc_args['page'] - 1) * int(aFunc_args['showcolnum']))

            if aFunc_args['func'] == 'dosort':
                if aFunc_args['sort'] == 'ASC':
                    aFunc_args['sort'] = 'DESC'
                elif aFunc_args['sort'] == 'DESC':
                    aFunc_args['sort'] = 'ASC'

            if (aFunc_args['search_options'] == 'All') or (aFunc_args['search_key'] == ''):
                aListsDataTc = self.oDB.select_all("lists_data_tc", '1=1', 'ORDER BY %s %s LIMIT %s, %s' % (aFunc_args['order'], aFunc_args['sort'], str(pagestart), str(aFunc_args['showcolnum'])))

                aListsDataTcs_count = self.oDB.count_datas("lists_data_tc")

                aProject = self.oDB.select_all("lists_data_project")
            elif (aFunc_args['search_options'] != 'All'):
                aListsDataTc = self.oDB.select_all("lists_data_tc", "%s LIKE '%s'" % (aFunc_args['search_options'], "%" + str(
                    aFunc_args['search_key']) + "%"), "ORDER BY %s %s LIMIT %s, %s" % (aFunc_args['order'], aFunc_args['sort'], str(pagestart), str(aFunc_args['showcolnum'])))

                aListsDataTcs_count = self.oDB.count_datas('lists_data_tc', "%s = '%s'" % (
                    aFunc_args['search_options'], str(aFunc_args['search_key'])))

                aProject = self.oDB.select_all("lists_data_project")
            else:
                aListsDataTc = self.oDB.select_all(
                    "lists_data_tc", f"{aFunc_args['search_options']} LIKE '%{aFunc_args['search_key']}%' ORDER BY {aFunc_args['order']} {aFunc_args['sort']} LIMIT {str(pagestart)}, {str(aFunc_args['showcolnum'])}")

                aListsDataTcs_count = self.oDB.count_datas(
                    'lists_data_tc', f"{aFunc_args['search_options']} LIKE '%{str(aFunc_args['search_key'])}%'")

                aProject = self.oDB.select_all("lists_data_project")

            # 存放各task_tc所屬project_no
            aProject_no = []
            for ListsDataTc in aListsDataTc:
                aProject_tc = json.loads(ListsDataTc['project_tc'])
                for key, val in aProject_tc.items():
                    if key == 'project_no':
                        aProject_no.append(val)

            iCount_datas = int(aListsDataTcs_count['total'])
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
                self.app = render_template('lists_data_tc.html',
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
                            aListsDataTc=aListsDataTc,
                            aProject_no=aProject_no,
                            colstart=(int(pagestart) + 1),
                            aProject=aProject,
                            zip=zip,
                            sfunc='ListsDataTc')
            elif methods == 'GET' and aFunc_args['func'] == 'dosort':
                self.app = redirect("/ListsDataTc?page=%s&items=%s&order=%s&sort=%s&search=%s&search_key=%s" % (str(iPage), str(
                    aFunc_args['showcolnum']), aFunc_args['order'], aFunc_args['sort'], aFunc_args['search_options'], aFunc_args['search_key']), code=302)
            elif methods == 'POST':
                self.app = redirect("/ListsDataTc?page=1&items=%s&order=l_tc_no&sort=ASC&search=%s&search_key=%s" % (
                    str(aFunc_args['showcolnum']), aFunc_args['search_options'], str(aFunc_args['search_key'])), code=302)

        except pymysql.OperationalError:
            flash('資料庫發生錯誤')
            print('database error')
            self.app = redirect("/ListsDataTc?page=1")
        except Exception as e:
            print("Show: %s\nerror line: %s" % (e, e.__traceback__.tb_lineno))
            self.app = redirect("/ListsDataTc?page=1")


    def add(self, methods):
        try:
            aAllProject = self.oDB.select_all('lists_data_project')
            aAllIndustry = self.oDB.select_all('industry')
            aAllSearchKey = self.oDB.select_all('search_key')
            aAllCity = self.oDB.select_all('city')
            aAllRegion = self.oDB.select_all('region')
            if methods == 'GET':
                l_tc_no = request.args.get('l_tc_no')
                if int(l_tc_no) == 0:
                    aListsDataTc = None
                else:
                    aListsDataTc = self.oDB.select_single(
                        'lists_data_tc', 'l_tc_no=%s' % (l_tc_no))

                self.app = render_template(
                    'lists_data_tc_edit.html', l_tc_no=int(l_tc_no), aListsDataTc=aListsDataTc, aAllProject=aAllProject, aAllIndustry=aAllIndustry, aAllSearchKey=aAllSearchKey, aAllCity=aAllCity, aAllRegion=aAllRegion, code=307)

            elif methods == 'POST':
                sc = {}
                l_tc_no = request.form['l_tc_no'] if request.form['l_tc_no'] else ''
                project_no = request.form['project_no'] if request.form['project_no'] else ''
                industry_no = request.form['industry_no'] if request.form['industry_no'] else ''
                search_key = request.form.getlist(
                    'search_key') if request.form.getlist('search_key') else ''
                city = request.form['c_no'] if request.form['c_no'] else ''
                region = request.form.getlist(
                    'r_no') if request.form.getlist('r_no') else ''
                street = request.form.getlist(
                    's_no') if request.form.getlist('s_no') else None
                status = request.form.getlist(
                    "status")[0] if request.form.getlist("status") else 0

                if 'on' in search_key:
                    search_key.remove('on')
                sSearch_key = ','.join(search_key)

                # 新增
                if l_tc_no == '':
                    sc_location = []
                    # 取得產業
                    aIndustry = self.oDB.select_single(
                        'industry', "industry_no = %s" % (industry_no))
                    sIndustry = aIndustry['industry_name']

                    # 取得搜尋關鍵字
                    aSearch_key = self.oDB.select_all(
                        'search_key', 'sk_no in (%s)' % (sSearch_key))
                    aSearch_key_list = []
                    for sk in aSearch_key:
                        aSearch_key_list.append(sk['sk_name'])

                    # 縣市
                    sCity = self.oDB.select_single(
                        'city', 'c_no = %s' % (city))

                    for i in region:
                        aRegion = self.oDB.select_single(
                            'region', 'c_no = %s AND r_no = %s' % (city, i))
                        if aRegion and street == ['']:
                            temp = {}
                            temp['sc_city'] = sCity['c_name']
                            temp['sc_region'] = aRegion['r_name']
                            sc_location.append(temp)
                        elif aRegion and (street != ['']) and (street != 'all'):
                            for k in street:
                                aStreet = self.oDB.select_single(
                                    "street", "r_no = %s AND s_no = %s " % (i, k))
                                if aStreet:
                                    temp = {}
                                    temp['sc_city'] = sCity['c_name']
                                    temp['sc_region'] = aRegion['r_name']
                                    temp['sc_street'] = aStreet['s_name']
                                    sc_location.append(temp)
                        elif aRegion and (street != ['']) and (street == 'all'):
                            aStreet = self.oDB.select_all(
                                "street", "r_no = %s" % (i))
                            if aStreet:
                                for k in aStreet:
                                    temp = {}
                                    temp['sc_city'] = sCity['c_name']
                                    temp['sc_region'] = aRegion['r_name']
                                    temp['sc_street'] = k['s_name']
                                    sc_location.append(temp)

                    sc['sc_industry'] = sIndustry
                    sc['sc_search_key'] = aSearch_key_list
                    sc['sc_location'] = sc_location
                    sc['project_no'] = project_no
                    sc = json.dumps(sc, ensure_ascii=False)

                    self.oDB.insert('lists_data_tc', "project_tc, created, modified", (
                        "'%s', NOW(), NOW()" % sc))
                else:
                    self.oDB.update('lists_data_tc', "industry_no = %s, status = %s, created = NOW(), modified = NOW()" % (
                        industry_no, status), "l_tc_no = %s" % (l_tc_no))
                self.app = redirect("/ListsDataTc?page=1")
        except Exception as e:
            print("ListsDataTc: %s " % e)
            flash('無法新增')
            self.app = redirect("/ListsDataTc?page=1")


    def generate_task(self, methods):
        """生成清單任務
        Args:
            methods (str)): 取得網頁傳址方式
        """
        try:
            l_tc_no = int(request.args.get('l_tc_no'))

            if l_tc_no == 0:
                aResult_datas = self.oDB.select_all("lists_data_tc", "status = 0")
            else:
                aResult_datas = self.oDB.select_all(
                    "lists_data_tc", "l_tc_no = %s AND status = 0" % l_tc_no)

            for aResult_data in aResult_datas:

                aProject_tc = json.loads(aResult_data['project_tc'])

                for i in aProject_tc['sc_search_key']:
                    for aSC_location in aProject_tc['sc_location']:

                        if "sc_street" in aSC_location.keys():
                            # 有選擇街道
                            sTask_url = "https://www.google.com.tw/maps/search/%s+%s+%s+%s" % (
                                aSC_location['sc_city'], aSC_location['sc_region'], aSC_location['sc_street'], i)
                        elif ("sc_region" in aSC_location.keys()) and ("sc_street" not in aSC_location.keys()):
                            # 僅行政區
                            sTask_url = "https://www.google.com.tw/maps/search/%s+%s+%s" % (
                                aSC_location['sc_city'], aSC_location['sc_region'], i)
                        else:
                            sTask_url = "https://www.google.com.tw/maps/search/%s+%s" % (
                                aSC_location['sc_city'], i)
                        # print("%s %s"%(aResult_data['l_tc_no'], sTask_url))
                        self.oDB.insert("lists_task", "l_tc_no, task_url, created, status", "%s, '%s', NOW(), 0" % (
                            aResult_data['l_tc_no'], sTask_url))
                # 更新任務條件狀態
                self.oDB.update("lists_data_tc", "status = 1, modified = NOW() WHERE l_tc_no = %s" % (
                    aResult_data['l_tc_no']))

            self.app = redirect("/ListsDataTc?page=1")
        except Exception as e:
            print('generate_task: %s\nerror line: %s' % (e, e.__traceback__.tb_lineno))
