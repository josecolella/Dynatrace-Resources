from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from abc import ABCMeta
from abc import abstractmethod
import logging
import time
import re

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
        self.driver = webdriver.PhantomJS(service_log_path="/dev/null")
        self.driver.maximize_window()
        self.windowSize = self.driver.get_window_size()
        self._username = username
        self._password = password

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @abstractmethod
    def login(self):
        pass

    def close(self):
        self.driver.quit()


class GPNPortal(AbstractPortal):

    homePage = "https://www.gomeznetworks.com/index.asp?g=1"
    usernameInputName = "username"
    passwordInputName = "pwd"
    submitButtonClass = "Login-Button"
    tableId = "ctl00_Content_XFSummaryTable"
    endOfMonthProjectionIdentifier = "ctl00_Content_XFProjectedUsage"

    def login(self):
        logging.debug("Fetching Dynatrace Login Page")
        self.driver.get(GPNPortal.homePage)
        logging.debug("Finish fetching page")
        self.driver.save_screenshot('gpn-portal.png')
        usernameInput = self.driver.find_element_by_name(
            GPNPortal.usernameInputName)
        passwordInput = self.driver.find_element_by_name(
            GPNPortal.passwordInputName)
        logging.debug("Sending username credentials")
        usernameInput.send_keys(self.username)
        logging.debug("Sending password credentials")
        passwordInput.send_keys(self.password)
        submitButton = self.driver.find_element_by_class_name(
            GPNPortal.submitButtonClass)
        logging.debug("Sending button click")
        submitButton.click()
        logging.debug("Waiting for page to load")
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "theme")))
        except Exception:
            logging.warning("The page could not load")
        time.sleep(5)
        self.driver.save_screenshot("gpn2.png")

    def getXFConsumption(self, startDate=0, endDate=0):
        # Open a new tab TODO
        body = self.driver.find_element_by_tag_name("body")
        body.send_keys(Keys.COMMAND + 't')
        xfConsumptionPage = "https://www.gomeznetworks.com/reports/flexReport.aspx?x=&startdate=2015/8/1&enddate=2015/8/30"
        self.driver.get(xfConsumptionPage)
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
        xfconsumption.setMonthlyOffset()
        xfconsumption.setSumXFConsumption(1, 31)
        return xfConsumption

    def setAccounts(self):
        # Button needs to be clicked in order to see other accounts
        self.driver.find_element_by_id("identity-btn-name").click()
        accountList = self.driver.find_element_by_id("divIdentityList")
        # Everything but the first and last element as the first element is the tr -> Switch accounts and the last tr
        # has an empty name
        accountListRows = accountList.find_elements_by_tag_name("tr")[1:-1]
        self.accounts = [{'name': accountListRow.text, 'node': accountListRow}
                         for accountListRow in accountListRows]
