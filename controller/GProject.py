#! /usr/bin/python
#! coding:utf-8

from flask import Flask, render_template, request, redirect, flash, session

import base
import math
import os
import pymysql
import sys


class Project():

    oDB = base.DB()
    oDB.connect("twd_SHU")


    def __init__(self, methods):
        try:
            page = request.args.get('page', '1')
            page = int(page)
            search_action = request.args.get('action', '')
            sort = request.args.get('sort', 'ASC')
            order = request.args.get('order', 'project_no')
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
            else:
                self.Show(methods, aFunc_args)

        except AttributeError as e:
            print("error: %s" % (e))
            self.app = redirect("/Project?page=1")
            flash('__init__ get value error')
        except IndexError as e:
            print("error: %s" % (e))
        except Exception as e:
            flash('__init__程序異常')
            self.app = redirect("/Project?page=1")
            print("error: %s" % (e))


    def Show(self, methods, aFunc_args):
        """顯示頁面資料
        Args:
            methods (str)): 頁面操作
            aFunc_args (str)): 函式變數
        """
        try:
            pagestart = (int(aFunc_args['page'] - 1)
                         * int(aFunc_args['showcolnum']))

            if aFunc_args['func'] == 'dosort':
                if aFunc_args['sort'] == 'ASC':
                    aFunc_args['sort'] = 'DESC'
                elif aFunc_args['sort'] == 'DESC':
                    aFunc_args['sort'] = 'ASC'

            if (aFunc_args['search_options'] == 'All') or (aFunc_args['search_key'] == ''):
                aProjects = self.oDB.select_all("lists_data_project", '1=1', 'ORDER BY %s %s LIMIT %s, %s' % (aFunc_args['order'], aFunc_args['sort'], str(pagestart), str(aFunc_args['showcolnum'])))
                aProjects_count = self.oDB.count_datas("lists_data_project")
                aIndustry = self.oDB.select_all('industry')
            elif (aFunc_args['search_options'] != 'All'):
                aProjects = self.oDB.select_all("lists_data_project", "%s LIKE '%s'" % (aFunc_args['search_options'], "%" + str(aFunc_args['search_key']) + "%"), "ORDER BY %s %s LIMIT %s, %s" % (aFunc_args['order'], aFunc_args['sort'], str(pagestart), str(aFunc_args['showcolnum'])))

                aProjects_count = self.oDB.count_datas('lists_data_project', "%s = '%s'" % (aFunc_args['search_options'], str(aFunc_args['search_key'])))
                
                aIndustry = self.oDB.select_all('industry')
            else:
                aProjects = self.oDB.select_all(
                    "lists_data_project", f"{aFunc_args['search_options']} LIKE '%{aFunc_args['search_key']}%' ORDER BY {aFunc_args['order']} {aFunc_args['sort']} LIMIT {str(pagestart)}, {str(aFunc_args['showcolnum'])}")

                aProjects_count = self.oDB.count_datas(
                    'lists_data_project', f"{aFunc_args['search_options']} LIKE '%{str(aFunc_args['search_key'])}%'")
                
                aIndustry = self.oDB.select_all('industry')

            iCount_datas = int(aProjects_count['total'])
            iLastpage = math.ceil(iCount_datas/int(aFunc_args['showcolnum']))
            iPage = int(aFunc_args['page'])  # 頁數

            # 頁碼判斷
            if iLastpage < 10:
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
                self.app = render_template('project_list.html',
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
                            aProjects=aProjects,
                            colstart=(int(pagestart) + 1),
                            aIndustry=aIndustry,
                            sfunc='Project')

            elif methods == 'GET' and aFunc_args['func'] == 'dosort':
                self.app = redirect("/Project?page=%s&items=%s&order=%s&sort=%s&search=%s&search_key=%s" % (str(iPage), str(
                    aFunc_args['showcolnum']), aFunc_args['order'], aFunc_args['sort'], aFunc_args['search_options'], aFunc_args['search_key']), code=302)

            elif methods == 'POST':
                self.app = redirect("/Project?page=1&items=%s&order=project_no&sort=ASC&search=%s&search_key=%s" % (
                    str(aFunc_args['showcolnum']), aFunc_args['search_options'], str(aFunc_args['search_key'])), code=302)

        except ValueError as e:
            self.app = redirect("/Project?page=1")
        except pymysql.OperationalError:
            print('database error')
        except Exception as e:
            print("Show: %s" % (e))
        except:
            flash('Show error')
            self.app = redirect("/Project?page=1")


    def add(self, methods):
        """編輯頁面 新增/修改

        Args:
            methods (str)): 取得頁面方式
        """
        try:
            aAllIndustry = self.oDB.select_all('industry')
            if methods == 'GET':
                project_no = request.args.get('project_no')
                if project_no == 0:
                    aProject = None
                else:
                    aProject = self.oDB.select_single('lists_data_project', 'project_no=%s' % (project_no))

                self.app = render_template(
                    'project_edit.html', project_no=int(project_no), aProject=aProject, aAllIndustry=aAllIndustry)

            elif methods == 'POST':
                project_no = request.form['project_no'] if request.form['project_no'] else ''
                project_name = request.form['project_name'] if request.form['project_name'] else ''
                project_desc = request.form['project_desc'] if request.form['project_desc'] else ''
                industry_no = request.form['industry_no'] if request.form['industry_no'] else ''
                s_date = request.form['s_date'] if request.form['s_date'] else ''
                status = request.form.getlist(
                    "status")[0] if request.form.getlist("status") else 0

                # 新增
                if project_no == '':
                    check_duplicate = self.oDB.select_single('lists_data_project', "project_name = '%s' AND industry_no = %s" % (project_name, industry_no))

                    aIndustry = self.oDB.select_single(
                        'industry', 'industry_no = %s' % (industry_no))

                    if check_duplicate == None:
                        # 建立新專案文件資料夾
                        
                        sFile_path = r'D:\\test\\Flask_test\\flask_sql\\各產業資料\\%s' % project_name

                        if not os.path.isdir(sFile_path):
                            os.mkdir(sFile_path)

                        # 建立新專案用資料表
                        list_table_name = "lists_data_%s%s" % (
                            project_name, (s_date.split()[0]).replace('/', ''))
                        score_table_name = "lists_data_google_score_%s%s" % (project_name, (s_date.split()[0]).replace('/',''))

                        self.oDB.insert('lists_data_project', "project_name, project_desc, industry_no, s_date, status, modified", (
                            "'%s', '%s',%s, '%s', %s, NOW()" % (project_name, project_desc, industry_no, s_date, status)))

                        # 新增list資料表 / score資料表
                        self.oDB.create_list_table(list_table_name)
                        self.oDB.create_score_table(score_table_name)
                    else:
                        flash('專案:%s 已於產業: %s 存在' % (project_name, aIndustry['industry_name']))
                        sys.exit(1)
                else:
                    self.oDB.update('lists_data_project', "project_name = '%s', project_desc = '%s', industry_no = %s, s_date = '%s', status = %s, modified = NOW()" % (
                        project_name, project_desc, industry_no, s_date, status), "project_no = %s" % (project_no))

                self.app = redirect("/Project?page=1")

        except Exception as e:
            flash('無法新增')
            print('error line: %s' % e.__traceback__.tb_lineno)
            self.app = redirect("/Project?page=1")
