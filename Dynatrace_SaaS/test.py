from __future__ import print_function
import urllib.request as http
import json


class SaaSWrapper(object):
    server = "https://datafeed-api.dynatrace.com"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.loginToken = None
        self.tests = {}
        self.authenticationHeader = {}
        self.testResult = None

    def login(self):
        loginUri = "{server}/publicapi/rest/v1.0/login?user={username}&password={password}".format(
            server=SaaSWrapper.server,
            username=self.username,
            password=self.password)
        request = http.urlopen(loginUri)
        self.loginToken = (request.read()).decode(encoding="utf-8")

    def getTests(self):
        assert self.loginToken is not None, "The authentication token must be initialized"
        testUri = "{server}/publicapi/rest/v1.0/tests?testType=backbone".format(
            server=SaaSWrapper.server)
        self.authenticationHeader = {
            "Authentication": "bearer {token}".format(token=self.loginToken)}
        requestObject = http.Request(
            testUri, None, self.authenticationHeader)
        request = http.urlopen(requestObject)
        self.tests = json.loads((request.read()).decode(encoding="utf-8"))

    def getTestResults(self, monitorID):
        testResultUri = "{server}/publicapi/rest/v1.0/testresults/{monitorId}?detailLevel=ALL&time=ARRIVAL".format(server=SaaSWrapper.server, monitorId=monitorID)
        self.authenticationHeader = {
            "Authentication": "bearer {token}".format(token=self.loginToken)}
        requestObject = http.Request(
            testResultUri, None, self.authenticationHeader)
        request = http.urlopen(requestObject)
        self.testResult = json.loads((request.read()).decode(encoding="utf-8"))

if __name__ == '__main__':
    username = "pyang.barclays"
    password = "C0mpuw@r3"
    saas = SaaSWrapper(username, password)
    saas.login()
    print("The bearerToken is :{}".format(saas.loginToken))
    saas.getTests()
    print("Tests")
    print(saas.tests)
    saas.getTestResults(21714842)
    print("Test Results")
    print(saas.testResult)
