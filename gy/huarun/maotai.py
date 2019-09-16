import requests
from urllib.parse import quote
import logging
import traceback
import re
import threading
import json
import os
import datetime
import time
import heapq
from gy.jd import Common

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

params = {
    'cityId' : '869',
    'ruleId' : '108',
    'longitude' : '113.361096',
    'latitude' : '23.193402',
    'max_retry': 5,
    'thread_count': 2
}
headers = {
    'osVersion': '12.4.1',
    'userId': '684262',
    'networkType': '4g',
    'unique': 'ios-A98DEB4C-DA46-410A-B17B-845B48369A8C',
    'userSession' : 'FE81B08A984DBFE631AEE0699DC5CC86',
    'subsiteId': '143',
    'channel': 'mobile',
    'os': 'ios',
    'appkey' : 'ef1fc57c13007e33',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'appVersion': '2.3.1',
    'language': 'zh-CN',
    'X-Requested-With': 'com.crv.wanjia',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
}
cookies = {
    'DISTRIBUTED_JSESSIONID': '6E17C405CC5F4DD78294C95B15CE68D6'
}
s = requests.Session()
s.headers.update(headers)
#s.cookies.update(cookies)


def get_user_info():
    r = s.post('https://app.crv.com.cn/app_api/v1/dc-app-api/mobile/api/user/info')
    return r.json()


def get_sale_store(cityId, ruleId):
    pm = '''{'cityId':'%s', 'ruleId' : '%s'}''' % (cityId, ruleId)
    url = 'https://app.crv.com.cn/app_timelimit/v1/dc-timelimit/presale/findPreSaleStore?param=%s' % (quote(pm))
    r = s.get(url)
    return r.json()


def get_store_detail(ruleId, code, longitude, latitude):
    pm = '''{"ruleId":"%s","code":"%s","longitude":%s,"latitude":%s}''' % (ruleId, code, longitude, latitude)
    url = 'https://app.crv.com.cn/app_timelimit/v1/dc-timelimit/presale/getPreSaleActivity?param=%s' % (quote(pm))
    r = s.get(url)
    return r.json()


def get_top_n_to_buy_store(stores, top):
    details = []
    for i in range(0, len(stores)):
        store = stores[i]
        print('#%d' % i)
        try:
            detail = get_store_detail(params['ruleId'], store['code'], params['longitude'], params['latitude'])
            time.sleep(3)
            if 0 == detail['stateCode']:
                details.append(detail)
        except:
            print('unable to get store %s avail to buy' % store['storeName'])
    details = heapq.nlargest(top - 1, details, key=lambda k: k['data']['saleCount'])
    return details


def get_token(productId, presaleRuleId, ncmsMemberId, mobile):
    pm = '''{"productId":%s,"presaleRuleId":"%s","ncmsMemberId":"%s","mobile":"%s"}''' \
         % (productId, presaleRuleId, ncmsMemberId, mobile)
    url = 'https://app.crv.com.cn/app_timelimit/v1/dc-timelimit/presale/token?param=%s' % (quote(pm))
    r = s.get(url)
    return r.json()


def order_tail_success_or_soldout(token, presaleRuleId, presaleTimeId, presaleStockCycleId, goodsId,
                                  productId, memberId, mobile, amount, max_retry):
    pm = '''{"token":"%s","presaleRuleId":"%s","presaleTimeId":%s, "presaleStockCycleId":%s,"goodsId":%s,"productId":%s,"ncmsMemberId":"%s", "mobile":"%s","number":%d}''' % (token, presaleRuleId, presaleTimeId, presaleStockCycleId, goodsId, productId,
                                     memberId, mobile, amount)
    url = 'https://app.crv.com.cn/app_timelimit/v1/dc-timelimit/presale/presaleLog/addTimeLimit'
    pd = 'param=%s' % pm
    ticker = 0
    while ticker < max_retry:
        ticker = ticker + 1
        r = None
        try:
            r = s.post(url, data=quote(pd))
            if 200 != r.status_code:
                print(r.text)
            data = r.json()
            if 0 == data['stateCode']:
                print('We succeed to make order')
                return True
            if 1 == data['stateCode']:
                continue
            time.sleep(0.3)
            print('%s#%d:%s' % (threading.currentThread().name, ticker, r.text))
        except:
            print('%s#%d unable to make order' % (threading.currentThread().name, ticker))
    return False


print('Get user info')
user_info = get_user_info()
time.sleep(1)
store_info = None
print('Get stores info')
while True:
    store_info = get_sale_store(params['cityId'], params['ruleId'])
    time.sleep(2)
    if 0 == store_info['stateCode']:
        break
print('Get max avail store info')
top_n = get_top_n_to_buy_store(store_info['data'], 3)
print(top_n)
ind = len(top_n)
threads = []
while ind >= 0:
    ind = ind - 1
    target_store = top_n[ind]
    print('Get token for store:%s' % target_store['data']['store']['storeName'])
    while True:
        token = get_token(target_store['data']['goodsInfo'][0]['productId'], target_store['data']['preSaleRuleId'],
                          user_info['data']['ncmsMemberId'], user_info['data']['mobile'])
        time.sleep(2)
        if 0 == token['stateCode'] and re.match('^[a-zA-Z0-9]+$', token['data']['result']):
            target_store['token'] = token['data']['result']
            break
    for x in range(0, params['thread_count']):
        t = threading.Thread(target=order_tail_success_or_soldout, args=(target_store['token'], target_store['data']['preSaleRuleId'],
            target_store['data']['preSaleTimeId'], target_store['data']['goodsInfo'][0]['preSaleStockCycleId'],
            target_store['data']['goodsInfo'][0]['goodsId'], target_store['data']['goodsInfo'][0]['productId'],
            user_info['data']['ncmsMemberId'], user_info['data']['mobile'], 2, params['max_retry'],))
        threads.append(t)
Common.block_precise_until_start(True, None)
for t in threads:
    t.start()
for t in threads:
    t.join()
print('End')
