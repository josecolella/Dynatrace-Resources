from __future__ import print_function
from selenium import webdriver
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DynatracePortal(object):
    homePage = "https://www.gomezapm.com"
    usernameInputId = "username"
    passwordInputId = "password"
    submitButtonId = "signIn"
    monitorAnalyzeId = "monitoranalyze"
    interactiveChartId = "apmInteractiveChart"
    chartsClass = "apm-btn-link"
    logoutId = "sign-out"
    iframeName = "apmframe"

    def __init__(self, username, password):
        """
        Args
        ----
        username: string
        password: string
        """
        # assert type(username) == "string", print("username is a string")
        # assert type(password) == "string", print("password is a string")
        # Make constant
        self.username = username
        # Make constant
        self.password = password
        self.driver = webdriver.PhantomJS(service_log_path="/dev/null")
        print("Initialized PhantomJS driver")
        self.driver.maximize_window()
        self.windowSize = self.driver.get_window_size()

    def login(self):
        """
        login()
        """
        logging.debug("Fetching Dynatrace Login Page")
        self.driver.get(DynatracePortal.homePage)
        logging.debug("Finish fetching page")
        usernameInput = self.driver.find_element_by_id(
            DynatracePortal.usernameInputId)
        passwordInput = self.driver.find_element_by_id(
            DynatracePortal.passwordInputId)
        logging.debug("Sending username credentials")
        usernameInput.send_keys(self.username)
        logging.debug("Sending password credentials")
        passwordInput.send_keys(self.password)
        submitButton = self.driver.find_element_by_id(
            DynatracePortal.submitButtonId)
        logging.debug("Sending button click")
        submitButton.click()
        logging.debug("Waiting for page to load")
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, DynatracePortal.monitorAnalyzeId)))
        except Exception:
            logging.warning("The page could not load")

    def getCharts(self):
        """
        """
        logging.debug("Clicking Monitor & Analyze Tab")
        self.driver.find_element_by_id(
            DynatracePortal.monitorAnalyzeId).click()
        self.driver.save_screenshot('here.png')
        logging.debug("Getting chart link element")
        chartLink = self.driver.find_element_by_id(
            DynatracePortal.interactiveChartId)
        href = chartLink.get_attribute("href")
        logging.debug(href)
        self.driver.get(href)
        # try:
        self.driver.save_screenshot('here2.png')
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "apmframe")))
            # Switch to iframe in order to obtain DOM elements
            self.driver.switch_to_frame(DynatracePortal.iframeName)
        except Exception:
            logging.warn("Element could not be found within the time frame")
        logging.debug("Sleeping for 5 seconds")
        time.sleep(5)
        self.driver.save_screenshot('here3.png')
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
        logging.debug("Classes are: {}".format([elem.text for elem in test3classes]))
        # Not moving to chart. Fails on the click
        # logging.debug("\nClicking on first chart: {}\n".format(
        #     test3classes[0].get_attribute("class")))
        # test3classes[0].click()
        # logging.debug("Saving screenshot")
        # self.driver.save_screenshot('here4.png')

    def logout(self):
        pass
        # signOutButton = self.driver.find_element_by_id(
        #     DynatracePortal.logoutId)
        # signOutButton.click()

    def close(self):
        self.driver.quit()
