#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
from gy.util import common
import time,json,os
import traceback
import datetime


def prepare_env(driver, jsession, page_id):
    print('Preparing environment')
    driver.get('https://mcard.boc.cn/')
    if not driver.get_cookie('JSESSIONID'):
        driver.add_cookie({"name" : "JSESSIONID", "value" : jsession})
    elif driver.get_cookie('JSESSIONID')['value'] != jsession:
        driver.delete_cookie('JSESSIONID')
        driver.add_cookie({"name" : "JSESSIONID", "value" : jsession})

    time.sleep(2)
    index_url = 'https://mcard.boc.cn/ebank/preferenMerchant/list.do?code=%s&state=boc' % page_id
    print('Go to index page:', index_url)
    driver.get(index_url)

    sleep_cnt = 1
    while sleep_cnt < 12:
        try:
            elem = driver.find_element_by_xpath("//img[@data-id='14']")
            break
        except:
            time.sleep(5)
            sleep_cnt += 1
    print('Here we @', driver.current_url)
    if sleep_cnt < 12:
        elem.click()
        return True
    else:
        return False


def assemble_order_url(driver, coupon_id):
    detail_url = 'https://mlife.jf365.boc.cn/CouponsMall/newCouponDetail.do?couponId=%s&cityId=110100' % coupon_id
    driver.get(detail_url)
    req_channel = driver.find_element_by_id('reqChannel').get_attribute('value')
    new_to_order_url = 'https://mlife.jf365.boc.cn/CouponsMall/newToCreateOrder.do?couponId=%s&cityId=110100&cardType=1&reqChannel=%s' % (coupon_id, req_channel)
    print('New to order url:', new_to_order_url)
    driver.get(new_to_order_url)
    coupon_type = driver.find_element_by_id('couponType').get_attribute('value')
    print(driver.find_element_by_id('selJsonLM').get_attribute('innerHTML'))
    card_list = json.loads(driver.find_element_by_id('selJsonLM').get_attribute('innerHTML'))
    card_no1 = '524b7ed3c00c4c20b432f12c1b261d19'
    for card in card_list:
        if card['cardNo'] == '625907 **** **** 1190':
            card_no1 = card['cardNo1']
    return 'https://mlife.jf365.boc.cn/CouponsMall/newCreateOrder.do?couponId=%s&couponType=%s&total=1&cardNo=C%s' % (coupon_id, coupon_type, card_no1)


def do_order(driver, url_list):
    js = r'''
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange=function(){
        if (xmlhttp.readyState==4 && xmlhttp.status==200){
            var today = new Date();
            var s = today.getFullYear()+"/"+(today.getMonth() + 1)+"/"+today.getDate()+" "+today.getHours()+":"+today.getMinutes()+":"+today.getSeconds() + "." + today.getMilliseconds();
            console.debug(s + "  " + xmlhttp.responseText);
        }
    }
    xmlhttp.open("GET",arguments[0],true);
    console.info(arguments[0]);
    xmlhttp.send();'''

    common.block_until_start_by_second(True, 1)
    st = datetime.datetime.now()
    for url in url_list:
        print(url)
        for cnt in range(1, 10):
            driver.execute_script(js, url)
    ed = datetime.datetime.now()
    restTime = 10
    print('AsynStart:', st, ',end:', ed)
    print('AsynGrapPrize elapse:%d(s). We sleep %d(s) before completed.' % ((ed - st).total_seconds(), restTime))
    time.sleep(restTime)


def load_coupon_id(day):
    if day > 0:
        week_day = day
    else:
        week_day = datetime.datetime.now().weekday() + 1
    print(week_day)
    PROJ_PATH= "E:/OnionMall/"
    if "PROJ_PATH" in os.environ:
        PROJ_PATH = os.environ['PROJ_PATH']
    with open('%sgy/boc/jf365.json' % PROJ_PATH, encoding='utf-8') as fp:
        return json.load(fp)['%d' % week_day]


chrome_options = Options()
conf = config.GyConfig()
if conf.is_headless():
    chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument(
    '-user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 12_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A404 MicroMessenger/6.7.3(0x16070321) NetType/WIFI Language/zh_CN')
chrome_options.add_argument('--lang=zh-CN.UTF-8')
chrome_options.add_argument('--user-data-dir=%s' % conf.get_chrome_user_dir_by_key('chrome_user_dir_boc'))
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
if conf.get_http_proxy():
    print('HTTP_PROXY:',conf.get_http_proxy())
    chrome_options.add_argument('--proxy-server=%s' % conf.get_http_proxy())

if conf.get_chrome_executable_path():
    driver = webdriver.Chrome(executable_path=conf.get_chrome_executable_path(),options=chrome_options)
else:
    driver = webdriver.Chrome(options=chrome_options)

driver.set_window_size(640, 700)
try:
    prepare_cnt = 1
    while not prepare_env(driver, '0000vXowIJ3FI-42D9G0eHR5yRl:19fhdbabq', '001obkak0zvoim1abjdk0Tebak0obkaP'):
        print('Retry:',prepare_cnt)
        prepare_cnt += 1
        if prepare_cnt > 5:
            break
    if prepare_cnt > 5:
        exit(-1)

    coupon_id = []
    for one in load_coupon_id(-1):
        coupon_id.append(one['id'])

    url_list = []
    for cid in coupon_id:
        for an in range(1,5):
            try:
                url_list.append(assemble_order_url(driver, cid))
                break
            except:
                print('assemble_order_url,error #', an)
                traceback.print_exc()
    do_order(driver, url_list)
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.PROG')
