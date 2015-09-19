from __future__ import print_function
import re
import json
import datetime
import calendar

__version__ = "1.0.0"
__author__ = "Jose Miguel Colella"
__email__ = "jose.colella@dynatrace.com"
__license__ = "MIT"


class XFMeasurement(object):

    """XFMeasurement represents the class that encapsulates everything that
    has to do with the XFMeasurement window that pop-up when clicking the
    admin tab in the GPN portal"""

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

    def setEndOfMonthProjection(self, projection):
        assert type(projection) == str, print(
            "End of Month Projection is a string")
        self.endOfMonthProjection = self._sanitizeIntegerString(projection)

    def _getNumberOfColumns(self, tableRowsList):
        assert type(tableRowsList) is list, print(
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

    def setSumXFMeasurement(self, startDay=1, endDay=calendar.monthrange(datetime.date.today().year, datetime.date.today().month)[1]):
        """
        setSumXFMeasurement(startDay, endDay) -> sets the sum of the xfconsumption measures

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
        self.xfSumConsumption = sum(xfConsumptionValues)

    def setMonthlyOffset(self, endDay=calendar.monthrange(datetime.date.today().year, datetime.date.today().month)[1]):
        """
        setMonthlyOffset() -> sets the monthly offset
        """
        assert self.xfTable is not None, print("xfTable can not be None")
        # Can be optimized using dates
        self.monthlyOffset = sum([elem["value"]
                                  for elem in self.xfTable][:endDay])

    def __str__(self):
        xfConsumptionString = json.dumps({
            "XFConsumption": [
                {"Sum of XF Measurements": self.xfSumConsumption},
                {"Monthly Offset": self.monthlyOffset},
                {"End of Month Projection": self.endOfMonthProjection}
            ]
        })
        return xfConsumptionString
