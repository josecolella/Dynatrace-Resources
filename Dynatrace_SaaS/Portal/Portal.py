from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from abc import ABCMeta
from abc import abstractmethod
import datetime
import calendar
import logging
import time
import re
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XFConsumption(object):

    """XFConsumption represents the class that encapsulates everything that
    has to do with the XFConsumption window that pop-up when clicking the admin tab
    in the GPN portal"""

    def __init__(self):
        self.lettersRegex = re.compile(r'[a-zA-Z]')
        self.usage = None
        self.endOfMonthProjection = None
        self.monthlyOffset = None
        self.tableRows = None
        self.xfTable = None
        self.xfSumConsumption = None

    def _sanitizeIntegerString(self, intString):
        """
        _sanitizeIntegerString('124,14') -> 12414

        Returns:
            int: The integer from the string, removing any punctuation
        """
        sanitizedInteger = int(re.sub(r',', '', intString))
        return sanitizedInteger

    def _sanitizeXFTable(self):
        assert self.tableRows is not None, print("tableRows can not be None")
        for element, index in zip(self.tableRows, range(self.tableRows.size)):
            if not re.search(self.lettersRegex, element):
                self.tableRows[index] = self._sanitizeIntegerString(element)

    def setEndOfMonthProjection(self, projection):
        assert type(projection) == str, print(
            "End of Month Projection is a string")
        self.endOfMonthProjection = self._sanitizeIntegerString(projection)

    def _getNumberOfColumns(self, tableRowsList):
        assert type(tableRowsList) == list, print(
            "tableRows expected to be list, but has type: {}".format(type(tableRowsList)))
        columnIndices = tuple(index for elem, index in zip(
            tableRowsList, range(len(tableRowsList))) if re.search(self.lettersRegex, elem))
        return columnIndices[1]

    def setXFTable(self, tableRowsHTML):
        tableRowsTextList = [elem.text for elem in tableRowsHTML]
        numColumn = self._getNumberOfColumns(tableRowsTextList)
        self.xfTable = [
            {
                'day': tableRowsTextList[index],
                'value': max(map(self._sanitizeIntegerString, tableRowsTextList[index + 1:index + numColumn]))
            }
            for index in range(0, len(tableRowsTextList), numColumn)]

    def setSumXFConsumption(self, startDay=1, endDay=31):
        """
        setSumXFConsumption(startDay, endDay) -> sets the sum of the xfconsumption measures

        Args
        ----
            startDay: int
                - The startday for calculating the xf consumption measures
            endDay: int
                - The endday for calculating the xf consumption measures

        """
        dayRegex = re.compile(r'^\d+ ')
        xfConsumptionValues = [elem["value"] for elem in self.xfTable if re.match(dayRegex, elem["day"]) and int(
            re.match(dayRegex, elem["day"]).group()) in range(startDay, endDay + 1)]
        logging.info(xfConsumptionValues)
        self.xfSumConsumption = sum(xfConsumptionValues)

    def setMonthlyOffset(self):
        """
        setMonthlyOffset() -> sets the monthly offset
        """
        assert self.xfTable is not None, print("xfTable can not be None")
        # Can be optimized using dates
        self.monthlyOffset = self.xfTable[-
                                          1]["value"] - self.xfTable[-2]["value"]

    def __str__(self):
        xfConsumptionString = "End of Month Projection: {}\nMonthly Offset: {}\nSum XF Consumption: {}\n".format(
            self.endOfMonthProjection, self.monthlyOffset, self.xfSumConsumption)
        return xfConsumptionString


class AbstractPortal(object):
    __metaclass__ = ABCMeta

    def __init__(self, username, password):
        assert type(username) == str, print('username is a string')
        assert type(password) == str, print('password is a string')
        # If the operating system is windows or *nix.
        self.osNull = {
            "nt": "NUL",
            "posix": "/dev/null"
        }
        self.driver = webdriver.PhantomJS(
            service_log_path=self.osNull[os.name], service_args=['--ignore-ssl-errors=true'])
        self.driver.maximize_window()
        self.windowSize = self.driver.get_window_size()
        self._username = username
        self._password = password

    @property
    @abstractmethod
    def homePage(self):
        pass

    @property
    @abstractmethod
    def usernameInputIdentifier(self):
        pass

    @property
    @abstractmethod
    def passwordInputIdentifier(self):
        pass

    @property
    @abstractmethod
    def submitButtonIdentifier(self):
        pass

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    def login(self):
        logging.debug("Fetching Dynatrace Login Page")
        self.driver.get(self.homePage)
        logging.debug("Finish fetching page")
        self.driver.save_screenshot('homePage.png')
        usernameInput = self.driver.find_element_by_name(
            self.usernameInputIdentifier)
        passwordInput = self.driver.find_element_by_name(
            self.passwordInputIdentifier)
        logging.debug("Sending username credentials")
        usernameInput.send_keys(self.username)
        logging.debug("Sending password credentials")
        passwordInput.send_keys(self.password)
        submitButton = self.driver.find_element_by_id(
            self.submitButtonIdentifier)
        logging.debug("Sending button click")
        submitButton.click()
        logging.debug("Waiting for page to load")

    def close(self):
        self.driver.quit()


class GPNPortal(AbstractPortal):

    tableId = "ctl00_Content_XFSummaryTable"
    endOfMonthProjectionIdentifier = "ctl00_Content_XFProjectedUsage"

    def __init__(self, username, password):
        super(GPNPortal, self).__init__(username, password)
        self.accountsList = set()

    @property
    def homePage(self):
        return "https://www.gomeznetworks.com/index.asp?g=1"

    @property
    def usernameInputIdentifier(self):
        return "username"

    @property
    def passwordInputIdentifier(self):
        return "pwd"

    @property
    def submitButtonIdentifier(self):
        return "loginbutton"

    def login(self):
        super(GPNPortal, self).login()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "black-1")))
        except Exception:
            logging.warning("The page could not load")
        time.sleep(5)
        self.portalWindow = self.driver.current_window_handle
        self.driver.save_screenshot("gpn2.png")

    def getXFConsumption(self, startDay=1, endDay=calendar.monthrange(datetime.date.today().year, datetime.date.today().month)[1], startMonth=datetime.date.today().month, endMonth=datetime.date.today().month):
        currentYear = datetime.date.today().year
        xfConsumptionPage = "https://www.gomeznetworks.com/reports/flexReport.aspx?x=&startdate={startYear}/{startMonth}/{startDay}&enddate={endYear}/{endMonth}/{endDay}".format(
            startYear=currentYear,
            startMonth=startMonth,
            startDay=startDay,
            endYear=currentYear,
            endMonth=endMonth,
            endDay=endDay
        )
        # self.driver.get(xfConsumptionPage)
        self.driver.execute_script(
            "window.open('{}')".format(xfConsumptionPage))
        self.driver.switch_to_window(self.driver.window_handles[1])
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "ctl00$Content$Chart")))
        except Exception:
            logging.warning("The page could not load")
        xfConsumption = XFConsumption()
        xfConsumption.setEndOfMonthProjection(
            self.driver.find_element_by_id(GPNPortal.endOfMonthProjectionIdentifier).text)
        summaryTable = self.driver.find_element_by_id(GPNPortal.tableId)
        xfMeasurementHtmlTable = summaryTable.find_elements_by_tag_name("td")
        xfConsumption.setXFTable(xfMeasurementHtmlTable)
        xfConsumption.setMonthlyOffset()
        xfConsumption.setSumXFConsumption(1, 31)
        return xfConsumption

    def addSubAccounts(self):
        if len(self.driver.window_handles) > 1:
            self.driver.execute_script("window.close()")
            self.driver.switch_to_window(self.driver.window_handles[0])
        # Button needs to be clicked in order to see other accounts
        self.driver.find_element_by_id("identity-btn-name").click()
        accountList = self.driver.find_element_by_id("divIdentityList")
        # Everything but the first and last element as the first element is the tr -> Switch accounts and the last tr
        # has an empty name
        accountListRows = accountList.find_elements_by_tag_name("tr")[1:-1]
        accounts = [{'name': accountListRow.text, 'node': accountListRow}
                    for accountListRow in accountListRows if accountListRow.text not in self.accountsList]
        logging.info(accounts)
        accounts[0]['node'].click()
        self.accountsList.add(accounts[0]['name'])
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "black-1")))
        except Exception:
            logging.warning("The page could not load")
        time.sleep(5)
        self.driver.save_screenshot('1.png')
        logging.info(self.accountsList)


class DynatracePortal(AbstractPortal):

    monitorAnalyzeId = "monitoranalyze"
    interactiveChartId = "apmInteractiveChart"
    chartsClass = "apm-btn-link"
    logoutId = "sign-out"
    iframeName = "apmframe"

    @property
    def homePage(self):
        return "https://www.gomezapm.com"

    @property
    def usernameInputIdentifier(self):
        return "username"

    @property
    def passwordInputIdentifier(self):
        return "pw"

    @property
    def submitButtonIdentifier(self):
        return "signIn"

    def login(self):
        """
        login()
        """
        super(DynatracePortal, self).login()
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, DynatracePortal.monitorAnalyzeId)))
        except Exception:
            logging.warning("The page could not load")
        self.driver.save_screenshot("Portal.png")

    def getCharts(self, index=0, upper=3):
        """
        """
        logging.debug("Clicking Monitor & Analyze Tab")
        self.driver.find_element_by_id(
            DynatracePortal.monitorAnalyzeId).click()
        self.driver.save_screenshot('here{}.png'.format(index))
        logging.debug("Getting chart link element")
        chartLink = self.driver.find_element_by_id(
            DynatracePortal.interactiveChartId)
        href = chartLink.get_attribute("href")
        logging.debug(href)
        self.driver.get(href)
        # try:
        self.driver.save_screenshot('here2{}.png'.format(index))
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "apmframe")))
            # Switch to iframe in order to obtain DOM elements
            self.driver.switch_to_frame(DynatracePortal.iframeName)
        except Exception:
            logging.warn("Element could not be found within the time frame")
        logging.debug("Sleeping for 5 seconds")
        time.sleep(5)
        self.driver.save_screenshot('here3{}.png'.format(index))
        test = self.driver.find_element_by_id("wrapper").get_attribute("class")
        logging.debug("Class is: {}".format(test))
        test2 = self.driver.find_element_by_class_name(
            "dataTable").get_attribute("style")
        logging.debug("Style is: {}".format(test2))
        test3 = self.driver.find_elements_by_class_name(
            DynatracePortal.chartsClass)
        logging.debug("Charts are: {}".format(test3))
        test3classes = list(filter(lambda node: DynatracePortal.chartsClass in node.get_attribute(
            "class") and node.text != '', test3))
        print("Classes are: {}".format([elem.text for elem in test3classes]))
        self.driver.save_screenshot('here4{}.png'.format(index))
        print(test3classes[0])
        print("Clicking on element")
        print(test3classes[0].click())
        # logging.debug("Saving screenshot")
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "apmframe")))
            # Switch to iframe in order to obtain DOM elements
            self.driver.switch_to_frame(DynatracePortal.iframeName)
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.TAG_NAME, "svg")))
        except Exception:
            logging.warn("Element could not be found within the time frame")
        time.sleep(25)
        self.driver.save_screenshot('here5{}.png'.format(index))

    def logout(self):
        pass
        # signOutButton = self.driver.find_element_by_id(
        #     DynatracePortal.logoutId)
        # signOutButton.click()
