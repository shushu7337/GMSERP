#! /usr/bin/python
#! coding:utf-8

from flask import Flask, render_template, request, redirect, flash, session, url_for

import base
import math
import pymysql


class ListsTask():
    """地標清單任務
    """

    oDB = base.DB()
    oDB.connect("twd_SHU")


    def __init__(self, methods):
        try:
            page = request.args.get('page', '1')
            page = int(page)
            search_action = request.args.get('action', '')
            sort = request.args.get('sort', 'ASC')
            order = request.args.get('order', 'l_task_no')
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
            else:
                self.Show(methods, aFunc_args)
        except AttributeError as e:
            print("error: %s" % (e))
            self.app = redirect("/ListsTask?page=1")
            flash('__init__ get value error')
        except IndexError as e:
            print("error: %s" % (e))
        except Exception as e:
            flash('__init__程序異常')
            self.app = redirect("/ListsTask?page=1")
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
                aListsTasks = self.oDB.select_all("lists_task", '1=1', 'ORDER BY %s %s LIMIT %s, %s' % (aFunc_args['order'], aFunc_args['sort'], str(pagestart), str(aFunc_args['showcolnum'])))
                aListsTasks_count = self.oDB.count_datas("lists_task")
            elif (aFunc_args['search_options'] != 'All'):
                aListsTasks = self.oDB.select_all("lists_task", "%s LIKE '%s'" % (aFunc_args['search_options'], "$" + str(
                    aFunc_args['search_key']) + "%"), "ORDER BY %s %s LIMIT %s, %s" % (aFunc_args['order'], aFunc_args['sort'], str(pagestart), str(aFunc_args['showcolnum'])))

                aListsTasks_count = self.oDB.count_datas("lists_task", "%s = '%s'" % (aFunc_args['search_options'], str(aFunc_args['search_key'])))
            else:
                aListsTasks = self.oDB.select_all(
                    "lists_task", f"{aFunc_args['search_options']} LIKE '%{aFunc_args['search_key']}%' ORDER BY {aFunc_args['order']} {aFunc_args['sort']} LIMIT {str(pagestart)}, {str(aFunc_args['showcolnum'])}")

                aListsTasks_count = self.oDB.count_datas(
                    "lists_task", f"{aFunc_args['search_options']} LIKE '%{str(aFunc_args['search_key'])}%'")

            iCount_datas = int(aListsTasks_count['total'])
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
                self.app = render_template('lists_task_list.html',
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
                            aListsTasks=aListsTasks,
                            colstart=(int(pagestart) + 1), sfunc='ListsTask')

            elif methods == 'GET' and aFunc_args['func'] == 'dosort':
                self.app = redirect("/ListsTask?page=%s&items=%s&order=%s&sort=%s&search=%s&search_key=%s" % (str(iPage), str(
                    aFunc_args['showcolnum']), aFunc_args['order'], aFunc_args['sort'], aFunc_args['search_options'], aFunc_args['search_key']), code=302)
            elif methods == 'POST':
                self.app = redirect("/ListsTask?page=1&items=%s&order=l_task_no&sort=ASC&search=%s&search_key=%s" % (
                    str(aFunc_args['showcolnum']), aFunc_args['search_options'], str(aFunc_args['search_key'])), code=302)

        except ValueError as e:
            self.app = redirect("/ListsTask?page=1")
        except pymysql.OperationalError:
            print('database error')
        except Exception as e:
            print("Show: %s" % (e))
        except:
            flash('Show error')
            self.app = redirect("/ListsTask?page=1")
