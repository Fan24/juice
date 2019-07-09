#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
from gy.jd import Common
from gy.util import common
from gy.mf178.mf178 import MF178
import time
import traceback

conf = config.GyConfig()
param = {
    "charge_url": "https://newcz.m.jd.com/newcz/index.action",
    "mobile_jd_home_url": "https://home.m.jd.com",
    "jdpay_passowrd" : ""
}


def get_wait_to_pay_recharge_order_id(driver, mobile_no):
    driver.get('https://order.jd.com/center/list.action?s=1')
    js_get_order_id = '''
        var $tbody = $("tbody").first();
        var mobile_info = $tbody.find(".o-info").text();
        if(mobile_info!=arguments[0]){
            return "NA";
        }
        return $tbody.find("a[name=orderIdLinks]").text();
    '''
    pattern = "充值号码：%s****%s" % (mobile_no[0:3], mobile_no[-4:])
    print(pattern)
    order_id = driver.execute_script(js_get_order_id, pattern)
    if order_id == "NA":
        return None
    return order_id


def get_wechat_pay_qr(driver, order_id, screen_path):
    driver.get('http://chongzhi.jd.com/order/order_pay.action?orderId=%s' % order_id)
    driver.execute_script('$("#weixin").click()')
    time.sleep(2)
    web_qr_file = '%swcp_qr.png' % screen_path
    driver.get_screenshot_as_file(web_qr_file)
    print('OrderID:%s wechat QR pay address from:\thttp://%s/pj/gy/jd/wcp_qr.html' % (order_id, common.get_host_ip()))
    command = input('please input command: q for exit, n for next, f for fresh QR')
    if command == "f":
        return get_wechat_pay_qr(driver, order_id, screen_path)
    return command


def get_order(source_type, driver, source_user_info, face_value, op_type, pay_type, discount_bar):
    if source_type == "MF178":
        mf178_order(driver, source_user_info, face_value, op_type, pay_type, discount_bar)
        return


def mf178_order(driver, source_user_info, face_value, op_type, pay_type, discount_bar):
    mf178 = MF178(source_user_info)
    cnt = 0
    retry = 3
    while not mf178.prepare_env(driver, conf.get_screen_path()):
        cnt += 1
        if cnt > retry:
            break
        print('Retry to prepare environment#', cnt)
    if cnt > retry:
        print('Unable to prepare environment, exit')
        exit(1)
    ticker = 0
    command = None
    while True:
        ticker += 1
        time.sleep(5)
        print('#%d to get order from mf178' % ticker)
        mf178.go_home(driver)
        result = mf178.get_order(driver, face_value, 1, op_type)
        if result.get('code') != '0' or result.get('phone') is None:
            continue
        recharge_phone_no = result.get('phone')
        place_charge_order(driver, result.get('phone'), face_value, discount_bar)
        time.sleep(3)
        if pay_type == "wechat":
            print('please pay by wechat manually')
            jd_order_id = get_wait_to_pay_recharge_order_id(driver, recharge_phone_no)
            if jd_order_id is None:
                print('Unable to get recharge order id with phone[%s]' % recharge_phone_no)
                command = input('Please input n for next order, q for exit when you handled this charge manually')
                if command == "n":
                    continue
                break
            else:
                print('JD phone recharge order ID:%s' % jd_order_id)
                command = get_wechat_pay_qr(driver, jd_order_id, conf.get_screen_path())
        try:
            report_result = mf178.report(driver)
            if report_result.get('type') != 'refresh':
                print('report error', report_result)
                print('order info', result)
                input('please interupt from manual, input any to continue')
            if command != "n":
                print('Exit!')
                break
        except:
            print(report_result)
            traceback.print_exc()


def place_charge_order(driver, mobile_phone, faceamount, discount):
    driver.execute_script('window.open("%s", "_blank")' % param['charge_url'])
    driver.switch_to.window(driver.window_handles[-1])
    print('Here we ready to charge phone %s with faceamout %s' % (mobile_phone, faceamount))
    driver.find_element_by_id('J-mobile').send_keys(mobile_phone)
    time.sleep(1)
    driver.find_element_by_xpath('//li[@faceamount="%d"]' % faceamount).click()
    time.sleep(1)
    pay_amount = float(driver.find_element_by_id('onlinePay').text)
    if pay_amount > faceamount * discount:
        print('Recharge with face amount[%d] need to pay %.2f, but we require less than %.2f after discount[%f]' %
              (faceamount, pay_amount, faceamount * discount, discount))
        return False
    driver.find_element_by_id('J-submit').click()
    time.sleep(2)
    try:
        pay_pw_elem = driver.find_element_by_class_name('pop-input')
        if param.get('jdpay_password') == "":
            param['jdpay_password'] == input('please input jd pay password once')
        pay_pw_elem.send_keys(param.get('jdpay_password'))
        driver.find_element_by_id('simplePopBtnSure').click()
    except:
        print('Do not need to input pay password')



def jd_login(driver, userInfo, screen＿path):
    for cnt in range(1, 4):
        print('#%s to login' % cnt)
        if userInfo.get('password') is None:
            pwd = input('Please input password for user[%s]' % userInfo['username'])
            userInfo['password'] = pwd
        if login_if_not(driver, userInfo) and Common.web_login(driver, userInfo, screen＿path):
            print('We login jd success!')
            return True
    return False


def login_if_not(driver, userInfo):
    print('Go home center ', param['mobile_jd_home_url'])
    driver.get(param['mobile_jd_home_url'])
    print('we are at', driver.current_url)
    time.sleep(5)
    if driver.current_url.startswith('https://plogin.m.jd.com/user/login.action'):
        Common.jd_login(driver, userInfo, conf)
    if driver.current_url.startswith(param['mobile_jd_home_url']):
        return True
    return False


userInfo = conf.get_user_info()
chrome_options = Options()
if conf.is_headless():
    chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument(
    'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) '
    'Version/9.0 Mobile/13B143 Safari/601.1"')
chrome_options.add_argument('--lang=zh-CN.UTF-8')
chrome_options.add_argument('--user-data-dir=%s' % conf.get_chrome_user_dir())
print('chrome user path:%s' % conf.get_chrome_user_dir())
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
    phone_source_user_info = {'username' : userInfo['phone_source_user_name'],
                              'password' : userInfo['phone_source_user_password']}
    jd_login(driver, userInfo, conf.get_screen_path())
    face_value = 100
    operators = {"MOBILE": "1", "UNICOM": "2", "ANY": "0"}
    operator_key = ["UNICOM", "MOBILE", "ANY"]
    key_ind = 2
    pay_types = ["wechat"]
    pay_type_ind = 0
    discount_bar = 0.98
    mf178_order(driver, phone_source_user_info, face_value, operators[operator_key[key_ind]],
                pay_types[pay_type_ind], discount_bar)
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.LINE')

