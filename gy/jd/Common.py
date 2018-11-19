#!/usr/bin/env python
import json,sys,os,time
import datetime
import math


def jd_login(driver, userInfo, conf):
    print('We are preparing to login')
    cnt = 0
    while driver.current_url.startswith('https://plogin.m.jd.com/user/login.action'):
        if cnt > 2:
            break;
        cnt += 1
        print('BeforeLogin#', cnt)
        time.sleep(1)
    if driver.current_url.startswith('https://plogin.m.jd.com/user/login.action'):
        driver.get_screenshot_as_file('%sbefore.png' % conf.get_screen_path())
        time.sleep(2)
        driver.find_element_by_id('username').send_keys(userInfo['username'])
        time.sleep(1)
        driver.find_element_by_id('password').send_keys(userInfo['password'])
        time.sleep(2)
        driver.find_element_by_id('loginBtn').click()
        time.sleep(5)
    if driver.current_url.startswith('https://plogin.m.jd.com/cgi-bin/ml/risk'):
        print('RiskUri:',driver.current_url)
        driver.find_element_by_class_name('.mode-btn.voice-mode').click()
        time.sleep(3)
    if driver.current_url.startswith('https://plogin.m.jd.com/cgi-bin/ml/sms_risk'):
        print('SmsUri:',driver.current_url)
        sms = input('Please input smscode:')
        driver.find_element_by_id('authCode').send_keys(sms)
        time.sleep(1)
        driver.find_element_by_class_name('smsSubmit').click()
        time.sleep(2)
    driver.get_screenshot_as_file('%safterLogin.png' % conf.get_screen_path())
    print('AfterLoginUrl@',driver.current_url)


def block_until_start(quick):
    block_until_start_by_second(quick, 2)


def block_precise_until_start(quick):
    ct = datetime.datetime.now()
    st = datetime.datetime(ct.year, ct.month, ct.day, ct.hour + 1)
    if quick:
        st = datetime.datetime(ct.year, ct.month, ct.day, ct.hour, ct.minute, ct.second + 5)
    gap = math.floor((st - ct).total_seconds()) - 2
    print('Here we @%s, activity start @%s, we sleep %d(s)' % (ct.strftime('%Y%m%d %H:%M:%S.%f'), st.strftime('%Y%m%d %H:%M:%S'), gap))
    time.sleep(gap)
    while True:
        ct = time.time()
        st_time = time.mktime(st.timetuple())
        diff = (st_time - ct) * 1000
        if diff < 300:
            break
            print(diff)


def block_until_start_by_second(quick, sec_ahead):
    ct = datetime.datetime.now()
    st = datetime.datetime(ct.year, ct.month, ct.day, ct.hour + 1)
    if quick:
        st = datetime.datetime(ct.year, ct.month, ct.day, ct.hour, ct.minute, ct.second + 3)
    gap = math.floor((st - ct).total_seconds()) - sec_ahead
    print('Here we @%s, activity start @%s, we sleep %d(s)' % (ct.strftime('%Y%m%d %H:%M:%S.%f'), st.strftime('%Y%m%d %H:%M:%S'), gap))
    time.sleep(gap)
