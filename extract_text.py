from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import xlsxwriter
import pandas as pd
import numpy as np
from random import randint
import time
import os
from bs4 import BeautifulSoup
import winsound
from datetime import datetime

frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second

from lxml import etree, html
htmlparser = etree.HTMLParser(encoding='utf-8')
proj_url = 'https://handasa.ramat-gan.muni.il/newengine/Pages/request2.aspx#request/'
table_elements_list = ['מספר הבקשה', 'כתובת', 'תאריך הגשה', 'מהות הבקשה', 'מספר תיק בניין', 'סוג הבקשה', 'שימוש עיקרי',
                       'תיאור הבקשה', 'מטפל', 'מספר היתר', 'תאריך הפקת היתר', 'שטח עיקרי', 'שטח שירות',
                       'סך מספר יחידות דיור המבוקשות', 'מבקש', 'בעל הנכס', 'עורך', 'מהנדס', 'מתנגד', 'מספר גוש',
                       'מספר חלקה', 'מספר מגרש', 'יעוד']
baaley_inyan = ['מבקש', 'בעל הנכס', 'עורך', 'מהנדס', 'מתנגד']

eruim_list = ['מסירת היתר בניה !', 'בהכנה לוועדה', 'תכנית (גרמושקה) הוחזרה לרישוי', 'פתיחת תיק במערכת השבחה', 'הועבר להשבחה',
              'שולם היטל השבחה', 'הוכנה שומת השבחה', 'הפקת נוסח פרסום לפי סעיף 149 - הקלה',
              'הפקת נוסח פרסום-תמ"א 38 / הקלה', 'פתיחת תיק', 'הוגשה תכנית מתוקנת', 'ישיבת ועדת משנה']

year_dict = {'2016': 512,
             '2017': 538,
             '2018': 486,
             '2019': 487,
             '2020': 317}


def textOrInnerHtmlByXpath(browser, xpath):
    text = browser.find_element_by_xpath(xpath).text
    if text:
        return text
    else:
        return browser.find_element_by_xpath(xpath).get_attribute('innerHTML')


def main():
    download_path = os.getcwd()
    print("download_path:", download_path)
    # open browser:
    # options = webdriver.ChromeOptions()
    # options.add_experimental_option("prefs", {
    #     "download.default_directory": download_path,
    #     "download.prompt_for_download": False,
    #     "download.directory_upgrade": True,
    #     "safebrowsing.enabled": True})
    # path_to_chromedriver = os.path.join(os.getcwd(), "chromedriver.exe")
    parse_element_list = ['//*[@id="info-main"]/table', '//*[@id="table-baaley-inyan"]',
                          '//*[@id="table-gushim-helkot"]', '//*[@id="table-events"]']
    dfToExcel = pd.DataFrame(columns=table_elements_list + eruim_list)


    # soup = BeautifulSoup(html_content)
    log_file_path = 'log.txt'
    for year in year_dict.keys():
        for file in [f for f in os.listdir('{}/'.format(year)) if f.endswith("html")]:
            print("file: ", file)
            try:
                html_content = open('{}/{}'.format(year, file), 'r', encoding='utf8').read()
            except UnicodeDecodeError:
                print("cant read file")
            tree = etree.parse('{}/{}'.format(year, file), htmlparser)
            row_list = []
            head_xpath_list = ['//*[@id="result-title-div-id"]/div[1]/div[2]',
                               '//*[@id="result-title-div-id"]/div[2]/div[2]',
                               '//*[@id="result-title-div-id"]/div[3]/div[2]',
                               '//*[@id="mahut"]']
            for n, xpath in enumerate(head_xpath_list):
                try:
                    if n == 3:
                        txt = ''
                        for decendent in tree.xpath('//*[@id="mahut"]')[0].iterdescendants():
                            txt += decendent.text.strip()
                        row_list.append(txt)
                    else:
                        row_list.append(tree.xpath(xpath)[0].text)

                except Exception as e:
                    with open(log_file_path, 'a') as f:
                        f.write('{} - {} - {}'.format(year, file, xpath))
                    winsound.Beep(frequency-1000, duration)
                    # time.sleep(1)
                    # winsound.Beep(frequency, duration)
                    # time.sleep(1)
                    # winsound.Beep(frequency, duration)
                    # time.sleep(1)
                    # print(e)
                    # # html_table = tree.xpath(xpath).getparent()  # .get_attribute("outerHTML")
                    # # print(html.tostring(html_table))
                    # print(html_content)
                    # answer = input("shuld we continue? (y/n)")
                    # if answer == 'y':
                    #     continue
                    # else:
                    #     break

            for num, elem in enumerate(parse_element_list):
                try:
                    html_table = tree.xpath(elem)[0]  # .get_attribute("outerHTML")
                    # print(html.tostring(html_table))
                    # with open('table.txt', 'w') as f:
                    #     f.write(html_table)
                    df = pd.read_html(html.tostring(html_table))[0]
                    if num == 0:
                        # df = df[df[0] != 'קישור לאתר הגיאוגרפי']
                        df = df[~df[0].isin(['קישור לאתר הגיאוגרפי', 'מספר הבקשה ברישוי זמין'])]
                        # print(df)
                        # print(list(df[1]))
                        row_list = row_list + list(df[1])
                    elif num == 1:
                        # print(df)
                        df = df[~df['סוג בעל עניין'].isin(['איש קשר', 'בודק בקשה'])]
                        # print(df)
                        df = df.drop_duplicates(subset='סוג בעל עניין', keep="first")
                        # print(df)
                        for baal in baaley_inyan:
                            try:
                                indx = list(df['סוג בעל עניין']).index(baal)
                                row_list.append(list(df['שם בעל עניין'])[indx])
                            except:
                                row_list.append('')
                        # row_list = row_list + list(df['שם בעל עניין'])
                    elif num == 2:
                        # print(df['מספר גוש'])
                        row_list.append(df['מספר גוש'][0])
                        row_list.append(df['מספר חלקה'][0])
                        row_list.append(df['מספר מגרש'][0])
                        row_list.append(df['יעוד'][0])
                        # for val in df.loc[0, :].values.tolist()[:4]:
                        #     print(val)
                        #     row_list.append(val)
                    elif num == 3:
                        # print(df)
                        existing_eruim = df['תיאור אירוע']
                        erua_dict = dict(zip(existing_eruim, df['תאריך אירוע']))
                        # print(erua_dict.keys())
                        erou_row = []
                        for key in eruim_list:
                            if key in erua_dict.keys():
                                erou_row.append(erua_dict[key])
                                # print("found erua: ", key)
                            else:
                                erou_row.append('')
                        row_list = row_list + erou_row

                except NoSuchElementException:
                    result = tree.xpath('//*[@id="MainContainerHandasa"]/div')[0].text
                    print(result)
                    break
                except Exception as e:
                    with open(log_file_path, 'a') as f:
                        f.write('{} - {} - {}'.format(year, file, elem))
                    winsound.Beep(frequency, duration)

            to_append = row_list
            df_length = len(dfToExcel)
            dfToExcel.loc[df_length] = to_append
    file_date = str(datetime.today().date())
    writer = pd.ExcelWriter('ramat_gan_{}.xlsx'.format(file_date), engine='xlsxwriter')
    dfToExcel = dfToExcel.replace('', np.nan)
    dfToExcel['תאריך הגשה'] = pd.to_datetime(dfToExcel['תאריך הגשה'], format='%d/%m/%Y')
    dfToExcel['מסירת היתר בניה !'] = pd.to_datetime(dfToExcel['מסירת היתר בניה !'], format='%d/%m/%Y')
    dfToExcel['בהכנה לוועדה'] = pd.to_datetime(dfToExcel['בהכנה לוועדה'], format='%d/%m/%Y')
    dfToExcel['תכנית (גרמושקה) הוחזרה לרישוי'] = pd.to_datetime(dfToExcel['תכנית (גרמושקה) הוחזרה לרישוי'], format='%d/%m/%Y')
    dfToExcel['פתיחת תיק במערכת השבחה'] = pd.to_datetime(dfToExcel['פתיחת תיק במערכת השבחה'], format='%d/%m/%Y')
    dfToExcel['הועבר להשבחה'] = pd.to_datetime(dfToExcel['הועבר להשבחה'], format='%d/%m/%Y')
    dfToExcel['שולם היטל השבחה'] = pd.to_datetime(dfToExcel['שולם היטל השבחה'], format='%d/%m/%Y')
    dfToExcel['הוכנה שומת השבחה'] = pd.to_datetime(dfToExcel['הוכנה שומת השבחה'], format='%d/%m/%Y')
    dfToExcel['הפקת נוסח פרסום לפי סעיף 149 - הקלה'] = pd.to_datetime(dfToExcel['הפקת נוסח פרסום לפי סעיף 149 - הקלה'], format='%d/%m/%Y')
    dfToExcel['הפקת נוסח פרסום-תמ"א 38 / הקלה'] = pd.to_datetime(dfToExcel['הפקת נוסח פרסום-תמ"א 38 / הקלה'], format='%d/%m/%Y')
    dfToExcel['פתיחת תיק'] = pd.to_datetime(dfToExcel['פתיחת תיק'], format='%d/%m/%Y')
    dfToExcel['הוגשה תכנית מתוקנת'] = pd.to_datetime(dfToExcel['הוגשה תכנית מתוקנת'], format='%d/%m/%Y')
    dfToExcel['ישיבת ועדת משנה'] = pd.to_datetime(dfToExcel['ישיבת ועדת משנה'], format='%d/%m/%Y')

    dfToExcel.to_excel(writer, sheet_name='Sheet1')
    writer.save()

main()
