from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import xlsxwriter
import pandas as pd
from random import randint, uniform, shuffle
import webbrowser
import time
import os
from test_automation import get_html
from datetime import datetime
import pickle
import csv
aruz7 = 'https://www.inn.co.il/News/Section.aspx/'
proj_url = 'https://handasa.ramat-gan.muni.il/newengine/Pages/request2.aspx#request/'
bniya_ym = 'https://jergisinfohub.jerusalem.muni.il/UI/?SystemID=26400361&processtype=2'
table_elements_list = ['מספר הבקשה', 'כתובת', 'תאריך הגשה', 'מהות הבקשה', 'מספר תיק בניין', 'סוג הבקשה', 'שימוש עיקרי',
                       'תיאור הבקשה', 'מטפל', 'מספר היתר', 'תאריך הפקת היתר', 'שטח עיקרי', 'שטח שירות',
                       'סך מספר יחידות דיור המבוקשות', 'מבקש', 'בעל הנכס', 'עורך', 'מהנדס', 'מתנגד', 'מספר גוש',
                       'מספר חלקה', 'מספר מגרש', 'יעוד']
baaley_inyan = ['מבקש', 'בעל הנכס', 'עורך', 'מהנדס', 'מתנגד']

eruim_list = ['מסירת היתר בניה !', 'בהכנה לוועדה', 'תכנית (גרמושקה) הוחזרה לרישוי', 'פתיחת תיק במערכת השבחה', 'הועבר להשבחה',
              'שולם היטל השבחה', 'הוכנה שומת השבחה', 'הפקת נוסח פרסום לפי סעיף 149 - הקלה',
              'הפקת נוסח פרסום-תמ"א 38 / הקלה', 'פתיחת תיק', 'הוגשה תכנית מתוקנת', 'ישיבת ועדת משנה']


def main(use_didnt_load):
    download_path = os.getcwd()
    print("download_path:", download_path)
    # open browser:
    # options = webdriver.ChromeOptions()
    # options.add_experimental_option("prefs", {
    #     "download.default_directory": download_path,
    #     "download.prompt_for_download": False,
    #     "download.directory_upgrade": True,
    #     "safebrowsing.enabled": True})
    path_to_chromedriver = os.path.join(os.getcwd(), "chromedriver")
    # print(path_to_chromedriver)
    today = datetime.today()
    dir_name = str(today.year)+'_'+str(today.month)+'_html'
    # if not os.path.exists(dir_name):
    #     os.mkdir(dir_name)
    reader = csv.DictReader(open("year_tochniyot.csv", 'r'))
    for row in reader:
        year_dict = row
    print([i for i in year_dict.keys()])

    # year_dict = {'2016': 512,
    #              '2017': 538,
    #              '2018': 486,
    #              '2019': 487,
    #              '2020': 317}

    year_list = list(year_dict.keys())
    for year_num in year_list:
        if not os.path.exists('{}/first_url_list.pkl'.format(year_num)):
            url_list = []
            projects_in_year = year_dict[year_num]
            if not os.path.exists(str(year_num)):
                os.mkdir(str(year_num))
            if year_num == '2016':
                for i in range(1, projects_in_year):
                    url_list.append(proj_url + year_num + str(i).zfill(3))
            else:
                for i in range(1, projects_in_year):
                    url_list.append(proj_url + year_num + str(i).zfill(5))
            for i in range(1, 85):
                url_list.append(aruz7 + str(i))
            for i in range(260, 360):
                url_list.append('https://jergisinfohub.jerusalem.muni.il/UI/?SystemID=26400{}&processtype=2'.format(str(i)))
            shuffle(url_list)
            with open('{}/first_url_list.pkl'.format(year_num), 'wb') as f:
                pickle.dump(url_list, f)

    for year_num in year_list:
        first_url_list = []
        # use_didnt_load = False
        with open('{}/first_url_list.pkl'.format(year_num), 'rb') as f:
            url_list = pickle.load(f)
        first_url_list = url_list

        try:
            with open('{}/didnt_load.pkl'.format(year_num), 'rb') as f:
                didnt_load = pickle.load(f)
            url_list = didnt_load
            print("using didnt load list of urls")
            for i in range(260, 260+len(didnt_load)):
                url_list.append('https://jergisinfohub.jerusalem.muni.il/UI/?SystemID=26400{}&processtype=2'.format(str(i)))
            shuffle(url_list)
        except:
            didnt_load = []


        try:
            with open('{}/bad_pages.pkl'.format(year_num), 'rb') as f:
                bad_pages = pickle.load(f)
        except:
            bad_pages = []


        try:
            with open('{}/updated_url_list.pkl'.format(year_num), 'rb') as f:
                updated_url_list = pickle.load(f)
        except:
            updated_url_list = []

        try:
            with open('{}/got_heter_list.pkl'.format(year_num), 'rb') as f:
                got_heter_list = pickle.load(f)
        except:
            got_heter_list = []

        if use_didnt_load and didnt_load != []:
            url_list = didnt_load
        elif updated_url_list == []:
            url_list = first_url_list
        else:
            url_list = updated_url_list

        # filter out all tochniyot that got a heter
        if got_heter_list != []:
            # url_list = [url for url in url_list if url.split(proj_url)[1] not in got_heter_list]
            for url in url_list:
                if proj_url in url and url.split(proj_url)[1] in got_heter_list:
                    print(url.split(proj_url))
                    url_list.remove(url)


        for num, url in enumerate(url_list):
            new_page = True
            if url not in bad_pages:
                if 'ramat' in url:
                    tochnit = url.split('/')[-1]
                    page_path = '{}/{}.html'.format(year_num, tochnit)
                else:
                    new_page = False
                    page_path = '{}/other.html'.format(year_num)
                bad_page_path = '{}/bad_page.html'.format(year_num)
                if os.path.exists(page_path):
                    print("exists all ready")
                else:
                    if new_page:
                        print('url: ', url)
                        # time.sleep(uniform(2.5, 3.4))
                        answer = get_html(url, page_path, bad_page_path)
                        if answer == 'bad page':
                            what_to_do = input("encountered a bad page to continue press 'y' to break press ANY OTHER KEY to"
                                               " move to another year: ")
                            if what_to_do == 'y':
                                continue
                            else:
                                print("didn't work")
                                break
                        elif answer == 'no page':
                            bad_pages.append(url)
                        elif answer == 'page didnt load':
                            didnt_load.append(url)
            else:
                print("is a bad page")
        with open('{}/didnt_load.pkl'.format(year_num), 'wb') as f:
            pickle.dump(didnt_load, f)
        with open('{}/bade_pages.pkl'.format(year_num), 'wb') as f:
            pickle.dump(bad_pages, f)
        for url in updated_url_list:
            if url in bad_pages:
                updated_url_list.remove(url)
            else:
                pass
        with open('{}/updated_url_list.pkl'.format(year_num), 'wb') as f:
            pickle.dump(updated_url_list, f)


if __name__ == "__main__":
    file_list = os.listdir(os.getcwd())
    print(file_list)
    if "use_didnt_load.txt" in file_list:
        main(use_didnt_load=True)
    else:
        main(use_didnt_load=False)
