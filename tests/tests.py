import sys
import os
import os.path
from nose.tools import assert_equals
from nose.tools import raises
sys.path.append(os.path.join("portal"))
import Portal

username = "pyang.produban.uk"
password = "C0mpuwar3"


def test_GPN_initialization():
    gpnPortal = Portal.GPNPortal(username, password)
    gpnPortal.close()
    assert type(gpnPortal.homePage) == str


@raises(Exception)
def test_GPN_exception_initialization():
    gpnPortal = Portal.GPNPortal(154741657, 4786454)
    gpnPortal.close()


# def test_GPN_test_login_url():
#     gpnPortal = Portal.GPNPortal(username, password)
#     gpnPortal.login()
#     assert_equals(
#         gpnPortal.driver.current_url, "http://www.gomeznetworks.com/start/home.asp")
#     gpnPortal.close()


# @raises(Exception)
# def test_GPN_getXFMeasurement_startMonth_endMonth_exception():
#     gpnPortal = Portal.GPNPortal(username, password)
#     gpnPortal.login()
#     gpnPortal.getXFMeasurement(startDay=1, endDay=7, startMonth=1, endMonth=2)
#     gpnPortal.close()
