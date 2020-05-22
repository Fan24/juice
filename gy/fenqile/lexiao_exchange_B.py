#!/usr/bin/env python
from gy import config
import time
import hashlib
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


def get_stamp():
    sec = str(int(time.time()))
    return sec[len(sec) - 10:]


def get_card_info(exchange_code, face_value):
    req_data = {'RedeemCode': exchange_code, 'Ts': get_stamp()}
    req_data['Sign'] = get_sign(req_data)
    while True:
        r = s.post('http://cdk.jpkj888.com/api/actionapi/Order/RedeemCode', data=req_data)
        print(exchange_code, r.text)
        res = r.json()
        if res.get('Code') == 5121:
            sec_to_sleep = 60
            print('Time to sleep for %d(s)' % sec_to_sleep)
            time.sleep(sec_to_sleep)
            continue
        if res.get('Code') == 200:
            break
        print('Unable to active exchage code %s' % exchange_code)
        return {'code' : -2}
    data = res
    if data['Code'] == 200 and data.get('Data') is not None:
        card_no = data.get('Data')['GCA']
        card_passwd = data.get('Data')['PWD']
        print('%s\t%s\t%s' % (card_no, card_passwd, exchange_code))
        return {'card_no': card_no, 'card_pw': card_passwd, 'exchange_code': exchange_code, 'code' : 0}
    else:
        print('could not find exchage code %s exchange info' % exchange_code)
        print(r.text)
        return {'code': -1}


def get_md5(data):
    m = hashlib.md5()
    m.update(data.encode(encoding='utf8'))
    return m.hexdigest().upper()


def get_sign(req_data):
    salt = 'Serge#57$768rtv0'
    return get_md5('%s%s%s' % (req_data['RedeemCode'], req_data['Ts'], salt)).upper()


s = requests.Session()
encData = get_md5("43D529BD41074E60AD50C54E9C12D9221590131794Serge#57$768rtv0")
assert "A579253F9A9E97DA1440BD5F9DCD24A0" == encData

exchange_codes = get_exchange_codes()
print('We find %d of exchange code' % len(exchange_codes))
if len(exchange_codes) == 0:
    exit(0)
card_infos = []
face_value = '100'
ind = 0
for ex in exchange_codes:
    ind = ind + 1
    print('Progess %d/%d' % (ind, len(exchange_codes)))
    if ind % 10 == 0:
        print('Sleep 10 sec')
    card_info = get_card_info(ex, face_value)
    if card_info['code'] == 0:
        card_infos.append(card_info)
    time.sleep(1)
print('Total exchange %d' % len(card_infos))
print('Total exchange code from file %d' % len(exchange_codes))
if len(card_infos) != len(exchange_codes):
    print('WARNING some exchage code miss')
else:
    print('All exchange code exchange success, as list follow')
for card_info in card_infos:
    print('%s\t%s\t%s\t%s' % (card_info['card_no'], card_info['card_pw'], face_value, card_info['exchange_code']))
print('END.OF.PROC')
