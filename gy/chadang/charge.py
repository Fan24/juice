#!/usr/bin/env python
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from gy import config
from gy.netease import KaolaUtil
import time
import json
import datetime
import traceback


def load_json(driver):
    """
    load /hhtml/body/pre to json object
    :param driver:
    :return:
    """
    try:
        return json.loads(driver.find_element_by_xpath('/html/body/pre').text)
    except NoSuchElementException:
        print(driver.page_source)
        traceback.print_exc()
        return {'errorCode' : '404'}


def kaola_offer(driver, url):
    driver.execute_script('window.open("https://www.baidu.com");')
    driver.switch_to.window(driver.window_handles[1])
    driver.get(url)
    while not driver.current_url.startswith('https://m-goods.kaola.com'):
        driver.get(url)
        time.sleep(2)

    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CLASS_NAME, 'mrkprice')))
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CLASS_NAME, 'nameShop')))
    return {'price': int(driver.find_element_by_class_name('mrkprice').text[1:]),
            'shop_name': driver.find_element_by_class_name('nameShop').text}


def kaola_do_order(driver, phone):
    driver.find_element_by_class_name('formbox').submit()
    time.sleep(2)
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CLASS_NAME, 'v-input-input')))
    driver.find_element_by_class_name('v-input-input').send_keys(phone)
    WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CLASS_NAME, 'v-submitorderbar-button')))
    driver.find_element_by_class_name('v-submitorderbar-button').click()
    WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CLASS_NAME, 'v-dialog-button-primary')))
    driver.find_element_by_class_name('v-dialog-button-primary').click()
    while not driver.current_url.startswith('https://tradenj.kaola.com/order/payway.html'):
        time.sleep(1)
    driver.find_element_by_xpath('//input[@value="6"]').click()
    driver.find_element_by_id('payNow').click()
    while not driver.current_url.startswith('https://mclient.alipay.com'):
        time.sleep(1)
    driver.find_element_by_class_name('J-h5pay').click()
    time.sleep(1)
    while True:
        cur_url = driver.current_url
        if cur_url.startswith('https://mclient.alipay.com/h5Continue.htm'):
            break
    title = driver.find_element_by_class_name('title-main').text
    if title != "付款详情":
        driver.find_element_by_xpath('//a[@seed="v5_need_phonelogin-login"]').click()
        time.sleep(1)
        driver.find_element_by_id('logon_id').send_keys('dreamsfan@gmail.com')
        driver.find_element_by_id('pwd_unencrypt').send_keys('802070')
        driver.find_element_by_id('cashier').submit()
        time.sleep(2)
    #cmd = input('input y to pay with this order')
    cmd = "y"
    if cmd == "y":
        driver.find_element_by_id('cashierPreConfirm').submit()
        time.sleep(1)
        pwd = [8,0,2,0,7,0]
        for word in pwd:
            driver.find_element_by_id('spwd_unencrypt').send_keys(word)
            time.sleep(0.3)
        time.sleep(2)
        print('wait to pay success')
        while not driver.current_url.startswith('https://tradenj.kaola.com/order/pay_success.html'):
            time.sleep(2)
        driver.close()
    return True


def get_real_phone_recharge(driver, face_value_list, channel, discount):
    """
    costless order
    :param driver:
    :param faceValue:
    :param channel: "KAO_LA", "TAO_BAO"
    :return:
    """
    driver.refresh()
    print(driver.get_cookies())
    jsession = driver.get_cookie('logged')['value']
    cnt = 0
    settle_rate_url = 'http://api.chadan.cn/product/queryCostProductPrice?JSESSIONID=%s&channel=%s' % (jsession, channel)
    driver.get(settle_rate_url)
    result = load_json(driver)
    if result.get('errorCode') != 200:
        print('unable to load discount')
        return
    if result.get('data')[0]['discount'] < discount:
        print('unable to satisify discount', result.get('data')[0]['discount'])
        return
    while True:
        time.sleep(3)
        cnt += 1
        print('#%d to get real phone recharge' % cnt)
        driver.get('http://api.chadan.cn/order/costOrderPool?JSESSIONID=%s&channel=%s' % (jsession, channel))
        result = load_json(driver)
        if result.get('errorCode') != 200:
            continue
        face_key = None
        faceValue = None
        for fv in face_value_list:
            face_key = 'faceValue%d' % fv
            if result.get('data').get(face_key) <= 0:
                continue
            faceValue = fv
            break
        if faceValue is None:
            continue
        driver.get('http://api.chadan.cn/order/getDirectCostOrder?JSESSIONID=%s&faceValue=%d&channel=%s' %(jsession, faceValue, channel))
        result = load_json(driver)
        print(result)
        if result.get('errorCode') == 200:
            order_id = result.get('data').get('id')
            place_order_url = result.get('data').get('naughty')
            url = 'http://api.chadan.cn/order/costOrderWaitRecharge?JSESSIONID=%s&id=%s&faceValue=%d' % (
                jsession, order_id, faceValue)
            driver.get(url)
            phone_result = load_json(driver)
            phone = None
            if phone_result.get('errorCode') == 200:
               phone = phone_result.get('data').get('rechargeAccount')
            if phone is None:
                cmd = input('could not find recharge phone, please handle manually')
                if cmd != "n":
                    break
                continue
            print(phone_result)
            print('Order found with charge value %d' % faceValue)
            offer = kaola_offer(driver, place_order_url)
            if kaola_do_order(driver, phone):
                print('charge order succeed to make')
                report_kaola_order(driver, order_id, jsession, faceValue)
            else:
                print('Unable to make order and pay')
            #cmd = input('input n for next, other to quit')
            #if cmd != "n":
            #    break


def report_kaola_order(driver, chadan_order_id, jsession, faceValue):
    driver.switch_to.window(driver.window_handles[0])
    report_url = 'http://api.chadan.cn/order/reportDirectCostOrder?JSESSIONID=%s&id=%s&faceValue=%d' % (
        jsession, chadan_order_id, faceValue
    )
    driver.get(report_url)
    result = load_json(driver)
    if result.get('errorCode') == 200:
        return True
    return False


def go_dashboard(driver, user_info):
    driver.get('http://chadan.wang/wang/makeMoney')
    time.sleep(3)
    if driver.current_url.startswith('http://chadan.wang/wang/login'):
        login(driver, user_info)


def get_order(driver, param):
    order_url: str = 'http://api.chadan.wang/order/getOrderdd623299?JSESSIONID=%s&faceValue=%d&province=&amount=1&channel=2' \
                     '&operator=%s' % (param['jsession'], param['faceValue'], param['operator'])
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


def get_job(driver, charge_type, oper_type,jsession):
    """
        get order form chadang
    :param driver:
    :param charge_type: money to charge
    :param oper_type: MOBILE,UNICOM,TELECOM,None. Choose one from four, None for not specified.
    :return:
    """
    pool_url = 'http://api.chadan.wang/order/pooldd623299?JSESSIONID=%s' % jsession
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
        return get_order(driver, {'faceValue': charge_type, 'operator': operator['operator'], 'jsession' : jsession})
    return {'code': -2}


def login(driver, user_info):
    print('Login@',driver.current_url)
    driver.find_element_by_id('account').send_keys(user_info['username'])
    driver.find_element_by_id('password').send_keys(user_info['password'])
    driver.execute_script('$("#loginButton").trigger("touchstart")')
    time.sleep(5)
    print('After login page@', driver.current_url)


def confirm_order(driver, charge_phone, jession):
    confirm_url = 'http://chadan.wang/wang/makeMoney'
    driver.get(confirm_url)
    time.sleep(2)
    try:
        driver.find_element_by_class_name('kfclose').click()
    except:
        print('Not kfclose')
    time.sleep(1)
    driver.get(driver.find_element_by_class_name('success').get_attribute('href'))
    time.sleep(3)
    driver.find_element_by_id('sureReport').click()
    time.sleep(3)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    check_url = 'http://api.chadan.cn/order/queryUserOrders?startTime=%s 00:00:00&endTime=%s 23:59:59&orderStatus=3' \
                '&JSESSIONID=%s' % (today, today, jession)
    driver.get(check_url)
    qry_result = json.loads(driver.find_element_by_xpath('/html/body/pre').text)
    if qry_result['errorCode'] == 200 and qry_result['data']['total'] == 0:
        print('charge phone[%s] report success' % charge_phone)
        return True
    print('Report phone[%s] to sucess fail, please check' % charge_phone)
    print(qry_result)

    return False


def get_charge_order(driver, charge_money, operator_type):
    cnt = 0
    sec = 3
    jsession = driver.get_cookie('logged')['value']
    while True:
        result = get_job(driver, charge_money, operator_type, jsession)
        if result['code'] == 0:
            print(
                '%s--charge phone:%s' % (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f'), result['chargePhone']))
            cmd = input('input n to get next charge phone with %d, q to exit\n' % charge_money)
            if confirm_order(driver, result['chargePhone'], jsession) and cmd == "n":
                continue
            else:
                break
        cnt += 1
        print('#%d.sleep %s sec' % (cnt, sec))
        time.sleep(sec)


def has_qr_job(driver, amount, operator_type):
    pool_url = 'http://chadan.wang/order/payForAnotherOrderPooldd623299?JSESSIONID=%s' % driver.get_cookie('logged')['value']
    driver.get(pool_url)
    try:
        pool = json.loads(driver.find_element_by_xpath('/html/body/pre').text)
    except:
        print('cloud not get pool', driver.page_source)
        traceback.print_exc()
        return {'code': -3}
    face_val_key = 'faceValue%d' % amount
    if pool['errorCode'] != 200:
        return {'code' : -2}
    for elem in pool['data']:
        target_op = False
        for op_typ in operator_type:
            if elem['operator'] != op_typ:
                continue
            target_op = True
        if target_op and elem[face_val_key] and elem[face_val_key] > 0:
            return {'code' : 0, 'operator' : elem['operator'], 'faceValue' : amount, 'amount' : 1}
    return {'code' : -1}


def make_qr_order(driver, info):
    url = 'http://api.chadan.cn/order/getPayForAnotherOrderdd623299?JSESSIONID=%s&faceValue=%s&operator=%s&amount=%d&' \
          'channel=1' %(info['logged'], info['faceValue'], info['operator'], info['amount'])
    driver.get(url)
    try:
        order_info = json.loads(driver.find_element_by_xpath('/html/body/pre').text)
    except:
        print('cloud not get qr order', driver.page_source)
        traceback.print_exc()
        return {'code': -3}

    print(order_info)
    if order_info['errorCode'] != 200:
        return {'code' : -2, 'msg' : order_info['errorMsg']}
    if len(order_info['data']) == 0:
        return {'code' : -1, 'msg' : 'empty order'}
    return {'code' : 0, 'msg' : 'success', 'order_id' : order_info['data'][0]['orderId']}


def get_qr_order(driver, amount, operator_type):
    cnt = 0
    sec = 3
    logged = driver.get_cookie('logged')['value']
    print(logged)
    while True:
        cnt = cnt + 1
        result = has_qr_job(driver, amount, operator_type)
        if result['code'] != 0:
            print('#%d sleep %d(s)' % (cnt, sec))
            time.sleep(sec)
            continue
        result['logged'] = logged
        result = make_qr_order(driver, result)
        if result['code'] != 0:
            print('#%d could not make order:%s.Sleep %d(s)' % (cnt, result['msg'], sec))
            time.sleep(sec)
            continue
        print('#%d make order with orderId[%s] and faceValue[%d]' % (cnt, result['order_id'], amount))
        cmd = input('Input n when you are ready to get next, other else will be exit')
        if cmd != "n":
            break


chrome_options = Options()
conf = config.GyConfig()
if conf.is_headless():
    chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument(
    'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"')
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
    user_info = conf.get_user_info()
    go_dashboard(driver, user_info)
    order_type_list = ["QR", "MBL_CHRG", "PHN_RECH", "KAO_LA"];
    order_type = order_type_list[1]
    if order_type == "QR":
        print('Go to get QR order')
        amount = 500
        ot_array = [None, "MOBILE", "UNICOM", "TELECOM"]
        operator_type = list()
        operator_type.append(ot_array[2])
        #operator_type.append(ot_array[3]), operator_type.append(ot_array[1])
        get_qr_order(driver, amount, operator_type)
    elif order_type == "KAO_LA":
        faceValue_Array = [50, 100, 200, 300, 500]
        faceValue = [faceValue_Array[0], faceValue_Array[1]]
        driver.execute_script('window.open("https://www.baidu.com");')
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[1])
        KaolaUtil.mobile_login(driver, user_info)
        time.sleep(1)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        get_real_phone_recharge(driver, faceValue, order_type, 9.95)
    else:
        charge_money = 100
        ot_array = [None, "MOBILE", "UNICOM", "TELECOM"]
        operator_type = ot_array[1]
        get_charge_order(driver, charge_money, operator_type)
except:
    traceback.print_exc()
finally:
    driver.close()
    driver.quit()
    print('END.OF.PROG')