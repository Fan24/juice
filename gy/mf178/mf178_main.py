import traceback
import time
from gy import config
from gy.mf178.mf178 import MF178
from gy.util import common


def loop_to_get_order(mf178, driver, amount, count, op_type):
    ticker = 0
    while True:
        ticker += 1
        print('#%d loop to get phone number order' % ticker)
        time.sleep(5)
        result = mf178.get_order(driver, amount, count, op_type)
        if result.get('code') != '0' or result.get('phone') is None:
            continue
        command = input('n for report and get next order, q for report and exit')
        try:
            report_result = mf178.report(driver)
            if report_result.get('type') != 'refresh':
                print('report error', report_result)
                print('order info', result)
                input('please interupt from manual, input any to continue')
        except:
            print(report_result)
            traceback.print_exc()
        if command != "n":
            break


conf = config.GyConfig()
user_info = conf.get_user_info()
mf178 = MF178(user_info)
driver = common.build_chrome(conf, 'chrome_user_dir_mf178')
try:
    cnt = 0
    retry = 3
    while not mf178.prepare_env(driver, conf.get_screen_path()):
        cnt += 1
        if cnt > retry:
            break
        print('Retry to prepare enviroment#', cnt)
    if cnt > retry:
        exit(1)
    order_type_list = ["QR", "MBL_CHRG"]
    order_type = order_type_list[1]
    if order_type == "MBL_CHRG":
        operators = {"MOBILE": "1", "UNICOM": "2", "ANY": "0"}
        operator_key = ["UNICOM", "MOBILE", "ANY"]
        amount = 100
        count = 1
        loop_to_get_order(mf178, driver, amount, count, operators[operator_key[2]])
    else:
        id_list = {"UNION_100": 21, "UNION_200": 22, "UNION_300": 23, "UNION_500": 25,
                   "MOBILE_100": 31, "MOBILE_200": 32, "MOBILE_300": 33, "MOBILE_500": 35,
                   "TELECOM_100": 11, "TELECOM_200": 12, "TELECOM_300": 13, "TELECOM_500": 15
                   }
        operators = ["UNION", "MOBILE", "TELECOM"]
        operator = operators[2]
        amount = 300
        mf178.get_qpay_order(driver, id_list.get('%s_%d' % (operator, amount)))
except:
    traceback.print_exc()
finally:
    driver.quit()
    print('END.OF.PROG')
