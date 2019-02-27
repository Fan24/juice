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
                console.info("TagID:" + tagID + "-----" + JSON.stringify(data));
                if(data.code == 'success' || data.error == 'success') {
                    window.location.href='/flow/team/46';
                }
            }
        });
        }
        for(var i = 0; i < arguments[0]; i++){
            add_cart(i); 
        }
    '''
    js_confrim = '''
        var post_data = {};
        //post_data.token = document.getElementsByName('token')[0].value;
        post_data.order_sn = document.getElementsByName('order_sn')[0].value;
        post_data.extension_code = document.getElementsByName('extension_code')[0].value;
        post_data.coupon_forced = document.getElementsByName('coupon_forced')[0].value;
        post_data.deposit = document.getElementsByName('deposit')[0].value;
        post_data.product_type = document.getElementsByName('product_type')[0].value;
        post_data.p = '1';
        post_data.pay_id = document.getElementsByName('pay_id')[0].value;
        post_data.num = 1;
        post_data.mobile= '13632265913';
        var confirm = function(tokenID, count, ID){
            if(count > 2) return false;
            var req_data = {};
            req_data['token'] = tokenID;
            for(var key in post_data){
                req_data[key] = post_data[key];
            }
            console.info(ID + "#" + count + "---" + JSON.stringify(req_data));
            $.post('/flow/done', req_data, function(data){
                console.info(ID + "#" + count + "---" + JSON.stringify(data));
                if(data.msg=="库存不够"){
                    return false;
                }
                if(null != data.data) confirm(data.data.token, count + 1, ID);
            });
        }
        confirm(document.getElementsByName('token')[0].value, 0, "AA");
        confirm(document.getElementsByName('token')[0].value, 0, "BB");
    '''
    common.block_precise_until_start(False)
    print('prepare to make order')

    max_try = 6
    print("try to add cart with max:", max_try)
    driver.execute_script(js_addcart, max_try)
    max_try = 20000
    print('start to check whether succeed to add cart or not with %d time(s)' % max_try)
    st = datetime.datetime.now()
    for test in range(1, max_try):
        if driver.current_url.endswith('46'):
            print('success to add cart, next for preparing confirm environment, execute confirm')
            print(driver.page_source)
            driver.execute_script(js_confrim)
            time_to_rest = 30
            print('we will sleep %d(s) before complete!' % time_to_rest)
            time.sleep(time_to_rest)
            print('After confirm , we are at ', driver.current_url)
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
