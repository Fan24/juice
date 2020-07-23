#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from requests.cookies import RequestsCookieJar
from gy import config
import time
import logging
import json
import traceback
import requests


conf = config.GyConfig()
param = {
    "order_list_url": "https://order.m.fenqile.com/index.html#/order/list?type=all"
}
'''
try: # for Python 3
    from http.client import HTTPConnection
except ImportError:
    from http import HTTPConnection
HTTPConnection.debuglevel = 1

logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
'''

s = requests.Session()


def get_order_list(offset, limit, detail_urls, last_include_url, exclude_order_id):
    print('offset:%d, limit:%d' % (offset, limit))
    url = 'https://order.m.fenqile.com/route0001/order/getOrderInfoDetail.json'
    str_data = '''{"system":{"controller":""},"data":{"state_filter":"","offset":%d,"limit":%d}}''' % (offset, limit)
    r = s.post(url, str_data)
    data_json = r.json()
    if data_json['result'] == 0:
        rows = data_json['data']['result_rows']
        for i in rows:
            order_id = i['order_info']['order_id']
            if i['template_content'][0]['state_info']['state_desc'] == '已关闭':
                print('CloseOrder:%s' % order_id)
                continue
            du = i['order_info']['detail_url']
            product_info = i['template_content'][1]['order_goods_info']['goods_info']['product_info']
            if exclude_order_id.get(order_id) == 1:
                print('Exlucde order id: %s' % order_id)
            else:
                detail_urls.append({'detail_url': du, 'order_id': order_id, 'product_info': product_info})
            if du == last_include_url:
                print('We find the last detail url')
                return False
    else:
        print(data_json)
        return False
    return True


def fql_login(driver):
    get_sms_code = False
    for cnt in range(1, 4):
        print('#%s to login' % cnt)
        driver.get(param['order_list_url'])
        time.sleep(2)
        if driver.current_url.startswith(param['order_list_url']):
            print('Login success!')
            if get_sms_code:
                print('Sleep 60(s) before get sms code')
                time.sleep(60)
            return True
        while not driver.current_url.startswith(param['order_list_url']):
            print('please login')
            get_sms_code = True
            time.sleep(5)
    return False


def cookies_transfer(driver):
    for cookie in driver.get_cookies():
        cookie_jar = RequestsCookieJar()
        cookie_jar.set(cookie['name'], cookie['value'], domain=cookie['domain'])
        s.cookies.update(cookie_jar)


def get_exclude_order_id():
    filename = '%s/data/fenqile.exclude' % conf.get_project_path()
    exclude_order_id = {}
    try:
        print('Get exclude order id from %s' % filename)
        fp = open(filename, "r")
        for line in fp.readlines():
            line = line.replace('\n', '')
            if exclude_order_id.get(line) == 1:
                print('Duplicate exclude order id %s' % line)
                continue
            exclude_order_id[line] = 1
        fp.close()
    except IOError:
        print('Open file[%s] error, file not exist' % filename)
    return exclude_order_id


def get_card_code(detail_urls):
    url = 'https://trade.m.fenqile.com/order/query_verify_fulu_and_coupon_sms.json'
    param = '''{"send_type":8,"sms_code":"%s","order_id":"%s","is_weex":1, "sale_type":800}'''
    code_count = 0
    sms_code = None
    car_pool = []
    get_sms_time = time.time()
    last_url = detail_urls[-1]
    for detail in detail_urls:
        if code_count == 0:
            code_count = 5
            sms_code = get_sms()
            get_sms_time = time.time()
            if sms_code is None:
                sms_code = input('Please input sms manually')
                get_sms_time = time.time()
        code_count = code_count - 1
        print('----%s' % detail['detail_url'])
        time.sleep(3)
        r = s.post(url, param % (sms_code, detail['order_id']))
        print(r.text)
        data = r.json()
        if data['retcode'] == 0:
            for info in data['virtual_info']['fulu_info']:
                card_no = info.get('card_number')
                if card_no is not None:
                    card_no = info['card_number']['value']
                else:
                    card_no = ""
                card_pw = info.get('passwd')
                if card_pw is not None:
                    card_pw = info['passwd']['value']
                else:
                    card_pw = ""
                print('%s\t%s\t%s\t%s' % (card_no, card_pw, detail.get('product_info'), detail.get('order_id')))
                car_pool.append({'OrderID' : detail['order_id'],
                                 'OrderInfo' : detail.get('product_info'),
                                 'CardNo' : card_no,
                                 'CardPw' : card_pw})
        elif data['retcode'] == 70023016:
            print(data)
            code_count = code_count + 1
            sms_code = input('sms code error please input correct sms code')
        else:
            print(data)
        if code_count == 0 and last_url != detail:
            sec_to_sleep = time.time() - get_sms_time
            sec_to_sleep = 60 - sec_to_sleep
            print('Waiting to get next sms code, progress:%d/%d' % (len(car_pool), len(detail_urls)))
            print('We will sleep %d(s)' % int(sec_to_sleep))
            time.sleep(sec_to_sleep)
    for cp in car_pool:
        print('%s\t%s\t%s\t%s' % (cp['OrderID'], cp['OrderInfo'], cp['CardNo'], cp['CardPw']))
    print('Total:%d' % (len(car_pool)))


def get_sms():
    r = s.post('https://trade.m.fenqile.com/order/query_send_sms.json', '{"send_type":8,"is_weex":1}')
    if r.json()['retcode'] == 0:
        return input('please input sms code')
    print('get sms error')
    print(r.json())
    return None


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
    if not fql_login(driver):
        print('Login FAIL, exit')
        exit(1)
    cookies_transfer(driver)
    exclude_order_id = get_exclude_order_id()
    print('There is %d of exclude order id' % len(exclude_order_id))
    detail_urls = []
    limit = 10
    offset = 0
    memo = {'2423':'O20200525289842309914', '5913': 'O20200602145673103626'}
    last_order_id = input('Please input last order id to get')
    last_include_url = 'https://trade.m.fenqile.com/order/detail/%s.html' % last_order_id
    while get_order_list(offset, limit, detail_urls, last_include_url, exclude_order_id):
        offset = offset + limit
    print(len(detail_urls))
    get_card_code(detail_urls)
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.LINE')
