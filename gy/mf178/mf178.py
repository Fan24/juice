import time
import datetime
import json
from gy.util import common


class MF178:
    def __init__(self, user_info):
        self.url = {'home': 'http://www.mf178.cn/customer/user/index',
                    'captcha': 'http://www.mf178.cn/login/captcha',
                    'list' : 'http://www.mf178.cn/customer/order/ajax?action=get_tasks&amount=%d&_%d'
                    }
        self.user_info = user_info

    def go_home(self, driver):
        driver.get(self.url['home'])

    def login(self, driver, screen_path):
        print('Prepare to login@', driver.current_url)
        js = '''
        document.getElementsByClassName('ajaxlink')[0].click();
        '''
        driver.execute_script(js)
        time.sleep(3)
        name_elem = driver.find_element_by_id('username')
        name_elem.clear()
        name_elem.send_keys(self.user_info['username'])
        pw_elem = driver.find_element_by_id('password')
        pw_elem.clear()
        pw_elem.send_keys(self.user_info['password'])
        captch_dir = '%smf.png' % screen_path
        driver.get_screenshot_as_file(captch_dir)
        print('URL to login for vcode\nhttp://%s/pj/gy/mf178/login_vcode.html' % common.get_host_ip())
        vcode = input('Please input vcode from %s\n' % captch_dir)
        vcode_elem = driver.find_element_by_id('vcode')
        vcode_elem.clear()
        vcode_elem.send_keys(vcode)
        driver.find_element_by_id('bt_login').click()
        time.sleep(2)
        print('After login, we are @', driver.current_url)

    def prepare_env(self, driver, screen_path):
        driver.get(self.url['home'])
        print(driver.current_url)
        cnt = 0
        retry = 3
        while not driver.current_url.startswith(self.url['home']):
            cnt += 1
            time.sleep(3)
            if cnt > retry:
                break
        if not driver.current_url.startswith(self.url['home']):
            self.login(driver, screen_path)
        driver.get(self.url['home'])
        cnt = 0
        while not driver.current_url.startswith(self.url['home']):
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

    def report(self, driver):
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

    def get_order(self, driver, amout, num, operator_id):
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
            time.sleep(5)
            result = driver.execute_script(js)
            if result.get('code') == 0:
                sb_result = driver.execute_script(js_submit, amout, num, result['SEQ'], operator_id)
                if sb_result.get('code') == '0' and sb_result.get('phone') is not None:
                    print('%s--charge phone:%s' % ( datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f'), sb_result['phone']))
                    return sb_result
            else:
                print('Unable to get SEQ,' + result)
