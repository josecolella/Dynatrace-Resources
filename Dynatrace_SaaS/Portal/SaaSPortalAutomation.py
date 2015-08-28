from __future__ import print_function
from selenium import webdriver
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DynatracePortal(object):
    homePage = "https://www.gomezapm.com"
    usernameInputId = "username"
    passwordInputId = "password"
    submitButtonId = "signIn"
    monitorAnalyzeId = "monitoranalyze"
    interactiveChartId = "apmInteractiveChart"
    chartsClass = "apm-btn-link"
    logoutId = "sign-out"

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
        print("Finish fetching page")
        usernameInput = self.driver.find_element_by_id(
            DynatracePortal.usernameInputId)
        passwordInput = self.driver.find_element_by_id(
            DynatracePortal.passwordInputId)
        print("Sending username credentials")
        usernameInput.send_keys(self.username)
        print("Sending password credentials")
        passwordInput.send_keys(self.password)
        submitButton = self.driver.find_element_by_id(
            DynatracePortal.submitButtonId)
        print("Sending button click")
        submitButton.click()
        print("Waiting for page to load")
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, DynatracePortal.monitorAnalyzeId)))
        except Exception:
            print("The page could not load")

    def getCharts(self):
        """
        """
        print("Clicking Monitor & Analyze Tab")
        self.driver.find_element_by_id(
            DynatracePortal.monitorAnalyzeId).click()
        self.driver.save_screenshot('here.png')
        print("Getting chart link element")
        chartLink = self.driver.find_element_by_id(
            DynatracePortal.interactiveChartId)
        href = chartLink.get_attribute("href")
        print(href)
        self.driver.get(href)
        try:
            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "p-synthetic-icon")))
            WebDriverWait(self.driver, 10).until(
                EC.eleme(By.CLASS_NAME, "gwt-Image"))
            self.driver.save_screenshot('charts5.png')
            tests = [elem.get_attribute("class") for elem in self.driver.find_elements_by_class_name(DynatracePortal.chartsClass) if elem.find("apm-table-data-cell") != -1]
            print(tests)
        except Exception:
            self.driver.save_screenshot('charts5.png')
            print("The page could not load")


    def logout(self):
        pass
        # signOutButton = self.driver.find_element_by_id(
        #     DynatracePortal.logoutId)
        # signOutButton.click()

    def close(self):
        self.driver.quit()
