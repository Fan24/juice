#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
import time, json,sys
import traceback

conf = config.GyConfig()
param = {
    "activityUrl": "https://pb.jd.com/activity/2018/18zhifu11/html/index.html?p_id=jrzhc",
    "prizeUrl": "https://pa.jd.com/prize/center/h5/draw?entranceKey=%s&_=%s"
}

entrance_key= ['dd6f21e50e0d764e8e5fffb76e7a6ad0','98afa61a3824fcefb8020d935d6e7635','6c576852a825dabba01dc7f360ecd357']


def visitActivity(driver, userInfo):
    driver.get(param['activityUrl'])
    time.sleep(3)
    if driver.current_url.startswith('https://plogin.m.jd.com/user/login.action'):
        login(driver, userInfo)
    if driver.current_url.startswith('https://pb.jd.com/activity/2018/18zhifu11/html/index.html'):
        return True
    return False


def grapPrize(driver):
    for key in entrance_key:
        pz_url = param['prizeUrl'] % (key, time.time() * 1000)
        print('For entrance_key:%s' % pz_url)
        for cnt in range(1, 3):
            print('#%d with prizeUrl:%s' % (cnt, pz_url))
            driver.get(pz_url)
            print('resultContent:%s' % driver.page_source)
            result = json.loads(driver.find_element_by_xpath('/html/body').text)
            if result['state'] == 1:
               break


def login(driver, userInfo):
    print('We are preparing to login')
    cnt = 0
    while driver.current_url.startswith('https://plogin.m.jd.com/user/login.action'):
        if cnt > 2:
            break;
        cnt += 1
        print('BeforeLogin#', cnt)
        time.sleep(1)
    if driver.current_url.startswith('https://plogin.m.jd.com/user/login.action'):
        driver.get_screenshot_as_file('%sbefore.png' % conf.get_screen_path())
        time.sleep(2)
        driver.find_element_by_id('username').send_keys(userInfo['username'])
        time.sleep(1)
        driver.find_element_by_id('password').send_keys(userInfo['password'])
        time.sleep(2)
        driver.find_element_by_id('loginBtn').click()
        time.sleep(5)
    if driver.current_url.startswith('https://plogin.m.jd.com/cgi-bin/ml/risk'):
        print('RiskUri:',driver.current_url)
        driver.find_element_by_class_name('.mode-btn.voice-mode').click()
        time.sleep(3)
    if driver.current_url.startswith('https://plogin.m.jd.com/cgi-bin/ml/sms_risk'):
        print('SmsUri:',driver.current_url)
        sms = input('Please input smscode:')
        driver.find_element_by_id('authCode').send_keys(sms)
        time.sleep(1)
        driver.find_element_by_class_name('smsSubmit').click()
        time.sleep(2)
    driver.get_screenshot_as_file('%safterLogin.png' % conf.get_screen_path())
    print('AfterLoginUrl@', driver.current_url)


userInfo = conf.get_user_info()
chrome_options = Options()
if conf.is_headless():
    chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument(
    'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"')
chrome_options.add_argument('--lang=zh-CN.UTF-8')
chrome_options.add_argument('--user-data-dir=%s' % conf.get_chrome_user_dir())
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
if conf.get_http_proxy():
    chrome_options.add_argument('--proxy-server=%s' % conf.get_http_proxy())

if conf.get_chrome_executable_path():
    driver = webdriver.Chrome(executable_path=conf.get_chrome_executable_path(),options=chrome_options)
else:
    driver = webdriver.Chrome(options=chrome_options)

driver.set_window_size(640, 700)
try:
    print('UserName:', userInfo['username'])
    cnt = 1
    for cnt in range(1, 4):
        print('#%d to activity' % cnt)
        if not visitActivity(driver, userInfo):
            continue
        grapPrize(driver)
        break
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.LINE')
