#! /usr/bin/python
#! coding:utf-8

from flask import Flask, render_template, request, redirect, flash, session, url_for

import base
import math
import pymysql
import sys


class Industry():
    """產業
    """

    oDB = base.DB()
    oDB.connect("twd_SHU")


    def __init__(self, methods):
        try:
            page = request.args.get('page', '1')
            page = int(page)
            search_action = request.args.get('action', '')
            sort = request.args.get('sort', 'ASC')
            order = request.args.get('order', 'industry_no')
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
                self.add(methods)
            else:
                self.Show(methods, aFunc_args)
        except AttributeError as e:
            print("error: %s" % (e))
            self.app = redirect("/Industry?page=1")
            flash('__init__ get value error')
        except IndexError as e:
            print("error: %s" % (e))
        except Exception as e:
            flash('__init__程序異常')
            self.app = redirect("/Industry?page=1")
            print("error: %s" % (e))

    def Show(self, methods, aFunc_args):
        """顯示清單資料

        Args:
            methods (str): _description_
            aFunc_args (): _description_
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
                aIndustrys = self.oDB.select_all("industry", '1=1', 'ORDER BY %s %s LIMIT %s, %s' % (aFunc_args['order'], aFunc_args['sort'], str(pagestart), str(aFunc_args['showcolnum'])))
                aIndustrys_count = self.oDB.count_datas("industry")
            elif (aFunc_args['search_options'] != 'All'):
                aIndustrys = self.oDB.select_all("industry", "%s LIKE '%s'" % (aFunc_args['search_options'], "%" + str(aFunc_args['search_key']) + "%"), "ORDER BY %s %s LIMIT %s, %s" % (aFunc_args['order'], aFunc_args['sort'], str(pagestart), str(aFunc_args['showcolnum'])))

                aIndustrys_count = self.oDB.count_datas('industry', "%s = '%s'" % (aFunc_args['search_options'], str(aFunc_args['search_key'])))
            else:
                aIndustrys = self.oDB.select_all(
                    "industry", f"{aFunc_args['search_options']} LIKE '%{aFunc_args['search_key']}%' ORDER BY {aFunc_args['order']} {aFunc_args['sort']} LIMIT {str(pagestart)}, {str(aFunc_args['showcolnum'])}")

                aIndustrys_count = self.oDB.count_datas(
                    'industry', f"{aFunc_args['search_options']} LIKE '%{str(aFunc_args['search_key'])}%'")

            iCount_datas = int(aIndustrys_count['total'])
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
                self.app = render_template('industry_list.html',
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
                            aIndustrys=aIndustrys,
                            colstart=(int(pagestart) + 1),
                            sfunc='Industry')
            elif methods == 'GET' and aFunc_args['func'] == 'dosort':
                self.app = redirect("/Industry?page=%s&items=%s&order=%s&sort=%s&search=%s&search_key=%s" % (str(iPage), str(
                    aFunc_args['showcolnum']), aFunc_args['order'], aFunc_args['sort'], aFunc_args['search_options'], aFunc_args['search_key']), code=302)
            elif methods == 'POST':
                self.app = redirect("/Industry?page=1&items=%s&order=industry_no&sort=ASC&search=%s&search_key=%s" % (
                    str(aFunc_args['showcolnum']), aFunc_args['search_options'], str(aFunc_args['search_key'])), code=302)
        except ValueError as e:
            self.app = redirect("/Industry?page=1")
        except pymysql.OperationalError:
            print('database error')
        except Exception as e:
            print("Show: %s" % (e))
        except:
            flash('Show error')
            self.app = redirect("/Industry?page=1")


    def add(self, methods):
        """新增/編輯 頁面操作

        Args:
            methods (str): 傳入操作值
        """
        try:
            if methods == 'GET':
                industry_no = request.args.get('industry_no')
                if int(industry_no) == 0:
                    aIndustry = None
                else:
                    aIndustry = self.oDB.select_single('industry', 'industry_no=%s' % (industry_no))

                self.app = render_template(
                    'industry_edit.html', industry_no=int(industry_no), aIndustry=aIndustry)

            elif methods == 'POST':
                industry_no = request.form['industry_no'] if request.form['industry_no'] else ''
                industry_name = request.form['industry_name'] if request.form['industry_name'] else ''
                industry_no = request.form['industry_no'] if request.form['industry_no'] else ''
                status = request.form.getlist("status")[0] if request.form.getlist("status") else 0

                # 新增
                if industry_no == '':
                    check_duplicate = self.oDB.select_single(
                        'industry', "industry_name = '%s'" % (industry_name))
                    if check_duplicate == None:
                        self.oDB.insert('industry', "industry_name, status, created, modified", (
                            "'%s', %s, NOW(), NOW()" % (industry_name, status)))
                    else:
                        flash('%s 已存在' % (industry_name))
                        sys.exit(1)
                else:
                    self.oDB.update('industry', "industry_name = '%s', industry_no = %s, status = %s, created = NOW(), modified = NOW()" % (industry_name, industry_no, status), "industry_no = %s" % (industry_no))
                self.app = redirect("/Industry?page=1")
        except:
            flash('無法新增')
            self.app = redirect("/Industry?page=1")
