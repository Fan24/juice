#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from PIL import Image,ImageEnhance
from gy import config
import time, json
import traceback
import math
import datetime

conf = config.GyConfig()
param = {
    "activityUrl": "https://pb.jd.com/activity/2018/bk/html/index.html?utm_source=pdappwakeupup_20170001,iosapp&utm_medium=appshare&utm_campaign=t_335139774&utm_term=CopyURL&ShareTm=n/9YUWgVfhJ%20NrS5cbboEf/Xxbs4ro4Tj7u/0kHFPwrvL3zpSnkIjPzkYlEJ71OugLYBRpba84kkF13HgziyvV6MIVOEn4sE7dpBKnG%20L/SOiAsMKlN2oJ0fdXBxhsO4F8ln2qo4I1E7wgNGawKMyOSSQRs2E1hkwHQno9iTSXY=&entranceId=9CpUGDst5mlvlLHm",
    "prizeUrl": "https://mk.jd.com/marketing/new/takeprize?callback=jQuery32106186221069453381_1539922481344&entranceId=%s&_=%d"
}


def visitActivity(driver, userInfo):
    driver.get(param['activityUrl'])
    time.sleep(3)
    if driver.current_url.startswith('https://plogin.m.jd.com/user/login.action'):
        login(driver, userInfo)
    if driver.current_url.startswith('https://pb.jd.com/activity/2018/bk/html/index.html'):
        return True
    return False


def blockUntilStart():
    ct = datetime.datetime.now()
    st = datetime.datetime(ct.year, ct.month, ct.day, ct.hour + 1)
    #st = datetime.datetime(ct.year, ct.month, ct.day, ct.hour, ct.minute, ct.second + 3)
    gap = math.floor((st - ct).total_seconds()) - 2
    print('Here we @%s, activity start @%s, we sleep %d(s)' % (ct.strftime('%Y%m%d %H:%M:%S.%f'), st.strftime('%Y%m%d %H:%M:%S'), gap))
    time.sleep(gap)


def parse_entrance_id(driver):
    return "9CpUGDst5mlvlLHm"

def get_prize_url(entrance_id):
    return param['prizeUrl'] % (entrance_id, time.time() * 1000)

def asynGrapPrize(driver, url):
    js = r'''
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange=function(){
        if (xmlhttp.readyState==4 && xmlhttp.status==200){
            var today = new Date();
            var s = today.getFullYear()+"/"+(today.getMonth() + 1)+"/"+today.getDate()+" "+today.getHours()+":"+today.getMinutes()+":"+today.getSeconds();
           console.debug(s + "  " + xmlhttp.responseText);
        }
    }
    xmlhttp.open("GET",arguments[0],true);
    console.info(arguments[0]);
    xmlhttp.send();'''
    st = datetime.datetime.now()
    for cnt in range(1, 7):
        driver.execute_script(js, url)
    ed = datetime.datetime.now()
    restTime = 15
    print('AsynStart:', st, ',end:', ed)
    print('AsynGrapPrize elapse:%d(s). We sleep %d(s) before completed.' % ((ed - st).total_seconds(), restTime))
    time.sleep(restTime)


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
    try:
        captcha = driver.find_element_by_id('captcha')
        cap_file = '%scaptcha.png' % conf.get_screen_path()
        driver.get_screenshot_as_file(cap_file)
        print(cap_file)
        code = driver.find_element_by_id('captcha')
        left = int(code.location['x'])
        top = int(code.location['y'])
        right = int(code.location['x'] + code.size['width'])
        bottom = int(code.location['y'] + code.size['height'])
        img = Image.open(cap_file)
        img = img.crop((left, top, right, bottom))
        img.save('%scaptcha2.png' % (conf.get_screen_path()))
        x = input('please input verify code x')
        y = input('please input verify code y')
        ActionChains(driver).move_to_element_with_offset(captcha, x, y).click().perform()
        time.sleep(5)
    except:
        print('not verify code')
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

driver.set_window_size(375, 812)
try:
    print('UserName:',userInfo['username'])
    cnt = 1
    for cnt in range(1, 4):
        print('#%d to activity' % cnt)
        if not visitActivity(driver, userInfo):
            continue
        entrance_id = parse_entrance_id(driver)
        przUrl = get_prize_url(entrance_id)
        print("PrizeUrl@", przUrl)
        blockUntilStart()
        asynGrapPrize(driver, przUrl)
        break
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.LINE')
