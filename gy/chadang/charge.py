#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
import time
import json
import datetime
import traceback


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


def get_job(driver, charge_type, oper_type):
    """
        get order form chadang
    :param driver:
    :param charge_type: money to charge
    :param oper_type: MOBILE,UNICOM,TELECOM,None. Choose one from four, None for not specified.
    :return:
    """
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
        if oper_type is not None and oper_type != operator['operator']:
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


def confirm_order(driver, charge_phone):
    confirm_url = 'http://chadan.wang/wang/makeMoney'
    driver.get(confirm_url)
    time.sleep(3)
    driver.get(driver.find_element_by_class_name('success').get_attribute('href'))
    time.sleep(3)
    driver.find_element_by_id('sureReport').click()
    time.sleep(3)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    check_url = 'http://chadan.wang/order/queryUserOrders?startTime=%s 00:00:00&endTime=%s 23:59:59&orderStatus=3&JSESSIONID=%s' % (today, today, driver.get_cookie('logged')['value'])
    driver.get(check_url)
    qry_result = json.loads(driver.find_element_by_xpath('/html/body/pre').text)
    if qry_result['errorCode'] == 200 and qry_result['data']['total'] == 0:
        print('charge phone[%s] report success' % charge_phone)
        return True
    print('Report phone[%s] to sucess fail, please check' % charge_phone)
    print(qry_result)

    return False


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
    charge_money = 100
    ot_array = [None, "MOBILE", "UNICOM", "TELECOM"]
    operator_type = ot_array[0]
    while True:
        result = get_job(driver, charge_money, operator_type)
        if result['code'] == 0:
            print('%s--charge phone:%s' % (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f'), result['chargePhone']))
            cmd = input('input n to get next charge phone with %d, q to exit\n'% charge_money)
            if confirm_order(driver, result['chargePhone']) and cmd == "n":
                continue
            else:
                break
        cnt += 1
        print('#%d.sleep %s sec' % (cnt, sec))
        time.sleep(sec)
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.PROG')
