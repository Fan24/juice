#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
import time
import traceback
import re

conf = config.GyConfig()
param = {
    "mobile_jd_home_url": "https://home.m.jd.com",
    "order_page" : "https://order.jd.com/center/list.action",
    "file_to_save": "E:/OnionMall/data/JDAppStoreCardInfo.txt"
}


def debug(elem):
    while True:
        cmd = input('Please input command')
        if cmd == "E":
            break
        try:
            print(elem.find_element_by_xpath(cmd).text)
        except:
            traceback.print_exc()


def travel_orders(driver, last_include_order_id):
    nick_name = driver.find_element_by_class_name('nickname').text
    print('Ready to find card info for user %s' % nick_name)
    order_ID_list = collect_order_id(driver, last_include_order_id)
    print('We find %d of order.' % len(order_ID_list))
    asCard_info = collect_asc_info(driver, order_ID_list)
    save_card_info(nick_name, asCard_info)


def save_card_info(nick_name, asCardInfo):
    if asCardInfo is None or 0 == len(asCardInfo):
        print('Empty card info')
        return
    with open(param['file_to_save'], "a+") as fp:
        for asc in asCardInfo:
            line = '%.2f\t%s\t%s\t%s\t%.2f\t%s' % \
               (asc['face_price'], asc['card_no'], asc['card_pw'], nick_name, asc['cost'], asc['prd_Dsc'])
            fp.write(line+'\n')
            print('%s\t%s' % (line, asc['order_ID']))


def collect_order_id(driver, last_include_order_id):
    url_pattern = 'https://order.jd.com/center/list.action?d=1&s=4096&page=%d'
    order_ID_list = []
    cnt = 1
    finish = False
    while not finish:
        url = url_pattern % cnt
        print('Go to page %d' % cnt)
        cnt = cnt + 1
        driver.get(url)
        tbodys = driver.find_elements_by_tag_name('tbody')
        for body in tbodys:
            try:
                order_id = body.find_element_by_xpath('.//a[@name="orderIdLinks"]').text
                if '游戏' == body.find_element_by_class_name('shop-txt').text:
                    order_ID_list.append(order_id)
                if order_id == last_include_order_id:
                    print('We find the last include order id:%s' % order_id)
                    finish = True
                    break
            except:
                continue
        time.sleep(2)
    return order_ID_list


def collect_asc_info(driver, order_ID_list):
    if order_ID_list is None or 0 == len(order_ID_list):
        print('Empty order list')
        return []
    asCardList = []
    number_of_orders = len(order_ID_list)
    process_ind = 0
    for ID in order_ID_list:
        process_ind = process_ind + 1
        url = 'https://card.jd.com/order/order_detail.action?orderId=%s' % ID
        driver.get(url)
        tbody = driver.find_elements_by_tag_name('tbody')
        tr_card_info = tbody[3].find_elements_by_tag_name('tr')[1]
        td_card_info = tr_card_info.find_elements_by_tag_name('td')
        product_id = td_card_info[0].text
        product_dsc = td_card_info[1].text
        total_price = float(td_card_info[2].text)
        card_number = int(td_card_info[5].text)
        print('Processing order[%s] with %d/%d, we found #%d of appstore card' % (ID, process_ind, number_of_orders, card_number))
        unit_price = total_price / card_number
        pay_price = float(driver.find_element_by_class_name('extra').find_element_by_tag_name('b').text)
        pay_unit_price = pay_price / card_number
        tr_elems = tbody[2].find_elements_by_tag_name('tr')
        cnt = 0
        for tr in tr_elems:
            cnt = cnt + 1
            if cnt == 1:
                continue
            try:
                card_no = tr.find_element_by_class_name('cards').find_element_by_tag_name('span').text
                card_pw = tr.find_element_by_class_name('c-psd').find_element_by_tag_name('span').text
                asCardList.append({'prd_ID': product_id, 'prd_Dsc': product_dsc, 'order_ID': ID,
                                   'face_price': unit_price, 'cost': pay_unit_price,
                                   'card_no': card_no, 'card_pw': card_pw})
            except:
                print('Can not find [', tr.text, '] with url:', url)
                traceback.print_exc()
                continue
        if cnt - 1 != card_number:
            print('Card number:%d is not equal with the number %d we found' % (card_number, cnt - 1))
            input('Please check manaully')
        time.sleep(3)
    return asCardList


def jd_login(driver):
    driver.get(param['order_page'])
    return input('Please login and input the last include order id, E for exit!')


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

with open(param["file_to_save"], "w+") as fp:
    fp.write('')
try:
    while True:
        last_include_order_id = jd_login(driver)
        if last_include_order_id == 'E':
            break
        travel_orders(driver, last_include_order_id)
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.LINE')
