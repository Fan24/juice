#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
from gy.jd import Common
from gy.util import common
import time
import traceback
import re

conf = config.GyConfig()
param = {
    "mobile_jd_home_url": "https://home.m.jd.com"
}


def order_clear(driver):
    driver.get(param['mobile_jd_home_url'])
    time.sleep(2)
    driver.execute_script('$(".entrance_text").first().click()')
    if driver.execute_script('return $(".oh_btn").length;') > 0:
        return False
    return True


def get_pay_order_info_and_prepare_to_pay(driver):
    order_info = {}
    driver.get(param['mobile_jd_home_url'])
    driver.execute_script('$(".entrance_text").first().click()')
    order_info['order_id'] = driver.execute_script('return $(".oh_btn").first().attr("data-orderid");')
    driver.execute_script('$(".oh_btn").first().click()')
    time.sleep(3)
    order_amount = driver.execute_script('return $(".JS-pay-total").text();')[1:]
    order_info['order_amount'] = float(order_amount)
    amount_to_pay = re.compile('\d+.\d{2}').search(driver.execute_script('return $(".pay-next").text();')).group()
    print(amount_to_pay)
    order_info['order_to_pay_amount'] = float(amount_to_pay)
    return order_info


def ready_to_inputpw(driver):
    try:
        amount = driver.find_element_by_class_name('remark').text
        for x in range(0, 10):
            if not driver.find_element_by_css_selector('div[data-key="%d"]' % x).is_displayed():
                return None
        return amount
    except:
        return None


def pay_order(driver, order_info, safe_amount, pay_password, screen_path):
    for x in range(0, 2):
        print('refresh #', x)
        #driver.refresh()
        driver.execute_script('location.reload();')
        pay_ready = 0
        while True:
            pay_ready += 1
            text_pay_amount = driver.execute_script('return $(".pay-next").text();')
            search_result = re.compile('\d+.\d{2}').search(text_pay_amount)
            if search_result is not None:
                amount_to_pay = search_result.group()
                print('Find amount to pay %s with loop #%d' % (amount_to_pay, pay_ready))
                break
        if order_info['order_amount'] - float(amount_to_pay) >= safe_amount:
            print('We arrive safe zone, order amount %.2f, actually pay: %.2f' %
                  (order_info['order_amount'], float(amount_to_pay)))
            driver.execute_script('$(".confirm-pay").trigger("touchend");')
            pswd_ready = 0
            need_password = True
            while True:
                pswd_ready += 1
                if ready_to_inputpw(driver) is None:
                    if pswd_ready > 200:
                        need_password = False
                        break
                    continue
                temp = driver.find_element_by_class_name('remark').text
                result = re.compile('\d+.\d{2}').search(temp)
                if result is not None:
                    print('Password input ready with loop #', pswd_ready)
                    break
            if not need_password:
                return True
                break
            for ps in pay_password:
                dk = 'div[data-key="%d"]' % ps
                driver.find_element_by_css_selector(dk).click()
            captch_dir = '%sjd_pay.png' % screen_path
            time.sleep(2)
            driver.get_screenshot_as_file(captch_dir)
            print('URL to see pay result \nhttp://%s/pj/gy/jd/web_pay_result.html' % common.get_host_ip())
            print('We sleep a while before to end!')
            time.sleep(5)
            return True
    return False


def jd_login(driver, userInfo, conf):
    for cnt in range(1, 4):
        print('#%s to login' % cnt)
        driver.get(param['mobile_jd_home_url'])
        time.sleep(2)
        if driver.current_url.startswith(param['mobile_jd_home_url']):
            print('Login success!')
            return True
        if Common.jd_login(driver, userInfo, conf):
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
    if not jd_login(driver, userInfo, conf):
        print('Login FAIL, exit')
        exit(1)
    order_info = get_pay_order_info_and_prepare_to_pay(driver)
    print('OrderID:%s, order amount:%.2f' % (order_info['order_id'], order_info['order_amount']))
    Common.block_precise_until_start(False)
    safe_amount = 2.0
    if pay_order(driver, order_info, safe_amount, userInfo['pay_password'], conf.get_screen_path()) \
            and order_clear(driver):
        print('Pay complete')
    else:
        print('Pay failed')
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.LINE')
