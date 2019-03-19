#!/usr/bin/env python
import time
import datetime,time,json
import math
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gy import config
import traceback
import socket


def block_until_start(quick):
    block_until_start_by_second(quick, 2)


def block_precise_until_start(quick, hour=None, minute=None):
    ct = datetime.datetime.now()
    if hour is None:
        hour = ct.hour + 1
    if minute is None:
        minute = 0
    st = datetime.datetime(ct.year, ct.month, ct.day, hour, minute)
    if quick:
        st = datetime.datetime(ct.year, ct.month, ct.day, ct.hour, ct.minute, ct.second + 5)
    gap = math.floor((st - ct).total_seconds()) - 2
    print('Here we @%s, activity start @%s, we sleep %d(s)' % (ct.strftime('%Y%m%d %H:%M:%S.%f'), st.strftime('%Y%m%d %H:%M:%S'), gap))
    time.sleep(gap)
    while True:
        ct = time.time()
        st_time = time.mktime(st.timetuple())
        diff = (st_time - ct) * 1000
        if diff < 20:
            break
            print(diff)


def block_until_start_with_time(quick, hour=None, minute=None):
    ct = datetime.datetime.now()
    if hour is None:
        hour = ct.hour
    if minute is None:
        minute = ct.minute
    st = datetime.datetime(ct.year, ct.month, ct.day, hour, minute)
    if quick:
        st = datetime.datetime(ct.year, ct.month, ct.day, ct.hour, ct.minute, ct.second + 3)
    gap = math.floor((st - ct).total_seconds()) - 2
    print('Here we @%s, activity start @%s, we sleep %d(s)' % (ct.strftime('%Y%m%d %H:%M:%S.%f'), st.strftime('%Y%m%d %H:%M:%S'), gap))
    if gap > 0:
        time.sleep(gap)


def block_until_start_by_second(quick, sec_ahead):
    ct = datetime.datetime.now()
    st = datetime.datetime(ct.year, ct.month, ct.day, ct.hour + 1)
    if quick:
        st = datetime.datetime(ct.year, ct.month, ct.day, ct.hour, ct.minute, ct.second + 3)
    gap = math.floor((st - ct).total_seconds()) - sec_ahead
    print('Here we @%s, activity start @%s, we sleep %d(s)' % (ct.strftime('%Y%m%d %H:%M:%S.%f'), st.strftime('%Y%m%d %H:%M:%S'), gap))
    time.sleep(gap)


def build_chrome(gy_config, chrome_user_dir_key=None):
    chrome_options = Options()
    conf = gy_config
    if conf.is_headless():
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-web-security')
    # chrome_options.add_argument(
    #    'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"')
    chrome_options.add_argument('--lang=zh-CN.UTF-8')
    user_data_dir = conf.get_chrome_user_dir()
    if chrome_user_dir_key:
        user_data_dir = conf.get_chrome_user_dir_by_key(chrome_user_dir_key)

    print(user_data_dir)
    chrome_options.add_argument('--user-data-dir=%s' %  user_data_dir)
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    if conf.get_http_proxy():
        print('HTTP_PROXY:', conf.get_http_proxy())
        chrome_options.add_argument('--proxy-server=%s' % conf.get_http_proxy())

    if conf.get_chrome_executable_path():
        driver = webdriver.Chrome(executable_path=conf.get_chrome_executable_path(), options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)

    driver.set_window_size(640, 700)
    return driver


def get_host_ip():
    try:
        ip = ''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
