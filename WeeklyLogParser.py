import sys
import re

"""
To do:
	- Add web interaction to get the string argument
directly from web instead of having to manually put the 
argument as a command line argument

"""

try:
	dates = sys.argv[1]
	listDates = dates.split('\n')
	xfConsumptionRegex = re.compile(r'[\d,]+$')

	xfConsumptionWeekly = [int(re.sub(r',', '', re.search(xfConsumptionRegex, i).group())) for i in listDates]

	sumXFConsumption = sum(xfConsumptionWeekly)

#print("List of Dates")
#print(listDates)
	print("XF Consumption List")
	print(xfConsumptionWeekly)
	print("Sum of XF Consumption")
	print(sumXFConsumption)
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
