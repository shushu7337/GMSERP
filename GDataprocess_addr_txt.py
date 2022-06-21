# !/usr/bin/python
# coding:utf-8

import base
import openpyxl


"""
    產生地址txt
"""


class Exc:
    # 資料庫連線
    oDB = base.DB()
    oDB.connect("twd_SHU")

    sFile_path = ''


    def __init__(self, sProject_no):
        aProject_data = self.oDB.select_single(
            "lists_data_project", "project_no = %s" % (sProject_no))
        sProject_name = aProject_data['project_name']

        # 讀取 Excel 檔案
        wb = openpyxl.load_workbook(
            r"D:\\test\\Flask_test\\flask_sql\\各產業資料\\%s\\Google評分_%s_店家名單資訊.xlsx" % (sProject_name, sProject_name))
        ws = wb["Google_List待確認"]  # 啟用[sheetname]工作表
        total_datas = []

        for row in ws.iter_rows(min_row=2):
            line = [col.value for col in row if row[3].value == 'v']
            if line != []:
                total_datas.append(line)

        addrdata = []

        for total_data in total_datas:
            New_txt = ""
            New_txt += str(total_data[0])
            New_txt += " >>> "
            New_txt += total_data[2]
            New_txt += "\n"
            addrdata.append(New_txt)


        txt_filename = "%s_%s_list_addr.txt" % (
            sProject_name, "Google_List待確認")  # 寫入txt filename

        # 寫入txt flie path
        self.sFile_path = r"D:\\test\\Flask_test\\flask_sql\\各產業資料\\%s\\%s" % (sProject_name, txt_filename)

        with open(self.sFile_path, "w", encoding="utf-8") as f:
            f.write(" 編號		店家名稱")
            f.write("\n")
            for k in addrdata:
                f.writelines(k)

if __name__ == "__main__":
    Exc()
