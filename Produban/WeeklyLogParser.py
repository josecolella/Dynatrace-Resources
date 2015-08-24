import sys
import re
import pprint


"""
To do:
	- Add web interaction to get the string argument
directly from web instead of having to manually put the
argument as a command line argument

"""

def getSumXFConsumption(dates):
	listDates = dates.split('\n')
	xfConsumptionRegex = re.compile(r'(?P<xfConsumption>[\d,]+$)')
   	# Only the last digits are grouped, the comma is removed, and converted to int
	xfConsumptionWeekly = [int(re.sub(r',', '', re.search(xfConsumptionRegex, i).group('xfConsumption'))) for i in listDates]

	sumXFConsumption = sum(xfConsumptionWeekly)
	return {
		"list": xfConsumptionWeekly,
		"sum": sumXFConsumption
	}


try:
	pp = pprint.PrettyPrinter()
	dates = sys.argv[1]
	consumptionStruct = getSumXFConsumption(dates)
	
	print("XF Consumption List")
	print(consumptionStruct["list"])
	print("Sum of XF Consumption")
	print(consumptionStruct["sum"])
except IndexError:
	print("""At least one argument required.
Example:

05 Jul 2015 1,546   10,260  0   11,806
06 Jul 2015 1,520   10,260  0   11,780
07 Jul 2015 1,530   10,247  0   11,777
08 Jul 2015 1,524   10,257  0   11,781
09 Jul 2015 1,516   10,261  0   11,777
10 Jul 2015 1,494   10,209  0   11,703
11 Jul 2015 1,506   10,272  0   11,778
12 Jul 2015 1,470   10,193  0   11,663""")
