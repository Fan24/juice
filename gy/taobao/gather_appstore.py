#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from requests.cookies import RequestsCookieJar
from selenium.webdriver.common.by import By
from gy import config
import time
from urllib import parse
from selenium.common.exceptions import TimeoutException
import logging
import json
import hashlib
import re
import traceback
import requests

conf = config.GyConfig()
param = {
    "home_url": "https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm?spm="
                "a21bo.2017.1997525045.2.5af911d97UfwFA",
    "m_home_url": "https://main.m.taobao.com/mytaobao/index.html?spm=a212db.index.toolbar.i1",
    'buy_list_url': 'https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm'
}

'''
try: # for Python 3
    from http.client import HTTPConnection
except ImportError:
    from http import HTTPConnection
HTTPConnection.debuglevel = 1

logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
'''

s = requests.Session()


def get_sign(str_data):
    md5 = hashlib.md5()
    md5.update(bytes(str_data, encoding="utf8"))
    return md5.hexdigest()


def find_face_value(elem):
    try:
        return elem.find_element_by_xpath('td[2]//del/span[2]').text
    except:
        return elem.find_element_by_xpath('td[5]//span[2]').text


def find_pay_money(elem):
    len_span = 2
    while len_span > 0:
        try:
            return elem.find_element_by_xpath('div/p/span[%d]' % len_span).text
        except:
            print('PayMoneyEx:', len)
        len_span = len_span - 1
    return 'NA'


def collect_order_info(elems, info_list, wall_order_id):
    if elems is None or len(elems) == 0:
        return False
    found = 0
    for elem in elems:
        biz_order_id = re.search('bizOrderId=(\d+)?&', elem.get_attribute('href')).group(1)
        tr_elem = elem.find_element_by_xpath('../../../..')
        '''
        while True:
            path = input('path to debug')
            try:
                print(tr_elem.find_element_by_xpath(path).text)
            except:
                print(1111)
            if path == "c":
                break
                '''
        price_elem = tr_elem.find_element_by_xpath('td[2]')
        pay_money = find_pay_money(price_elem)
        #face_value = price_elem.find_element_by_xpath('//del/span[2]').text
        #face_value = tr_elem.find_element_by_xpath('td[5]//span[2]').text
        face_value = find_face_value(tr_elem)
        order = {'biz_order_id': biz_order_id, 'face_value' : face_value, 'pay_money' : pay_money}
        print('bizID:%s, face_vaule:%s, pay_money:%s' % (biz_order_id, face_value, pay_money))
        info_list.append(order)
        found = found + 1
        if biz_order_id == wall_order_id:
            print('we reach the last order id %s, which include to collect' % wall_order_id)
            return False
    return True


def collect_card_info(driver, biz_info):
    print('Total number of biz(s) %d' % len(biz_info))
    cnt = 0
    total = len(biz_info)
    for biz in biz_info:
        cnt = cnt + 1
        print('Get biz:%s, %d/%d' % (biz['biz_order_id'], cnt, total))
        get_card_info(driver, biz)
        time.sleep(1.5)
    print('Total number of biz(s) %d' % len(biz_info))
    for biz in biz_info:
        print('\'%s\t%s\t%s\t%s\t%s' % (biz['biz_order_id'], biz.get('face_value'), biz.get('card_no'), biz.get('card_pass'), biz['pay_money']))


def get_card_info(driver, biz_info):
    url = 'https://h5api.m.taobao.com/h5/mtop.wtt.order.distribution.applecard.query/1.0/?'
    app_key = '12574478'
    t = int(time.time() * 1000)
    token = s.cookies['_m_h5_tk'].split("_", 1)[0]
    print(token)
    pm_data = '''{"tbOrderNo":"%s"}''' % biz_info['biz_order_id']
    pm_data_encode = '''%7B%22tbOrderNo%22%3A%22'''+biz_info['biz_order_id']+'''%22%7D'''
    sign = get_sign('%s&%d&%s&%s' % (token, t, app_key, pm_data))
    p = 'jsv=2.4.5&appKey=%s&t=%d&sign=%s&api=mtop.wtt.order.distribution.applecard.query&v=1.0&timeout=10000&' \
        'AntiCreep=true&AntiFlood=true&type=jsonp&dataType=jsonp&preventFallback=true&callback=mtopjsonp2&'\
        'data=%s' % (app_key, t, sign, pm_data_encode)
    target_url = '%s%s' % (url, p)
    driver.get(target_url)
    resp = driver.find_element_by_xpath('/html/body/pre').text
    resp = resp[len('mtopjsonp2('):-1]
    json_resp = json.loads(resp)
    if json_resp.get('data') is not None and json_resp.get('data').get('code') == "0" \
            and json_resp.get('data').get('data') is not None:
        card_data = json_resp.get('data').get('data')[0]
        biz_info['face_value'] = card_data['facePrice']
        biz_info['card_no'] = card_data['cardNo']
        biz_info['card_pass'] = card_data['cardPass']
    else:
        print('Unable to get order id[%s] card info' % (biz_info['biz_order_id']))


def get_pc_order_list(driver, wall_order_id):
    url = 'https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm'
    driver.get(url)
    time.sleep(2)
    biz_order_info_list = []
    page_no = 1
    success_to_next_page = True
    while success_to_next_page:
        print('Go to page#%d' % page_no)
        elems = driver.find_elements_by_link_text('查看卡密')
        if not collect_order_info(elems, biz_order_info_list, wall_order_id):
            cmd = "other"
            if biz_order_info_list[len(biz_order_info_list) - 1]['biz_order_id'] != wall_order_id:
                cmd = input('Page #%d have no order, c for continue, other to quit' % page_no)
            if cmd != "c":
                break
        page_no = page_no + 1
        while True:
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'pagination-item-%d' % page_no)))
                driver.find_element_by_class_name('pagination-item-%d' % page_no).click()
                break
            except TimeoutException:
                cmd = input('Unable to navigated to page#%d, input r to retry, other to end' % page_no)
                if cmd == "r":
                    continue
                success_to_next_page = False
                break
        time.sleep(3)
    print('We find #%d of order' % len(biz_order_info_list))
    return biz_order_info_list


def get_order_list_address(driver):
    url = 'https://h5api.m.taobao.com/h5/mtop.order.queryboughtlist/4.0/?jsv=2.5.1&appKey=%s&t=%d&sign=%s&api=%s&v=4.0'\
          '&ttid=%s&isSec=0&ecode=1&AntiFlood=true&AntiCreep=true&LoginRequest=true&needLogin=true&H5Request=true'\
          '&type=jsonp&dataType=jsonp&callback=mtopjsonp8&data=%s'
    list_param = {
        'jsv': '2.5.1',
        'appKey' : 12574478,
        'api': 'mtop.order.queryboughtlist',
        'v': '4.0',
        'ttid': '##h5',
        'isSec': 0,
        'ecode': 1,
        'AntiFlood': 'true',
        'AntiCreep': 'true',
        'LoginRequest': 'true',
        'needLogin': 'true',
        'H5Request': 'true',
        'type': 'jsonp',
        'dataType': 'jsonp',
        'callback': 'mtopjsonp8',
        'data': '''{"tabCode":"all","spm":"a2141.7756461.mytaobao_v4_order_list_1.i0","page":7,"appVersion":"1.0","appName":"tborder"}'''
    }
    t = int(time.time() * 1000)
    token = s.cookies['_m_h5_tk'].split("_", 1)[0]
    sign = get_sign('%s&%d&%s&%s' % (token, t, list_param['appKey'], json.dumps(list_param['data'])))
    list_param['sign'] = sign
    list_param['t'] = t
    url2 = 'https://h5api.m.taobao.com/h5/mtop.order.queryboughtlist/4.0/?%s' % (parse.urlencode(list_param))
    print(url2)
    print(url)
    t_url = url % (list_param['appKey'], t, sign, list_param['api'], parse.quote(list_param['ttid']), parse.quote(list_param['data']))
    print(t_url)
    input('press to load')
    #driver.get(url2)
    r = s.get(t_url)
    print(r.text)


def tb_login(driver):
    #driver.get('https://taobao.com')
    driver.get(param['buy_list_url'])
    input('please login')
    driver.execute_script('window.open("https://www.baidu.com");')
    driver.switch_to.window(driver.window_handles[1])
    driver.get(param['m_home_url'])
    time.sleep(2)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return True


def cookies_transfer(driver):
    for cookie in driver.get_cookies():
        cookie_jar = RequestsCookieJar()
        cookie_jar.set(cookie['name'], cookie['value'], domain=cookie['domain'])
        s.cookies.update(cookie_jar)


userInfo = conf.get_user_info()
chrome_options = ChromeOptions()
if conf.is_headless():
    chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-web-security')
'''chrome_options.add_argument(
    'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) '
    'Version/9.0 Mobile/13B143 Safari/601.1"')
    '''
chrome_options.add_argument('--lang=zh-CN.UTF-8')
chrome_options.add_argument('--user-data-dir=%s' % conf.get_chrome_user_dir())
print('chrome user path:%s' % conf.get_chrome_user_dir())
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
if conf.get_http_proxy():
    chrome_options.add_argument('--proxy-server=%s' % conf.get_http_proxy())

if conf.get_chrome_executable_path():
    driver = webdriver.Chrome(executable_path=conf.get_chrome_executable_path(),options=chrome_options)
else:
    driver = webdriver.Chrome(options=chrome_options)

driver.set_window_size(900, 900)
try:
    if not tb_login(driver):
        print('Login FAIL, exit')
        exit(1)
    cookies_transfer(driver)
    #get_order_list_address(driver)
    #the last order id to search, if we reach this order id, the proccess will return to get card no
    #include this order
    #wall_order_id = '828822691038164392'
    wall_order_id = input('please input the last include order to collected')
    order_list = get_pc_order_list(driver, wall_order_id)
    collect_card_info(driver, order_list)
except:
    traceback.print_exc()
finally:
    input('press to finish')
    driver.close()
    driver.quit()
    print('END.OF.LINE')
