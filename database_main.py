# !/usr/bin/python
# coding:utf-8

import pymysql
import sys


class oDB:
    """
    #####################
    # twd_source (main) #
    #####################
    """

    def __init__(self):
        db_settings = {
            "host": "****",
            "user": "****",
            "password": "****",
            "db": "twd_source",
            "port": 3306,
            "cursorclass": pymysql.cursors.DictCursor,
            "charset": "utf8mb4"
        }
        self.db = pymysql.connect(**db_settings)
        self.cursor = self.db.cursor()


    def count_items_data(self, sDivision_no, sWhere='', sPostFix=''):
        """count main database.items_data data

        Args:
            sDivision_no (string): 科別字串組
            sWhere (str, optional): 搜尋條件語句. Defaults to ''.
            sPostFix (str, optional): 搜尋條件語句. Defaults to ''.

        Returns:
            [int]: 資料筆數
        """
        try:
            sSql = "SELECT COUNT(DISTINCT ID.co_id) AS total FROM items_data AS ID LEFT JOIN seo_company_division_rel AS SC ON ID.co_id = SC.co_id "

            if sWhere != '':
                sSql += "WHERE SC.division_no IN(%s) AND " % (sDivision_no) + sWhere
            else:
                sSql += "WHERE SC.division_no IN(%s) AND " % (sDivision_no)
            if sPostFix != '':
                sSql += sPostFix
            
            self.cursor.execute(sSql)
            self.db.commit()
            result = self.cursor.fetchone()['total']
        except Exception:
            print(sys.exc_info())
        return result

    def check_co_id(self, sDivision_no, sCo_id):
        """取得指定co_id資料

        Args:
            sDivision_no (str): 
            sCo_id (str): co_id

        Returns:
            [array]: 符合搜尋條件陣列資料
        """
        try:
            sSql = "SELECT * FROM items_data AS ID LEFT JOIN seo_company_division_rel AS SC ON ID.co_id = SC.co_id WHERE SC.division_no IN(%s) AND ID.co_id = %s" % (sDivision_no, sCo_id)

            self.cursor.execute(sSql)
            self.db.commit()
            result = self.cursor.fetchone()
        except Exception as e:
            print("check_co_id: %s" % (e))

        return result

    def find_data(self, sDivision_no, sWhere='', sPostFix=''):
        """取得符合條件的主庫資料

        Args:
            sDivision_no (str]): 科別字串組
            sWhere (str, optional): 搜尋條件語句. Defaults to ''.
            sPostFix (str, optional): 搜尋條件語句. Defaults to ''.

        Returns:
            [array]: 符合搜尋條件陣列資料
        """
        try:
            sSql = "SELECT DISTINCT(ID.co_id), ID.co_info ->>'$.name' AS name, ID.co_info ->>'$.google_url' AS url, ID.co_info ->>'$.co_addr' as addr FROM items_data AS ID LEFT JOIN seo_company_division_rel AS SC ON ID.co_id = SC.co_id "

            if sWhere != '':
                sSql += "WHERE SC.division_no IN(%s) AND " % (sDivision_no) + sWhere
            else:
                sSql += "WHERE SC.division_no IN(%s) " % (sDivision_no)
            if sPostFix != '':
                sSql += sPostFix
            else:
                sSql += ' ORDER BY RAND() LIMIT 1'

            self.cursor.execute(sSql)
            self.db.commit()
            result = self.cursor.fetchone()
            return result
        except Exception:
            print(sys.exc_info())
        return False


    def update(self, sTable='', sValue='', sWhere=''):
        """更新資料

        Args:
            sTable (str, optional): 資料表名稱. Defaults to ''.
            sValue (str, optional): 欄位名稱. Defaults to ''.
            sWhere (str), optional): 值. Defaults to ''.
        """
        try:
            sSql = "UPDATE %s SET %s " % (sTable, sValue)
            if sWhere != '':
                sSql += "WHERE %s" % (sWhere)

            self.cursor.execute(sSql)
            self.db.commit()
        except Exception as e:
            print("Update: %s" % (e))


    def find_google_score(self, sDivision_no, sWhere='', sPostFix=''):
        """取得

        Args:
            sDivision_no (str): 科別字串組
            sWhere (str, optional): 搜尋條件語句. Defaults to ''.
            sPostFix (str, optional): 搜尋條件語句. Defaults to ''.

        Returns:
            [array]: 多筆陣列資料
        """
        try:
            sSql = "SELECT IDGS.* FROM items_data_google_score AS IDGS LEFT JOIN seo_company_division_rel AS SC ON IDGS.co_id = SC.co_id "
            if sWhere != '':
                sSql += "WHERE SC.division_no IN(%s) AND " % (sDivision_no) + sWhere
            else:
                sSql += "WHERE SC.division_no IN(%s) " % (sDivision_no)
            if sPostFix != '':
                sSql += sPostFix

            self.cursor.execute(sSql)
            self.db.commit()
            result = self.cursor.fetchone()
        except Exception:
            print(sys.exc_info())
        return result


    def search_google_score(self, sDivision_no, sWhere='', sPostFix=''):
        """取得所有評分資料

        Args:
            sDivision_no (str): 科別字串組
            sWhere (str, optional): 搜尋條件語句. Defaults to ''.
            sPostFix (str, optional): 搜尋條件語句. Defaults to ''.

        Returns:
            [array]]: 多筆陣列資料
        """
        try:
            sSql = "SELECT IDGS.co_id, IDGS.google_result->>'$.url' AS url, IDGS.google_result->>'$.title' AS name FROM items_data_google_score  AS IDGS LEFT JOIN seo_company_division_rel AS SC ON IDGS.co_id = SC.co_id LEFT JOIN items_data AS ID ON SC.co_id = ID.co_id "

            if sWhere != '':
                sSql += "WHERE SC.division_no IN(%s) AND " % (sDivision_no) + sWhere
            else:
                sSql += "WHERE SC.division_no IN(%s) " % (sDivision_no)
            if sPostFix != '':
                sSql += sPostFix
            else:
                sSql += "ORDER BY RAND() LIMIT 1"
            self.cursor.execute(sSql)
            self.db.commit()

            result = self.cursor.fetchone()
        except Exception as e:
            print("search_google_score: %s" % (e))
        return result


    def count_google_score(self, sDivision_no, sWhere='', sPostFix=''):
        """計算主庫google_score資料筆數

        Args:
            sDivision_no (string): 科別字串組
            sWhere (str, optional): 搜尋條件語句. Defaults to ''.
            sPostFix (str, optional): 搜尋條件語句. Defaults to ''.

        Returns:
            [int]: 資料筆數
        """
        try:
            sSql = "SELECT COUNT(DISTINCT IDGS.co_id) AS total FROM items_data_google_score AS IDGS LEFT JOIN seo_company_division_rel AS SC ON IDGS.co_id = SC.co_id LEFT JOIN items_data AS ID ON ID.co_id = IDGS.co_id "

            if sWhere != '':
                sSql += "WHERE SC.division_no IN(%s) AND " % (sDivision_no) + sWhere
            else:
                sSql += "WHERE SC.division_no IN(%s) AND " % (sDivision_no)
            if sPostFix != '':
                sSql += sPostFix

            self.cursor.execute(sSql)
            self.db.commit()
            
            return self.cursor.fetchone()['total']
        except Exception as e:
            print("count_google_score: %s" % (e))
        return False
