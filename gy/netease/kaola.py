#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
from gy.util import common
from gy.jd import Common
import time
import datetime
import traceback

conf = config.GyConfig()
param = {
    "user_center_url": "https://m-user.kaola.com/user/usrCenter.html",
    "pc_order_url": "https://buy.kaola.com/personal/my_order_new.html"
}


def pc_login(driver, userInfo, conf):
    try:
        driver.switch_to.frame(driver.find_element_by_id('loginbox').find_element_by_tag_name('iframe'))
        driver.execute_script('''
            document.getElementById('phoneipt').value=arguments[0];
            document.getElementsByClassName('getsmscode')[0].click()
        ''', userInfo['username'])
        sms_code = Common.get_sms_code()
        driver.execute_script('''
            document.getElementsByName('phonecode')[0].value=arguments[0];
            document.getElementsByClassName('u-loginbtn')[0].click();
        ''', sms_code)
        time.sleep(2)
        if driver.current_url.startswith(param['pc_order_url']):
            return True
        return False
    except:
        traceback.print_exc()
        return False


def mobile_login(driver, userInfo, conf):
    try:
        driver.execute_script('''
            if(document.getElementsByClassName('km-modal__container-outer')[0].style.display==""){
               document.getElementsByClassName('opt-btn_agree')[0].click(); 
            }
        ''')
        driver.switch_to.frame(driver.find_element_by_id('loginbox1').find_element_by_tag_name('iframe'))
        driver.execute_script('''
            document.getElementById('phoneipt').value=arguments[0];
            document.getElementsByClassName('getsmscode')[0].click()
        ''', userInfo['username'])
        sms_code = Common.get_sms_code()
        driver.execute_script('''
            document.getElementsByName('phonecode')[0].value=arguments[0];
            document.getElementsByClassName('u-loginbtn')[0].click();
        ''', sms_code)
        time.sleep(2)
        if driver.current_url.startswith(param['user_center_url']):
            return True
        return False
    except:
        traceback.print_exc()
        return False


def login_if_logout(driver, userInfo, conf, type):
    url = param.get('user_center_url')
    if type == "pc":
        url = param.get('pc_order_url')
    for cnt in range(1, 4):
        print('#%s to login' % cnt)
        driver.get(url)
        time.sleep(2)
        if driver.current_url.startswith(url):
            return True
        if type == "pc" and pc_login(driver, userInfo, conf):
            return True
        if type != "pc" and mobile_login(driver, userInfo, conf):
            return True
    return False


def make_order(driver, product_url, face_value, discount, screen_path):
    count = 0
    succ = False
    while count < 10:
        count = count + 1
        price = float(driver.execute_script('''
            return document.getElementsByName('goods[0].tempCurrentPrice')[0].value;
        '''))
        print('PRICE[%.2f], discount[%.2f]' % (price, discount))
        if price > face_value * discount:
            continue
        driver.execute_script('''
            document.getElementsByName('goods[0].tempBuyAmount')[1].value = 100;
                document.getElementById('buyBtn').click();''')
        while driver.current_url.startswith(product_url):
            continue
        confirm_page_url = driver.current_url
        print('Time to click buyBtn[%s]' % (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f')))
        driver.execute_script('''
            document.getElementsByClassName('z-submitbtn')[0].click();
            console.debug('to-click confirm');
            ''')
        print('Time to click confirm[%s]' % (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f')))
        time.sleep(2)
        if driver.current_url != confirm_page_url:
            succ = True
        break
    print('We loop %d time(s)' % count)
    driver.fullscreen_window()
    result_shot = '%skl_order.png' % screen_path
    driver.get_screenshot_as_file(result_shot)
    print('URL to see make order result \nhttp://%s/pj/gy/netease/order_result.html' % common.get_host_ip())
    if succ:
        print('Success to make order')
    else:
        print('Unable to make order')
    return succ


userInfo = conf.get_user_info()
chrome_options = Options()
if conf.is_headless():
    chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-web-security')
##chrome_options.add_argument(
 ##   'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) '
  ##  'Version/9.0 Mobile/13B143 Safari/601.1"')
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

driver.set_window_size(900, 1200)
try:
    web_mode = "pc"
    if not login_if_logout(driver, userInfo, conf, web_mode):
        print('Login FAIL, exit')
        exit(1)
    print('Login success with user', userInfo['username'])
    app_store_product_id = {
        "1000" : "5288081",
        "500" : "5287149",
        "200" : "5287147",
        "100": "5286150",
        "50": "5286007"
    }
    product_face = "200"
    app_store_product_url = "https://goods.kaola.com/product/%s.html" % app_store_product_id[product_face]
    driver.get(app_store_product_url)
    Common.block_until_start(False)
    discount = 0.95
    make_order(driver, app_store_product_url, int(product_face), discount, conf.get_screen_path())

except:
    traceback.print_exc()
finally:
    input('input to end')
    driver.close()
    driver.quit()
    print('END.OF.LINE')
