#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
from gy.jd import Common
from gy.util import common
import time
import datetime
import traceback

conf = config.GyConfig()
param = {
    "activityUrl": "https://pro.m.jd.com/mall/active/ajxN8wHWSbPejA5G2pC4jNGZLkg/index.html",
    "coupon_id" : "m_1_2"
}


def visit_activity(driver, userInfo):
    print('go to ', param['activityUrl'])
    driver.get(param['activityUrl'])
    print('we are at', driver.current_url)
    driver.execute_script('$("#%s").children().first().click()' % param['coupon_id'])
    time.sleep(5)
    if driver.current_url.startswith('https://plogin.m.jd.com/user/login.action'):
        Common.jd_login(driver, userInfo, conf)
    if driver.current_url.startswith(param['activityUrl']):
        return True
    return False


def click_to_get(driver):
    command = []
    command.append('$("#%s").children().first().click()' % param['coupon_id'])
    command.append('$("#%s").children().eq(1).click()' % param['coupon_id'])
    for cmd in command:
        driver.execute_script(cmd)
        print(cmd)
    driver.get_screenshot_as_file('%sjd_coupon.png' % conf.get_screen_path())
    print('URL for clicking to get coupon PNG\nhttp://%s/pj/gy/jd/coupon_png.html' % common.get_host_ip())
    time.sleep(5)


def get_act_key():
    return '2018101815415505201'


def asyn_grap_prize(driver):
    js = r'''
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange=function(){
        if (xmlhttp.readyState==4 && xmlhttp.status==200){
            var today = new Date();
            var s = today.getFullYear()+"/"+(today.getMonth() + 1)+"/"+today.getDate()+" "+today.getHours()+":"+today.getMinutes()+":"+today.getSeconds() + "." + today.getMilliseconds();
           console.debug(s + "  " + xmlhttp.responseText);
        }
        if(xmlhttp.readyState==1 || xmlhttp.readyState==0){
            var today = new Date();
            var s = today.getFullYear()+"/"+(today.getMonth() + 1)+"/"+today.getDate()+" "+today.getHours()+":"+today.getMinutes()+":"+today.getSeconds() + "." + today.getMilliseconds();
            console.debug("Send:" +  xmlhttp.readyState + "----" + s)
        }
    }
    xmlhttp.open("GET",arguments[0],true);
    console.info(arguments[0]);
    xmlhttp.send();'''

    body = '''{"scene":"3","actKey":"%s","mitemAddrId":"","geo":{"lng":"","lat":""},"addressId":"","posLng":"","posLat":"","focus":"","innerAnchor":""}'''
    body = body % get_act_key()
    print(driver.get_cookies())
    argv = [
        "functionId=newBabelAwardCollection",
        "screen=877*969",
        "client=wh5",
        "clientVersion=1.0.0",
        "sid=",
        "uuid=%s" % driver.get_cookie('mba_muid')['value'],
        "area=",
        "body=%s" % body,
        "_=%d" % (time.time() * 1000)
    ]
    url = '%s?%s' % (param['prizeUrl'], "&".join(argv))
    print('PrizeUrl:', url)
    st = datetime.datetime.now()
    driver.execute_script(js, url)
    ed = datetime.datetime.now()
    rest_time = 20
    print('AsynStart:', st, ',end:', ed)
    print('AsynGrapPrize elapse:%d(s). We sleep %d(s) before completed.' % ((ed - st).total_seconds(), rest_time))
    time.sleep(rest_time)


userInfo = conf.get_user_info()
chrome_options = Options()
if conf.is_headless():
    chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument(
    'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"')
chrome_options.add_argument('--lang=zh-CN.UTF-8')
chrome_options.add_argument('--user-data-dir=%s' % conf.get_chrome_user_dir())
print(conf.get_chrome_user_dir())
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
if conf.get_http_proxy():
    chrome_options.add_argument('--proxy-server=%s' % conf.get_http_proxy())

if conf.get_chrome_executable_path():
    driver = webdriver.Chrome(executable_path=conf.get_chrome_executable_path(),options=chrome_options)
else:
    driver = webdriver.Chrome(options=chrome_options)

driver.set_window_size(640, 900)
try:
    print('UserName:', userInfo['username'])
    cnt = 1
    for cnt in range(1, 4):
        print('#%d to activity' % cnt)
        if not visit_activity(driver, userInfo):
            continue
        Common.block_precise_until_start(True)
        click_to_get(driver)
        break
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.LINE')
