import pyautogui
import pyperclip  # handy cross-platform clipboard text handler
import time
import webbrowser
x_size, y_size = pyautogui.size()
url = 'https://handasa.ramat-gan.muni.il/newengine/Pages/request2.aspx#request/2016012'
path = 'html/test.html'
bad_page_path = 'html/bad.html'


def move_to_search():
    pyautogui.moveTo(500, 60, 2)
# move_to_search()


def copy_clipboard():
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1.2)  # ctrl-c is usually very fast but your program may execute faster
    return pyperclip.paste()


def get_html(url, path, bad_page_path):
    webbrowser.open('http://127.0.0.1:8000/')
    time.sleep(2)
    pyautogui.hotkey('ctrl', 't')
    time.sleep(2)
    move_to_search()
    pyautogui.doubleClick()
    pyautogui.typewrite(url)
    time.sleep(1)
    pyautogui.press('Enter')
    time.sleep(2)
    pyautogui.press('Enter')
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'shift', 'i')
    time.sleep(2)
    pyautogui.moveTo(x_size-200, 180, 15)
    pyautogui.click()
    html = copy_clipboard()
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'w')
    time.sleep(3)
    pyautogui.hotkey('ctrl', 'w')
    if "לא ניתן לצפות" in html:
        print("bad page")
        with open(bad_page_path, 'w') as f:
            f.write(html)
        return "bad page"
    elif "מצטערים" in html:
        print("no page")
        return "no page"
    elif "inn" in url or "jerusalem" in url:
        print(url)
    else:
        if 'מספר הבקשה:' in html:
            print("found good page")
            with open(path, 'w', encoding='utf8') as f:
                f.write(html)
            print("success")
            return "success"
        else:
            return "page didnt load"


# print(get_html(url, path, bad_page_path))
