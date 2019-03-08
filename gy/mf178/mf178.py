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
    js = '''
        document.getElementsByClassName('ajaxlink')[0].click();
    '''
    driver.execute_script(js)
    time.sleep(3)
    name_elem = driver.find_element_by_id('username')
    name_elem.clear()
    name_elem.send_keys(user_info['username'])
    pw_elem = driver.find_element_by_id('password')
    pw_elem.clear()
    pw_elem.send_keys(user_info['password'])
    captch_dir = '%smf.png' % conf.get_screen_path()
    driver.get_screenshot_as_file(captch_dir)
    print('URL to login for vcode\nhttp://%s/pj/gy/mf178/login_vcode.html' % common.get_host_ip())
    vcode = input('Please input vcode from %s\n' % captch_dir)
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


def get_qpay_order(driver, id):
    print('Get QPay order')
    driver.get('http://www.mf178.cn/customer/qpay/mytasks')
    js = r'''
        var js_result = {}, target_url = "http://www.mf178.cn/customer/qpay/ajax?action=get_tasks&id=" + arguments[0];
        $.ajax({
            "type": "get",
            "async" : false,
            "url": target_url,
            success: function (result1) {
                result = $.parseJSON(result1); 
                if(result.type=="dialog"){
                    js_result["SEQ"] = $(result.data).find("input[name='SEQ']").val();
                    js_result["code"] = 0
                }else{
                    console.info(result1);
                    js_result["code"] = 1;
                    js_result["message"] = result;
                }
            }
        }); 
        return js_result;
    '''
    js_get = r'''
        var js_result = {}, target_url = "http://www.mf178.cn/customer/qpay/get_tasks";
        $.ajax({
            "type": "post",
            "async" : false,
            "url": target_url,
            "data":{
                "id":arguments[0],
                "count" : 1,
                "role": 1,
                "SEQ" : arguments[1]
            },
            success: function (result) {
                console.info(result);
                var $order = $(result).find('table').last().find('td').first();
                if($.isEmptyObject($order) || $order.length == 0){
                    js_result['code'] = -1;
                }else{
                    js_result['code'] = 0;
                    js_result['order_id'] = $order.text();
                }
            }
        }); 
        return js_result;
    '''
    cnt = 1
    while True:
        result = driver.execute_script(js, id)
        print(result)
        if result.get('code') is None:
            input('check code')
        if result.get('code') == 0:
            order_result = driver.execute_script(js_get, id, result['SEQ'])
            if order_result.get('code') == 0:
                print('Order find--', order_result)
                if input('n for continue, q for exit') == "n":
                    cnt = 1
                    continue
                else:
                    return
        time.sleep(5)
        print('#%d retry' % cnt)
        cnt += 1


def report(driver):
    now_url = driver.current_url
    driver.get('http://www.mf178.cn/mobile/order/order_list_doing')
    order_id = driver.find_elements_by_class_name('mui-col-xs-7')[0].text
    print(order_id)
    url = "http://www.mf178.cn/customer/order/ajax?action=task_report&op=succ&id=%s" % order_id
    driver.get(url)
    result = json.loads(driver.find_element_by_xpath('/html/body/pre').text)
    result['url'] = url
    driver.get(now_url)
    return result


def get_order(driver, amout, num, operator_id):
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
            "operator_id" : arguments[3],
            "prov_name" : "",
            "count" : arguments[1],
            "role" : "1",
            "contract": [1, 2, 4, 8, 16, 32, 64, 128, 256,512], 
            "SEQ" : arguments[2]
        };
        var js_result = {};
        $.ajax({
            "type": "post",
            "async" : false,
            "data": param_data,
            "url" : target_url,
            success : function(result){
                var rsl_doc = $(result);
                console.info(result);
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
        result = driver.execute_script(js)
        if result.get('code') == 0:
            sb_result = driver.execute_script(js_submit, amout, num, result['SEQ'], operator_id)
            if sb_result.get('code') == '0' and sb_result.get('phone') is not None:
                print('%s--charge phone:%s' % (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f'), sb_result['phone']))
                command = input('n for report and get next order, q for report and exit')
                try:
                    report_result = report(driver)
                    if report_result.get('type') != 'refresh':
                        print('report error', report_result)
                        print('order info', sb_result)
                        input('please interupt from manual, input any to continue')
                except:
                    print(report_result)
                    traceback.print_exc()
                if command == "n":
                    continue
                else:
                    break
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
    order_type_list = ["QR", "MBL_CHRG"]
    order_type = order_type_list[0]
    if order_type == "MBL_CHRG":
        operators = {"MOBILE": "1", "UNICOM": "2", "ANY": "0"}
        operator_key = ["UNICOM", "MOBILE", "ANY"]
        amount = 50
        count = 1
        get_order(driver, amount, count, operators[operator_key[1]])
    else:
        id_list = {"UNION_100": 21, "UNION_200": 22, "UNION_300": 23, "UNION_500": 25,
                   "MOBILE_100": 31, "MOBILE_200": 32, "MOBILE_300": 33, "MOBILE_500": 35,
                   "TELECOM_100": 11, "TELECOM_200": 12, "TELECOM_300": 13, "TELECOM_500": 15
                   }
        operators = ["UNION", "MOBILE", "TELECOM"]
        operator = operators[0]
        amount = 500
        get_qpay_order(driver, id_list.get('%s_%d' % (operator, amount)))
except:
    traceback.print_exc()
finally:
    #input('input anything to end')
    driver.quit()
    print('END.OF.PROG')