# -*- coding:utf-8 -*-
import schedule, time, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from weiyi.department import DepartmentInfo
from weiyi.doctor import DoctorInfo
from weiyi.hospital import HospitalLinkCache, HospitalInfo
from common.tools import timethis
from common.logger import getLogger

logger = getLogger('hospital')


def update_one_hospital(url):
    hospital = HospitalInfo()
    hospital.update_one(url)
    for section_link in hospital.section_links:
        department = DepartmentInfo()
        department.update_one(section_link)
        for doctor_link in department.doctor_links:
            DoctorInfo().update_one(doctor_link)


@timethis
def main():
    HospitalLinkCache().start()
    logger.info('hospital link cache done!')
    HospitalInfo().start()
    logger.info('hospital info done!')
    DepartmentInfo().start()
    logger.info('department info done!')
    DoctorInfo().start()
    logger.info('doctor info done!')


if __name__ == '__main__':
    # print('main Start')
    # main()
    # print('main over')
    update_one_hospital('https://www.guaao.com/hospital/56ff0efc-899c-4840-ba7f')
