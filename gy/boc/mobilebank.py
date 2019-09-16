#!/usr/bin/env python
import requests
import logging
import traceback
import threading
import json
import os
import datetime
import time
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
    'jsession' : '0000c-h5px_n9uqUJFGLUijxSg8:cluserver10',
    'deviceToken' : 'BF91F7336A0B33A619B397AB6D3360639B5405091A42F78DE0B8B3C41185ED77',
    'cardId' : 'toppYFsXA2Nvsfvms3El8yDv2G8JKNe8',
    'cardNum' : '9F332DA182D94A81994971FE1DE418E5',
}
jf_headers = {'User-Agent' : '%E4%B8%AD%E5%9B%BD%E9%93%B6%E8%A1%8C/3.8.3 CFNetwork/978.0.7 Darwin/18.7.0',
              'reqChannelId': 'boc-mlife-app'}

s = requests.Session()
s.headers.update(jf_headers)
s.cookies.update({'JSESSIONID': params['jsession']})

body_params = {
    'txnId' : '2NEW100027',
    'couponType': 2,
    'total' : 1,
    'brandNo' : '',
    'cardNum' : params['cardNum'],
    'imei' : '18BBFA52-C78E-47D4-A142-DA0874FADC4A',
    'lon' : '113.378497',
    'lat' : '23.129389',
    'city' : '广州',
    'cityIdCde' : '440100',
    'cityId' : '440100',
    'clientVersion': '3.8.1',
    'c' : '',
    'cityIdCde': '440100',
    'deviceToken': params['deviceToken'],
    'cardId' : params['cardId']
}


def make_order(product):
    order_params = body_params.copy()
    for p in product.keys():
        order_params[p] = product[p]
    st = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f')
    print(threading.currentThread().name + ' start @' + st + '--' + product['couponId'])
    ticker = 0
    succ = False
    final_text = None
    while not succ:
        ticker = ticker + 1
        try:
            r = s.post('https://mlife.jf365.boc.cn/AppPrj/newCreatPayOrder.do', data=order_params)
            final_text = r
            stat = r.json()['stat']
            print('#%d to get:%s' % (ticker, r.json()))
            if stat == "00":
                print('Success to make order with product id:%s' % product['couponId'])
                succ = True
                break
            if stat == "33":
                print('Out of stock, unable to make order with product id:%s' % product['couponId'])
                continue
            if stat == "99":
                print('Order make before with product id:%s' % product['couponId'])
                continue
            if stat == "09":
                time.sleep(1)
        except:
            traceback.print_exc()
    end = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f')
    print('%s end @%s -- %s after run %d' % (threading.currentThread().name, end, product['couponId'], ticker))
    print(final_text.text)
    return succ


def check_env():
    req_param = {'call':'newMySelfGift', 'txnId': '2NEW100024', 'status':1, 'pageNo':1,'userId':'13632265913',
                 'reqChannel':'P', 'cityId':body_params['cityId'], 'imei':body_params['imei'], 'lon': body_params['lon'],
                 'lat': body_params['lat'], 'city': body_params['city'], 'cityIdCde': body_params['cityIdCde'],
                 'deviceToken': params['deviceToken'], 'clientVersion': body_params['clientVersion']}
    r = s.post('https://mlife.jf365.boc.cn/AppPrj/coupons.do', data=req_param)
    print(r.text)
    return r.json()['stat'] == '00'


def get_product_list():
    req_param = {'call':'newCouponList', 'txnId': '2NEW000008', 'cityId':body_params['cityId'], 'couponType':'',
           'buyType': '', 'pageNo': 1, 'imei':body_params['imei'], 'lon': body_params['lon'],
           'lat': body_params['lat'], 'city': body_params['city'], 'cityIdCde': body_params['cityIdCde'],
           'deviceToken': params['deviceToken'], 'clientVersion': body_params['clientVersion']}
    r = s.post('https://mlife.jf365.boc.cn/AppPrj/coupons.do', data=req_param)
    return r.json()


def get_product_detail(couponId):
    req_param = {
        'call' : 'newCouponDetail', 'txnId' : '2NEW000009', 'couponId' : couponId, 'cardId': body_params['cardId'],
        'cityId': body_params['cityId'], 'imei': body_params['imei'], 'lon' : body_params['lon'],
        'lat' : body_params['lat'], 'city' : body_params['city'],'cityIdCde' : body_params['cityIdCde'],
        'deviceToken': body_params['deviceToken'], 'clientVersion': body_params['clientVersion'], 'c' : body_params['c']
    }
    r = s.post('https://mlife.jf365.boc.cn/AppPrj/coupons.do', data=req_param)
    return r.json()


def match_product_list(target_product_list):
    match_product = []
    all_product = get_product_list()
    print(all_product)
    for tl in target_product_list:
        print('Get %s detail' % tl['id'])
        while True:
            detail = get_product_detail(tl['id'])
            if detail['stat'] != "00":
                continue
            match_product.append({'couponId': tl['id'], 'payMoney': detail['price'], 'points': detail['loyt'],
                                  'couponType': detail['couponType']})
            break
    return match_product


def load_coupon_id(day):
    if day > 0:
        week_day = day
    else:
        week_day = datetime.datetime.now().weekday() + 1
    PROJ_PATH= "E:/OnionMall/"
    if "PROJ_PATH" in os.environ:
        PROJ_PATH = os.environ['PROJ_PATH']
    with open('%sgy/boc/jf365.json' % PROJ_PATH, encoding='utf-8') as fp:
        return json.load(fp)['%d' % week_day]

ticker = 1
while not check_env():
    print('#%d prepare environment error' % ticker)
    ticker = ticker + 1
product_list = match_product_list(load_coupon_id(-1))
print(product_list)
threads = []
for x in range(0, 1):
    for t in [threading.Thread(target=make_order, args=(pd, )) for pd in product_list]:
        threads.append(t)
Common.block_precise_until_start(True, check_env)
for t in threads:
    t.start()
for t in threads:
    t.join()
print('We end')
