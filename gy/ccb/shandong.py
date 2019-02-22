#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
from gy.util import common
import time
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
    var succ = false;
    $.ajax({
            "type": "post",
            "async" : false,
            "url":  '/flow/add_cart',
            "dataType" : "json", 
            data:{
                "id": 46, 
                "type" : 3,
                "num": 1
            },
            success: function (data) {
                if(data.error=='success'){
                    succ = true; 
                }
            }
        }); 
    return succ;
    '''
    js_confrim = '''
        $("#p").val('1');
        $("#mobile").val("13632265913");
        $("#orderForm").submitForm();
    '''
    common.block_precise_until_start(False)
    print('prepare to make order')
    succ = False
    for cnt in range(1, 10):
        if driver.execute_script(js_addcart):
            succ = True
            break
    if succ is True:
        driver.get('https://mall.wktop.cn/flow/team/46')
        driver.execute_script(js_confrim)
        print('After confirm, we at ', driver.current_url)


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
