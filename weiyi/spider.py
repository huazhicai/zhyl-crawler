# -*- coding:utf-8 -*-
from utils.tools import timethis
from weiyi.department import DepartmentInfo
from weiyi.doctor import DoctorInfo
from weiyi.hospital import HospitalLinkCache, HospitalInfo
import schedule, time


@timethis
def main():
    HospitalLinkCache().start()
    print('hospital link cache done!')
    HospitalInfo().start()
    print('hospital info done!')
    DepartmentInfo().start()
    print('department info done!')
    DoctorInfo().start()
    print('doctor info done!')


if __name__ == '__main__':
    schedule.every().monday.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
