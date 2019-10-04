#!/usr/bin/env python
from gy.jd import Common
import time
import traceback


def mobile_login(driver, userInfo):
    driver.get('https://m-user.kaola.com/user/usrCenter.html')
    time.sleep(2)
    if driver.current_url.startswith('https://m-user.kaola.com/user/usrCenter.html'):
        return True
    try:
        driver.execute_script('''
            if(document.getElementsByClassName('km-modal__container-outer')[0].style.display==""){
               document.getElementsByClassName('opt-btn_agree')[0].click(); 
            }
        ''')
        driver.switch_to.frame(driver.find_element_by_id('loginbox1').find_element_by_tag_name('iframe'))
        driver.execute_script('''
            document.getElementById('phoneipt').value=arguments[0];
            document.getElementsByClassName('getsmscode')[0].click()
        ''', userInfo['username'])
        sms_code = Common.get_sms_code()
        driver.execute_script('''
            document.getElementsByName('phonecode')[0].value=arguments[0];
            document.getElementsByClassName('u-loginbtn')[0].click();
        ''', sms_code)
        time.sleep(2)
        if driver.current_url.startswith('https://m-user.kaola.com/user/usrCenter.html'):
            return True
        return False
    except:
        traceback.print_exc()
        return False