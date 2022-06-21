# !/usr/bin/python
# coding:utf-8

import pymysql
import sys


class oDB:
    """
    ########################################
    # twd_googlelist (Google地標清單資料庫) #
    ########################################
    """

    def __init__(self):
        """db connect setting
        """
        db_settings = {
            "host": "****",
            "user": "****",
            "password": "****",
            "db": "twd_SHU",
            "port": 3306,
            "cursorclass": pymysql.cursors.DictCursor,
            "charset": "utf8mb4"
        }
        self.db = pymysql.connect(**db_settings)
        self.cursor = self.db.cursor()


    def count_lists_data(self, sTable='', sWhere='', sPostFix=''):
        """計算 lists_data 待(新增/更新)資料比數
        Args:
            sWhere (str, optional): Sql條件語句. Defaults to ''.
            sPostFix (str, optional): Sql條件語句. Defaults to ''.
        Returns:
            [array]: Sql回傳筆數資料
        """
        try:
            sSql = "SELECT COUNT(*) AS total FROM %s " % (sTable)

            if sWhere != '':
                sSql += "WHERE " + sWhere
            else:
                sSql += "WHERE "
            if sPostFix != '':
                sSql += sPostFix

            self.cursor.execute(sSql)
            self.db.commit()
            result = self.cursor.fetchone()['total']
        except Exception:
            print(sys.exc_info())
        return result


    def check_lists_data(self, sTable='', sWhere='', sPosFix=''):
        """檢查重複資料
        Args:
            g_no ([int]]): Google清單資料流水號

        Returns:
            [array]: Sql回傳資料
        """
        try:
            sSql = "SELECT * FROM lists_data_%s " % (sTable)

            if sWhere:
                sSql += "WHERE %s" % (sWhere)
            if sPosFix:
                sSql += sPosFix

            self.cursor.execute(sSql)
            self.db.commit()
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print("check_lists_data: %s" % (e))


    def find_google_data(self, sTable='', sWhere='', sPostFix=''):
        """依features選擇,取得單筆lists_data資料
        Args:
            features (str, optional): 新增/更新,功能選擇. Defaults to ''.
            sWhere (str, optional): Sql條件語句. Defaults to ''.
            sPostFix (str, optional): Sql條件語句. Defaults to ''.

        Returns:
            [array]: Sql資料
        """
        try:
            sSql = "SELECT gs_no, google_list->>'$.name' AS name, google_list->>'$.data_code' AS data_code, google_list->>'$.url' AS url , google_list->>'$.tag' AS tag FROM %s " % (sTable)

            if sWhere != '':
                sSql += "WHERE " + sWhere

            if sPostFix != '':
                sSql += sPostFix
            else:
                sSql += ' ORDER BY RAND() LIMIT 1'

            self.cursor.execute(sSql)
            self.db.commit()
            result = self.cursor.fetchone()
        except Exception:
            print(sys.exc_info())
        return result


    def find_non_google_data(self, sTable='', sWhere='', sPostFix=''):
        """依功能選擇,取得單筆lists_data資料
        Args:
            sWhere (str, optional): Sql條件語句. Defaults to ''.
            sPostFix (str, optional): Sql條件語句. Defaults to ''.

        Returns:
            [array]: Sql資料
        """
        try:
            sSql = "SELECT LD.g_no, LD.google_list->>'$.name' AS name, LD.google_list->>'$.data_code' AS data_code, LD.google_list->>'$.url' AS url , LD.google_list->>'$.tag' AS tag FROM lists_data_%s AS LD LEFT JOIN lists_data_google_score_%s AS LDGS ON LD.g_no = LDGS.g_no " % (sTable)

            if sWhere != '':
                sSql += "WHERE LD.status = 2 AND " + sWhere
            else:
                sSql += "WHERE LD.status = 2"
            if sPostFix != '':
                sSql += sPostFix
            else:
                sSql += ' ORDER BY RAND() LIMIT 1'

            self.cursor.execute(sSql)
            self.db.commit()
            result = self.cursor.fetchone()
        except Exception:
            print(sys.exc_info())
        return result


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


    def insert(self, sTable='', row='', value=''):
        """新增資料

        Args:
            sTable (str, optional): 資料表名稱. Defaults to ''.
            row (str, optional): 欄位名稱. Defaults to ''.
            value (str, optional): 值. Defaults to ''.
        """
        try:
            sSql = "INSERT INTO " + sTable + " (" + row + ") VALUES ("+value+")"
            self.cursor.execute(sSql)
            self.db.commit()
            # print(self.cursor._executed)
        except Exception:
            print(sys.exc_info())


    def find_google_score(self, sTable='', sWhere='', sPostFix=''):
        """查找 lists_data_google_score
        Args:
            sWhere (str, optional): Sql條件語句. Defaults to ''.
            sPostFix (str, optional): Sql條件語句. Defaults to ''.

        Returns:
            [array]: Sql資料
        """
        try:
            sSql = "SELECT * FROM lists_data_google_score_%s AS LDGS LEFT JOIN lists_data_%s AS LD on LDGS.gs_no = LD.gs_no " % (sTable, sTable)
            if sWhere != '':
                sSql += "WHERE " + sWhere

            if sPostFix != '':
                sSql += sPostFix

            self.cursor.execute(sSql)
            self.db.commit()
            result = self.cursor.fetchone()

        except Exception:
            print(sys.exc_info())
        return result


    def check_google_score(self, sWhere='', sPostFix=''):
        """查找 lists_data_google_score
        Args:
            sWhere (str, optional): Sql條件語句. Defaults to ''.
            sPostFix (str, optional): Sql條件語句. Defaults to ''.

        Returns:
            [array]: Sql資料
        """
        try:

            sSql = "SELECT * FROM lists_data_google_score "
            if sWhere != '':
                sSql += "WHERE " + sWhere

            if sPostFix != '':
                sSql += sPostFix

            self.cursor.execute(sSql)
            self.db.commit()
            result = self.cursor.fetchone()

        except Exception:
            print(sys.exc_info())
        return result


    def search_google_score(self, sTable='', sWhere='', sPostFix=''):
        """取得lists_data_google_score單筆資料
        Args:
            sWhere (str, optional): Sql條件語句. Defaults to ''.
            sPostFix (str, optional): Sql條件語句. Defaults to ''.

        Returns:
            [array]: Sql資料
        """
        try:
            sSql = "SELECT LDGS.gs_no, LDGS.google_result->>'$.data_code' AS data_code, LDGS.google_result->>'$.title' AS name, LDGS.google_result->>'$.url' AS url, LD.google_list->>'$.tag' AS tag FROM lists_data_google_score_%s AS LDGS LEFT JOIN lists_data_%s AS LD ON LD.gs_no = LDGS.gs_no " % (
                sTable, sTable)

            if sWhere != '':
                sSql += "WHERE " + sWhere

            if sPostFix != '':
                sSql += sPostFix
            else:
                sSql += " ORDER BY RAND() LIMIT 1"

            self.cursor.execute(sSql)
            self.db.commit()

            result = self.cursor.fetchone()
        except Exception as e:
            print("search_google_score: %s" % (e))
        return result


    def count_google_score(self, sTable='', sWhere='', sPostFix=''):
        """計算lists_data_google_score資料筆數
        Args:
            sWhere (str, optional): Sql條件語句. Defaults to ''.
            sPostFix (str, optional): Sql條件語句. Defaults to ''.
        Returns:
            [array]: Sql資料
        """
        try:
            sSql = "SELECT COUNT(*) AS total FROM lists_data_google_score_%s AS LDGS LEFT JOIN lists_data_%s AS LD ON LD.gs_no = LDGS.gs_no " % (sTable, sTable)

            if sWhere != '':
                sSql += "WHERE " + sWhere

            if sPostFix != '':
                sSql += sPostFix

            self.cursor.execute(sSql)
            result = self.cursor.fetchone()['total']
            self.db.commit()
            return result
        except Exception as e:
            print("count_google_score: %s" % (e))
            return False


    def select_all(self, sTable, sWhere='', sPos=''):
        """搜尋多筆陣列資料

        Args:
            sTable (string): 搜尋資料表
            sWhere (str, optional): 搜尋條件語句. Defaults to ''.
            sPos (str, optional): 搜尋條件排列語句. Defaults to ''.

        Returns:
            [array]: 資料陣列
        """
        try:
            sSql = "SELECT * FROM %s" % (sTable)
            if sWhere != '':
                sSql += " WHERE %s" % (sWhere)

            if sPos != '':
                sSql += sPos

            self.cursor.execute(sSql)
            self.db.commit()
            return self.cursor.fetchall()
        except Exception as e:
            print("Select_all: %s" % (e))
        return False


    def select_single(self, sTable, sWhere='', sPos=''):
        """搜尋單筆陣列資料

        Args:
            sTable (string): 搜尋資料表
            sWhere (str, optional): 搜尋條件語句. Defaults to ''.
            sPos (str, optional): 搜尋條件排列語句. Defaults to ''.

        Returns:
            [array]: 資料陣列
        """
        try:
            sSql = "SELECT * FROM %s" % (sTable)
            if sWhere != '':
                sSql += " WHERE %s" % (sWhere)

            if sPos != '':
                sSql += sPos

            self.cursor.execute(sSql)
            self.db.commit()
            return self.cursor.fetchone()
        except Exception as e:
            print("Select_single: %s" % (e))
        return False
