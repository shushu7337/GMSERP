# !/usr/bin/python
# coding:utf-8

import pymysql


class DB:
    """共用sql
    """
    def connect(self, database):
        db_settings = {
            "host": "****",
            "user": "****",
            "password": "****",
            "db": database,
            "port": 3306,
            "cursorclass": pymysql.cursors.DictCursor,
            "charset": "utf8mb4"
        }

        self.db = pymysql.connect(**db_settings)
        self.cursor = self.db.cursor()


    def insert(self, sTable='', sRow='', sValue=''):
        """新增資料
        Args:
            sTable (str, optional): 資料表名稱. Defaults to ''.
            sRow (str, optional): 欄位名稱. Defaults to ''.
            sValue (str, optional): 值. Defaults to ''.
        """
        try:
            sSql = "INSERT INTO " + sTable + " ("+sRow+") VALUES("+sValue+")"

            self.cursor.execute(sSql)
            self.db.commit()
        except Exception as e:
            print("Insert: %s" % (e))


    def update(self, sTable='', sValue='', sWhere=''):
        """更新資料

        Args:
            sTable (str, optional): 資料表名稱. Defaults to ''.
            sValue (str, optional): 值. Defaults to ''.
            sWhere (str, optional): 更新條件. Defaults to ''.
        """
        try:
            sSql = "UPDATE %s SET %s " % (sTable, sValue)
            if sWhere != '':
                sSql += "WHERE %s" % (sWhere)

            self.cursor.execute(sSql)
            self.db.commit()
        except Exception as e:
            print("Update: %s" % (e))


    def create_list_table(self, table):
        """建立專案清單資料表

        Args:
            table (str): 資料表名稱
        """
        try:
            sSql = "CREATE TABLE IF NOT EXISTS `% s` (`gs_no` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Google地標清單編號', `l_tc_no` INT(11) NOT NULL COMMENT '專案任務條件編號', `l_task_no` INT(11) NOT NULL COMMENT '清單任務編號', `google_list` JSON NOT NULL COMMENT 'Google 地標清單JSON資料\r\n',  `created` DATETIME NOT NULL COMMENT '建立日期', `modified` DATETIME NULL DEFAULT NULL COMMENT '修改日期', `status` TINYINT(1) NULL DEFAULT '0' COMMENT '資料狀態\r\n0 : 未處理\r\n1 : 已被選入lists_data_tc條件中,尚未取得評分\r\n2 : 已取得評分,且評分資料不為空值,待匯入Final lists_data\r\n3 : 已匯入Final lists_data', PRIMARY KEY(`gs_no`) USING BTREE) COLLATE = 'utf8mb4_general_ci' ENGINE = InnoDB ROW_FORMAT = DYNAMIC" % (table)

            self.cursor.execute(sSql)
            self.db.commit()
        except Exception as e:
            print("Create: %s" % (e))


    def create_score_table(self, table):
        """建立專案評分資料表

        Args:
            table (str): 資料表名稱
        """
        try:
            sSql = "CREATE TABLE `%s` (`gs_no` INT(11) NOT NULL DEFAULT '0', `google_result` JSON NOT NULL, `created` DATETIME NOT NULL, `modified` DATETIME NOT NULL, UNIQUE INDEX `g_no` (`gs_no`) USING BTREE ) COLLATE = 'utf8mb4_general_ci' ENGINE = InnoDB ROW_FORMAT = DYNAMIC " % (table)

            self.cursor.execute(sSql)
            self.db.commit()
        except Exception as e:
            print("Create_score_table: %s" % (e))


    def check_table_exists(self, sTable_name):
        """撿查資料表是否存在

        Args:
            sTable_name (string): 資料表名稱
        """
        try:
            sSql = "SHOW TABLES LIKE '%%s%'" % (sTable_name)
            self.cursor.execute(sSql)
            self.db.commit()
            return self.cursor.fetchone()
        except Exception as e:
            print("Check_table_exists: %s" % (e))
        return False


    def select_all(self, sTable, sWhere='', sPos=''):
        """搜尋所有合乎條件資料

        Args:
            sTable ([string]): 搜尋的資料表名稱
            sWhere (str, optional): 搜尋條件語句. Defaults to ''.
            sPos (str, optional): 搜尋位置語句. Defaults to ''.

        Returns:
            [array]: 合乎條件陣列資料
        """
        try:
            sSql = "SELECT * FROM %s" % (sTable)
            if sWhere != '':
                sSql += " WHERE %s " % (sWhere)

            if sPos != '':
                sSql += sPos

            self.cursor.execute(sSql)
            self.db.commit()
            return self.cursor.fetchall()
        except Exception as e:
            print("Select_all: %s" % (e))
        

    def select_single(self, sTable, sWhere='', sPos=''):
        """搜尋單筆條件資料

        Args:
            sTable (str)): 資料表名稱
            sWhere (str, optional): 搜尋條件語句. Defaults to ''.
            sPos (str, optional): 搜尋條件語句. Defaults to ''.

        Returns:
            array: 符合搜尋條件陣列資料
        """
        try:
            sSql = "SELECT * FROM %s" % (sTable)
            if sWhere != '':
                sSql += " WHERE %s " % (sWhere)
            if sPos != '':
                sSql += sPos

            self.cursor.execute(sSql)
            self.db.commit()
            return self.cursor.fetchone()
        except Exception as e:
            print("Select_single: %s\n  sql: %s\n   error: %s" % (e, sSql, e.__traceback__.tb_lineno))


    def select_city_group_info(self):
        try:
            sSql = "SELECT DISTINCT(CG.cg_name), C.c_name FROM city_package AS CP LEFT JOIN city_group AS CG ON CP.cg_no = CG.cg_no LEFT JOIN city AS C ON C.c_no = CP.c_no"

            self.cursor.execute(sSql)
            self.db.commit()
            return self.cursor.fetchall()
        except Exception as e:
            print("Select_city_group_info: %s" % (e))


    def count_datas(self, sTable = '', sWhere='', sPos=''):
        """計算資料筆數

        Args:
            sTable (str, optional): 資料表名稱. Defaults to ''.
            sWhere (str, optional): 搜尋條件語句. Defaults to ''.
            sPos (str, optional): 搜尋條件語句. Defaults to ''.

        Returns:
            int: 資料筆數
        """
        try:
            sSql = "SELECT COUNT(*) AS total FROM %s "%(sTable)
            if sWhere != '':
                sSql += "WHERE %s " % (sWhere)
            if sPos != '':
                sSql += sPos

            self.cursor.execute(sSql)
            self.db.commit()
            return self.cursor.fetchone()
        except Exception as e:
            print("Count_datas: %s"% (e))
