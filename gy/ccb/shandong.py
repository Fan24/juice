#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
from gy.util import common
import time
import datetime
import math
import traceback


def prepare_env(driver, conf):
    print('Preparing environment')
    info = conf.get_user_info()
    home_index = 'https://mall.wktop.cn/?user_id=%s&CCBTIMESTAMP=%s&CCBSIGN=%s' % (info['user_id'], info['CCBTIMESTAMP'], info['CCBSIGN'])
    print('home_url:', home_index)
    driver.get(home_index)
    time.sleep(4)
    driver.execute_script('inOrder();')
    time.sleep(4)
    print(driver.current_url)
    if not driver.current_url.startswith('https://mall.wktop.cn/member/order'):
        print('Login failed!')
        return False

    print('Login succeed')
    driver.get('https://mall.wktop.cn/')
    return True


def do_order(driver):
    js_addcart = '''
        var add_cart = function(tagID){
            $.ajax({
            "type": "post",
            "async" : "true",
            "url":  '/flow/add_cart',
            "dataType" : "json", 
            data:{
                "id": 46, 
                "type" : 3,
                "num": 1
            },
            success: function (data) {
                console.info(JSON.stringify(data));
                if(data.error=='success') window.location.href='/flow/team/46';
            }
        });
        }
        for(var i = 0; i < arguments[0]; i++){
            add_cart(i); 
        }
    '''
    js_confrim = '''
        document.getElementById('p').value='1';
        document.getElementById('mobile').value='13632265913';
        document.getElementById('orderForm').submit();
    '''
    common.block_precise_until_start(False)
    print('prepare to make order')

    max_try = 8
    print("try to add cart with max:", max_try)
    driver.execute_script(js_addcart, max_try)
    print('start to check whether  succeed to add cart or not')
    max_try = 20000
    st = datetime.datetime.now()
    for test in range(1, max_try):
        if driver.current_url.endswith('46'):
            print('success to add cart, next for preparing confirm environment, execute confirm')
            driver.execute_script(js_confrim)
            print('After confirm, we at ', driver.current_url)
            return
    end = datetime.datetime.now()
    gap = math.floor((end - st).total_seconds()) - 2
    print('We use %d(s) to check if we success!' % gap)
    print('We have checked %d time(s), unable to add_cart' % max_try)


chrome_options = Options()
conf = config.GyConfig()
if conf.is_headless():
    chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument(
    '-user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 12_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A404 MicroMessenger/6.7.3(0x16070321) NetType/WIFI Language/zh_CN')
chrome_options.add_argument('--lang=zh-CN.UTF-8')
chrome_options.add_argument('--user-data-dir=%s' % conf.get_chrome_user_dir_by_key('chrome_user_dir_ccb_sd'))
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
    for cnt in range(1, 4):
        print('#%s try to prepare' % cnt)
        if prepare_env(driver, conf):
            do_order(driver)
            break
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.PROG')
