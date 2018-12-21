#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
import time, json
import traceback
import math


def go_dashboard(driver):
    driver.get('http://chadan.wang/wang/makeMoney')
    time.sleep(3)
    if driver.current_url.startswith('http://chadan.wang/wang/login'):
        login(driver)


def get_order(driver, param):
    order_url: str = 'http://chadan.wang/order/getOrderdd623299?JSESSIONID=%s&faceValue=%d&province=&amount=1&channel=2&operator=%s' % (driver.get_cookie('logged')['value'], param['faceValue'], param['operator'])
    driver.get(order_url)
    result = json.loads(driver.find_element_by_xpath('/html/body/pre').text)
    print(result)

    code = -4
    phone = ''
    if result['errorCode'] == 200:
        code = 0
        if len(result['data']) == 0:
            code = -5
        else:
            phone = result['data'][0]['rechargeAccount']
    return {'code':code, 'chargePhone': phone}


def get_job(driver, charge_type):
    pool_url = 'http://chadan.wang/order/pooldd623299?JSESSIONID=%s' % driver.get_cookie('logged')['value']
    driver.get(pool_url)
    try:
        pool = json.loads(driver.find_element_by_xpath('/html/body/pre').text)
    except:
        print('cloud not get pool', driver.page_source)
        traceback.print_exc()
        return {'code': -3}
    if pool['errorCode'] != 200:
        return {'code':-1}

    for operator in pool['data']:
        if operator['faceValue%d' % charge_type] == 0:
            continue
        return get_order(driver, {'faceValue': charge_type, 'operator': operator['operator']})
    return {'code': -2}


def login(driver):
    print('Login@',driver.current_url)
    driver.find_element_by_id('account').send_keys('13632265913')
    driver.find_element_by_id('password').send_keys('lcl12345')
    driver.execute_script('$("#loginButton").trigger("touchstart")')
    time.sleep(5)
    print('After login page@', driver.current_url)


chrome_options = Options()
conf = config.GyConfig()
if conf.is_headless():
    chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-web-security')
#chrome_options.add_argument(
#    'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"')
chrome_options.add_argument('--lang=zh-CN.UTF-8')
chrome_options.add_argument('--user-data-dir=%s' % conf.get_chrome_user_dir_by_key('chrome_user_dir_chadang'))
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
    go_dashboard(driver)
    cnt = 0
    sec = 3
    while True:
        result = get_job(driver, 30)
        if result['code'] == 0:
            break
        cnt += 1
        print('#%d.sleep %s sec' % (cnt, sec))
        time.sleep(sec)
    print('Success to get order, chargePhone:',result['chargePhone'])
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.PROG')
