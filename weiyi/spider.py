# -*- coding:utf-8 -*-
import schedule, time, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from weiyi.department import DepartmentInfo
from weiyi.doctor import DoctorInfo
from weiyi.hospital import HospitalLinkCache, HospitalInfo
from utils.tools import timethis


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
    # main()
    schedule.every().monday.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
