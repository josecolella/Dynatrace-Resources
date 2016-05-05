#!/usr/bin/env python3
from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from abc import ABCMeta
from abc import abstractmethod
from PIL import Image
import PortalProperties
import datetime
import calendar
import logging
import time
import re
import os

__version__ = "1.0.1"
__author__ = "Jose Miguel Colella"
__email__ = "jose.colella@dynatrace.com"
__license__ = "MIT"

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="portal.log", format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)


class AbstractPortal(object):

    """AbstractPortal is an abstract class that encapsulates all the
    common attributes and methods of the Synthetic Portal such as
    username, password, login


    Attributes:
        driver (selenium.webdriver.phantomjs.webdriver.WebDriver): The webdriver instance
    """
    __metaclass__ = ABCMeta
    screenshotDebugDir = "screenshotDebug"

    def __init__(self, username, password):
        assert type(username) is str, print("username is a string")
        assert type(password) is str, print("password is a string")
        # If the operating system is windows or *nix.
        self._osNull = {
            "nt": "NUL",
            "posix": "/dev/null"
        }
        self.driver = webdriver.PhantomJS(
            service_log_path=self._osNull[os.name], service_args=["--ignore-ssl-errors=true"])
        self.driver.maximize_window()
        self.windowSize = self.driver.get_window_size()
        self._username = username
        self._password = password
        self._screenshotDebugDumpDirPath = "{path}/{directory}".format(
            path=os.getcwd(), directory=AbstractPortal.screenshotDebugDir)
        self._checkDumpDirIsCreated()

    @property
    @abstractmethod
    def homePage(self):
        """
        str: The url of the portal
        """
        pass

    @property
    @abstractmethod
    def usernameInputIdentifier(self):
        """
        str: The DOM attribute to fetch the username <input>
        """
        pass

    @property
    @abstractmethod
    def passwordInputIdentifier(self):
        """
        str: The DOM attribute to fetch the password <input>
        """
        pass

    @property
    @abstractmethod
    def submitButtonIdentifier(self):
        """
        str: The DOM attribute to fetch the log in button
        """
        pass

    @property
    def username(self):
        """
        str: The username used to login. (Read-Only)
        """
        return self._username

    @property
    def password(self):
        """
        str: The password used to login.(Read-Only)
        """
        return self._password

    def _checkDumpDirIsCreated(self):
        if not os.path.isdir(self.screenshotDebugDir):
            os.mkdir(self._screenshotDebugDumpDirPath)

    def _saveDebugScreenshot(self, screenshotName):
        self.driver.save_screenshot(
            "{}/{}-{}.png".format(AbstractPortal.screenshotDebugDir, datetime.datetime.today(), screenshotName))

    def login(self):
        """login() inputs the username and password into the corresponding DOM elements
        of the home page and establishes a session that allows for the interaction
        """
        logging.debug("Fetching Dynatrace Login Page")
        self.driver.get(self.homePage)
        logging.debug("Finish fetching page")
        self._saveDebugScreenshot("Home")
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
        """Closes the driver session and the phantomjs process.
        """
        self.driver.quit()


class GPNPortal(AbstractPortal):

    tableId = "ctl00_Content_XFSummaryTable"
    endOfMonthProjectionIdentifier = "ctl00_Content_XFProjectedUsage"
    accountsListIdentifier = "identity-btn-name"
    accountsListDropdownIdentifier = "divIdentityList"

    def __init__(self, username, password):
        super(GPNPortal, self).__init__(username, password)
        self.accountsList = set()
        self.accountNameRegex = re.compile(r":(?P<accountName>.+):")

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

    def _getCurrentAccountName(self):
        currentAccountName = self.driver.find_element_by_id(
            "identity-btn-name").text
        return currentAccountName

    def login(self):
        super(GPNPortal, self).login()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "black-1")))
        except Exception:
            logging.warning("The page could not load")
        time.sleep(5)
        self.portalWindow = self.driver.current_window_handle
        self._saveDebugScreenshot("Login")

    def getXFMeasurement(self, startDay=1, endDay=calendar.monthrange(datetime.date.today().year, datetime.date.today().month)[1], startMonth=datetime.date.today().month, endMonth=datetime.date.today().month):
        """getXFMeasurement(startDay, endDay, startMonth, endMonth) returns the XF consumption for the current account
        calculating the monthly offset, end of month projection, and the sum of the xf measurements from `startDay` to
        `endDay`

        Args:
            startDay (Optional[int]): The initial day to get the XF measurements. Defaults to 1
            endDay (Optional[int]): The last day to get the XF measurements. Defaults to the last day of the month
            startMonth (Optional[int]): The starting month from which to fetch the XF measurements. Defaults to current month
            endMonth (Optional[int]): The ending month from which to fetch the XF measurem

        Returns:
            XFMeasurement: an instance of the XFMeasurement class initialized with the monthly offset, end of month projection, and the sum of the
            XF measurements from `startDay` to `endDay`

        Raises:
            AssertionError: If `startMonth` is not equal to `endMonth`. The GPN Portal will only show XF consumption
            measurement one month at a time
        """
        assert startMonth == endMonth, "Expected startMonth to be equal to endMonth. {} is not equal to {}".format(
            startMonth, endMonth)
        currentYear = datetime.date.today().year
        xfConsumptionPage = "https://www.gomeznetworks.com/reports/flexReport.aspx?x=&startdate={startYear}/{startMonth}/{startDay}&enddate={endYear}/{endMonth}/{endDay}".format(
            startYear=currentYear,
            startMonth=startMonth,
            startDay=startDay,
            endYear=currentYear,
            endMonth=endMonth,
            endDay=endDay
        )
        self.driver.execute_script(
            "window.open('{}')" .format(xfConsumptionPage))
        self.driver.switch_to_window(self.driver.window_handles[1])
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "ctl00$Content$Chart")))
        except Exception:
            logging.warning("The page could not load")
        print("Account: {}".format(
            self.driver.find_element_by_class_name("black-1").text))
        xfConsumption = PortalProperties.XFMeasurement()
        xfConsumption.setEndOfMonthProjection(
            self.driver.find_element_by_id(GPNPortal.endOfMonthProjectionIdentifier).text)
        summaryTable = self.driver.find_element_by_id(GPNPortal.tableId)
        xfMeasurementHtmlTable = summaryTable.find_elements_by_tag_name("td")
        xfConsumption.setXFTable(xfMeasurementHtmlTable)
        xfConsumption.setSumXFMeasurement(startDay, endDay)
        xfConsumption.setMonthlyOffset(endDay)
        return xfConsumption

    def switchAccount(self):
        if len(self.driver.window_handles) > 1:
            self.driver.execute_script("window.close()")
            self.driver.switch_to_window(self.driver.window_handles[0])
        cleanAccountName = lambda account: (
            re.search(self.accountNameRegex, account).group("accountName")).strip()
        self.accountsList.add(cleanAccountName(self._getCurrentAccountName()))
        # Button needs to be clicked in order to see other accounts
        self.driver.find_element_by_id(
            GPNPortal.accountsListIdentifier).click()
        accountList = self.driver.find_element_by_id(
            GPNPortal.accountsListDropdownIdentifier)
        # Everything but the first and last element as the first element is the tr -> Switch accounts and the last tr
        # has an empty name
        accountListRows = accountList.find_elements_by_tag_name("tr")[1:-1]
        accounts = [{"name": cleanAccountName(accountListRow.text), "node": accountListRow}
                    for accountListRow in accountListRows if cleanAccountName(accountListRow.text) not in self.accountsList]
        logging.info(accounts)
        # Click the first account in the dropdown
        accounts[0]["node"].click()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "black-1")))
        except Exception:
            logging.warning("The page could not load")
        time.sleep(5)
        logging.info("Current Account: {}".format(
            cleanAccountName(self._getCurrentAccountName())))
        self._saveDebugScreenshot("SwitchAccount.png")
        logging.info(self.accountsList)


class DynatracePortal(AbstractPortal):

    monitorAnalyzeId = "monitoranalyze"
    interactiveChartId = "apmInteractiveChart"
    chartsClass = "apm-btn-link"
    logoutId = "sign-out"
    iframeName = "apmframe"
    chartsUrl = "http://cr02.dynatrace.com/en_US/group/guest/interactive-charts"

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

    def __init__(self, username, password):
        super(DynatracePortal, self).__init__(username, password)
        # Sets the driver to wait 10 seconds to poll the DOM. Very useful for
        # sites like Dynatrace Portal that take a while to load elements
        self.driver.implicitly_wait(10)
        self.chartsCaptured = set()
        self.currentAccountName = self.username
        self.croppingChartsDimension = {
            "left": 675,
            "up": 270,
            "right": 675,
            "down": 150
        }
        self.performanceMapDimension = {
            "right": 600,
            "up": 285,
            "left": 600,
            "down": 400
        }

    def _cropChart(self, imgFile, isPerformanceMap=False):
        chartImage = Image.open(imgFile)

        half_the_width = chartImage.size[0] // 2
        half_the_height = chartImage.size[1] // 2
        if not isPerformanceMap:
            croppedImage = chartImage.crop(
                (
                    half_the_width - self.croppingChartsDimension["right"],
                    half_the_height - self.croppingChartsDimension["up"],
                    half_the_width + self.croppingChartsDimension["left"],
                    half_the_height + self.croppingChartsDimension["down"]
                )
            )
        else:
            croppedImage = chartImage.crop(
                (
                    half_the_width - self.performanceMapDimension["right"],
                    half_the_height - self.performanceMapDimension["up"],
                    half_the_width + self.performanceMapDimension["left"],
                    half_the_height + self.performanceMapDimension["down"]
                )
            )
        croppedImage.save(imgFile)

    def login(self):
        super(DynatracePortal, self).login()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, DynatracePortal.monitorAnalyzeId)))
            logging.info(
                "Successfully logged in with user: {}".format(self.username))
        except Exception:
            logging.warning("WARNING: The login page could not load")
        logging.debug("Sleeping for 15 seconds")
        time.sleep(15)
        self._saveDebugScreenshot("Login")

    def getInteractiveCharts(self):
        logging.debug("navigating to charts URL")
        self.driver.get(DynatracePortal.chartsUrl)
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "dataTable")))
            # Switch to iframe in order to obtain DOM elements
            # self.driver.switch_to_frame(DynatracePortal.iframeName)
        except Exception:
            logging.warn(
                "WARNING: Element could not be found within the time frame")
        logging.debug("Sleeping for 15 seconds")
        time.sleep(15)
        self._saveDebugScreenshot("ChartsAvailable")

    def getChartPage(self, chartName):
        self.getInteractiveCharts()
        availableCharts = self.driver.find_elements_by_class_name(
            DynatracePortal.chartsClass)
        try:
            chartNodes = filter(
                lambda node: node.text == chartName and node.text != "", availableCharts)
            chartNode = next(chartNodes)
            # Click on chart node
            chartNode.click()
            logging.debug("Sleeping for 20 seconds")
            time.sleep(20)
        except Exception:
            raise Exception("Expected valid chart name. Available charts are: {}".format(
                [elem.text for elem in availableCharts]))

    def saveChartToScreenshot(self, chartName, cropChart=False, saveDir="."):
        """saveChartToScreenshot saves a screenshot of the `chartName` provided
        as a parameter.


        Args:
            chartName (str): The name of the chart to get the screenshot
            cropChart (Optional[bool]): Crop only chart section. Defaults to False
            saveDir (Optional[str]): The directory to save the screenshot. Defaults to '.'
        """
        self.getChartPage(chartName)
        imageName = "{}/{}.png".format(saveDir, chartName)
        self.driver.save_screenshot(imageName)
        if cropChart:
            self._cropChart(imageName)
        logging.info("Finished saving {chartName} screenshot to {directory} directory".format(
            chartName=chartName, directory=saveDir))
