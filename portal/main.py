import argparse
import logging
import Portal
import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="Dynatrace Synthetic Screenshot Automation")
    parser.add_argument(
        "-u", "--username", help="The username for the account", type=str, required=True)
    parser.add_argument(
        "-p", "--password", help="The password for the account", type=str, required=True)
    parser.add_argument(
        "-d", "--directory", help="The directory to save the chart screenshots", type=str, default=".")
    parser.add_argument(
        "-v", "--verbose", help="Display debug message", action="store_true")
    parser.add_argument(
        "-c", "--chart-names", nargs="+", help="The name of the chart to capture")
    args = parser.parse_args()
    print("Initializing Phantom JS web driver")
    portal = Portal.DynatracePortal(args.username, args.password)
    print("Initialized Phantom JS web driver")
    print("Logging in to Dynatrace portal")
    portal.login()
    print("Successfully logged in to Dynatrace portal")
    for chart in tqdm.tqdm(args.chart_names):
        tqdm.tqdm.write("Beginning to process chart: {}".format(chart))
        portal.saveChartToScreenshot(
            chartName=chart, specificElements=["tag", "svg", "class", "gwt-ScrollTable"], saveDir=args.directory)
        tqdm.tqdm.write("Finished saving image: \"{chartName}\" screenshot to {directory} directory".format(
            chartName=chart, directory=args.directory))
