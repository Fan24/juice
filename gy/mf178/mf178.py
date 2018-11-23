import time
import traceback
import datetime
import json
from gy import config
from gy.util import common


param_url = {
    'home' : 'http://www.mf178.cn/customer/user/index',
    'captcha' : 'htpp://www.mf178.cn/login/captcha',
    'list' : 'http://www.mf178.cn/customer/order/ajax?action=get_tasks&amount=%d&_%d'
}


def login(driver, conf):
    print('Prepare to login@', driver.current_url)
    user_info = conf.get_user_info()
    driver.find_elements_by_class_name('ajaxlink')[1].click()
    time.sleep(3)
    name_elem = driver.find_element_by_id('username')
    name_elem.clear()
    name_elem.send_keys(user_info['username'])
    pw_elem = driver.find_element_by_id('password')
    pw_elem.clear()
    pw_elem.send_keys(user_info['password'])
    captch_dir = '%smf.png' % conf.get_screen_path()
    driver.get_screenshot_as_file(captch_dir)
    vcode = input('Please input vcode from %s' % captch_dir)
    vcode_elem = driver.find_element_by_id('vcode')
    vcode_elem.clear()
    vcode_elem.send_keys(vcode)
    driver.find_element_by_id('bt_login').click()
    time.sleep(2)
    print('After login, we are @', driver.current_url)


def prepare_env(driver, conf):
    driver.get(param_url['home'])
    print(driver.current_url)
    cnt = 0
    retry = 3
    while not driver.current_url.startswith(param_url['home']):
        cnt += 1
        time.sleep(3)
        if cnt > retry:
            break
    if not driver.current_url.startswith(param_url['home']):
        login(driver, conf)
    driver.get(param_url['home'])
    cnt = 0
    while not driver.current_url.startswith(param_url['home']):
        cnt += 1
        time.sleep(3)
        if cnt > retry:
            print('Login fail')
            return False
    print('Login success')
    return True


def get_order(driver, amout, num):
    js = r'''
        var target_url = "http://www.mf178.cn/customer/order/ajax?_" + new Date().getTime();
        var js_result = {};
        $.ajax({
            "type": "get",
            "async" : false,
            "data": {
                "action" : "get_tasks",
                "amout": arguments[0]
            },
            "url": target_url,
            "dataType": "json",
            success: function (result) {
                console.info(result);
                if(result.type=="dialog"){
                    js_result["SEQ"] = $(result.data).find("input[name='SEQ']").val();
                    js_result["code"] = 0
                }else{
                    js_result["code"] = 1;
                    js_result["message"] = result;
                }
            }
        }); 
        return js_result;
    '''
    js_submit = r'''
        var target_url = "http://www.mf178.cn/customer/order/get_tasks?_" + new Date().getTime();
        var param_data = {
            "amount" : arguments[0],
            "operator_id" : "0",
            "prov_name" : "",
            "count" : arguments[1],
            "role" : "1",
            "contract": [1, 2, 4, 8, 16, 32, 64, 128, 256], 
            "SEQ" : arguments[2]
        };
        var js_result;
        $.ajax({
            "type": "post",
            "async" : false,
            "data": param_data,
            "url" : target_url,
            success : function(result){
                var rsl_doc = $(result);
                var elem_phone = rsl_doc.find(".btn-xs");
                if($.isEmptyObject(elem_phone)){
                    js_result = {'code':'-1', 'phone':'NA'};
                }else{
                    js_result = {'code':'0', 'phone':elem_phone.val(), 
                            'order_id' : rsl_doc.find('table:last').find('td:first').text()};
                }
            }
        });
        return js_result;
    '''
    cnt = 0
    while True:
        cnt += 1
        print('#%d attempting to get phone number' % cnt)
        input('input anything before u prepare')
        result = driver.execute_script(js)
        if result['code'] == 0:
            print(result['SEQ'])
            sb_result = driver.execute_script(js_submit, amout, num, result['SEQ'])
            if sb_result['code'] == '0':
                print('%s--charge phone%s' % (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f'), sb_result['phone']))
                input('n for report and get next order')

        else:
            print('Unable to get SEQ,' + result)
        time.sleep(5)


conf = config.GyConfig()
user_info = conf.get_user_info()
driver = common.build_chrome(conf, 'chrome_user_dir_mf178')
try:
    cnt = 0
    retry = 3
    while not prepare_env(driver, conf):
        cnt += 1
        if cnt > retry:
            break
        print('Retry to prepare enviroment#', cnt)
    if cnt > retry:
        exit(1)
    get_order(driver, 100, 1)
except:
    traceback.print_exc()
finally:
    input('input anything to end')
    driver.quit()
    print('END.OF.PROG')