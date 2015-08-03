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
        self.authenticationHeader = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip,deflate"
        }
        self.testResult = None

    def login(self):
        """
        login() -> Initializes the login token required for any resource retrieval in the REST API
        """
        loginUri = "{server}/publicapi/rest/v1.0/login?user={username}&password={password}".format(
            server=SaaSWrapper.server,
            username=self.username,
            password=self.password)
        request = http.urlopen(loginUri)
        self.loginToken = (request.read()).decode(encoding="utf-8")

    def getTests(self):
        """
        getTests() -> Returns all the tests that are present and stores them in self.tests
        """
        self._isTokenInitialized()
        testUri = "{server}/publicapi/rest/v1.0/tests?testType=backbone".format(
            server=SaaSWrapper.server)
        self.authenticationHeader["Authentication"] = "bearer {token}".format(token=self.loginToken)
        requestObject = http.Request(
            testUri, None, self.authenticationHeader)
        request = http.urlopen(requestObject)
        self.tests = json.loads((request.read()).decode(encoding="utf-8"))

    def getTestResults(self, monitorId, start, end):
        """
        getTestResults(monitorId, start, end) -> Fetches the test results for a specific test provided the monitor id
        of the test, the starting timestamp, and ending timestamp

        ----------------
        Arguments:
            - monitorId: int
                the monitor id corresponding to the test
            - start: int
                timestamp for the starting timerange for the test
            - end: int
                timestamp for the ending timerange for the test
        """
        self._isTokenInitialized()
        testResultUri = "{server}/publicapi/rest/v1.0/testresults/{monitorId}?start={start}&end={end}&detailLevel=TEST".format(
            server = SaaSWrapper.server,
            start = start,
            end = end,
            monitorId = monitorId)
        self.authenticationHeader["Authentication"] = "bearer {token}".format(token=self.loginToken)
        requestObject = http.Request(
            testResultUri, None, self.authenticationHeader)
        request = http.urlopen(requestObject)
        self.testResult = json.loads((request.read()).decode(encoding="utf-8"))

    def _isTokenInitialized(self):
        assert self.loginToken is not None, "The authentication token must be initialized"


if __name__ == '__main__':
    username = "pyang.barclays"
    password = "C0mpuw@r3"
    saas = SaaSWrapper(username, password)
    saas.login()
    print("The bearerToken is :{}".format(saas.loginToken))
    saas.getTests()
    print("Tests")
    print(saas.tests)
    # Fails here
    saas.getTestResults(21714841, 1437350400, 1437436800)
    print("Test Results")
    print(saas.testResult)
