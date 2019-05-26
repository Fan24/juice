import time
import datetime
import re
from gy.util.common import OPERATOR


class Ninetyninth:
    def __init__(self, user_info):
        self.url = {'dashboard': 'http://51maiquan.com/charge/phone/table?type=doing',
                    'order': 'http://51maiquan.com/charge/phone/receive/info?facevalue=%d&receiveNum=1&%s'
                }
        self.user_info = user_info
        self.order = {}

    def login(self, driver):
        print('99 prepare to login')
        driver.get(self.url['dashboard'])
        time.sleep(2)
        if driver.current_url.startswith(self.url['dashboard']):
            print('Login succeed!')
            return True
        print('Login@',driver.current_url)
        driver.find_element_by_id('signupform-username').send_keys(self.user_info['username'])
        driver.find_element_by_id('signupform-password').send_keys(self.user_info['password'])
        driver.execute_script('$("#form-signup")[0].submit()')
        time.sleep(2)
        print('After login page@', driver.current_url)
        driver.get(self.url['dashboard'])
        if driver.current_url.startswith(self.url['dashboard']):
            print('Login succeed!')
            return True
        return False

    def get_order_info(self, driver):
        js_order_info = '''
        var js_result = {}; 
         $.ajax({
            "type": "post",
            "async" : false,
            "url": '/charge/phone/order/table/infos',
            "data": {
                "type": "doing",
                "page": 1,
                "limit": 10,
                "stamp": new Date().getTime()
            },
            dataType:'json',
            success: function (result) {
                console.info("order-info:" + JSON.stringify(result));
                if(result.code == 0){
                    js_result['code'] = 0;
                    js_result['order'] = result['data'][0];
                 }else{
                        js_result['code'] = -1;
                        js_result['msg'] = result['msg'];
                    }
                }
        }); 
        return js_result;
        '''
        order_info = driver.execute_script(js_order_info)
        if order_info['code'] == 0:
            self.order = order_info['order']
            return True
        print('Unable to get order info with error[%s]' % order_info['msg'])

    @staticmethod
    def has_phone_charge_order(driver, face_value, operator):
        if type(operator) is not OPERATOR:
            raise TypeError('operator must be OPERATOR')
        url = 'http://51maiquan.com/charge/phone/receive?facevalue=%d&stamp=%d' % (face_value, time.time())
        driver.get(url)
        if operator == OPERATOR.ANY:
            key = ["yd", "lt", "dx"]
        elif operator == OPERATOR.MOBILE:
            key = ["yd"]
        elif operator == OPERATOR.UNICOM:
            key = ["lt"]
        elif operator == OPERATOR.TELECOM:
            key = ["dx"]
        key_len = len(key)
        for i in range(len(key)):
            title = driver.find_element_by_id(key[i]).get_attribute('title')
            if key_len == 1:
                print(title)
            pool_num = int(re.search(r'\d+', title).group())
            if pool_num > 0:
                return True
        return False

    def get_phone_charge_order(self, driver, face_value, operator):
        self.order = {}
        if not Ninetyninth.has_phone_charge_order(driver, face_value, operator):
            return False
        js_order = '''
        var reqData = {"facevalue": arguments[0], "receiveNum": arguments[1]};
        if(arguments[2] == 0){
            reqData["channel[0]"] = "1";
            reqData["channel[1]"] = "2";
            reqData["channel[2]"] = "3";
        }else{
            reqData["channel"] = arguments[2];
            console.debug(reqData["channel"]);
        }
        var js_result = {};
        $.ajax({
            "type": "post",
            "async" : false,
            "url": '/charge/phone/receive/info',
            "data": reqData,
            dataType:'json',
            success: function (result) {
                console.info(JSON.stringify(result));
                if(result.rtnCode == "000000"){
                    js_result['code'] = 0;
                    js_result['data'] = result;
                 }else{
                        js_result['code'] = -1;
                        js_result['msg'] = result['rtnMsg'];
                    }
                }
        }); 
        return js_result;
        '''
        js_result = driver.execute_script(js_order, face_value, 1, operator.value)
        if js_result['code'] == 0:
            if self.get_order_info(driver):
                return True
            input('We get order but can not get order info, '
                      'please press any key to continue to get next order after handled manaully')
            return False
        else:
            print(js_result['msg'])
            return False

    def get_phone_charge_order_til_success(self, driver, face_value, operator):
        cnt = 1
        print('#%d to get order' % cnt)
        while not self.get_phone_charge_order(driver, face_value, operator):
            time.sleep(3)
            cnt += 1
            print('#%d to get order with [%s]' % (cnt, operator))
        print(self.order)
        print(
            '%s--charge phone:%s, amount'
                % (datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f'), self.order['phoneNo']), face_value)

    def confirm_order(self, driver):
        js_confirm = '''
        var js_result = {};
        $.ajax({
            "type": "post",
            "async" : false,
            "url": "/charge/phone/order/report",
            "data": {
                "id": arguments[0],
                "needImg": true,
                "imageId": "",
                "chargeStatus": "0"
            },
            dataType:'json',
            success: function (result) {
                console.info("report:" + JSON.stringify(result));
                if(result.rtnCode == "000000"){
                    js_result['code'] = 0;
                 }else{
                    js_result['code'] = -1;
                    js_result['msg'] = result['rtnMsg'];
                }
            }
        }); 
        return js_result;
        '''
        result = driver.execute_script(js_confirm, self.order.get('id'))
        if result.get('code') == 0:
            print('Report order[%s] for phone no[%s] with face value[%d] success' % (self.order.get('id'),
                                self.order.get('phoneNo'), self.order.get('facevalue')))
            return True
        return False
