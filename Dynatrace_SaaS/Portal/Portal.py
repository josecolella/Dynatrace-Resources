from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from abc import ABCMeta
from abc import abstractmethod
import logging
import time
import numpy as np
import re


class XFConsumption(object):

    """XFConsumption represents the class that encapsulates everything that
    has to do with the XFConsumption window that pop-up when clicking the admin tab
    in the GPN portal"""

    def __init__(self):
        self.usage = None
        self.endOfMonthProjection = None

    def _sanitizeIntegerString(self, intString):
        """
        _sanitizeIntegerString('124,14') -> 12414

        Returns:
            int: The integer from the string, removing any punctuation
        """
        sanitizedInteger = int(re.sub(r',', '', intString))
        return sanitizedInteger

    def _sanitizeXFTable(self):
        # TODO
        lettersRegex = re.compile(r'[a-zA-Z]')
        print(self.tableRows)
        # for element, index in zip(self.tableRows, range(self.tableRows.size)):
            # if not re.search(lettersRegex, element):
                # self.tableRows[index] = self._sanitizeIntegerString(element)

    def setTableRows(self, tableRowsHTML):
        # TODO
        self.tableRows = np.array([elem.text for elem in tableRowsHTML])
        self._sanitizeXFTable()
        # self.tableRows.resize(self.TableRows.size / 3, self.TableRows.size / 3)


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
    xfConsumptionPage = "https://www.gomeznetworks.com/reports/flexReport.aspx?x=&startdate=2015/9/1&enddate=2015/9/30"
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

    def getXFConsumption(self, startDate, endDate):
        # Open a new tab
        body = driver.find_element_by_tag_name("body")
        body.send_keys(Keys.CONTROL + 't')
        self.driver.get(GPNPortal.xfConsumptionPage)
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, endOfMonthProjectionIdentifier)))
        except Exception:
            logging.warning("The page could not load")
        xfConsumption = XFConsumption()
        xfConsumption.endOfMonthProjection = self.driver.find_element_by_id(
            GPNPortal.endOfMonthProjectionIdentifier).text
        print("End of the month Projection: {}".format(
            xfConsumption.endOfMonthProjection))
        summaryTable = self.driver.find_element_by_id(
            GPNPortal.tableId)
        xfMeasurementHtmlTable = summaryTable.find_elements_by_tag_name("td")
        xfConsumption.setTableRows(xfMeasurementHtmlTable)
        print("Table Rows: {}".format(xfConsumption.tableRows))

    def setAccounts(self):
        # Button needs to be clicked in order to see other accounts
        self.driver.find_element_by_id("identity-btn-name").click()
        accountList = self.driver.find_element_by_id("divIdentityList")
        # Everything but the first and last element as the first element is the tr -> Switch accounts and the last tr
        # has an empty name
        accountListRows = accountList.find_elements_by_tag_name("tr")[1:-1]
        self.accounts = [{'name': accountListRow.text, 'node': accountListRow}
                         for accountListRow in accountListRows]
