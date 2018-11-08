#!/usr/bin/env python
import time
import datetime
import math


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
