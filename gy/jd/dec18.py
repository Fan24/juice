#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
from gy.jd import Common
import time
import datetime
import traceback

conf = config.GyConfig()
param = {
    "activityUrl": "https://m.jr.jd.com/activity/lifeactivity/lifed12/index.html",
    "price_url" : "https://m.jdpay.com/marketing/jdm/takeprize?entranceId=HmnjLzRghizVDkUMCnX"
}


def visit_activity(driver, userInfo):
    driver.get(param['activityUrl'])
    if driver.current_url.startswith('https://plogin.m.jd.com/user/login.action'):
        Common.jd_login(driver, userInfo, conf)
    if driver.current_url.startswith(param['activityUrl']):
        return True
    return False


def get_ent_key(hour):
    if hour == 20:
        return ['ACUDzhSIEWT1HB', 'H1dum6ShzDUCj']
    return ['HmnjLzRghizVDkUMCnX', 'Hv7PKESXhNzKDCUWCK2']


def asyn_grap_prize(driver, st_hour):
    driver.get('https://payrisk.jd.com/m.html')
    mhtml = driver.find_element_by_xpath('/html/body').text
    driver.get('https://payrisk.jd.com/js/m.js')
    mjs = driver.find_element_by_xpath('/html/body/pre').text
    driver.get(param['price_url'])
    js = mhtml + mjs + r''';
    var risk_jd;
    try{
        risk_jd = getJdEid();
    }catch(e){}
    var formData = new FormData();
    formData.append("entranceId", arguments[0]);
    formData.append("eid", risk_jd.eid); 
    formData.append("token", risk_jd.token); 
    formData.append("source", "H5"); 
    formData.append("browser", window.navigator.userAgent); 
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange=function(){
        if (xmlhttp.readyState==4 && xmlhttp.status==200){
            var today = new Date();
            var s = today.getFullYear()+"/"+(today.getMonth() + 1)+"/"+today.getDate()+" "+today.getHours()+":"+today.getMinutes()+":"+today.getSeconds() + "." + today.getMilliseconds();
           console.debug(s + "  " + xmlhttp.responseText);
        }
    }
    xmlhttp.open("POST", "/marketing/jdm/takeprize/direct",true);
    xmlhttp.send(formData);
    console.debug(arguments[0]);
    '''
    ent_key = get_ent_key(st_hour)
    Common.block_until_start(False)
    st = datetime.datetime.now()
    for x in range(1, 5):
        for key in ent_key:
            driver.execute_script(js, key)
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
print('chrome dir', conf.get_chrome_user_dir())
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
    for cnt in range(1, 5):
        print('#%d to activity' % cnt)
        if not visit_activity(driver, userInfo):
            continue
        st_hour = datetime.datetime.now().hour + 1
        asyn_grap_prize(driver, st_hour)
        break
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.LINE')
