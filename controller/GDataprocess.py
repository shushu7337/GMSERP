#! /usr/bin/python
#! coding:utf-8

from flask import Flask, render_template, request, redirect, flash, session

import base
import math
import os
import pymysql


"""資料剖析
"""


class Dataprocess():
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
            elif search_action != '':
                if search_action == "firstTag":
                    self.firstTag()
                elif search_action == "secondTag":
                    self.secondTag()
                elif search_action == "scoreData":
                    self.scoredata()
                elif search_action == "nameTxt":
                    self.nameTxt()
                elif search_action == "addrTxt":
                    self.addrTxt()
                elif search_action == "readTxt":
                    self.readTxt()
                elif search_action == "import_lists_data":
                    self.import_lists_data()
                elif search_action == "ready_to_item_data":
                    self.ready_to_item_data()
            else:
                self.Show(methods, aFunc_args)
        except AttributeError as e:
            print("error: %s" % (e))
            self.app = redirect("/Dataprocess?page=1")
            flash('__init__ get value error')
        except IndexError as e:
            print("error: %s" % (e))
        except Exception as e:
            flash('__init__程序異常')
            self.app = redirect("/Dataprocess?page=1")
            print("error: %s" % (e))


    def Show(self, methods, aFunc_args):
        try:
            pagestart = (int(aFunc_args['page'] - 1) * int(aFunc_args['showcolnum']))

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
                aProjects = self.oDB.select_all("lists_data_project", "%s LIKE '%s'" % (aFunc_args['search_options'], "%" + str(
                    aFunc_args['search_key']) + "%"), "ORDER BY %s %s LIMIT %s, %s" % (aFunc_args['order'], aFunc_args['sort'], str(pagestart), str(aFunc_args['showcolnum'])))

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
                self.app = render_template('data_process.html',
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
                self.app = redirect("/Dataprocess?page=%s&items=%s&order=%s&sort=%s&search=%s&search_key=%s" % (str(iPage), str(
                    aFunc_args['showcolnum']), aFunc_args['order'], aFunc_args['sort'], aFunc_args['search_options'], aFunc_args['search_key']), code=302)

            elif methods == 'POST':
                self.app = redirect("/Dataprocess?page=1&items=%s&order=project_no&sort=ASC&search=%s&search_key=%s" % (
                    str(aFunc_args['showcolnum']), aFunc_args['search_options'], str(aFunc_args['search_key'])), code=302)

        except ValueError as e:
            self.app = redirect("/Dataprocess?page=1")
        except pymysql.OperationalError:
            print('database error')
        except Exception as e:
            print("Show: %s" % (e))
        except:
            flash('Show error')
            self.app = redirect("/Dataprocess?page=1")


    def firstTag(self):
        """產生1st Tag excel
        """
        try:
            sProject_no = request.args.get('project_no')

            import GDataprocess_first_tags

            oFirst_tags = GDataprocess_first_tags.Exc(sProject_no)
            self.check_dataprocess_file(oFirst_tags.sFile_path, "1st Tag")
            self.app = redirect("/Dataprocess?page=1")
        except Exception as e:
            flash("產生1st Tag錯誤: %s" % e)
            print("產生1st Tag錯誤: %s\nerror line: %s" % (e, e.__traceback__.tb_lineno))
            self.app = redirect("/Dataprocess?page=1")


    def secondTag(self):
        """ 產生 google score Tag excel file
        """
        try:
            sProject_no = request.args.get('project_no')

            import GDataprocess_second_tags
            oSec_tags = GDataprocess_second_tags.Exc(sProject_no)

            self.check_dataprocess_file(oSec_tags.sFile_path, "Sec Tag")
            self.app = redirect("/Dataprocess?page=1")
        except Exception as e:
            print("產生 google score Tag excel file: %s\nerror line: %s" % (e, e.__traceback__.tb_lineno))
            self.app = redirect("/Dataprocess?page=1")


    def scoredata(self):
        """產生指定專案Google店家清單excel資料
        """
        try:
            sProject_no = request.args.get('project_no')

            import GDataprocess_scoredata
            oScore_data = GDataprocess_scoredata.Exc(sProject_no)

            self.check_dataprocess_file(oScore_data.sFile_path, "店家資料")
            self.app = redirect("/Dataprocess?page=1")
        except Exception as e:
            print("產生指定專案Google店家清單excel資料: %s\nerror line: %s" % (e, e.__traceback__.tb_lineno))
            self.app = redirect("/Dataprocess?page=1")


    def nameTxt(self):
        """產生店家名稱txt檔案
        """
        try:
            sProject_no = request.args.get('project_no')

            import GDataprocess_name_txt
            oName_txt = GDataprocess_name_txt.Exc(sProject_no)

            sFile_path = r"D:\\test\\Flask_test\\flask_sql\\各產業資料\\%s\\%s.7z" % (
                oName_txt.sProject_name, oName_txt.sProject_name)

            self.check_dataprocess_file(sFile_path, "Name .txt")
            self.app = redirect("/Dataprocess?page=1")
        except Exception as e:
            print("產生nameTxt: %s" % e)
            self.app = redirect("/Dataprocess?page=1")


    def addrTxt(self):
        """產生店家地址txt檔案
        """
        try:
            sProject_no = request.args.get('project_no')

            import GDataprocess_addr_txt
            oAddr_txt = GDataprocess_addr_txt.Exc(sProject_no)

            self.check_dataprocess_file(oAddr_txt.sFile_path, "Addr txt")
            self.app = redirect("/Dataprocess?page=1")
        except Exception as e:
            print("產生addr_txt: %s" % e)
            self.app = redirect("/Dataprocess?page=1")


    def readTxt(self):
        """根據txt檔來回寫excel檔案,並更新資料庫
        """
        try:
            sProject_no = request.args.get('project_no')

            import GDataprocess_read_txt
            oRead_txt = GDataprocess_read_txt.Exc(sProject_no)

            if oRead_txt:
                flash("讀取txt: %s\n%s" % (oRead_txt.sSuccess_log, oRead_txt.sRemove_log))
            else:
                flash(oRead_txt.sFail_log)

            self.app =redirect("/Dataprocess?page=1")
        except Exception as e:
            print("根據txt檔來回寫excel檔案,並更新資料庫: %s\n line:%s" % (e, e.__traceback__.tb_lineno))


    def import_lists_data(self):
        """專案資料匯入lists_data資料,並更改資料狀態
        """
        try:
            sProject_no = request.args.get('project_no')

            import GDataprocess_import_lists_data
            GDataprocess_import_lists_data.Exc(sProject_no)

            flash("專案資料已匯入lists_data")
            self.app = redirect("/Dataprocess?page=1")
        except Exception as e:
            print("專案資料匯入lists_data資料: %s\nerror line: %s" % (e, e.__traceback__.tb_lineno))
            self.app = redirect("/Dataprocess?page=1")


    def ready_to_item_data(self):
        """已人工審核資料轉換成待匯入主庫狀態
        """
        try:
            sProject_no = request.args.get('project_no')

            self.oDB.update('lists_data', 'status = 2, modified = NOW()', 'project_no = %s AND status = 1' % sProject_no)

            flash('資料庫更新完成')

            try:
                import GDataprocess_scoredata
                GDataprocess_scoredata.Exc(sProject_no)
                
            except Exception as e:
                print("更新excel檔案: %s" % e)
            self.app = redirect("/Dataprocess?page=1")
        except Exception as e:
            print("已人工審核資料轉換成待匯入主庫狀態: %s\nerror line: %s" % (e, e.__traceback__.tb_lineno))
            self.app = redirect("/Dataprocess?page=1")


    def check_dataprocess_file(self, sFile_path, sAction):
        """確認資料處理檔案是否產生
        Args:
            sFile_path (str): 欲檢查的檔案路徑
            sAction (str): 執行項目
        """
        try:
            if os.path.isfile(sFile_path):
                flash("已產生 %s" % sAction)
            else:
                flash("產生%s 發生錯誤" % sAction)
        except Exception as e:
            print("確認資料處理檔案是否產生: %s" % e)
