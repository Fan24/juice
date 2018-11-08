#coding=utf-8
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image,ImageEnhance
from pymongo import MongoClient
import pytesseract
import time,sys,logging
import datetime
import traceback
import json
import math

logger = logging.getLogger('myLog')
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler('/home/ap/fan/workshop/jd/log/miki.txt')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s-% (name)s-%(levelname)s-%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


screen_dir='/home/ap/fan/workshop/jd/screen/'

def loadAuthCode():
        codefile = '/home/ap/fan/workshop/jd/data/authcode'
        while True:
                try:
                        with open(codefile, 'r') as fp:
                                authcode = fp.readline()
                                if authcode == "" :
                                        print 'please input imgcode@',codefile
                                        time.sleep(3)
                                        continue
                                return authcode
                except:
                        time.sleep(3)


def login(driver, userInfo):
        uri = 'https://plogin.m.jd.com/user/login.action?appid=579&returnurl=https%3A%2F%2Fpb.jd.com%2Factivity%2F2018%2Fhyjaug%2Fhtml%2Findex.html%3Fcu%3Dtrue%26utm_source%3Dkong%26utm_medium%3Djingfen%26utm_campaign%3Dt_352888004_%26utm_term%3Da49c20788c4c4835a3e6c2489719473a%26abt%3D3'
        driver.get(uri)
        cnt = 0
        while driver.current_url.startswith('https://plogin.m.jd.com/user/login.action'):
                if cnt > 2:
                        break;
                cnt += 1
                print 'BeforeLogin#',cnt
                time.sleep(1)
        if driver.current_url.startswith('https://plogin.m.jd.com/user/login.action'):
                time.sleep(2)
                #driver.get_screenshot_as_file('%s/1beforeClick.png'%(screen_dir))
                driver.find_element_by_id('account_login_txt').click()
                time.sleep(1)
                imgName = '%s/beforeClick.png'%(screen_dir)
                driver.get_screenshot_as_file(imgName)
                code = driver.find_element_by_id('imgCode')
                left = int(code.location['x'])
                top = int(code.location['y'])
                right = int(code.location['x'] + code.size['width'])
                bottom = int(code.location['y'] + code.size['height'])
                img = Image.open(imgName)
                img = img.crop((left, top, right, bottom))
                img = img.convert('L')
                img = ImageEnhance.Contrast(img)
                img = img.enhance(2.0)
                img.save('%s/imagecode.png' % (screen_dir))
                text = raw_input('Please input imgcode:')
                #logger.info('please input authcode')
                #text = loadAuthCode()
                driver.find_element_by_id('username').send_keys(userInfo['username'])
                driver.find_element_by_id('password').send_keys(userInfo['password'])
                driver.find_element_by_id('code').send_keys(text)
                driver.get_screenshot_as_file('%s/beforeClick.png' % (screen_dir))
                driver.find_element_by_id('loginBtn').click()
                time.sleep(5)

        print 'LoginUri2:', driver.current_url

        if driver.current_url.startswith('https://plogin.m.jd.com/cgi-bin/ml/risk'):
                print 'RiskUri:',driver.current_url
                driver.find_element_by_class_name('.mode-btn.voice-mode').click()

                time.sleep(5)
        if driver.current_url.startswith('https://plogin.m.jd.com/cgi-bin/ml/sms_risk'):
                print 'SmsUri:',driver.current_url
                sms = raw_input('Please input smscode:')
                driver.find_element_by_id('authCode').send_keys(sms)
                time.sleep(1)
                driver.find_element_by_class_name('smsSubmit').click()
        cnt = 0
        while driver.current_url.startswith('https://plogin.m.jd.com/user/login.action'):
                #driver.get_screenshot_as_file(('%s/AfterClick%d.png') % (screen_dir, cnt))
                if cnt > 3:
                        return False
                cnt += 1
                print 'AfterClick2Login#',cnt
                time.sleep(3)
        print 'activityUrl:', driver.current_url
        return True

def loadUserInfo(file):
        with open(file, 'r') as fp:
                return json.load(fp)

def testIfLoginSuccess(driver):
        couponList = getCouponList(driver)
        if couponList['code'] == 'F_000000' and couponList['success']:
                print 'Login Success'
                return True
        else:
                print 'Login Fail'
                return False


def getCouponList(driver):
        couponUri = 'https://payhome.jd.com/my/api/firstAnnAct/couponList?_=%s' % (int(time.time() * 1000))
        cnt = 0
        while cnt < 3:
                cnt += 1
                driver.get(couponUri)
                try:
                        return json.loads(driver.find_element_by_xpath('/html/body/pre').text)
                except:
                        traceback.print_exc()
        return {"code":"F_999999", "success" : False}

def visitActivity(driver):
        activityUri = 'https://pb.jd.com/activity/2018/hyjaug/html/index.html'
        cnt = 0
        while cnt < 3:
                try:
                        cnt += 1
                        print '#%d go to activity address:%s' % (cnt, activityUri)
                        st = datetime.datetime.now()
                        driver.get(activityUri)
                        ed = datetime.datetime.now()
                        print 'Request activity address need %d(s)' % ((ed - st).total_seconds())
                        return True
                except:
                        traceback.print_exc()
        return False



cookieDir = '../data/cookies.json'

def loadCookies(driver):
        with open(cookieDir, 'r') as fp:
                cookies = json.load(fp)
                for cookie in cookies:
                        driver.add_cookie(cookie)

def getPrizeUri(startHour, couponList):
        coupons = couponList['data']['coupons']['%d' % (startHour)]
        entranceKeys = {"10":["2018080220115362101"], "14":["2018080215442176401"], "20":["2018080217194312701", "2018080215413271301"]}
        currEntranceKey = entranceKeys['%d' % (startHour)]
        uriList = []
        for ekID in currEntranceKey:
                for cp in coupons:
                        if cp["id"] == ekID:
                                uriList.append('https://pa.jd.com/prize/center/h5/draw?entranceKey=%s&_=%d' % (cp["entranceKey"], int(time.time() * 1000)))
        return uriList

def asynGrapPrize(driver, uriList):
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
        for cnt in range(1, 5):
                for uri in uriList:
                        driver.execute_script(js, uri)
        ed = datetime.datetime.now()
        restTime = 15
        print 'AsynStart:',st,',end:',ed
        print 'AsynGrapPrize elapse:%d(s). We sleep %d(s) before completed.' % ((ed - st).total_seconds(), restTime)
        time.sleep(restTime)


def dumpCookies(driver):
        cookies = driver.get_cookies()
        with open(cookieDir, 'w') as fp:
                json.dump(cookies, fp)
def getStartHour():
        nowHour = datetime.datetime.now().hour
        stHour = 20

        if nowHour < 10:
                stHour = 10
        if nowHour >= 10 and nowHour < 14:
                stHour = 14
        if nowHour >=14:
                stHour = 20
        return stHour


def blockUntilStart():
        ct = datetime.datetime.now()
        st = datetime.datetime(ct.year, ct.month, ct.day, ct.hour + 1)
        #st = datetime.datetime(ct.year, ct.month, ct.day, ct.hour, ct.minute, ct.second + 3)
        gap = math.floor((st - ct).total_seconds()) - 2
        print 'Here we @%s, activity start @%s, we sleep %d(s)' % (ct.strftime('%Y%m%d %H:%M:%S.%s'), st.strftime('%Y%m%d %H:%M:%S'), gap)
        time.sleep(gap)

def goGetPrize(driver):
        try:
                visitActivity(driver)
                couponList = getCouponList(driver)
                if couponList['code'] == 'F_000000' and couponList['success']:
                        print 'We login success@',datetime.datetime.now()
                        pzUri = getPrizeUri(getStartHour(), couponList)
                        print pzUri
                        blockUntilStart()
                        print 'It\'s time 2 grap prize@',datetime.datetime.now()
                        asynGrapPrize(driver, pzUri)
                else:
                        print 'We fail 2 login',couponList

        except:
                traceback.print_exc()
def shouldContinue():
        try:
                with open('/home/ap/fan/workshop/jd/data/stop.dat', 'r') as fp:
                        sign = fp.readline()
                        if sign == 'stop':
                                return False
                        return True
        except:
                traceback.print_exc()


print sys.argv[1]
userInfo = loadUserInfo(sys.argv[1])
chrome_options = Options()
# specify headless mode
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument('user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"')
chrome_options.add_argument('--lang=zh-CN.UTF-8')
chrome_options.add_argument('--user-data-dir=/home/ap/fan/chrome/%s' % (userInfo['username']))
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.set_window_size(640, 960)

print 'Welcome %s'%(userInfo['username']),'@',datetime.datetime.now()
loginCounter = 0
loginSuccess = False
while loginCounter < 10:
        loginCounter += 1
        print 'Login attempt #',loginCounter
        try:
                if login(driver, userInfo):
                        loginSuccess = True
                        break;
                else:
                        time.sleep(2)

        except:
                traceback.print_exc()

if not loginSuccess:
        print 'Fail to login@',datetime.datetime.now()
        exit()

if not testIfLoginSuccess(driver):
        exit()
#logger.info('%s login success' % (userInfo['username']))

#goGetPrize(driver)

try:
        goGetPrize(driver)
except:
        traceback.print_exc()
finally:
        driver.quit()
        print 'Finish @',datetime.datetime.now()