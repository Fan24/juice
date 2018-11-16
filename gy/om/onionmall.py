#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
from gy.util import common
import time, json
import math
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


def get_cart_list(driver):
    driver.get(param['cart_list_url'] % (time.time()*1000))
    print(driver.current_url)
    key_map = {'freshList': 'freshList', 'aniList': 'onionList', 'drinksList' : 'wineFirstList', 'seasList' : 'onionList'}
    data = json.loads(driver.find_element_by_xpath('/html/body/pre').text)['data']
    cart_ids = {'foreignList': []}
    foreign_list = data['foreignList']
    if 0 < len(foreign_list):
        for good in foreign_list:
            if good['goods'][0]['isTick'] != 1:
                continue
            cart_ids['foreignList'].append({"id": str(good['goods'][0]['product']['id']), "count" : str(int(good['goods'][0]['num']))})
    for (key,val) in key_map.items():
        array = data.get(key)
        if not cart_ids.get(key):
            cart_ids[val] = []
        if 0 == len(array):
            continue
        for good in array[0]['goods']:
            if good['isTick'] != 1:
                continue
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
            'dataType':'json',
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


def order_from_cart(driver):
    addr_id = get_address_id(driver)
    if not addr_id:
        print('address id empty,exit')
        return False

    cart_ids = get_cart_list(driver)
    cart_ids_str = to_cart_ids_str(cart_ids)
    coupon_no = get_coupon_no(driver, cart_ids_str)
    print(coupon_no)
    return True


conf = config.GyConfig()
user_info = conf.get_user_info()
driver = common.build_chrome(conf)
try:
    prepare_env(driver, user_info)
    order_from_cart(driver)
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.PROG')

