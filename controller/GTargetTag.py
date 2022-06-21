#!/usr/bin/python
#! coding:utf-8

from flask import Flask, render_template, request, redirect, flash, session

import base
import math
import pymysql
import sys


class TargetTag():

    oDB = base.DB()
    oDB.connect("twd_SHU")


    def __init__(self, methods):
        try:
            page = request.args.get('page', '1')
            page = int(page)
            search_action = request.args.get('action', '')
            sort = request.args.get('sort', 'ASC')
            order = request.args.get('order', 'tt_no')
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
            self.app = redirect("/TargetTag?page=1")
            flash('__init__ get value error')
        except IndexError as e:
            print("error: %s" % (e))
        except Exception as e:
            flash('__init__程序異常')
            self.app = redirect("/TargetTag?page=1")
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
                aTargetTags = self.oDB.select_all("target_tag", '1=1', 'ORDER BY %s %s LIMIT %s, %s' % (aFunc_args['order'], aFunc_args['sort'], str(pagestart), str(aFunc_args['showcolnum'])))
                aTargetTags_count = self.oDB.count_datas("target_tag")

            elif (aFunc_args['search_options'] != 'All'):
                aTargetTags = self.oDB.select_all("target_tag", "%s = '%s'" % (aFunc_args['search_options'], "%" + str(
                    aFunc_args['search_key']) + "%"), "ORDER BY %s %s LIMIT %s, %s" % (aFunc_args['order'], aFunc_args['sort'], str(pagestart), str(aFunc_args['showcolnum'])))
                aTargetTags_count = self.oDB.count_datas('target_tag', "%s = '%s'" % (aFunc_args['search_options'], str(aFunc_args['search_key'])))

            else:
                aTargetTags = self.oDB.select_all("target_tag", f"{aFunc_args['search_options']} LIKE '%{aFunc_args['search_key']}%' ORDER BY {aFunc_args['order']} {aFunc_args['sort']} LIMIT {str(pagestart)}, {str(aFunc_args['showcolnum'])}")
                aTargetTags_count = self.oDB.count_datas('target_tag', f"{aFunc_args['search_options']} LIKE '%{str(aFunc_args['search_key'])}%'")

            aIndustry = self.oDB.select_all("industry")
            iCount_datas = int(aTargetTags_count['total'])
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
                self.app = render_template('target_tag_list.html',
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
                            aTargetTags=aTargetTags,
                            colstart=(int(pagestart) + 1),
                            aIndustry=aIndustry,
                            sfunc='TargetTag')

            elif methods == 'GET' and aFunc_args['func'] == 'dosort':
                self.app = redirect("/TargetTag?page=%s&items=%s&order=%s&sort=%s&search=%s&search_key=%s" % (str(iPage), str(
                    aFunc_args['showcolnum']), aFunc_args['order'], aFunc_args['sort'], aFunc_args['search_options'], aFunc_args['search_key']), code=302)
            elif methods == 'POST':
                self.app = redirect("/TargetTag?page=1&items=%s&order=tt_no&sort=ASC&search=%s&search_key=%s" % (
                    str(aFunc_args['showcolnum']), aFunc_args['search_options'], str(aFunc_args['search_key'])), code=302)

        except ValueError as e:
            self.app = redirect("/TargetTag?page=1")
        except pymysql.OperationalError:
            print('database error')
        except Exception as e:
            print("Show: %s" % (e))
        except:
            flash('Show error')
            self.app = redirect("/TargetTag?page=1")


    def add(self, methods):
        """編輯頁面 新增/修改
        Args:
            methods (str)): 取得頁面方式
        """
        try:
            aAllIndustry = self.oDB.select_all('industry')
            if methods == 'GET':
                tt_no = request.args.get('tt_no')
                if int(tt_no) == 0:
                    aTargetTag = None
                else:
                    aTargetTag = self.oDB.select_single(
                        'target_tag', 'tt_no=%s' % (tt_no))

                self.app = render_template(
                    'target_tag_edit.html', tt_no=int(tt_no), aTargetTag=aTargetTag, aAllIndustry=aAllIndustry)

            elif methods == 'POST':
                tt_no = request.form['tt_no'] if request.form['tt_no'] else ''
                aTag_name = request.form.getlist('tag_name[]') if request.form.getlist('tag_name[]') else ''
                aStatus = request.form.getlist('status[]') if request.form.getlist('status[]') else ''
                sIndustry_no = request.form['industry_no'] if request.form['industry_no'] else ''
                
                # 新增
                if tt_no == '':
                    for tag_name, status in zip (aTag_name, aStatus):
                        check_duplicate = self.oDB.select_single(
                            'target_tag', "tag_name = '%s' AND industry_no = %s" % (tag_name, sIndustry_no))

                        aIndustry = self.oDB.select_single(
                            'industry', 'industry_no = %s' % (sIndustry_no))

                        if check_duplicate == None:
                            self.oDB.insert('target_tag', "tag_name, industry_no, status, created, modified", (
                                "'%s', %s, %s, NOW(), NOW()" % (tag_name, sIndustry_no, status)))
                        else:
                            flash('目標Tag %s 已於產業: %s 存在' %
                                (tag_name, aIndustry['industry_name']))
                            sys.exit(1)
                else:
                    self.oDB.update('target_tag', "tag_name = '%s', industry_no = %s, status = %s, created = NOW(), modified = NOW()" % (aTag_name[0], sIndustry_no, aStatus[0]), "tt_no = %s" % (tt_no))

                self.app = redirect("/TargetTag?page=1")
        except:
            flash('發生錯誤')
            self.app = redirect("/TargetTag?page=1")
