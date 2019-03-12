#!/usr/bin/env python
from gy import config
from gy.util import common
import time, json
import sys
import traceback


param = {
    'cart_url' : 'https://m.msyc.cc/wx/ucenter/cart-new.html?_v=%d&tmn=200392',
    'address_url' : 'https://m.msyc.cc/address/findAddressNoJSONP',
    'cart_list_url' : 'https://m.msyc.cc/app/cart/list/v666?tmn=200392&pageNum=0&t=%d'
}


def login(driver, user_info):
    driver.find_element_by_id('userCode').send_keys(user_info['username'])
    time.sleep(1)
    driver.find_element_by_id('passWord').send_keys(user_info['password'])
    time.sleep(1)
    driver.execute_script('login();')
    time.sleep(5)
    print('After login we @',driver.current_url)


def prepare_env(driver, user_info):
    driver.get(param.get('cart_url') % (time.time() * 1000))
    time.sleep(5)
    print('Here we at:', driver.current_url)
    if driver.current_url.startswith('https://m.msyc.cc/wx/login.html'):
        login(driver, user_info)
    if driver.current_url.startswith('https://m.msyc.cc/wx/login.html'):
        return False
    return True


def get_address_id(driver):
    driver.get(param.get('address_url'))
    for add in json.loads(driver.find_element_by_xpath('/html/body/pre').text):
        if add['isDelete'] != 0:
            continue
        return add['addressId']

    print('Unable to locate address_id')
    print(driver.page_source)
    return None


def get_cart_list(driver, need_tick):
    driver.get(param['cart_list_url'] % (time.time()*1000))
    print(driver.current_url)
    key_map = {'freshList': 'freshList', 'aniList': 'onionList', 'drinksList' : 'wineFirstList', 'seasList' : 'onionList'}
    data = json.loads(driver.find_element_by_xpath('/html/body/pre').text)['data']
    print(data)
    cart_ids = {'foreignList': []}
    foreign_list = data['foreignList']
    if 0 < len(foreign_list):
        for good in foreign_list:
            if need_tick and good['goods'][0]['isTick'] != 1:
                continue
            cart_ids['foreignList'].append({"id": str(good['goods'][0]['product']['id']), "count" : str(int(good['goods'][0]['num']))})
    for (key,val) in key_map.items():
        array = data.get(key)
        if not cart_ids.get(key):
            cart_ids[val] = []
        if 0 == len(array):
            continue
        for good in array[0]['goods']:
            cart_ids[val].append({"id": str(good['product']['id']), "count" : str(int(good['num']))})
    return cart_ids


def to_cart_ids_str(cart_ids):
    cart_ids_str = []
    for (list, val) in cart_ids.items():
        if 0 == len(val):
            continue
        for ids in val:
            cart_ids_str.append('%s_%s' % (ids['id'], ids['count']))
    return ','.join(cart_ids_str)


def get_coupon_no(driver, cart_ids_str):
    driver.get(param.get('cart_url') % (time.time() * 1000))
    js = r'''
        var result = 1;
        var cartIds = arguments[0];
        $.ajax({
            url:'https://m.msyc.cc/couponRest/oneUserUsableCouponList',
            type:'post',
            dataType:'json',
            async:false,
            data:{"cartIds": cartIds},
            success:function(data){
                result = data;
                console.info(data);
            },
            fail:function(data){
                console.error(data);
            }
        });
        return result;
        '''
    return driver.execute_script(js, cart_ids_str)


def wait_order_result(driver, id_key):
    script = r'''
        return sessionStorage['arguments[0]'];
    '''
    results = []

    recheck = 20
    for x in range(1, recheck):
        for key in id_key:
            result = driver.execute_script(script, key)
            if result is None:
                results.clear()
                break
            results.append(result)
        print('len_result:%d, len_id_key:%d' % (len(results), len(id_key)))
        if len(results) == len(id_key):
            break
        print('#%d waiting result.' % x)
        time.sleep(3)
        if x == recheck - 1:
            print('We have ckecked with %d time(s) with uncerntain result, return fail and abort!' % x)
    if len(results) != len(id_key):
        print('Cloud not find all result')
        return False
    for result in results:
        print(result)
        json_result = json.loads(result)
        if json_result['errCode'] == 10000:
            print('Order no is:', json_result['sodNo'])
            return True
    return False


def order_from_cart(driver, hour=None, minute=None, need_tick=True):
    addr_id = get_address_id(driver)
    if not addr_id:
        print('address id empty,exit')
        return False

    cart_ids = get_cart_list(driver, need_tick)
    cart_ids_str = to_cart_ids_str(cart_ids)
    coupon_no = get_coupon_no(driver, cart_ids_str)
    print('Coupon no:', coupon_no)
    common.block_until_start_with_time(False, hour, minute)

    js = r'''
        var target_url = 'https://m.msyc.cc/app/sodrest/createSod/v2?t=' + new Date().getTime();
        console.info(target_url);
        console.info(arguments[0]);
        console.info(JSON.stringify(arguments[1]));
        console.info(arguments[2]);
        $.ajax({
            "type": "post",
            "data": {
                "client": "web",
                "tmnId": "200392",
                "cartIds": JSON.stringify(arguments[1]),
                "addressId": arguments[2],
                "isSingle": 0,
                "couponNo": ""
            },
            "url": target_url,
            "dataType": "json",
            success: function (result) {
                console.info(JSON.stringify(result));
                sessionStorage['arguments[0]']=JSON.stringify(result);
            }
        }); 
    '''
    id_key = []
    for c in range(1, 7):
        key = 'ID%d' % c
        print(key)
        id_key.append(key)
        driver.execute_script(js, key, cart_ids, addr_id)
    return wait_order_result(driver, id_key)


conf = config.GyConfig()
user_info = conf.get_user_info()
driver = common.build_chrome(conf)
try:
    prepare_env(driver, user_info)
    hour = None
    minute = None
    tick = False
    if len(sys.argv) > 3:
        hour = int(sys.argv[2])
        minute = int(sys.argv[3])
        print('Start time %02d:%02d' % (hour, minute))
    if len(sys.argv) > 4:
        if sys.argv[4] == "tick":
            tick = True
    order_from_cart(driver, hour, minute, tick)
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.PROG')

