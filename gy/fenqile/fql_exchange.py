#!/usr/bin/env python
from gy import config
import time
from requests.cookies import RequestsCookieJar
import logging
import json
import traceback
import requests
import pyDes
import base64


conf = config.GyConfig()
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

def inital_des():
    key = b'qAfmGitJ'
    iv = b'12345678'
    return pyDes.des(key, pyDes.CBC, iv, pad=None, padmode=pyDes.PAD_PKCS5)


def encrytDes(des, card_code):
    return des.encrypt(card_code)


def base64_encode(encryt_data):
    return str(base64.b64encode(encryt_data), encoding="utf-8")


def get_exchange_codes():
    filename = '%s/data/fql.ex_code' % conf.get_project_path()
    exchange_codes = []
    exchange_codes_set = {}
    try:
        print('Get exchange code from %s' % filename)
        fp = open(filename, "r")
        for line in fp.readlines():
            line = line.replace('\n', '')
            if exchange_codes_set.get(line) == 1:
                print('Duplicate exchange code %s' % line)
                continue
            exchange_codes_set[line] = 1
            exchange_codes.append(line)
        fp.close()
    except IOError:
        print('Open file[%s] error, file not exist' % filename)
    return exchange_codes


def check_card_status(pwd):
    url = 'http://11888pay.cn/exchange/checkCardStatus'
    r = s.post(url, data={'userId': 452, 'cardPwd' :pwd, 'flag': 'fenqile'})
    return r.json()


def collect_card_info(exchange_code, des, face_value, card_package):
    pwd = base64_encode(encrytDes(des, exchange_code))
    product_ids = {'100': '18001364', '500': '18001293', '1000' : '18001362', '100*10' : '18001365', '1000*2' : '18001641', '500*4': '18001688'}
    url_pattern = 'cardExchangeOrder'
    if face_value == '100*10' or face_value == '1000*2' or face_value == '500*4':
        url_pattern = 'cardCamiloPackage'
    post_target = 'https://11888pay.cn/exchange/%s' % url_pattern
    print(post_target)
    while True:
        if check_card_status(pwd)['errorCode'] == 5104:
            print('Card exchanged')
            break
        time.sleep(3)
        r = s.post(post_target, data={'productId': product_ids[face_value], 'cardPwd': pwd, 'flag': 'fenqile'})
        print(exchange_code, r.text)
        res = r.json()
        if res.get('errorCode') == 5121:
            sec_to_sleep = 60
            print('Time to sleep for %d(s)' % sec_to_sleep)
            time.sleep(sec_to_sleep)
            continue
        if res.get('errorCode') == 5000 or res.get('errorCode') == 5104:
            break
        print('Unable to active exchage code %s' % exchange_code)
        break
    url = 'https://11888pay.cn/exchange/orderList'
    r = s.post(url, data={'pageNumber': 1, 'pageSize' : 9999, 'cardPwd': pwd, 'flag' : 'fenqile'})
    print(r.json())
    data = r.json()
    if data['errorCode'] == 200 and data.get('data') is not None:
        for row in data['data']['rows']:
            card_no = row['cardNumber']
            card_passwd = row['cardPwd']
            card_info = row['productName']
            print('%s\t%s\t%s' % (card_no, card_passwd, card_info))
            card_package.append({'card_no': card_no, 'card_pw': card_passwd, 'card_info': card_info,
                    'exchange_code': exchange_code, 'encryt_ex_code': pwd})
        return {'code' : 0}
    else:
        print('could not find exchage code %s exchange info' % exchange_code)
        print(r.text)
        return {'code': -1}


s = requests.Session()
cookie_jar = RequestsCookieJar()
cookie_jar.set('SESSION', '', domain='11888pay.cn')
s.cookies.update(cookie_jar)
print(s.cookies)
des = inital_des()
encData = base64_encode(encrytDes(des, "VXMH7YVZ67654UU7"))
assert "SKVB4sf5cQ6PDZPXav1Wucc91byuoQx2" == encData

exchange_codes = get_exchange_codes()
print('We find %d of exchange code' % len(exchange_codes))
if len(exchange_codes) == 0:
    exit(0)
card_infos = []
face_value = '500*4'
ind = 0
for ex in exchange_codes:
    ind = ind + 1
    print('Progess %d/%d' % (ind, len(exchange_codes)))
    if ind % 10 == 0:
        print('Sleep 60 sec')
        time.sleep(60)
    collect_card_info(ex, des, face_value, card_infos)
    time.sleep(1)
print('Total exchange %d' % len(card_infos))
print('Total exchange code from file %d' % len(exchange_codes))
if len(card_infos) != len(exchange_codes):
    print('WARNING some exchage code miss')
else:
    print('All exchange code exchange success, as list follow')
for card_info in card_infos:
    print('%s\t%s\t%s\t%s' % (card_info['card_no'], card_info['card_pw'], card_info['card_info'],
                             card_info['exchange_code']))
print('END.OF.PROC')
