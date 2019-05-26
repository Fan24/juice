#!/usr/bin/env python
from gy.ninetyninth.ninetyninth import Ninetyninth
from gy.util.common import OPERATOR
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
import traceback


chrome_options = Options()
conf = config.GyConfig()
if conf.is_headless():
    chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument(
    'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 '
    '(KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"')
chrome_options.add_argument('--lang=zh-CN.UTF-8')
chrome_options.add_argument('--user-data-dir=%s' % conf.get_chrome_user_dir_by_key('chrome_user_dir_99'))
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
    nn = Ninetyninth(conf.get_user_info())
    nn.login(driver)
    face_value = 100
    ticker = 0
    operator = OPERATOR.TELECOM
    print(operator.value)
    while True:
        ticker += 1
        print("#%d loop to get order" % ticker)
        nn.get_phone_charge_order_til_success(driver, face_value, operator)
        cmd = input('please input n for next order with face value[%d], other to exit, after order complete'
                    % face_value)
        if not nn.confirm_order(driver):
            input('Unable to report this order to success, please handle manaully and press anything to continue')
        if cmd == "n":
            continue
        break
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.PROG')
