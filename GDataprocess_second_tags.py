# !usr/bin/python
# coding:utf-8

import base
import openpyxl


"""
    統計 {取得評分資料} 範圍內縣市Tag數量
"""


class Exc:
    # 資料庫連線
    oDB = base.DB()
    oDB.connect("twd_SHU")
    sFile_path = ''


    def __init__(self, sProject_no):

        aProject_data = self.oDB.select_single("lists_data_project", "project_no = %s " % (sProject_no))

        # 取得專案日期
        sProject_date = aProject_data['s_date'].strftime('%Y%m%d')

        # 取得專案組成名稱
        sProject_table = aProject_data['project_name']+sProject_date

        # 資料路徑名稱
        self.sFile_path = r"D:\\test\\Flask_test\\flask_sql\\各產業資料\\%s\\Google評分_%s_Tag總表.xlsx" % (aProject_data['project_name'], aProject_data['project_name'])

        # 取得已符合(產業&目標Tag評分資料)
        aTotal_score_tags = self.get_tag_total(sProject_table)
        Total_data = []

        for aTotal_tag in aTotal_score_tags:
            New_excel = []
            New_excel.append(aTotal_tag['Tag_Name'])
            New_excel.append(aTotal_tag['Tag_Counts'])

            Total_data.append(New_excel)

        # 寫入 xlsx file
        wb = openpyxl.Workbook()
        Titles = ("Tag_Name", "Tag_Counts")
        sheet = wb.create_sheet("Google_List Tags", 0)
        sheet.append(Titles)
        sheet.column_dimensions["A"].width = 30

        for data in Total_data:
            sheet.append(data)

        wb.save(self.sFile_path)


    def get_tag_total(self, sProject_table):
        """取得tag名稱,與該tag數量並排序

        Args:
            sProject_table (str): lists_data專案資料表

        Returns:
            [array]: tag名稱,tag數量陣列資料
        """
        try:
            sSql = "SELECT LDGS.google_result->>'$.tag' AS Tag_Name, COUNT(*) AS Tag_Counts FROM lists_data_google_score_%s AS LDGS GROUP BY Tag_Name ORDER BY Tag_Counts DESC" % (
                sProject_table)

            self.oDB.cursor.execute(sSql)
            self.oDB.db.commit()
            return self.oDB.cursor.fetchall()
        except Exception as e:
            print("取得tag名稱,與該tag數量並排序: %s" % e)


if __name__ == '__main__':
    oExc = Exc()
