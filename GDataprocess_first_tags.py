import base
import openpyxl
import os


"""
    統計範圍內縣市Tag數量
"""


class Exc:
    oDB = base.DB()
    oDB.connect("twd_SHU")
    sFile_path = ''


    def __init__(self, sProject_no):
        try:
            # 取得目標專案資料
            aProject_data = self.oDB.select_single(
                "lists_data_project", "project_no = %s" % sProject_no)

            # 取得目標專案日期
            sProject_date = aProject_data['s_date'].strftime('%Y%m%d')

            # 取得目標專案資料表名稱
            sProject_table = 'lists_data_' + aProject_data['project_name'] + sProject_date

            # 資料夾路徑
            sDir_path = r"D:\\test\\Flask_test\\flask_sql\\各產業資料/%s" % aProject_data['project_name']

            # 資料路徑名稱
            self.sFile_path = r"D:\\test\\Flask_test\\flask_sql\\各產業資料/%s/Google店家清單_%s_Tag總表.xlsx" % (
                aProject_data['project_name'], aProject_data['project_name'])

            # 確認資料夾是否存在
            if not os.path.isdir(sDir_path):
                os.mkdir(sDir_path)

            city_res = self.get_city(sProject_no)
            aCity = []
            for city in city_res:
                aCity.append(city['city'])

            # 取得目標Tag排序資料
            aGet_tag_total = {}
            aGet_tag_total['project_table'] = sProject_table
            aGet_tag_total['project_no'] = aProject_data['project_no']

            aTotal_tags = self.get_tag_total(aGet_tag_total)  # 取得目標Tag排序資料

            # 存放excel資料
            aTotal_data = []

            iCount = 0
            for aTotal_tag in aTotal_tags:
                aData_row = []
                aData_row.append(aTotal_tag['Tag_Name'])
                aData_row.append(aTotal_tag['Tag_Counts'])

                for city in aCity:
                    # get_tag_cities 搜尋變數
                    aGet_tag_cities = {}
                    aGet_tag_cities['project_table'] = sProject_table
                    aGet_tag_cities['industry_no'] = aProject_data['industry_no']
                    aGet_tag_cities['project_no'] = aProject_data['project_no']
                    aGet_tag_cities['city'] = city
                    aGet_tag_cities['tag_name'] = aTotal_tag['Tag_Name']

                    if self.get_tag_cities(aGet_tag_cities):
                        aCity_datas = self.get_tag_cities(
                            aGet_tag_cities)
                        iCity_counts = aCity_datas['Tag_Counts']
                    else:
                        iCity_counts = 0
                    aData_row.append(iCity_counts)

                iCount += 1
                aTotal_data.append(aData_row)

            # 寫入 xlsx file
            wb = openpyxl.Workbook()
            Titles = ("Tag_Name", "Tag_Counts")

            # 逐一增加城市資料
            for city in aCity:
                Titles += (city,)
            sheet = wb.create_sheet('Google_List Tags', 0)

            sheet.append(Titles)
            sheet.column_dimensions["A"].width = 30

            for data in aTotal_data:
                sheet.append(data)

            wb.save(self.sFile_path)
        except Exception as e:
            print("error line: %s" % e.__traceback__.tb_lineno)


    def get_city(self, sProject_no):
        """取得Google地標清單縣市

        Args:
            sProject_no (int): 專案任務編號

        Returns:
            array: 縣市資料
        """
        try:
            sSql = "SELECT DISTINCT(project_tc->>'$.sc_location[0].sc_city') AS city FROM lists_data_tc WHERE project_tc->>'$.project_no' = %s" % (sProject_no)
            
            self.oDB.cursor.execute(sSql)
            self.oDB.db.commit()
            return self.oDB.cursor.fetchall()
        except Exception as e:
            print("取得Google地標清單縣市資料: %s" % e)


    def get_tag_total(self, aArgs):
        """取得Google地標清單 tag總數量並排序
        Args:
            aArgs (dict): 搜尋變數
        Returns:
            array: Tag名稱與統計數量陣列資料
        """
        try:
            sSql = "SELECT LD.google_list->>'$.tag' AS Tag_Name, COUNT(*) AS Tag_Counts FROM %s AS LD LEFT JOIN lists_data_tc AS LDT ON LDT.l_tc_no = LD.l_tc_no LEFT JOIN lists_data_project AS LDP ON LDP.project_no = LDT.project_tc->>'$.project_no' LEFT JOIN industry ON industry.industry_no = LDP.industry_no WHERE LDP.project_no = %s AND LDT.project_tc->>'$.project_no' = %s GROUP BY Tag_Name ORDER BY Tag_Counts DESC" % (
                aArgs['project_table'], aArgs['project_no'], aArgs['project_no'])

            self.oDB.cursor.execute(sSql)
            self.oDB.db.commit()
            return self.oDB.cursor.fetchall()
        except Exception as e:
            print("取得tag總數量並排序: %s" % e)


    def get_tag_cities(self, aArgs):
        """取得Google地標清單含有 某Tag 的縣市總數量
        Args:
            aArgs (dict): 搜尋變數
        Returns:
            array: 縣市含有 某Tag資料
        """
        try:
            sSql = "SELECT LD.google_list->>'$.tag' AS Tag_Name, COUNT(*) AS Tag_Counts FROM %s AS LD LEFT JOIN lists_data_tc AS LDT ON LDT.l_tc_no = LD.l_tc_no LEFT JOIN lists_data_project AS LDP ON LDP.project_no = LDT.project_tc->>'$.project_no' LEFT JOIN industry ON industry.industry_no = LDP.industry_no WHERE industry.industry_no = %s AND LDP.project_no = %s AND LDT.project_tc->>'$.project_no' = %s AND LDT.project_tc->>'$.sc_location[0].sc_city' = '%s' AND LD.google_list->>'$.tag' = '%s' GROUP BY Tag_Name" % (
                aArgs['project_table'], aArgs['industry_no'], aArgs['project_no'], aArgs['project_no'], aArgs['city'], aArgs['tag_name'])

            self.oDB.cursor.execute(sSql)
            self.oDB.db.commit()
            return self.oDB.cursor.fetchone()
        except Exception as e:
            print("取得lists_data含有該tag 的縣市總資料數量: %s" % e)


if __name__ == '__main__':
    oExc = Exc()
