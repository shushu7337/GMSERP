#!/usr/bin/python
# coding:utf-8

from pymysql.converters import escape_string

import base
import collections
import json
import re


"""專案資料匯入lists_data資料,並更改資料狀態
"""


class Exc:
    oDB = base.DB()
    oDB.connect("twd_SHU")


    def __init__(self, sProject_no):

        aProject_data = self.oDB.select_single(
            "lists_data_project", "project_no = %s" % (sProject_no))
        sProject_date = aProject_data['s_date'].strftime('%Y%m%d')
        sProject_table = aProject_data['project_name'] + sProject_date
        aTotal_datas = self.get_import_datas(sProject_table)

        # 取得lists_data專案資料
        for aTotal_data in aTotal_datas:
            aFor_main = collections.OrderedDict()
            aFor_main['name'] = ''
            aFor_main['co_tel'] = ''
            aFor_main['co_addr'] = ''
            aFor_main['google_url'] = ''
            aFor_main['co_details'] = {}
            aFor_main_tag = []

            aGoogle_result = json.loads(aTotal_data['google_result'])
            aGoogle_list = json.loads(aTotal_data['google_list'])

            if ('title' in aGoogle_result.keys()):
                aFor_main['name'] = escape_string(
                    aGoogle_result['title'].strip())
            else:
                aFor_main['name'] = escape_string(aGoogle_list['name'].strip())
            if ('contact' in aGoogle_result.keys()):
                aFor_main['co_tel'] = aGoogle_result['contact']
            if ('location' in aGoogle_result.keys()):
                aFor_main['co_addr'] = escape_string(
                    aGoogle_result['location'].strip().replace("號號", "號"))
            if ('url' in aGoogle_result.keys()):
                aFor_main['google_url'] = escape_string(
                    aGoogle_result['url'].strip())
            else:
                if aGoogle_list['google_url'].find('?authuser'):
                    sTmp_url = aGoogle_list['google_url']
                    coor_end_pos = sTmp_url.find('?authuser')
                    aFor_main['google_url'] = escape_string(
                        sTmp_url[:coor_end_pos:].strip())
                else:
                    aFor_main['google_url'] = escape_string(
                        sTmp_url[:coor_end_pos:].strip())
                aFor_main['google_url'] = aGoogle_list['google_url']

            # 郵遞區號移除
            addr_Regex1 = re.compile(r'^\d\d\d[\u4e00-\u9fa5]+')
            addr_Regex2 = re.compile(r'^\d\d\d\d\d[\u4e00-\u9fa5]+')
            addr_Regex3 = re.compile(r'^\d\d\d\d\d\d[\u4e00-\u9fa5]+')

            addr_3 = addr_Regex3.search(aFor_main['co_addr'])
            if addr_3 is not None:
                aFor_main['co_addr'] = aFor_main['co_addr'][6::]

            addr_2 = addr_Regex2.search(aFor_main['co_addr'])
            if addr_2 is not None:
                aFor_main['co_addr'] = aFor_main['co_addr'][5::]

            addr_1 = addr_Regex1.search(aFor_main['co_addr'])
            if addr_1 is not None:
                aFor_main['co_addr'] = aFor_main['co_addr'][3::]

            # Tag 處理
            sTag1 = aGoogle_list['tag'] if (
                'tag' in aGoogle_list.keys()) else None
            sTag2 = aGoogle_result['tag'] if (
                'tag' in aGoogle_result.keys()) else None

            if sTag1 != sTag2:
                if sTag1 != None:
                    aFor_main_tag.append(sTag1)
                if sTag2 != None:
                    aFor_main_tag.append(sTag2)
            else:
                if sTag1 == None:
                    aFor_main_tag.append(sTag1)
                else:
                    aFor_main_tag.append(sTag2)

            if ('data_code' in aGoogle_result.keys()):
                aFor_main['co_details']['data_code'] = aGoogle_result['data_code']
            aFor_main['co_details']['gs_no'] = aTotal_data['gs_no']
            aFor_main['co_details']['project_table'] = sProject_table

            # 刪除key value 為None
            for i in list(aFor_main):
                if(aFor_main[i] in ({}, [], "")):
                    del aFor_main[i]

            sFor_main = json.dumps(aFor_main, ensure_ascii=False)

            # 新增前檢查for_main 中的 project_no, gs_no 是否已存在    {check item : co_details 中的 project_no, gs_no}
            aCheck_result = self.check_duplicate_data(aProject_data['project_no'], aFor_main['co_details'])

            # 不存在才新增
            if aCheck_result is None:
                self.oDB.insert('lists_data', 'project_no, industry_no, for_main, created, modified', "%s, %s, '%s', NOW(), NOW()" % (aProject_data['project_no'], aProject_data['industry_no'], sFor_main))

                # 取得相對應g_no做存入評分資料的準備
                aLists_data = self.oDB.select_single('lists_data', "for_main->>'$.co_details.gs_no' = '%s' AND for_main->>'$.co_details.data_code' = '%s' AND for_main->>'$.co_details.project_table' = '%s'" % (
                    aFor_main['co_details']['gs_no'], aFor_main['co_details']['data_code'], aFor_main['co_details']['project_table']))
                sScore_data = escape_string(aTotal_data['google_result'])

                # 新增評分資料
                self.oDB.insert('lists_data_google_score', 'g_no, google_result, created, modified', "%s, '%s', NOW(), NOW()" % (aLists_data['g_no'], sScore_data))

            # 修改原專案資料狀態為 3
            self.oDB.update('lists_data_%s' % (sProject_table), 'status = 3, modified = NOW()', 'gs_no = %s' % (aTotal_data['gs_no']))

        # 修改lists_project狀態為 3
        self.oDB.update('lists_data_project', 'status = 3, modified = NOW()', 'project_no = %s' % (sProject_no))


    def check_duplicate_data(self, iProject_no, aCheck_data):
        """檢查重覆資料
        Args:
            iProject_no (int): 專案編號
            aCheck_data (array): 檢查陣列資料
        Returns:
            array: 單筆陣列資料
        """
        sSql = "SELECT * FROM lists_data WHERE project_no = %s AND for_main->>'$.co_details.gs_no' = %s AND for_main->>'$.co_details.project_table' = '%s'" % (iProject_no, aCheck_data['gs_no'], aCheck_data['project_table'])

        self.oDB.cursor.execute(sSql)
        self.oDB.db.commit()
        return self.oDB.cursor.fetchone()


    def get_import_datas(self, sProject_table):
        """取得各專案lists_data資料
        Args:
            sProject_table (string): 欲選擇的資料表
        Returns:
            [array]: 合乎條件的資料條件
        """
        sSql = "SELECT LD.gs_no AS gs_no, LD.google_list AS google_list, LDGS.google_result AS google_result FROM lists_data_%s AS LD LEFT JOIN lists_data_google_score_%s AS LDGS ON LDGS.gs_no = LD.gs_no WHERE LD.status = 2 " % (sProject_table, sProject_table)

        self.oDB.cursor.execute(sSql)
        self.oDB.db.commit()
        return self.oDB.cursor.fetchall()


if __name__ == '__main__':
    oExc = Exc()
